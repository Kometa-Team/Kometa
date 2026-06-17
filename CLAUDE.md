# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Kometa Is

Kometa is a metadata editor for Plex media servers. It creates and manages collections, overlays, and metadata for movies/TV shows by pulling data from external services (TMDb, Trakt, IMDb, AniDB, MyAnimeList, Letterboxd, Radarr, Sonarr, etc.) and writing it back to Plex.

## Running Kometa

```bash
python kometa.py [options]
```

Key flags:

- `--config/-c <path>` — specify config file (default: `config/config.yml`)
- `--run/-r` — run immediately without the scheduler
- `--tests/-ts` — run only collections with `test: true`
- `--debug/-db` — enable debug logging
- `--run-collections/-rc "Name1|Name2"` — run specific collections (pipe-separated)
- `--run-libraries/-rl "Library1|Library2"` — run specific libraries
- `--times/-t HH:MM` — scheduler run times (default `05:00`)

## Testing

```bash
pytest tests/
pytest tests/test_builder.py          # single file
pytest tests/test_builder.py::TestName  # single test
```

Tests live in `tests/` — current files: `test_builder.py`, `test_textfile.py`, `test_apprise_notify.py`, `test_collection_schema.py`, `test_letterboxd.py`, `test_simkl.py`, `test_tmdb.py`, `test_tvdb.py`, `test_validator.py`.

## Linting & Formatting

Dev tools are in `dev-requirements.txt`. Configuration is in `pyproject.toml` (line-length 256 for all tools).

```bash
black .
isort .
flake8 .
mypy .
bandit -r modules/
```

Pre-commit hooks (black, isort, flake8, pyspelling) are configured in `.pre-commit-config.yaml`.

## Changelog & Versioning

- `CHANGELOG.md` follows [keepachangelog](https://keepachangelog.com/en/1.1.0/) format. All changes go under `## [Unreleased]` until a release is tagged.
- `VERSION` is managed by GitHub workflows. The `release-master.yml` workflow controls version bumps (major/minor/patch). The nightly merge workflow auto-increments the `-buildXX` suffix on each merged PR.
- Kometa follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). New features → minor bump; bug fixes only → patch; breaking changes → major.
- See `CONTRIBUTING.md` for the full contributor guide (branching model, PR checklist, CHANGELOG.md section conventions).

## Architecture

### Data Flow

```text
kometa.py (CLI + scheduler)
  → config.py (parse config.yml)
    → plex.py (connect to Plex library)
      → builder.py (CollectionBuilder — fetch from APIs, build collections/overlays)
        → tmdb.py / trakt.py / imdb.py / mal.py / ... (external data sources)
        → cache.py (SQLite cache for API responses)
      → overlays.py / overlay.py (generate overlay images via Pillow)
      → operations.py (library-level operations: sort, label, etc.)
  → meta.py (playlist files)
```

### Key Modules (`modules/`)

| File | Role |
| ---- | ---- |
| `builder.py` (273 KB) | `CollectionBuilder` — the central class that processes every collection/overlay definition, queries all data sources, and applies results to Plex |
| `config.py` (121 KB) | Parses and validates `config.yml`; instantiates library and API objects |
| `plex.py` (102 KB) | `PlexAPI` wrapper; all reads/writes to the Plex server |
| `meta.py` (162 KB) | Playlist file handling |
| `operations.py` (78 KB) | Library operations (mass-edit, sort, remove, etc.) |
| `cache.py` (73 KB) | SQLite-backed cache for all external API responses |
| `overlays.py` / `overlay.py` | Overlay image composition |
| `util.py` (45 KB) | Shared utilities, custom logger (`logger`), and the `Failed` / `NotScheduled` exception sentinels |

Each external service has its own module: `tmdb.py`, `trakt.py`, `imdb.py`, `anidb.py`, `anilist.py`, `mal.py`, `letterboxd.py`, `mdblist.py`, `omdb.py`, `tvdb.py`, `radarr.py`, `sonarr.py`, `tautulli.py`.

### Configuration Files

- `config/config.yml.template` — annotated template for user config
- `defaults/` — pre-made Kometa-shipped collection/overlay YAML files, split by `movie/`, `show/`, `overlays/`, etc.
- `config/overlays/` — user overlay definitions

### Logging

`util.py` exposes a custom `logger` object (wraps Python logging with extra methods like `logger.ghost`, `logger.separator`). Log files rotate and are written to `logs/` by default. Use `logger` rather than `print` everywhere.

### Error Handling Conventions

- `Failed` — raised inside builders to abort a single collection without stopping the run
- `NotScheduled` — raised when a collection's schedule doesn't match the current run time
- Both are caught in `kometa.py`'s orchestration loops and treated as non-fatal
