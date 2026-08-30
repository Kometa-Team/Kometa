"""Tests for ``kometa.py`` (the top-level entry script).

The script itself is mostly argparse + scheduling + a thin orchestration
loop, so most behaviour is covered by the per-module suites. This file
exists for regression checks that pin invariants of the entry script
itself — things that, if broken, would crash users at launch before any
other test had a chance to fire.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KOMETA_PY = REPO_ROOT / "kometa.py"


def _module_ast() -> ast.Module:
    """Parse kometa.py once and return its AST."""
    return ast.parse(KOMETA_PY.read_text(encoding="utf-8"))


def _summary_log_groups() -> list[tuple[str, str]]:
    """Extract the summary grouping rules without importing kometa.py."""
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "summary_log_groups" for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("summary_log_groups was not found in kometa.py")


def _other_log_groups() -> list[tuple[str, str]]:
    """Extract the named summary section rules without importing kometa.py."""
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "other_log_groups" for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("other_log_groups was not found in kometa.py")


def _summarize_log_message(message: str) -> str:
    for pattern, replacement in _summary_log_groups():
        if re.match(pattern, message):
            return replacement
    return message


def _named_log_group(message: str) -> tuple[str, str] | None:
    for key, pattern in _other_log_groups():
        if message.startswith(key) and (match := re.match(pattern, message)):
            return key, match.group(1)
    return None


def test_issue_3244_resource_import_is_guarded() -> None:
    """Regression for #3244: ``import resource`` must be wrapped in try/except.

    The ``resource`` module is POSIX-only. PR #3235 added a bare
    ``import resource`` at module scope in ``kometa.py`` to bump
    ``RLIMIT_NOFILE`` from 256 to 4096 on macOS. That import crashed
    every Windows user at launch with::

        ModuleNotFoundError: No module named 'resource'

    The fix (PR #3244) wraps the import in ``try: import resource /
    except ImportError: resource = None`` and guards every subsequent
    use with ``if resource is not None:``.

    This test enforces the guard *statically* — it does not execute
    ``kometa.py``, so it catches the regression on every platform
    (including the Linux CI runner where ``import resource`` would
    succeed and hide the bug).
    """
    tree = _module_ast()

    # Walk top-level statements only. A nested ``import resource`` inside
    # a function body is fine; the bug is specifically a module-scope
    # unconditional import.
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "resource", (
                    "Found unconditional `import resource` at module scope in kometa.py. " "This crashes on Windows (POSIX-only module). " "Wrap it in `try: import resource / except ImportError: resource = None` instead. " "See PR #3244."
                )

    # Belt-and-braces: confirm the *guarded* form is still present, so a
    # well-meaning refactor that removes the try/except (e.g. while
    # cleaning up "dead code") gets caught here too.
    guarded_import_found = False
    for node in tree.body:
        if isinstance(node, ast.Try):
            for sub in node.body:
                if isinstance(sub, ast.Import):
                    for alias in sub.names:
                        if alias.name == "resource":
                            guarded_import_found = True
                            break
    assert guarded_import_found, (
        "Expected a `try: import resource / except ImportError: ...` block at module scope "
        "in kometa.py. Either the guard was removed, or the file layout changed in a way "
        "this test doesn't recognise. If the guard is genuinely no longer needed (e.g. the "
        "code was moved into a function), update this test."
    )


def test_issue_3244_resource_uses_are_guarded() -> None:
    """Regression for #3244: every ``resource.<attr>`` access must be guarded.

    A guarded import is necessary but not sufficient — if ``resource`` is
    ``None`` on Windows, calls like ``resource.getrlimit(...)`` will
    raise ``AttributeError``. This test asserts that every reference to
    ``resource.<something>`` at module scope lives inside an ``if
    resource is not None:`` block (or another guard that proves
    ``resource`` is truthy).
    """
    tree = _module_ast()

    # Collect every ``resource.X`` Attribute reference and the line it's on.
    resource_uses: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "resource":
            resource_uses.append(node.lineno)

    if not resource_uses:
        return  # No uses at all is fine — the import is also a no-op.

    # Find the line range of every ``if resource is not None:`` block at
    # module scope so we can confirm each use sits inside one.
    guarded_ranges: list[tuple[int, int]] = []
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            # Match `resource is not None` exactly
            left = node.test.left
            ops = node.test.ops
            comparators = node.test.comparators
            if isinstance(left, ast.Name) and left.id == "resource" and len(ops) == 1 and isinstance(ops[0], ast.IsNot) and len(comparators) == 1 and isinstance(comparators[0], ast.Constant) and comparators[0].value is None:
                guarded_ranges.append((node.lineno, node.end_lineno or node.lineno))

    for use_line in resource_uses:
        inside_guard = any(start <= use_line <= end for start, end in guarded_ranges)
        assert inside_guard, f"`resource.<attr>` at kometa.py:{use_line} is not inside an `if resource is not None:` block. " f"On Windows `resource` is `None`, so this will raise AttributeError. See PR #3244."


def test_overlay_summary_uses_warning_labeling() -> None:
    """Regression for overlay missing-rating summaries.

    The summary should consistently label these as warnings rather than
    errors, since the overlay code now raises ``OverlayWarning``-style
    messages for missing ratings.
    """
    text = KOMETA_PY.read_text(encoding="utf-8")
    assert "(\"Overlay Warning: No 'anidb_average_rating' found\"," in text
    assert 'logger.separator("Overlay Summary", space=False, border=False)' in text
    assert 'logger.info("Count | Message")' in text
    assert 'logger.separator("Convert Summary", space=False, border=False)' in text
    assert 'return f"{message} for {source}"' in text
    assert 'r".+ Warning: No Logo Found at .+", "Warning: No Logo Found"' in text
    assert "Plex Error: resolution: No matches found with regex pattern" not in text


def test_overlay_attempts_are_reported_in_overlay_summary() -> None:
    """Regression for overlay attempt noise from failed item overlays.

    Per-item overlay failures should now be grouped into the overlay
    summary instead of only surfacing in the generic error table.
    """
    text = KOMETA_PY.read_text(encoding="utf-8")
    assert '("Overlays Attempted on", r"Overlays Attempted on (.*): .+")' in text
    assert 'key == "Overlays Attempted on"' in text


def test_missing_overlay_template_values_are_grouped_by_placeholder() -> None:
    """Generic text-overlay misses belong in Overlay Summary, grouped by template value."""
    assert _named_log_group("Overlay Error: No '<<user_rating>>' found") == ("Overlay Error: No '", "<<user_rating>>")
    assert _named_log_group("Overlay Error: No '<<critic_rating>>' found") == ("Overlay Error: No '", "<<critic_rating>>")
    text = KOMETA_PY.read_text(encoding="utf-8")
    assert 'key.startswith(("Overlay Warning", "Overlay Error"))' in text
    assert 'other_message[key]["name_counts"][_name] += 1' in text
    assert "Overlay Warning: No '{template_value}' found" in text


def test_letterboxd_tmdb_failures_are_summarized() -> None:
    """Regression for repeated Letterboxd per-item TMDb lookup noise.

    These are high-volume item-level messages that should collapse into
    the end-of-run summary instead of filling the report with one line
    per title.
    """
    text = KOMETA_PY.read_text(encoding="utf-8")
    assert 'r"Letterboxd Error: TMDb Movie ID not found at .+ item is type .+ with tmdb_id .+\\."' in text
    assert 'r"Letterboxd Warning: TMDb link for .+ is for a TV show, not a movie; ignoring TMDb ID .+ from link\\."' in text


def test_dynamic_run_summary_messages_are_consolidated() -> None:
    """IDs, titles, GUIDs, and URLs from the supplied large log should not create one row each."""
    cases = {
        "Config Warning: Skipping duplicate collection: Pusher": "Config Warning: Skipping duplicate collection",
        "MDBList Warning: Batch lookup returned no data for 6 of 6 requested tmdb IDs: 584729, 586152": "MDBList Warning: Batch lookup returned no data for requested IDs",
        "No MdbItem for 4k77 DNR (Guid: local://597050)": "MDBList Warning: No item found",
        "Letterboxd Warning: letterboxdpy does not reliably support films page https://letterboxd.com/user/films/rated/5/; using Kometa fallback parsing.": "Letterboxd Warning: Using fallback films-page parsing",
        "Letterboxd Warning: cloudscraper hit a Cloudflare challenge for https://letterboxd.com/user/list/example/; retrying with curl_cffi.": "Letterboxd Warning: Cloudflare challenge; retrying with curl_cffi",
        "TMDb Error: No Movie found for TMDb ID: 1710116": "TMDb Error: No Movie found for TMDb ID",
        "TMDb Error: No Movie found for TMDb ID 1710116: (404 [Not Found]) Requested Item Not Found": "TMDb Error: No Movie found for TMDb ID",
        "TMDb Error: No Episode found for TMDb ID 330444 Season 1931 Episode 17: (404 [Not Found]) Requested Item Not Found": "TMDb Error: No Episode found for TMDb ID",
    }
    for message, expected in cases.items():
        assert _summarize_log_message(message) == expected


def test_asset_paths_and_warnings_are_summarized() -> None:
    """Variable asset paths should not produce one summary row per file."""
    cases = {
        "Asset Warning: Asset Directory Not Found and Created: /config/assets": "Asset Warning: Asset Directory Not Found and Created",
        "Asset Warning: No supported artwork found in the assets folder '/config/assets'": "Asset Warning: No supported artwork found in the assets folder",
        "Collection Error: Background Path Does Not Exist: /config/background.jpg": "Error: Background Path Does Not Exist",
        "Overlay Error: Logo Path Does Not Exist: /config/logo.png": "Error: Logo Path Does Not Exist",
        "Playlist Error: Poster Path Does Not Exist: /config/poster.jpg": "Error: Poster Path Does Not Exist",
        "Collection Error: Square Art Path Does Not Exist: /config/square.jpg": "Error: Square Art Path Does Not Exist",
        "Collection Error: Theme Path Does Not Exist: /config/theme.mp3": "Error: Theme Path Does Not Exist",
    }
    for message, expected in cases.items():
        assert _summarize_log_message(message) == expected


def test_reset_image_warnings_are_summarized() -> None:
    """Reset misses with item labels should collapse by image type."""
    cases = {
        "Poster | No Reset Image Found": "Poster Warning: No Reset Image Found",
        "Season 06 Poster | No Reset Image Found": "Poster Warning: No Reset Image Found",
        "S03E02 Poster | No Reset Image Found": "Poster Warning: No Reset Image Found",
        "Example Background | No Reset Image Found": "Background Warning: No Reset Image Found",
        "Example Logo | No Reset Image Found": "Logo Warning: No Reset Image Found",
        "Example Square Art | No Reset Image Found": "Square Art Warning: No Reset Image Found",
    }
    for message, expected in cases.items():
        assert _summarize_log_message(message) == expected


def test_summary_parser_preserves_internal_pipe_delimiters() -> None:
    """Messages such as ``S03E02 Poster | No Reset Image Found`` must not be truncated to the item label."""
    text = KOMETA_PY.read_text(encoding="utf-8")
    assert 'log_line.split("|", 1)[1].rsplit("|", 1)[0].strip()' in text
    assert 'log_line.split("|")[1].strip()' not in text


def test_missing_tmdb_collections_are_summarized() -> None:
    """Variable collection IDs should collapse into one summary row."""
    message = "TMDb Error: Collection ID 1698578 missing on TMDb; add '1698578' to the franchise exclude list if this is auto-built."
    expected = "TMDb Error: Collection ID missing on TMDb; add it to the franchise exclude list if this is auto-built"
    assert _summarize_log_message(message) == expected


def test_missing_builder_parts_are_summarized() -> None:
    """Variable IDs and item data should collapse for collections and playlists."""
    cases = {
        "Collection Warning: tvdb_episode:75710_1_1 -> Criminal Minds Season: 1 Episode: 1 Missing": "TVDb Episode Missing",
        "Playlist Warning: tvdb_episode:75710_1_2 -> Criminal Minds Season: 1 Episode: 2 Missing": "TVDb Episode Missing",
        "Collection Warning: tvdb_season:75710_1 -> Criminal Minds Season: 1 Missing": "TVDb Season Missing",
        "Playlist Warning: tvdb_season:75710_2 -> Criminal Minds Season: 2 Missing": "TVDb Season Missing",
        "Collection Warning: imdb:tt0452812 -> Criminal Minds Season: 1 Episode: 1 Missing": "IMDb Episode Missing",
        "Playlist Warning: imdb:tt0452813 -> Criminal Minds Season: 1 Episode: 2 Missing": "IMDb Episode Missing",
    }
    for message, expected in cases.items():
        assert _summarize_log_message(message) == expected


def test_status_summary_skips_empty_tables() -> None:
    """Regression for the run-status table header.

    If there is no status data to report, the summary should stay quiet
    rather than printing an empty header row.
    """
    text = KOMETA_PY.read_text(encoding="utf-8")
    assert "if not status:\n            return" in text
