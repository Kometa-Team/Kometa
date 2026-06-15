# Kometa — Agent Development Guide

> This file is intended for AI coding agents working on the Kometa codebase. Kometa was formerly known as Plex Meta Manager (PMM).

---

## Project Overview

Kometa is a Python CLI tool that gives users granular control over Plex media libraries. It automates the creation of:

- **Collections** — grouped content (e.g., "Trending on Netflix", "Marvel Cinematic Universe")
- **Overlays** — visual badges on posters (e.g., ratings, resolution, studio logos)
- **Metadata updates** — titles, summaries, artwork, and tags
- **Playlist management** — cross-library playlists
- **Library operations** — mass updates, missing item reporting, and integration with Sonarr/Radarr

Kometa connects to dozens of third-party services (TMDb, IMDb, Trakt, AniDB, MyAnimeList, TVDb, Letterboxd, etc.) to build dynamic collections and overlays. Users configure everything through YAML files.

---

## Technology Stack

- **Language**: Python 3.10+
- **Plex API**: PlexAPI (python-plexapi)
- **Image processing**: Pillow
- **YAML parsing**: ruamel.yaml
- **HTTP**: requests + cloudscraper (Cloudflare bypass)
- **Caching**: SQLite via `modules/cache.py`
- **Scheduling**: schedule library
- **Docs**: MkDocs (Material theme)
- **Container**: Docker (`python:3.13-slim` base)
- **Dev tools**: black, isort, flake8, mypy, bandit (see `dev-requirements.txt`)

Full dependency list: `requirements.txt` (runtime) and `dev-requirements.txt` (development).

---

## Project Structure

```
.
├── kometa.py                 # Main entry point: argument parsing, scheduler, run loop
├── VERSION                   # SemVer string (e.g., "2.3.1-build7")
├── PART                      # Build-part counter used by CI
├── CHANGELOG                 # Human-readable release notes
├── requirements.txt          # Runtime dependencies (pinned)
├── dev-requirements.txt      # Lint / format / type-check dependencies
├── pyproject.toml            # Tool configuration (black, isort, bandit)
├── Dockerfile                # Multi-stage-ish Docker build
├── mkdocs.yml                # Documentation site configuration
│
├── modules/                  # Core application code (~26k lines)
│   ├── config.py             # YAML parsing & validation
│   ├── builder.py            # CollectionBuilder: core collection logic
│   ├── plex.py               # Plex library interaction
│   ├── overlays.py           # Overlay rendering & application
│   ├── cache.py              # SQLite caching layer
│   ├── meta.py               # Metadata & playlist parsing
│   ├── util.py               # Shared utilities & exceptions
│   ├── logs.py               # MyLogger singleton
│   └── ... (37 more: API integrations, notifications, scrapers)
│
├── defaults/                 # Pre-built YAML templates shipped with Kometa
│   ├── award/                # Award-season defaults (Oscars, etc.)
│   ├── both/                 # Defaults that apply to movies & shows
│   ├── chart/                # Chart-based defaults (top 10, trending, etc.)
│   ├── movie/                # Movie-specific defaults
│   ├── show/                 # Show-specific defaults
│   ├── overlays/             # Overlay definition templates
│   ├── posters/              # Default poster assets
│   ├── playlist.yml          # Default playlists
│   └── templates.yml         # Shared Jinja2/YAML macros
│
├── tests/                    # pytest test suite (currently small)
│   ├── test_builder.py
│   ├── test_simkl.py
│   └── test_textfile.py
│
├── docs/                     # MkDocs source
│   ├── requirements.txt      # Docs build dependencies
│   ├── kometa/               # User-facing wiki pages
│   ├── config/               # Config reference docs
│   ├── defaults/             # Defaults documentation
│   ├── files/                # File builder docs
│   └── overrides/            # MkDocs theme overrides
│
├── json-schema/              # JSON Schema for config validation
│   ├── config-schema.json
│   ├── kitchen_sink_config.yml
│   └── prototype_config.yml
│
├── config/                   # Runtime config directory (user data, caches, logs)
│   └── ... (user configs live here; NOT committed)
│
├── fonts/                    # Bundled font files for overlay text rendering
└── .github/
    ├── workflows/            # GitHub Actions (see CI/CD below)
    ├── python/
    │   └── update_sponsors.py
    ├── ISSUE_TEMPLATE/
    ├── pull_request_template.md
    └── ...
```

---

## Architecture Notes

### Key Architecture

- **Execution**: CLI args → config parsing → scheduler → per-library `CollectionBuilder` → overlays/metadata/operations.
- **Builders**: Each data source (TMDb, Trakt, Plex) exposes builder names (e.g., `tmdb_collection`, `trakt_list`). `CollectionBuilder` dispatches dynamically.
- **Exception flow**: Custom exceptions (`Failed`, `NotScheduled`, `FilterFailed`) replace deep nesting for control flow.
- **Caching**: SQLite in `modules/cache.py` caches API responses and overlay images with configurable TTL.
- **Logging**: `MyLogger` singleton in `modules/logs.py` with trace mode and request logging.
- **Retries**: `tenacity` library handles 429 rate limits with `Retry-After` header awareness.

---

## Build & Test

```bash
# Install
pip install -r requirements.txt          # Runtime
pip install -r dev-requirements.txt      # Development

# Run
python kometa.py --run                   # One-shot
python kometa.py --run --config FILE     # Custom config
python kometa.py --run --collections-only --overlays-only --metadata-only

# Test
pytest

# Lint & format
prek run --all-files --show-diff-on-failure  # Runs black, isort, flake8, mypy, bandit

# Docs
pip install -r docs/requirements.txt && mkdocs serve
```

---

## Code Style

- **Formatter**: Black (line length 256)
- **Imports**: isort (profile: black)
- **Linter**: flake8 (max 256, ignore E203/W503)
- **Type hints**: Encouraged; mypy runs informational
- **Security**: bandit (B101 skipped, tests/config/ excluded)
- **Layout**: Flat root (`kometa.py` + `modules/` package)

---

## Testing

- **Unit tests**: `tests/` with pytest, heavily mocked (no live Plex/API required).
- **Integration**: Docker builds on PRs; community testing on Discord.

---

## CI/CD & Deployment

- **Branches**: `nightly` (dev) → `develop` (beta) → `master` (stable). **All PRs must target `nightly`.**
- **Docker**: Multi-arch images at `kometateam/kometa:<tag>` via GitHub Actions on tag/push.
- **Workflows**: Validation, Docker builds, releases. See `.github/workflows/` for details.

---

## Security Considerations

- **Secrets**: API keys and tokens live in the YAML config or environment variables (`KOMETA_*`). The CLI redacts known secrets from logged command lines.
- **SSL verification**: `--no-verify-ssl` disables global SSL verification (not recommended for production).
- **Bandit**: Runs on `modules/` in CI; skips `B101` (assert used outside tests).
- **Cloudscraper**: Used to bypass Cloudflare protection on some scraping targets (IMDb, etc.); keep this dependency up to date.
- **Input validation**: `pathvalidate` sanitizes filenames before writing overlays and reports to disk.

---

## Contributing

1. Target `nightly` branch.
2. Update `CHANGELOG` and docs if needed.
3. Add tests in `tests/` where feasible.
4. Run `prek run --all-files --show-diff-on-failure` locally.
5. Keep PRs focused.

---

## Useful References

- User Wiki: <https://kometa.wiki>
- Discord: <https://kometa.wiki/en/latest/discord/>
- Docker Hub: <https://hub.docker.com/r/kometateam/kometa>
- JSON Schema: `json-schema/config-schema.json` (validate user configs)
- Default templates: `defaults/` directory

---


