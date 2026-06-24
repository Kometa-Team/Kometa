# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Downgrade "Skipping `<name>`: Item not found" log message from `ERROR` to `WARNING` in metadata file processing when a mapped item cannot be found in the Plex library.
- Allow `builder_level` to work with playlists. Fixes #2267
- Consolidate repeated asset warning messages in the warning summary into shared count buckets so the same warning is reported once instead of one row per affected folder or item.
- Fix `ModuleNotFoundError: No module named 'resource'` crash on Windows at startup. The file-descriptor limit fix introduced in #3235 used the POSIX-only `resource` module unconditionally. Now wrapped in a `try`/`except ImportError` so the bump is applied on POSIX systems and skipped cleanly on Windows. (#3244)
- Fix `kometa.py` crashing with `TypeError: HEAD is a detached symbolic reference` when run from a detached-HEAD checkout (release-tag checkouts, CI runners that check out by SHA, etc.). (#3232)
- Fix `cache.update_anime_map()` writing the AniDB id into the AniList column on UPDATE. The original `anime_map` row was written correctly on INSERT but each subsequent update would clobber `anilist_id` with the AniDB value. (#3232)

### Changed

- Internal: add a comprehensive pytest test suite (580 tests, up from 203) covering most of `modules/`, plus a regression-test convention (`test_issue_NNNN_*`) for documented bugs. (#3232)
- Internal: add a GitHub Actions test workflow with separate jobs for `lint` (black + isort + flake8), `test` (pytest with 20% coverage gate), `regression` (regression-only suite), `schema` (JSON Schema validation of `json-schema/*.json` + kitchen-sink config), `imports` (auto-discovered import smoke check across all 40 modules), `perf` (slow-test reporting via `pytest --durations-min`), and `smoke` (`kometa.py --help` + minimal-config dry-run). (#3232)

## [v2.4.3] - 2026-06-22

### Fixed

- Fix image size validation during metadata uploads so local poster/background/square art files are checked using their actual file size instead of the string `compare` field, avoiding a `TypeError` in operations.

## [v2.4.2] - 2026-06-22

### Added

- Add jsonschema 4.23.0.
- Add letterboxdpy 6.5.0.
- Report deactivated Trakt accounts [Trakt returns a 410].
- Add E4 to network overlay and show network collection. #2975
- Adds new `text_file` builder.
- Initial support for SIMKL.com; trending lists and dvd-releases list.
- Add Apprise as a webhook notification provider.
- Added `language` parameter to `mass_poster_update` and `mass_background_update` operations to override TMDb language for image fetching (e.g. `xx` for textless posters).
- Added `plex_csm` and `plex_csm0` sources to `mass_content_rating_update` (reads CSM age rating from Plex's own cached `commonSenseMedia.ageRatings`, no external API key required).
- Add Plex square art support: upload `square.ext` assets for movies, shows, seasons, albums, and playlists via `find_and_upload_assets`. Extends metadata file items and library operations.
- Add comprehensive config validation with `--validate`, `--validate-level`, `--validate-schema`, and `--schema-path` CLI flags. Supports syntax, structure, full, and schema-level validation with a gap report showing missing/extra fields.
- Add `--validate-file` and `--validate-dir` CLI flags for standalone and batch YAML validation against auto-detected schema types (config, collection, metadata, overlay, playlist). Output written to `validate.log`.
- Add `modules/validator.py` with `ConfigValidator` (multi-level config validation) and `FileSetValidator` (standalone/batch YAML validation with schema type detection).
- Expand `json-schema/config-schema.json` with full coverage and add per-type schemas: `collection-schema.json`, `metadata-schema.json`, `overlay-schema.json`, `playlist-schema.json`.
- Add `apprise` and `schedule_overlays` to the config JSON schema.
- Add `auto_sort_hubs` global/library setting to sort Recommendation Hub rows on the Plex home screen after all collections are processed. Accepts `sort_title`, `sort_title.desc`, `alpha`, `alpha.desc`, `configured`, `configured.desc`, or `random`.
- Add `hub_priority` per-collection attribute to pin a collection's hub row to a specific position (lower number = higher up). Collections with `hub_priority` are sorted first; the remainder follow in `auto_sort_hubs` order.
- Add `monthly(last)` schedule option: fires on the last day of every month regardless of its length (Feb 28/29, Apr/Jun/Sep/Nov 30, or the 31st in 31-day months).
- Add `hub_priority` and `hub_priority_<<key>>` template variables to the shared default templates so collections can set hub row priority from templates.
- Add `hub_priority` to the collection config schema so the new template variable validates correctly.
- Add support for boxd.it urls, used for letterboxd share lists.
- Allow metadata updates to proceed on existing collections even if the builder returns 0 items.
- Add new operations attributes `respect_ignore_ids` to skip operations processing items in `ignore_ids` or `ignore_imdb_ids`, and `ignore_labels` to skip operations processing items with the specified label(s).
- Add new TMDb release date types for `mass_originally_available_update` and `mass_added_at_update` operations: `tmdb_premiere`, `tmdb_theatrical`, `tmdb_theatricallimited`, `tmdb_digital`, `tmdb_physical`, `tmdb_tv`.

### Changed

- Bump lxml to 6.0.4.
- Bump packaging to 26.1.
- Bump gitpython to 3.1.50.
- Bump letterboxdpy to 6.5.7.
- Bump lxml to 6.1.1.
- Bump packaging to 26.2.
- Bump plexapi to 4.18.1.
- Bump python-dotenv to 1.2.2.
- Bump pillow to 12.2.0.
- Bump pywin32 to 312.
- Bump requests to 2.34.2.
- Bump setuptools to 82.0.1.
- Bump prek to 0.4.5.
- Switch to GraphQL for IMDb charts retrieval, with a fallback to the old method if the GraphQL request fails. #3006
- Replace Kometa's internal Letterboxd scraping with a letterboxdpy-backed adapter while preserving existing Letterboxd builder names.
- Process collection alterations [add/remove] in batches of 100 to avoid "400 Bad Request" on mile-long URLs.
- Exit early if more than one of the `--SOMETHING-only` flags are set.
- Cache people data for media items since it's unlikely to change.
- The `tmdb_discover` YAML validator now enforces: unknown keys are rejected, value types are checked, `certification_country`/`certification` must co-occur, `watch_region` must accompany any watch-provider or monetization key, and movie-only and TV-only parameters are mutually exclusive. Note: `with_watch_providers` and `without_watch_providers` now require `watch_region` at validation time (the TMDb Discover API requires this), which is stricter than the runtime check in `builder.py`.
- `--validate` now implies immediate run (like `--run-libraries`).
- Use the SQLite cache for TMDb queries in `check_filters` and `check_missing_filters` instead of bypassing it with `ignore_cache=True`.
- Only force-reload Plex items in the overlay loop when `reapply_overlays` is set; reuse the session cache on normal runs.
- Use set lookup instead of list scan when checking collection membership in `add_to_collection` and `run_collections_again`, reducing complexity from O(n×m) to O(n).
- Extend default "Metacritic Must See" collection to work with TV.
- Improve JSON schemas and add prototype YAML configuration files for all builders.
- Add translations for Genre Defaults posters.
- Updates to Quickstart docs about limitations.
- Updates to Trakt and MAL flow pages.
- Update Letterboxd builder docs to reflect letterboxdpy-backed filtering, ordering, and incremental behavior.
- Document the valid `font_style` values for the default Inter font and note that valid styles are font-specific. #2925
- Call out the schema file as supporting only `config.yml` explicitly.
- Sync `pyproject.toml` pinned dependencies to match `requirements.txt` (lxml, requests, pillow, packaging, gitpython, pywin32; add letterboxdpy).
- Align Black `target-version` to `["py312"]` in `pyproject.toml` to match the project's existing `requires-python = ">=3.12"`.
- Standardise GitHub Actions checkout version to `@v6` in `spellcheck.yml` and `lint.yml`.
- Fix `lint.yml` target paths from `src/` to `modules/` to reflect actual codebase structure.
- Sync `.pre-commit-config.yaml` hook revisions to match `dev-requirements.txt` (black 26.5.1, isort 8.0.1, flake8 7.3.0).
- Fix `.dockerignore` entry `CHANGELOG` → `CHANGELOG.md` after changelog file rename.
- Normalise `AGENTS.md` and `.dockerignore` line endings from CRLF to LF.
- Remove stale `Dockerfile.lxml` entry from `.dockerignore` (file was removed from the repo long ago).
- Update `CLAUDE.md` test file list to reflect all current test files in `tests/`.
- Add "Chore" PR type option to pull request template to match the project's existing `chore/` branch convention.
- Remove `reciperr_list` from `collection-schema.json` (Reciperr builder was removed).
- Update spellcheck configuration: exclude `docs/kometa/acknowledgements.md` (credits file) and update wordlist.
- Add spellcheck to pre-commit configuration.

### Removed

- Reciperr builder removed; the Reciperr site has been unresponsive for an extended period.

### Fixed

- Dynamic collection titles with unresolved template variables in `title_format` (e.g. `<<limit>>` from a template `default:` block, or `<<key>>` from per-key dynamic variables) no longer cause `delete_collections: configured: true` to incorrectly treat those collections as unconfigured and delete them. #1904
- When `run_order` places `operations` before `collections`, configured collections are no longer incorrectly reported as unconfigured by `show_unconfigured` or targeted by `delete_collections: configured: true`. #1968
- Fix "Movies Removed" report entries missing release year; titles now match the "Movies Missing" format e.g. `The Grapes of Wrath (1939)`. Fixes #2028
- Invalidate cached Plex items after each batch edit in operations so that the overlay phase reads post-operations values (e.g. updated ratings) rather than stale pre-operations values. Fixes rating overlays not updating when `mass_critic_rating_update` (or audience/user equivalents) runs before overlays in the same Kometa pass. #2357
- Overlay backdrops with `back_line_color` set but no `back_line_width` no longer crash; `back_line_width` now defaults to 1 in that case. #2645
- Fix `monthly(N)` schedule: values greater than the current month's last day (e.g. `monthly(31)` in November) no longer fire on the last day of the month as a fallback. `monthly(N)` now only triggers when today is exactly day N. A warning is logged when a configured day does not exist in the current month, directing users to the new `monthly(last)` option. Fixes #2884
- Streaming default's `run_definition` now honors `use_all: false`; previously dynamic keys without an explicit `use_<key>` ran regardless. #2922
- Catch KeyError on Plex NFO build.
- Fixing "list index out of range" error when processing IMDb charts. #3006
- TMDB language now reflected in `mass_poster_update`; cache extension.
- Reduce size of FILMIN logo.
- Reduce size of FILMIN white logo.
- Replace top-ten-pirated default list with an updated, Kometa-controlled one.
- Align Kometa's AniList season translation from `current` to match AniList.
- Fix an issue where `tvdb_to_imdb` writes the wrong IMDb ID when a TVDb movie ID collides with a TVDb series ID.
- Update Letterboxd list/watchlist parser for the React-based `LazyPoster` markup, which replaced the `data-film-id` nodes the `letterboxd_list`, `letterboxd_user_films`, and `letterboxd_user_reviews` builders relied on.
- Update Letterboxd URL parsing to handle unlisted lists and shuffle argument in the URL.
- Restore support for Letterboxd `/detail/` list views and `/USERNAME/films/reviews/` URLs.
- Update Letterboxd Top 100 Western to use official list.
- Fix `imdb_awards` failing when any one of the `award_filters` or `category_filters` does not exist; this now produces a warning and the builder will only fail if all of the `award_filters` or all of the `category_filters` do not exist.
- Fix `imdb_watchlist` rejecting the new IMDb user ID format (`p.xxxxxxx`). Now accepts both `ur########` (legacy) and `p.xxxxxxx` formats, as a bare ID or full watchlist URL.
- TVDb 4xx responses (series/movie removed or merged on TVDb) now raise a dedicated `tvdb.NotFound` so the missing-show iteration and TVDb-filter paths log them at debug instead of error. Stale TVDb IDs returned by TMDb `external_ids` no longer spam logs or trigger webhook failure notifications. #3047
- Replace `mass_imdb_parental_labels` HTML scrape of `/parentalguide` with IMDb's GraphQL API, which is not WAF-gated and returns structured parental guide data directly. Fixes silent label failures caused by IMDb's CloudFront WAF returning HTTP 202 (empty body) to scraper requests. #3053
- Fix trakt_chart watched/collected URLs to use `/movies(shows)/watched(collected)/{period}` and default period to "weekly"; fix recommended to use `/recommendations/movies(shows)`. #3057
- TMDb collection requests that 404 (collection deleted upstream — TMDb now only permits collections for true movie sequels) now raise a dedicated `tmdb.NotFound`. When the ID was auto-discovered by a default (e.g. the `franchise` default scanning `tmdb_collection` IDs from the library), the collection is skipped as "Ignored" instead of failing with a critical error and webhook notification. IDs in user-authored config files still raise as before.
- TMDb collection, movie, and show 404 responses now raise a dedicated `tmdb.NotFound` (mirroring the existing `tvdb.NotFound` pattern); `validate_tmdb_ids` logs an actionable hint for stale collection IDs pointing franchise-default users to the `exclude` template variable.
- Fix MDBList Sync Progress percentage overflowing for lists over 1000 items (e.g. `6378/378 (1687%)`). Fetch list metadata upfront to get the true total item count. #3157
- Fix `ZeroDivisionError` crash in `plex_update_in_batches` when running `mass_genre_update` or `mass_imdb_parental_labels` (and any operation producing multiple label/genre groups per item). Cache eviction introduced by #3156 is now scoped to rating updates only via an `evict_cache` parameter; a defensive guard prevents any future empty-list crash. #3163
- Guard against `_graph_request` returning `None` for items with no IMDb record (e.g. `Looney Tunes`); previously the unguarded `.get()` call raised an `AttributeError` that escaped the `except Failed` handler in `operations.py` and aborted processing for the entire library. #3165
- Fix `mass_imdb_parental_labels` crash when IMDb GraphQL returns `null` for the title node (e.g. items whose only Plex GUIDs are `tmdb://` or `tvdb://`, such as `Looney Tunes`); `.get("title", {})` returns `None` when the key exists with a null value, causing `AttributeError` on the next `.get()` call. Replaced the chained one-liner with explicit variable extraction using `or {}` at each level. Added a pre-call guard in `operations.py` to skip items with no IMDb ID entirely. #3165
- `delete_collections: configured: false` no longer incorrectly deletes configured Kometa-managed collections when `run_order` places `operations` before `collections`. The check previously relied on `library.collections` (populated during the collection run), which is always empty when operations executes first — so every managed collection appeared unconfigured and was deleted. The fix uses `collection_names` (pre-populated from config before the run-order loop) expanded with English-translated titles, so default collections whose YAML key differs from their Plex title (e.g. `award/spirit` → `Spirit Best Feature Winners`) are also correctly recognised as configured. #3168
- Addresses edge case where missing `settings:minimum_items` would make Kometa redact `1` in the log.
- Hide some traceback errors for "known good" errors that don't require a full trace.
- Fix an issue where collections would not be recognised as configured if they were not scheduled to run.
- Fix an issue where Plex would fail to update collections if the casing of the collection name did not match the YAML (e.g. "Dogs And Cats" vs "Dogs and Cats").
- Fix shared `ignore_ids` and `ignore_imdb_ids` template variables for builders that resolve Plex `ratingKey`s first.
- Fix dynamic collection sync loop when `translation_key` and `title_format`/`name_format` are both set — `meta.py` sync key now follows the same name-resolution priority as `builder.py` (`name_format` → translation → `title_format`), eliminating the orphan-delete loop on every run. If the translation name still contains unresolvable library-context variables (e.g. `<<library_translationU>>`), `meta.py` falls back to `title_format` (which has `<<library_typeU>>` pre-resolved) to ensure the sync key matches what `builder.py` writes to Plex. #3189
- Fix `title_format` fallback value in `award/sag.yml` to match its translation name (`Screen Actors Guild Awards <<key_name>>`); fix accent typo in `award/cesar.yml` (`César <<key_name>>`). #3189
- Fix inconsistent asset poster selection and overlay cache invalidation when replacing local asset files. #3196
- Fix `audio_language`/`subtitle_language` `plex_search` on show libraries returning fewer results than expected when Plex returns regional language codes (e.g. `en-US`) instead of base codes (`en`). #2777
- Sanitize PR branch names in CI workflows (`validate-pull.yml`, `increment-build.yml`, `tag-cleanup.yml`) by replacing non-Docker-safe characters with `-`; branch names containing `/` (e.g. `feature/my-fix`) previously caused Docker Hub tag pushes and deletes to fail. #3207
- Fix `tag-cleanup.yml` output key mismatch (`tag_name` vs `tag-name`) that caused the Docker Hub tag DELETE to always target an empty tag name, leaving stale tester tags behind. #3207
- Fix sync-based collections with `minimum_items: 1` and `delete_below_minimum: true` so they remove the last stale item and delete the collection when the source list drops to zero items. #3209
- Invalidate cached Plex items after batched edits in operations so metadata files can override values in the same run instead of flip-flopping on later runs. #3211
- Fix `other_name` in dynamic collections: `<<library_type>>` and `<<library_typeU>>` placeholders are now resolved (they were applied to `title_format` but not to `other_name`). Also fix a long-standing copy-paste bug where `other_name` supplied via `template_variables` was read from `self.temp_vars["remove_suffix"]` instead of `self.temp_vars["other_name"]`. #3215
- Fix an issue with AniList search date modifiers not working. #3220
- Fix Studio Defaults capitalization issues. #3221

## [v2.3.1] - 2026-04-01

Prior history is captured in [GitHub Releases](https://github.com/Kometa-Team/Kometa/releases).

[unreleased]: https://github.com/Kometa-Team/Kometa/compare/v2.4.3...HEAD
[v2.4.3]: https://github.com/Kometa-Team/Kometa/compare/v2.4.2...v2.4.3
[v2.4.2]: https://github.com/Kometa-Team/Kometa/compare/v2.3.1...v2.4.2
[v2.3.1]: https://github.com/Kometa-Team/Kometa/releases/tag/v2.3.1
