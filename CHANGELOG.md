# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New `text_file` builder.
- Initial support for SIMKL.com; trending lists and dvd-releases list.
- Add `language` parameter to `mass_poster_update` and `mass_background_update` to override TMDb language for image fetching (e.g. `xx` for textless posters).
- Add `plex_csm` and `plex_csm0` sources to `mass_content_rating_update` (reads CSM age rating from Plex's own cached `commonSenseMedia.ageRatings`, no external API key required).
- Add Apprise as a webhook notification provider.
- Add Plex square art support: upload `square.ext` assets for movies, shows, seasons, albums, and playlists via `find_and_upload_assets`. Extends metadata file items and library operations.
- Add comprehensive config validation with `--validate`, `--validate-level`, `--validate-schema`, and `--schema-path` CLI flags. Supports syntax, structure, full, and schema-level validation with a gap report showing missing/extra fields.
- Add `--validate-file` and `--validate-dir` CLI flags for standalone and batch YAML validation against auto-detected schema types (config, collection, metadata, overlay, playlist). Output written to `validate.log`.
- Add `modules/validator.py` with `ConfigValidator` (multi-level config validation) and `FileSetValidator` (standalone/batch YAML validation with schema type detection).
- Expand `json-schema/config-schema.json` with full coverage and add per-type schemas: `collection-schema.json`, `metadata-schema.json`, `overlay-schema.json`, `playlist-schema.json`.
- Add `apprise` and `schedule_overlays` to the config JSON schema.
- Add E4 to network overlay and show network collection. #2975
- Add jsonschema 4.23.0.
- Add letterboxdpy 6.5.0.
- Report deactivated Trakt accounts [Trakt returns a 410].

### Changed

- Sync `pyproject.toml` pinned dependencies to match `requirements.txt` (lxml, requests, pillow, packaging, gitpython, pywin32; add letterboxdpy).
- Align Black `target-version` to `["py312"]` in `pyproject.toml` to match the project's existing `requires-python = ">=3.12"`.
- Standardise GitHub Actions checkout version to `@v6` in `spellcheck.yml` and `lint.yml`.
- Fix `lint.yml` target paths from `src/` to `modules/` to reflect actual codebase structure.
- Sync `.pre-commit-config.yaml` hook revisions to match `dev-requirements.txt` (black 26.5.1, isort 8.0.1, flake8 7.3.0).
- Fix `.dockerignore` entry `CHANGELOG` → `CHANGELOG.md` after changelog file rename.
- Normalise `AGENTS.md` and `.dockerignore` line endings from CRLF to LF.
- Remove stale `Dockerfile.lxml` entry from `.dockerignore` (file was removed from the repo long ago).
- Update `CLAUDE.md` test file list to reflect all 9 current test files in `tests/`.
- Add "Chore" PR type option to pull request template to match the project's existing `chore/` branch convention.
- Remove `reciperr_list` from `collection-schema.json` (Reciperr builder was removed).
- Update spellcheck configuration: exclude `docs/kometa/acknowledgements.md` (credits file) and update wordlist.
- Add spellcheck to pre-commit configuration.
- Switch to GraphQL for IMDb charts retrieval, with a fallback to the old method if the GraphQL request fails. #3006
- Replace Kometa's internal Letterboxd scraping with a letterboxdpy-backed adapter while preserving existing Letterboxd builder names.
- Extend default "Metacritic Must See" collection to work with TV.
- Process collection alterations [add/remove] in batches of 100 to avoid "400 Bad Request" on mile-long URLs.
- Exit early if more than one of the `--SOMETHING-only` flags are set.
- Cache people data for media items since it's unlikely to change.
- The `tmdb_discover` YAML validator now enforces: unknown keys are rejected, value types are checked, `certification_country`/`certification` must co-occur, `watch_region` must accompany any watch-provider or monetization key, and movie-only and TV-only parameters are mutually exclusive. Note: `with_watch_providers` and `without_watch_providers` now require `watch_region` at validation time (the TMDb Discover API requires this), which is stricter than the runtime check in `builder.py`.
- `--validate` now implies immediate run (like `--run-libraries`).
- Use the SQLite cache for TMDb queries in `check_filters` and `check_missing_filters` instead of bypassing it with `ignore_cache=True`.
- Only force-reload Plex items in the overlay loop when `reapply_overlays` is set; reuse the session cache on normal runs.
- Use set lookup instead of list scan when checking collection membership in `add_to_collection` and `run_collections_again`, reducing complexity from O(n×m) to O(n).
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
- Updates to Quickstart docs about limitations.
- Updates to Trakt and MAL flow pages.
- Update Letterboxd builder docs to reflect letterboxdpy-backed filtering, ordering, and incremental behavior.
- Document the valid `font_style` values for the default Inter font and note that valid styles are font-specific. #2925
- Call out the schema file as supporting only `config.yml` explicitly.

### Removed

- Reciperr builder removed; the Reciperr site has been unresponsive for an extended period.

### Fixed

- Catch KeyError on Plex NFO build.
- Fixing "list index out of range" error when processing imdb charts #3006
- TMDB language now reflected in mass_poster_update; cache extension
- Reduce size of FILMIN logo
- Replace top-ten-pirated default list with an updated, kometa-controlled one.
- Overlay backdrops with `back_line_color` set but no `back_line_width` no longer crash; `back_line_width` now defaults to 1 in that case. #2645
- Update Letterboxd list/watchlist parser for the React-based `LazyPoster` markup, which replaced the `data-film-id` nodes the `letterboxd_list`, `letterboxd_user_films`, and `letterboxd_user_reviews` builders relied on.
- Streaming default's `run_definition` now honors `use_all: false`; previously dynamic keys without an explicit `use_<key>` ran regardless. #2922
- Reduce size of FILMIN white logo
- Fix trakt_chart watched/collected URLs to use /movies(shows)/watched(collected)/{period} and default period to "weekly"; fix recommended to use /recommendations/movies(shows). #3057
- TVDb 4xx responses (series/movie removed or merged on TVDb) now raise a dedicated `tvdb.NotFound` so the missing-show iteration and TVDb-filter paths log them at debug instead of error. Stale TVDb IDs returned by TMDb `external_ids` no longer spam logs or trigger webhook failure notifications. #3047
- Align Kometa's AniList season translation from `current` to match Anilist.
- TMDb collection requests that 404 (collection deleted upstream — TMDb now only permits collections for true movie sequels) now raise a dedicated `tmdb.NotFound`. When the ID was auto-discovered by a default (e.g. the `franchise` default scanning `tmdb_collection` IDs from the library), the collection is skipped as "Ignored" instead of failing with a critical error and webhook notification. IDs in user-authored config files still raise as before.
- Update Letterboxd Top 100 Western to use Official list
- Fix MDBList Sync Progress percentage overflowing for lists over 1000 items (e.g. `6378/378 (1687%)`). Fetch list metadata upfront to get the true total item count. #3157
- Fix "Movies Removed" report entries missing release year; titles now match the "Movies Missing" format e.g. `The Grapes of Wrath (1939)`. Fixes #2028
- When `run_order` places `operations` before `collections`, configured collections are no longer incorrectly reported as unconfigured by `show_unconfigured` or targeted by `delete_collections: configured: true`. #1968
- Dynamic collection titles with unresolved template variables in `title_format` (e.g. `<<limit>>` from a template `default:` block, or `<<key>>` from per-key dynamic variables) no longer cause `delete_collections: configured: true` to incorrectly treat those collections as unconfigured and delete them. #1904
- Invalidate cached Plex items after each batch edit in operations so that the overlay phase reads post-operations values (e.g. updated ratings) rather than stale pre-operations values. Fixes rating overlays not updating when `mass_critic_rating_update` (or audience/user equivalents) runs before overlays in the same Kometa pass. #2357
- TMDb collection, movie, and show 404 responses now raise a dedicated `tmdb.NotFound` (mirroring the existing `tvdb.NotFound` pattern); `validate_tmdb_ids` logs an actionable hint for stale collection IDs pointing franchise-default users to the `exclude` template variable.
- TVDb 5xx server errors now raise `TVDbServerError` (not a `Failed` subclass) so tenacity retries them up to 6 times; previously a single flaky 5xx response aborted the item without any retry.
- Replace `mass_imdb_parental_labels` HTML scrape of `/parentalguide` with IMDb's GraphQL API, which is not WAF-gated and returns structured parental guide data directly. Fixes silent label failures caused by IMDb's CloudFront WAF returning HTTP 202 (empty body) to scraper requests. #3053
- Fix `mass_imdb_parental_labels` crash when IMDb GraphQL returns `null` for the title node (e.g. items whose only Plex GUIDs are `tmdb://` or `tvdb://`); replaced chained one-liner with explicit `or {}` guards at each level and added a pre-call guard in `operations.py` to skip items with no IMDb ID. #3165
- Addresses edge case where missing `settings:minimum_items` would make Kometa redact `1` in the log. #3169
- Update Letterboxd URL parsing to handle unlisted lists and shuffle argument in the url. #3151

## [2.3.1] - 2026-04-01

For changes prior to this version, see the [GitHub Releases](https://github.com/Kometa-Team/Kometa/releases) page.

[unreleased]: https://github.com/Kometa-Team/Kometa/compare/v2.3.1...HEAD
[2.3.1]: https://github.com/Kometa-Team/Kometa/releases/tag/v2.3.1
