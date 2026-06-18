# tests/
<!-- Maintained by module-mapping. Derived block is auto-generated — do not hand-edit. -->

<!-- derived:start (generated 2026-06-09) -->
## Facts (auto-generated)
- Files:
    - test_apprise_notify.py
    - test_builder.py
    - test_letterboxd.py
    - test_simkl.py
    - test_textfile.py
    - test_tvdb.py
    - test_validator.py
- Public API / entry points (best-effort):
    - class FakeCache / FakeEpisode / FakeFilms / FakeList / FakeLogger / FakeMovie / FakeRequests / FakeResponse / FakeScraper / FakeSeason / FakeShow / FakeShowLibrary / FakeTVDbLibrary / FakeUser / FakeWatchlist
    - class TestAppriseNotifyInit / TestAppriseNotifyNotification
    - class TestDvdIds / TestRequest / TestTrendingIds / TestValidateSimklDict
    - def _episode_builder / _make_apobj / _make_params / _make_tvdb / _write_temp_file
    - def adapter / make_anime_item / make_dvd_item / make_movie_item / make_tv_item / make_validator / patch_logger
    - def test_collect_yaml_files_directory / test_collect_yaml_files_single_file
    - def test_detect_schema_type_collection / test_detect_schema_type_config / test_detect_schema_type_dynamic_collections / test_detect_schema_type_metadata / test_detect_schema_type_overlay
- Depends on (internal): modules/ (builder, letterboxd, simkl, textfile, tvdb, util, validator)
- Depends on (external): pytest, unittest.mock, bs4 (beautifulsoup4), plexapi.exceptions
- Referenced by (fan-in): (no external references found)
- Coupling points to check:
    - contains contract/flag/env reference: tests/test_validator.py (schema type detection)
    - verify consumers in other modules/areas are updated to match
- Governed by (business-logic doc): none mapped
- Business-critical: no
- Possible duplicated rules: none detected
<!-- derived:end -->

<!-- narrative:start -->
## Notes (human-owned)
<!-- Fill in intent, gotchas, and cross-repo couplings detection can't see.
     Leave this stub if not yet written; module-mapping will not overwrite it. -->
<!-- narrative:end -->
