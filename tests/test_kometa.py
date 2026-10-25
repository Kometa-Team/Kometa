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
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.log_summary import SUMMARY_NORMALIZATIONS, RunLogSummary, normalize_summary_message, print_status

REPO_ROOT = Path(__file__).resolve().parent.parent
KOMETA_PY = REPO_ROOT / "kometa.py"


def _module_ast() -> ast.Module:
    """Parse kometa.py once and return its AST."""
    return ast.parse(KOMETA_PY.read_text(encoding="utf-8"))


def _process_pool_context(multiprocessing):
    """Load the context-selection helper without importing kometa.py."""
    for node in _module_ast().body:
        if isinstance(node, ast.FunctionDef) and node.name == "_process_pool_context":
            helper_module = ast.Module(body=[node], type_ignores=[])
            namespace = {"multiprocessing": multiprocessing}
            exec(compile(helper_module, str(KOMETA_PY), "exec"), namespace)
            return namespace["_process_pool_context"]()
    raise AssertionError("_process_pool_context was not found in kometa.py")


def test_album_only_missing_items_trigger_reporting():
    for node in _module_ast().body:
        if isinstance(node, ast.FunctionDef) and node.name == "missing_item_counts":
            namespace = {}
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(KOMETA_PY), "exec"), namespace)
            counts = namespace["missing_item_counts"](SimpleNamespace(missing_albums=[{"name": "Album"}]))
            assert counts == {"movies": 0, "shows": 0, "artists": 0, "albums": 1, "tracks": 0}
            assert any(counts.values())
            return
    raise AssertionError("missing_item_counts was not found in kometa.py")


def test_process_pool_uses_fork_instead_of_forkserver() -> None:
    expected_context = object()
    multiprocessing = SimpleNamespace(
        get_start_method=MagicMock(return_value="forkserver"),
        get_all_start_methods=MagicMock(return_value=["forkserver", "fork", "spawn"]),
        get_context=MagicMock(return_value=expected_context),
    )

    assert _process_pool_context(multiprocessing) is expected_context
    multiprocessing.get_context.assert_called_once_with("fork")


def test_process_pool_preserves_spawn_when_fork_is_unavailable() -> None:
    multiprocessing = SimpleNamespace(
        get_start_method=MagicMock(return_value="spawn"),
        get_all_start_methods=MagicMock(return_value=["spawn"]),
        get_context=MagicMock(),
    )

    assert _process_pool_context(multiprocessing) is None
    multiprocessing.get_all_start_methods.assert_not_called()
    multiprocessing.get_context.assert_not_called()


def _summarize_log_message(message: str) -> str:
    return normalize_summary_message(message)


@pytest.mark.parametrize("severity", ["WARNING", "ERROR", "CRITICAL"])
@pytest.mark.parametrize("details", [False, True])
def test_run_summary_ignores_blank_messages(severity, details):
    summary = RunLogSummary([], details=details)
    for message in ("", " ", "\t", "\n"):
        summary.add(severity, message)
        summary.add_formatted_line(f"[2026-10-11] [kometa.py:1] [{severity}] | {message.rstrip()} |")
    assert not summary.has_messages()
    assert summary.severity_rows(severity) == []


@pytest.mark.parametrize("severity", ["WARNING", "ERROR", "CRITICAL"])
def test_run_summary_preserves_real_messages_with_pipes(severity):
    summary = RunLogSummary([])
    for message in ("", " ", "Example diagnostic: A | B", "Example diagnostic: A | B", "\t"):
        summary.add_formatted_line(f"[2026-10-11] [kometa.py:1] [{severity}] | {message} |")
    assert summary.has_messages()
    assert summary.severity_rows(severity) == [("Example diagnostic: A | B", 2)]


@pytest.mark.parametrize("err_type", ["Collection", "Playlist"])
@pytest.mark.parametrize("resource", ["list", "watchlist", "films page"])
def test_letterboxd_validation_missing_resources_are_grouped(err_type, resource):
    summary = RunLogSummary([])
    detailed = RunLogSummary([], details=True)
    messages = []
    for name in ("anxiety-inducing-cinema", "black-directors-the-official-top-100-narrative"):
        url = f"https://letterboxd.com/example/list/{name}/"
        message = f"{err_type} Error: Could not validate {url}: Letterboxd Error: Failed to load {resource} {url}: Resource not found: {url.rstrip('/')}"
        messages.append(message)
        summary.add_formatted_line(f"[2026-10-11] [kometa.py:1] [ERROR] | {message} |")
        detailed.add("ERROR", message)
        assert sum(bool(re.match(pattern, message)) for pattern, _ in SUMMARY_NORMALIZATIONS) == 1
    assert summary.severity_rows("ERROR") == [(f"{err_type} Error: Could not validate Letterboxd {resource} (resource not found)", 2)]
    assert detailed.severity_rows("ERROR") == [(message, 1) for message in messages]


@pytest.mark.parametrize(
    "message",
    [
        "Collection Error: Could not validate https://letterboxd.com/example/list/test/: Letterboxd Error: Failed to load list https://letterboxd.com/example/list/test/: Connection timed out",
        "Collection Error: Could not validate https://letterboxd.com/example/list/test/: Letterboxd Error: Unsupported list URL",
        "Collection Error: Could not validate https://example.com/test/: Other Error: Resource not found: https://example.com/test/",
    ],
)
def test_unknown_validation_failures_keep_their_diagnostics(message):
    assert normalize_summary_message(message) == message


def test_duplicate_collection_details_do_not_repeat_in_warning_summary():
    nodes = [node for node in _module_ast().body if isinstance(node, ast.FunctionDef) and node.name in ("summarize_duplicate_collections", "report_duplicate_collections")]
    logger = MagicMock()
    namespace = {"logger": logger}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(KOMETA_PY), "exec"), namespace)
    libraries = [SimpleNamespace(name=name, get_all_collections=lambda: [SimpleNamespace(title="A | B"), SimpleNamespace(title="A | B")]) for name in ("Movies", "Shows")]
    namespace["report_duplicate_collections"](SimpleNamespace(libraries=libraries))
    info_messages = [call.args[0] for call in logger.info.call_args_list]
    assert info_messages.count("") == 3
    assert info_messages.count("  2 instances: A | B") == 2
    assert info_messages.count("If this is unexpected, check for an empty or stale smart collection and consider checking Plex DBRepair.") == 2
    messages = [call.args[0] for call in logger.warning.call_args_list]
    assert messages == [f"Plex Warning: Duplicate collection titles detected in {name} Library" for name in ("Movies", "Shows")]
    summary = RunLogSummary([])
    for message in info_messages:
        summary.add_formatted_line(f"[2026-10-11] [kometa.py:1] [INFO] | {message} |")
    for message in messages:
        summary.add_formatted_line(f"[2026-10-11] [kometa.py:1] [WARNING] | {message} |")
    assert summary.severity_rows("WARNING") == [(message, 1) for message in messages]


def _section_rows(message: str, rating_sources: list[str] | None = None) -> list[tuple[int, str, list[str]]]:
    summary = RunLogSummary(rating_sources or [])
    summary.add("WARNING", message)
    return list(summary.section_rows("overlay"))


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


def test_overlay_summary_removes_redundant_section_prefix() -> None:
    """The Overlay Summary heading makes another ``Overlay Warning`` prefix redundant."""
    assert _section_rows("Overlay Warning: No 'critic_rating' found for 'Example'") == [(1, "No 'critic_rating' found", ["'Example'"])]


def test_overlay_summary_groups_follow_current_rating_sources() -> None:
    """The generated groups must follow active sources instead of a stale manual copy."""
    overlay_tree = ast.parse((REPO_ROOT / "modules" / "overlay.py").read_text(encoding="utf-8"))
    sources = None
    for node in ast.walk(overlay_tree):
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "rating_sources" for target in node.targets):
            sources = ast.literal_eval(node.value)
            break
    assert sources is not None
    assert "floppy_rating" in sources
    assert "serializd_rating" in sources
    assert "plex_user_rating" not in sources

    summary = RunLogSummary(sources)
    summary.add("WARNING", "Overlay Warning: No 'serializd_rating' found for 'Example'")
    assert list(summary.section_rows("overlay")) == [(1, "No 'serializd_rating' found", ["'Example'"])]


@pytest.mark.parametrize("message", ["Convert Warning: No MyAnimeList Found for AniDB ID: 123", "Collection Error: No Filter Created", "Trakt Error: No TVDb ID found for 123"])
def test_retired_summary_messages_are_left_unchanged(message):
    assert normalize_summary_message(message) == message


def test_overlay_attempts_are_reported_in_overlay_summary() -> None:
    """Regression for overlay attempt noise from failed item overlays.

    Per-item overlay failures should now be grouped into the overlay
    summary instead of only surfacing in the generic error table.
    """
    assert _section_rows("Overlays Attempted on Example: Resolution, Ratings") == [(1, "Overlays Attempted on", ["Example"])]


def test_multiline_overlay_attempt_continuation_is_reported() -> None:
    summary = RunLogSummary([])
    summary.add_formatted_line("[2026-09-26] [overlays.py:1] [ERROR] |   Overlay Error: failed")
    summary.add_formatted_line("  Overlays Attempted on Example: Resolution, Ratings |")
    assert list(summary.section_rows("overlay")) == [(1, "Overlays Attempted on", ["Example"])]


def test_missing_overlay_template_values_are_grouped_by_placeholder() -> None:
    """Generic text-overlay misses belong in Overlay Summary, grouped by template value."""
    assert _section_rows("Overlay Error: No '<<user_rating>>' found") == [(1, "No '<<user_rating>>' found", [])]
    assert _section_rows("Overlay Error: No '<<critic_rating>>' found") == [(1, "No '<<critic_rating>>' found", [])]


@pytest.mark.parametrize(
    "message, expected",
    [
        ("Letterboxd Error: TMDb Movie ID not found at example item is type movie with tmdb_id 123.", "Letterboxd Error: TMDb Movie ID not found"),
        ("Letterboxd Warning: TMDb link for example is for a TV show, not a movie; ignoring TMDb ID 123 from link.", "Letterboxd Warning: TMDb link is for a TV show, not a movie"),
    ],
)
def test_letterboxd_tmdb_failures_are_summarized(message, expected):
    assert normalize_summary_message(message) == expected


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
        "FlickList Warning: No usable ID found for Example; skipping": "FlickList Warning: No usable ID found; skipping item",
        "MDBList Warning: Skipping Example: Convert Warning: No TMDb ID found for TVDb ID '123'": "MDBList Warning: Skipping item because no TMDb ID was found",
        "TVDb Error: Skipping Movie: Example": "TVDb Error: Skipping movie",
        "Plex Warning: Collection 'Example' already exists; skipping creation": "Plex Warning: Collection already exists; skipping creation",
        "Filter Error: No IMDb ID found for Example": "Filter Error: No IMDb ID found",
        "TMDb Warning: unable to load movie TMDb ID 123; skipping item: service unavailable": "TMDb Warning: Unable to load movie; skipping item: service unavailable",
    }
    for message, expected in cases.items():
        assert _summarize_log_message(message) == expected


def test_asset_paths_and_warnings_are_summarized() -> None:
    """Variable asset paths should not produce one summary row per file."""
    cases = {
        "Asset Warning: Asset Directory Not Found and Created: /config/assets": "Asset Warning: Asset Directory Not Found and Created",
        "Asset Warning: No supported artwork found in the assets folder '/config/assets'": "Asset Warning: No supported artwork found in the assets folder",
        "Asset Warning: No poster found for 'Example' in the assets folder '/config/assets'": "Asset Warning: No poster found in assets",
        "Asset Warning: No poster 'poster.png' found in the assets folders": "Asset Warning: No poster found in assets",
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
    summary = RunLogSummary([])
    summary.add_formatted_line("[2026-09-26] [plex.py:1] [WARNING] | S03E02 Poster | No Reset Image Found |")
    assert summary.severity_rows("WARNING") == [("Poster Warning: No Reset Image Found", 1)]


def test_item_not_found_warnings_are_consolidated() -> None:
    summary = RunLogSummary([])
    summary.add("WARNING", "Skipping Star Wars Rebels: Item not found")
    summary.add("WARNING", "Skipping Ahsoka: Item not found in Metadata File 'Shows'")
    assert summary.severity_rows("WARNING") == [("Item not found", 2)]


def test_high_volume_normalizations_do_not_overlap() -> None:
    messages = [
        "Skipping Star Wars Rebels: Item not found",
        "MDBList Warning: Skipping Example: Convert Warning: No TMDb ID found for TVDb ID '123'",
        "Plex Warning: Unable to batch label update for Example; using an individual edit",
        "Asset Warning: No poster found for 'Example' in the assets folder '/config/assets'",
    ]
    for message in messages:
        assert sum(bool(re.match(pattern, message)) for pattern, _ in SUMMARY_NORMALIZATIONS) == 1


def test_additional_item_messages_are_consolidated() -> None:
    cases = [
        (["No AniDB ID for Guid: plex://movie/1", "No AniDB ID for Guid: plex://movie/2"], "No AniDB ID for Guid"),
        (["No Poster found to restore for Movie One", "No Poster found to restore for Movie Two"], "No Poster found to restore"),
        (["Plex Warning: Show One has no Season 1 Episode 1", "Plex Warning: Show Two has no Season 1 Episode 1 "], "Plex Warning: No Season 1 Episode 1 found"),
        (
            [
                "TMDb Error: Movie ID 101 missing on TMDb. Verify it still exists and update your config.",
                "TMDb Error: Movie ID 202 missing on TMDb. Verify it still exists and update your config.",
            ],
            "TMDb Error: Movie ID missing on TMDb. Verify it still exists and update your config.",
        ),
        (
            [
                "MDBList Warning: Ignoring unexpected IMDb ID in batch response: tt0000001",
                "MDBList Warning: Ignoring unexpected IMDb ID in batch response: tt0000002",
            ],
            "MDBList Warning: Ignoring unexpected IMDb ID in batch response",
        ),
    ]
    for messages, expected in cases:
        summary = RunLogSummary([])
        for message in messages:
            summary.add("WARNING", message)
        assert summary.severity_rows("WARNING") == [(expected, 2)]


def test_no_items_overlay_group_accepts_arbitrary_mapping_names() -> None:
    assert _section_rows("No Items found for Resolution") == [(1, "No Items found", ["Resolution"])]


def test_convert_summary_counts_ids_with_one_counter() -> None:
    summary = RunLogSummary([])
    summary.add("WARNING", "Convert Warning: No TVDb ID found for TMDb ID '10'")
    summary.add("WARNING", "Convert Warning: No TVDb ID found for TMDb ID '11'")
    assert list(summary.section_rows("convert")) == [(2, "No TVDb ID found for TMDb IDs", ["10", "11"])]


def test_detail_mode_preserves_generic_messages() -> None:
    summary = RunLogSummary([], details=True)
    message = "Skipping Star Wars Rebels: Item not found"
    summary.add("WARNING", message)
    assert summary.severity_rows("WARNING") == [(message, 1)]


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


def test_status_summary_skips_empty_tables():
    logger = MagicMock()
    print_status({}, 20, logger)
    logger.info.assert_not_called()
    logger.separator.assert_not_called()


def test_status_summary_renders_counts_and_errors():
    logger = MagicMock(separating_character="-")
    print_status({"Example": {"added": 1, "unchanged": 2, "removed": 3, "run_time": "0:00:01", "status": "Modified", "errors": ["Failure detail"]}}, 20, logger)
    messages = [call.args[0] for call in logger.info.call_args_list]
    assert messages[0].strip().startswith("Title")
    assert [part.strip() for part in messages[1].split("|")] == ["Example", "1", "2", "3", "0:00:01", "Modified"]
    assert messages[2:] == ["Failure detail", ""]


@pytest.mark.parametrize("severity", ["WARNING", "ERROR"])
def test_missing_tmdb_lookup_summaries_group_ids_and_keep_types_separate(severity):
    summary = RunLogSummary([])
    detailed = RunLogSummary([], details=True)
    for kind in ["Collection", "Movie", "Show"]:
        messages = [
            f"TMDb Error: No {kind} found on TMDb for ID(s) [1719379]. Verify the ID(s) still exist and update your config.",
            f"TMDb Error: No {kind} found on TMDb for ID(s) [1698578, 1677089]. Verify the ID(s) still exist and update your config.",
        ]
        for message in messages:
            summary.add(severity, message)
            detailed.add(severity, message)
        assert (f"TMDb Error: No {kind} found on TMDb", 2) in summary.severity_rows(severity)
        assert all((message, 1) in detailed.severity_rows(severity) for message in messages)
    assert len(summary.severity_rows(severity)) == 3


def test_unrelated_tmdb_failure_keeps_diagnostic_details():
    message = "TMDb Error: No Collection found on TMDb for ID(s) [1719379]. Request timed out."
    assert normalize_summary_message(message) == message


@pytest.mark.parametrize("severity", ["WARNING", "ERROR"])
def test_alternate_tmdb_lookup_summaries_keep_types_separate(severity):
    summary = RunLogSummary([])
    detailed = RunLogSummary([], details=True)
    for kind in ("Collection", "Movie", "Show"):
        messages = [
            f"TMDb Error: No {kind} found for TMDb ID: 12345",
            f"TMDb Error: No {kind} found for TMDb ID 67890: (404 [Not Found]) Requested Item Not Found",
        ]
        for message in messages:
            summary.add_formatted_line(f"[2026-10-11] [tmdb.py:1] [{severity}] | {message} |")
            detailed.add(severity, message)
            assert sum(bool(re.match(pattern, message)) for pattern, _ in SUMMARY_NORMALIZATIONS) == 1
        assert (f"TMDb Error: No {kind} found for TMDb ID", 2) in summary.severity_rows(severity)
        assert all((message, 1) in detailed.severity_rows(severity) for message in messages)
    assert len(summary.severity_rows(severity)) == 3


@pytest.mark.parametrize(
    "message",
    [
        "TMDb Error: No Person found for TMDb ID 12345: API unavailable",
        "TMDb Error: No Movie or Collection found for TMDb ID 12345",
        "TMDb Error: No Show found for TMDb ID 12345 Season 2: API unavailable",
    ],
)
def test_alternate_tmdb_rule_preserves_other_lookup_failures(message):
    assert normalize_summary_message(message) == message
