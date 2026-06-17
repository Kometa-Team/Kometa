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

| Layer | Technology |
| ----- | ---------- |
| Language | Python 3.12+ (strict minimum) |
| Main entry | `kometa.py` (CLI script, ~1,290 lines) |
| Plex API | `PlexAPI` (python-plexapi) |
| Image processing | `Pillow` |
| YAML parsing | `ruamel.yaml` |
| HTTP requests | `requests` + `cloudscraper` |
| Scheduling | `schedule` |
| Caching / DB | Custom SQLite cache in `modules/cache.py` |
| Docs site | MkDocs (Material theme) |
| Container runtime | Docker (`python:3.13-slim` base) |

### Key Runtime Dependencies

See `requirements.txt` for the full pinned list. Notable ones:

- `arrapi==1.4.14` — Sonarr/Radarr API wrapper
- `PlexAPI==4.18.1` — Plex server interaction
- `tmdbapis==1.2.30` — TMDb API wrapper
- `pillow==12.2.0` — image manipulation for overlays
- `lxml==6.1.1` — HTML/XML scraping (IMDb, etc.)
- `ruamel.yaml==0.19.1` — round-trip YAML editing
- `requests==2.34.2` + `cloudscraper==1.2.71` — HTTP with Cloudflare bypass
- `pathvalidate==3.3.1` — safe filename generation
- `python-dotenv==1.2.2` — `.env` file support

### Development Dependencies

See `dev-requirements.txt`:

- `black==26.5.1`
- `isort==8.0.1`
- `flake8==7.3.0`
- `mypy==2.1.0`
- `bandit==1.9.4`
- `prek==0.4.5` (wrapper around the above)

---

## Project Structure

```text
.
├── kometa.py                 # Main entry point: argument parsing, scheduler, run loop
├── VERSION                   # SemVer string (e.g., "2.4.0-build1") — drives nightly build numbering
├── PART                      # Build-part counter used by CI
├── CHANGELOG.md              # Release notes in keepachangelog format
├── CONTRIBUTING.md           # Contributor guide (branching, versioning, code style, PR checklist)
├── requirements.txt          # Runtime dependencies (pinned)
├── dev-requirements.txt      # Lint / format / type-check dependencies
├── pyproject.toml            # Tool configuration (black, isort, bandit)
├── Dockerfile                # Multi-stage-ish Docker build
├── mkdocs.yml                # Documentation site configuration
│
├── modules/                  # Core application code (~26k total lines)
│   ├── config.py             # ConfigFile class: parses kometa config YAML
│   ├── builder.py            # CollectionBuilder: the heart of collection creation
│   ├── plex.py               # Plex class: library scanning, item lookups, edits
│   ├── operations.py         # Library-level operations (mass update, delete, etc.)
│   ├── cache.py              # SQLite-based caching for API responses
│   ├── overlay.py            # Single overlay rendering logic
│   ├── overlays.py           # Overlay application engine
│   ├── meta.py               # PlaylistFile and metadata file parsing
│   ├── util.py               # Shared utilities, exceptions, constants
│   ├── logs.py               # MyLogger: custom formatting, dividers, file handlers
│   ├── request.py            # Requests wrapper: versioning, headers, retries
│   ├── library.py            # Library abstraction helpers
│   ├── tmdb.py               # TMDb API integration
│   ├── trakt.py              # Trakt API integration
│   ├── imdb.py               # IMDb scraping + GraphQL
│   ├── anidb.py              # AniDB integration
│   ├── anilist.py            # AniList integration
│   ├── mal.py                # MyAnimeList integration
│   ├── tvdb.py               # TVDb API integration
│   ├── mdblist.py            # MDBList integration
│   ├── letterboxd.py         # Letterboxd scraping
│   ├── simkl.py              # SIMKL integration
│   ├── radarr.py             # Radarr add/remove/upgrade
│   ├── sonarr.py             # Sonarr add/remove/upgrade
│   ├── textfile.py           # text_file builder
│   ├── github.py             # GitHub raw-file fetcher
│   ├── webhooks.py           # Discord/Slack/generic webhook notifications
│   ├── gotify.py             # Gotify notifications
│   ├── notifiarr.py          # Notifiarr notifications
│   ├── ntfy.py               # ntfy notifications
│   ├── tautulli.py           # Tautulli integration
│   ├── stevenlu.py           # StevenLu lists
│   ├── icheckmovies.py       # ICheckMovies integration
│   ├── mojo.py               # Box Office Mojo integration
│   ├── ergast.py             # Ergast F1 data
│   ├── poster.py             # KometaImage / poster manipulation
│   ├── convert.py            # Unit/data conversion helpers
│   ├── omdb.py               # OMDb integration
│   ├── apprise_notify.py     # Apprise multi-platform notifications
│   └── ... (39 modules total)
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
│   ├── test_apprise_notify.py
│   ├── test_builder.py
│   ├── test_collection_schema.py
│   ├── test_letterboxd.py
│   ├── test_simkl.py
│   ├── test_textfile.py
│   ├── test_tmdb.py
│   ├── test_tvdb.py
│   └── test_validator.py
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
│   ├── collection-schema.json
│   ├── metadata-schema.json
│   ├── overlay-schema.json
│   ├── playlist-schema.json
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

See `CONTRIBUTING.md` for the full guide. Key points for agents:

1. All PRs target `nightly`.
2. Update `CHANGELOG.md` under `## [Unreleased]` and docs where needed.
3. Add tests in `tests/` where feasible.
4. Run `prek run --all-files --show-diff-on-failure` locally before committing.
5. Keep PRs focused — one logical change per PR.

---

## Useful References

- User Wiki: <https://kometa.wiki>
- Discord: <https://kometa.wiki/en/latest/discord/>
- Docker Hub: <https://hub.docker.com/r/kometateam/kometa>
- JSON Schema: `json-schema/config-schema.json` (validate user configs)
- Default templates: `defaults/` directory

---
