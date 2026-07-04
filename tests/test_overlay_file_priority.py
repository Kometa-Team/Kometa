"""
Tests for Overlay._resolve_image_path() — decides which image asset backs an overlay when
multiple sources are configured at once (`file`, `default`, `pmm`, `git`, `repo`, `url`).

Regression coverage for a bug reported against build34/35 (PR #3253, "overlay cache redesign"):
that PR gave critic/audience ratings real built-in default assets (Critic.png, CriticFresh.png,
etc.) for the first time. Before that, `rating<n>_default` for those rating types resolved to
nothing, so a `file:` override always won by accident -- the "default wins over file" branch
ordering in this method existed but was dormant. Once real default assets shipped, any overlay
that combined a custom `file:` with a resolvable `default:` (e.g. `rating1: critic` +
`rating1_file: /config/images/mal-rounded.png`) silently got the built-in asset instead of the
user's file. `file` (and the other explicit overrides: `git`, `repo`, `url`) must always win over
a built-in `default`/`pmm`/PMM-git asset.
"""

from unittest.mock import MagicMock

from modules import overlay as overlay_module
from modules.overlay import Overlay


def _make_overlay(data, config=None, library=None, requests=None, name="text(<<critic_rating>>)"):
    """Minimal Overlay stub -- bypasses __init__, wires only what _resolve_image_path needs."""
    ov = Overlay.__new__(Overlay)
    ov.data = data
    ov.name = name
    ov.config = config or MagicMock()
    ov.library = library or MagicMock()
    ov.requests = requests or MagicMock()
    return ov


# ── The regression: file + a resolvable built-in default ───────────────────────


def test_file_wins_over_default_when_both_set():
    # Antwan's exact reported config: rating1: critic with a custom file, where "default" also
    # resolves to a real built-in asset (Critic/CriticFresh/CriticRotten shipped in #3253).
    ov = _make_overlay({"file": "/config/images/mal-rounded.png", "default": "rating/CriticFresh"})

    assert ov._resolve_image_path() == "/config/images/mal-rounded.png"


def test_file_wins_over_default_rotten_variant():
    ov = _make_overlay({"file": "/config/images/mal-rounded.png", "default": "rating/CriticRotten"})

    assert ov._resolve_image_path() == "/config/images/mal-rounded.png"


def test_file_wins_over_pmm():
    ov = _make_overlay({"file": "/config/images/anilist.png", "pmm": "rating/Star"})

    assert ov._resolve_image_path() == "/config/images/anilist.png"


def test_file_wins_over_pmm_prefixed_git():
    ov = _make_overlay({"file": "/config/images/anilist.png", "git": "PMM/rating/Star"})

    assert ov._resolve_image_path() == "/config/images/anilist.png"


# ── Existing behavior that must not regress ─────────────────────────────────────


def test_default_used_when_no_file_present():
    # No file override -- the built-in default asset should still resolve normally.
    ov = _make_overlay({"default": "rating/Critic"})
    path = ov._resolve_image_path()

    assert path is not None
    assert path.replace("\\", "/").endswith("defaults/overlays/images/rating/Critic.png")


def test_default_ignored_when_file_is_blank_string():
    # An empty/falsy file value must not block the default branch.
    ov = _make_overlay({"file": "", "default": "rating/Critic"})
    path = ov._resolve_image_path()

    assert path is not None
    assert path.replace("\\", "/").endswith("defaults/overlays/images/rating/Critic.png")


def test_git_used_when_present_and_not_pmm(tmp_path, monkeypatch):
    # A plain (non-"PMM/"-prefixed) git reference is a user override, same tier as `file`.
    # modules.overlay.logger is only wired up at runtime by kometa.py's startup, so stub it
    # here since get_and_save_image logs when it has to create the overlay folder.
    monkeypatch.setattr(overlay_module, "logger", MagicMock())
    requests = MagicMock()
    response = MagicMock(status_code=200, headers={"Content-Type": "image/png"}, content=b"")
    requests.get.return_value = response
    config = MagicMock()
    config.GitHub.configs_url = "https://example.com/"
    library = MagicMock()
    library.overlay_folder = str(tmp_path / "overlays")

    ov = _make_overlay({"git": "someuser/repo"}, config=config, library=library, requests=requests)
    ov._resolve_image_path()

    requests.get.assert_called_once_with("https://example.com/someuser/repo.png")


def test_git_not_fetched_when_file_present():
    # file must pre-empt a plain git reference too -- no network call should happen.
    requests = MagicMock()
    ov = _make_overlay({"file": "/config/images/mal-rounded.png", "git": "someuser/repo"}, requests=requests)

    assert ov._resolve_image_path() == "/config/images/mal-rounded.png"
    requests.get.assert_not_called()


def test_none_when_nothing_configured():
    ov = _make_overlay({})

    assert ov._resolve_image_path() is None


def test_missing_default_asset_raises():
    # Built-in branch still validates the asset exists on disk.
    ov = _make_overlay({"default": "rating/DoesNotExist"})

    try:
        ov._resolve_image_path()
        assert False, "expected OverlayError"
    except Exception as e:
        assert type(e).__name__ == "OverlayError"
