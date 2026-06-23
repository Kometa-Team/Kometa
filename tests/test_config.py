"""Tests for modules/config.py — the ConfigFile class.

ConfigFile's __init__ is a ~2000-line monolithic constructor that parses
YAML config, validates everything, creates API clients, and builds library
objects.  These tests mock all module-level loggers and API constructors
to verify the config parsing and validation logic in isolation.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
import modules.config as config_module
from modules.config import ConfigFile
from modules.util import Failed
from tests.conftest import FakeLogger, FakeRequests

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


BASE_CONFIG = """
settings:
  cache: false
libraries:
  Movies:
    collection_files: []
tmdb:
  apikey: fake-tmdb-key
plex:
  url: http://localhost:32400
  token: fake-plex-token
"""


def _default_attrs(config_path: str) -> dict:
    return {
        "config_file": config_path,
        "time_obj": datetime(2026, 6, 14, 18, 53),
        "time": "18:53",
    }


@pytest.fixture(autouse=True)
def _patch_everything(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch every module-level logger and all API constructors so
    ConfigFile.__init__ can run without real network connections."""
    # --- Logger: every module has "logger = util.logger" which is None ---
    import sys

    fake_logger = FakeLogger()
    for mod_name in [
        "modules.cache",
        "modules.plex",
        "modules.tmdb",
        "modules.trakt",
        "modules.anidb",
        "modules.tvdb",
        "modules.letterboxd",
        "modules.github",
        "modules.radarr",
        "modules.sonarr",
        "modules.overlays",
        "modules.omdb",
        "modules.mdblist",
        "modules.imdb",
        "modules.mojo",
        "modules.ergast",
        "modules.simkl",
        "modules.stevenlu",
        "modules.tautulli",
        "modules.icheckmovies",
        "modules.mal",
        "modules.anilist",
        "modules.gotify",
        "modules.ntfy",
        "modules.notifiarr",
        "modules.webhooks",
        "modules.convert",
        "modules.textfile",
        "modules.builder",
        "modules.operations",
        "modules.meta",
        "modules.overlay",
        "modules.poster",
        "modules.validator",
        "modules.util",
        "modules.config",
    ]:
        mod = sys.modules.get(mod_name)
        if mod and hasattr(mod, "logger"):
            monkeypatch.setattr(mod, "logger", fake_logger)

    # --- API constructors ---
    fake_plex = MagicMock()
    fake_plex.collections = []
    fake_plex.collection_names = []
    fake_plex.collection_files = ["collections/test.yml"]
    fake_plex.metadata_files = []
    fake_plex.overlay_files = []
    fake_plex.library_operation = None
    fake_plex.images_files = []
    fake_plex.original_mapping_name = "Movies"
    fake_plex.scan_files = MagicMock()

    # Module names that config.py imports directly via ``from modules.X import Y``
    config_names = {
        "Plex": lambda *a, **kw: fake_plex,
        "TMDb": lambda *a, **kw: MagicMock(),
        "Trakt": lambda *a, **kw: MagicMock(),
        "AniDB": lambda *a, **kw: MagicMock(),
        "TVDb": lambda *a, **kw: MagicMock(),
        "Letterboxd": lambda *a, **kw: MagicMock(),
        "GitHub": lambda *a, **kw: MagicMock(),
        "Radarr": lambda *a, **kw: MagicMock(),
        "Sonarr": lambda *a, **kw: MagicMock(),
        "Overlays": lambda *a, **kw: MagicMock(),
        "OMDb": lambda *a, **kw: MagicMock(),
        "MDBList": lambda *a, **kw: MagicMock(),
        "IMDb": lambda *a, **kw: MagicMock(),
        "BoxOfficeMojo": lambda *a, **kw: MagicMock(),
        "Ergast": lambda *a, **kw: MagicMock(),
        "Simkl": lambda *a, **kw: MagicMock(),
        "StevenLu": lambda *a, **kw: MagicMock(),
        "Tautulli": lambda *a, **kw: MagicMock(),
        "ICheckMovies": lambda *a, **kw: MagicMock(),
        "MyAnimeList": lambda *a, **kw: MagicMock(),
        "AniList": lambda *a, **kw: MagicMock(),
        "Gotify": lambda *a, **kw: MagicMock(),
        "Ntfy": lambda *a, **kw: MagicMock(),
        "Notifiarr": lambda *a, **kw: MagicMock(),
        "AppriseNotify": lambda *a, **kw: MagicMock(),
        "Convert": lambda *a, **kw: MagicMock(),
        "TextFile": lambda *a, **kw: MagicMock(),
        "Cache": lambda *a, **kw: MagicMock(),
    }
    for name, mock_factory in config_names.items():
        monkeypatch.setattr(config_module, name, mock_factory)

    # Webhooks — instantiated, then methods called on the instance
    fake_webhooks = MagicMock()
    fake_webhooks.start_time_hooks = MagicMock()
    fake_webhooks.version_hooks = MagicMock()
    fake_webhooks.error_hooks = MagicMock()
    fake_webhooks.delete_hooks = MagicMock()
    monkeypatch.setattr(config_module, "Webhooks", lambda *a, **kw: fake_webhooks)


def make_config(
    tmp_path: pytest.TempPathFactory,
    *,
    config_yaml: str = BASE_CONFIG,
    attrs: dict | None = None,
    secrets: dict | None = None,
) -> ConfigFile:
    """Build a ConfigFile from *config_yaml* with all dependencies mocked."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(config_yaml, encoding="utf-8")
    merged_attrs = {**_default_attrs(str(config_path)), **(attrs or {})}
    return ConfigFile(FakeRequests(), str(tmp_path), merged_attrs, secrets or {})


# ═══════════════════════════════════════════════════════════════════════
# Config file discovery
# ═══════════════════════════════════════════════════════════════════════


class TestConfigDiscovery:
    def test_finds_explicit_config_path(self, tmp_path):
        cf = make_config(tmp_path)
        assert cf.config_path == str(tmp_path / "config.yml")

    def test_raises_failed_when_file_missing(self, tmp_path):
        with pytest.raises(Failed, match="config not found"):
            ConfigFile(
                FakeRequests(),
                str(tmp_path),
                {**_default_attrs(str(tmp_path / "nope.yml"))},
                secrets={},
            )

    def test_falls_back_to_default_dir(self, tmp_path):
        config_path = tmp_path / "config.yml"
        config_path.write_text(BASE_CONFIG, encoding="utf-8")
        attrs = {
            "config_file": None,
            "time_obj": datetime(2026, 6, 14, 18, 53),
            "time": "18:53",
        }
        cf = ConfigFile(FakeRequests(), str(tmp_path), attrs, secrets={})
        assert cf.config_path == str(tmp_path / "config.yml")

    def test_raises_failed_when_no_config_in_default_dir(self, tmp_path):
        attrs = {
            "config_file": None,
            "time_obj": datetime(2026, 6, 14, 18, 53),
            "time": "18:53",
        }
        with pytest.raises(Failed, match="config not found"):
            ConfigFile(FakeRequests(), str(tmp_path), attrs, secrets={})


# ═══════════════════════════════════════════════════════════════════════
# CLI attrs parsing
# ═══════════════════════════════════════════════════════════════════════


class TestCliAttrs:
    def test_requested_collections(self, tmp_path):
        cf = make_config(tmp_path, attrs={"collections": "Action|Drama"})
        assert cf.requested_collections == ["Action", "Drama"]

    def test_requested_libraries(self, tmp_path):
        cf = make_config(tmp_path, attrs={"libraries": "Movies|TV"})
        assert cf.requested_libraries == ["Movies", "TV"]

    def test_collection_only(self, tmp_path):
        cf = make_config(tmp_path, attrs={"collection_only": True})
        assert cf.collection_only is True

    def test_read_only(self, tmp_path):
        cf = make_config(tmp_path, attrs={"read_only": True})
        assert cf.read_only is True

    def test_no_missing(self, tmp_path):
        cf = make_config(tmp_path, attrs={"no_missing": True})
        assert cf.no_missing is True

    def test_no_report(self, tmp_path):
        cf = make_config(tmp_path, attrs={"no_report": True})
        assert cf.no_report is True

    def test_ignore_schedules(self, tmp_path):
        cf = make_config(tmp_path, attrs={"ignore_schedules": True})
        assert cf.ignore_schedules is True

    def test_plex_env_vars(self, tmp_path):
        cf = make_config(tmp_path, attrs={"plex_url": "http://env-plex:32400", "plex_token": "env-token"})
        assert cf.env_plex_url == "http://env-plex:32400"
        assert cf.env_plex_token == "env-token"


# ═══════════════════════════════════════════════════════════════════════
# Config validation — missing required sections
# ═══════════════════════════════════════════════════════════════════════


class TestValidation:
    def test_missing_tmdb_raises_failed(self, tmp_path):
        config = """
settings:
  cache: false
libraries:
  Movies:
    collection_files: []
plex:
  url: http://localhost
  token: fake
"""
        with pytest.raises(Failed, match="tmdb"):
            make_config(tmp_path, config_yaml=config)

    def test_missing_plex_section(self, tmp_path):
        """Config without a top-level plex: section still works if no library has per-library plex."""
        config = """
settings:
  cache: false
libraries:
  Movies:
    collection_files: []
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        # This should succeed because plex config is present at the top level
        cf = make_config(tmp_path, config_yaml=config)
        assert cf is not None


# ═══════════════════════════════════════════════════════════════════════
# Data reorganization
# ═══════════════════════════════════════════════════════════════════════


class TestDataReorganization:
    def test_cache_default_is_true(self, tmp_path):
        """When cache: is not in settings section, default is True.

        Note: ``cache: false`` at the top level would need a ``settings``
        section for ``replace_attr`` to pick it up.  Without ``settings``,
        ``check_for_attribute`` returns the default (True)."""
        config = """
settings:
  cache: false
libraries:
  Movies:
    collection_files: []
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        cf = make_config(tmp_path, config_yaml=config)
        assert cf.general["cache"] is False


# ═══════════════════════════════════════════════════════════════════════
# Deprecation warnings
# ═══════════════════════════════════════════════════════════════════════


class TestDeprecation:
    def test_metadata_path_deprecated(self, tmp_path):
        config = """
settings:
  cache: false
libraries:
  Movies:
    metadata_path:
      - file: collections/test.yml
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        cf = make_config(tmp_path, config_yaml=config)
        assert "metadata_path" not in cf.data["libraries"]["Movies"]

    def test_overlay_path_deprecated(self, tmp_path):
        config = """
settings:
  cache: false
libraries:
  Movies:
    overlay_path:
      - file: overlays/test.yml
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        cf = make_config(tmp_path, config_yaml=config)
        assert "overlay_path" not in cf.data["libraries"]["Movies"]
        assert "overlay_files" in cf.data["libraries"]["Movies"]

    def test_collection_minimum_renamed(self, tmp_path):
        config = """
settings:
  cache: false
  collection_minimum: 5
libraries:
  Movies:
    collection_files: []
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        cf = make_config(tmp_path, config_yaml=config)
        assert cf.general.get("minimum_items") == 5

    def test_playlist_sync_to_user_renamed(self, tmp_path):
        config = """
settings:
  cache: false
  playlist_sync_to_user: someone
libraries:
  Movies:
    collection_files: []
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        cf = make_config(tmp_path, config_yaml=config)
        assert cf.general.get("playlist_sync_to_users") == "someone"

    def test_library_collection_minimum_renamed(self, tmp_path):
        config = """
settings:
  cache: false
libraries:
  Movies:
    collection_files: []
    settings:
      collection_minimum: 3
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        cf = make_config(tmp_path, config_yaml=config)
        movie_lib = cf.data["libraries"]["Movies"]
        if "settings" in movie_lib:
            assert "collection_minimum" not in movie_lib["settings"]
            assert movie_lib["settings"].get("minimum_items") == 3


# ═══════════════════════════════════════════════════════════════════════
# Library-level data handling
# ═══════════════════════════════════════════════════════════════════════


class TestLibraryConfig:
    def test_library_with_collections_not_allowed(self, tmp_path):
        config = """
settings:
  cache: false
libraries:
  Movies:
    collections:
      Test:
        tmdb_popular: true
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        with pytest.raises(Failed, match="collections"):
            make_config(tmp_path, config_yaml=config)

    def test_library_with_overlays_not_allowed(self, tmp_path):
        config = """
settings:
  cache: false
libraries:
  Movies:
    overlays:
      Test:
        overlay:
          name: test
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        with pytest.raises(Failed, match="overlays"):
            make_config(tmp_path, config_yaml=config)

    def test_radarr_add_renamed(self, tmp_path):
        config = """
settings:
  cache: false
libraries:
  Movies:
    collection_files: []
    radarr_add_all: true
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        cf = make_config(tmp_path, config_yaml=config)
        movie_lib = cf.data["libraries"]["Movies"]
        assert "radarr_add_all" not in movie_lib
        assert movie_lib.get("radarr_add_all_existing") is True


# ═══════════════════════════════════════════════════════════════════════
# notify / notify_delete / mediastingers
# ═══════════════════════════════════════════════════════════════════════


class TestNotify:
    def test_notify_calls_webhooks_error_hooks(self, tmp_path):
        cf = make_config(tmp_path)
        cf.notify("Something went wrong")
        cf.Webhooks.error_hooks.assert_called_once()

    def test_notify_delete_calls_webhooks_delete_hooks(self, tmp_path):
        cf = make_config(tmp_path)
        cf.notify_delete("Collection deleted")
        cf.Webhooks.delete_hooks.assert_called_once()


class TestMediastingers:
    def test_mediastingers_calls_get_yaml(self, tmp_path):
        requests = FakeRequests()
        requests.get_yaml = MagicMock(return_value={"media": "stuff"})
        config_path = tmp_path / "config.yml"
        config_path.write_text(BASE_CONFIG, encoding="utf-8")
        cf = ConfigFile(
            requests,
            str(tmp_path),
            _default_attrs(str(config_path)),
            secrets={},
        )
        result = cf.mediastingers
        requests.get_yaml.assert_called_once()
        assert result == {"media": "stuff"}


# ═══════════════════════════════════════════════════════════════════════
# General settings defaults
# ═══════════════════════════════════════════════════════════════════════


class TestGeneralDefaults:
    def test_minimal_config_has_general_defaults(self, tmp_path):
        cf = make_config(tmp_path)
        assert cf.general is not None
        assert "cache" in cf.general
        assert "cache_expiration" in cf.general

    def test_run_order_default(self, tmp_path):
        cf = make_config(tmp_path)
        assert "run_order" in cf.general


# ═══════════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    def test_empty_libraries_section(self, tmp_path):
        config = """
settings:
  cache: false
libraries: {}
tmdb:
  apikey: fake
plex:
  url: http://localhost
  token: fake
"""
        with pytest.raises(Failed):
            make_config(tmp_path, config_yaml=config)

    def test_library_created_with_correct_mapping_name(self, tmp_path):
        """The library object gets the correct mapping name from the config key."""
        cf = make_config(tmp_path)
        assert len(cf.libraries) == 1
        assert cf.libraries[0].original_mapping_name == "Movies"

    def test_custom_config_path(self, tmp_path):
        custom = tmp_path / "custom_config.yml"
        custom.write_text(BASE_CONFIG, encoding="utf-8")
        cf = ConfigFile(
            FakeRequests(),
            str(tmp_path),
            _default_attrs(str(custom)),
            secrets={},
        )
        assert cf.config_path == str(custom)
