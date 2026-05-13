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
|-------|------------|
| Language | Python 3.10+ (strict minimum) |
| Main entry | `kometa.py` (CLI script, ~1,270 lines) |
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
- `lxml==6.0.4` — HTML/XML scraping (IMDb, etc.)
- `ruamel.yaml==0.19.1` — round-trip YAML editing
- `requests==2.33.1` + `cloudscraper==1.2.71` — HTTP with Cloudflare bypass
- `pathvalidate==3.3.1` — safe filename generation
- `python-dotenv==1.2.2` — `.env` file support

### Development Dependencies

See `dev-requirements.txt`:

- `black==26.3.1`
- `isort==8.0.1`
- `flake8==7.3.0`
- `mypy==1.20.1`
- `bandit==1.9.4`
- `prek==0.3.9` (wrapper around the above)

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
│   ├── simkl.py              # SIMKL integration (new)
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
│   └── ... (40 modules total)
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

### Execution Flow

1. `kometa.py` parses CLI arguments and environment variables (`KOMETA_*` and legacy `PMM_*`).
2. On first run (or missing config), it downloads `config.yml.template` from GitHub raw.
3. `ConfigFile` (`modules/config.py`) validates and loads the YAML, instantiating service objects (TMDb, Trakt, Plex, etc.).
4. The scheduler (`schedule` library) triggers `start()` at configured times, or runs immediately with `--run`.
5. `run_libraries()` iterates over each Plex library defined in config.
6. Per library, `run_collection()` creates a `CollectionBuilder` that evaluates builders (TMDb list, Trakt list, Plex search, etc.) and applies filters.
7. Overlays, metadata, and operations run in a defined order configurable by the user.
8. `ProcessPoolExecutor(max_workers=1)` is used to isolate some runs in a subprocess.

### Key Patterns

- **Builders**: Each external source exposes a `builders` tuple of strings (e.g., `tmdb_collection`, `trakt_list`). `CollectionBuilder` dynamically validates and dispatches to the correct source module.
- **Custom Exceptions**: `Failed`, `NotScheduled`, `Deleted`, `NonExisting`, `FilterFailed`, `Continue` drive control flow without deep nesting.
- **Logger**: `MyLogger` in `modules/logs.py` is a singleton-like object attached to `util.logger`. It supports custom width, divider characters, ghost-message suppression, trace mode, and request logging.
- **Retries**: `tenacity` is used for 429-rate-limit retries with `Retry-After` header awareness (`util.py`).
- **Cache**: `modules/cache.py` uses SQLite to cache TMDb/Trakt/IMDb responses and overlay images, with configurable expiration.

---

## Build and Test Commands

### Install Dependencies

```bash
# Runtime
pip install -r requirements.txt

# Development
pip install -r dev-requirements.txt
```

### Run Kometa Locally

```bash
# One-shot run
python kometa.py --run

# With custom config
python kometa.py --run --config /path/to/config.yml

# Debug / trace modes
python kometa.py --run --debug
python kometa.py --run --trace

# Run only specific subsystems
python kometa.py --run --collections-only
python kometa.py --run --overlays-only
python kometa.py --run --metadata-only
python kometa.py --run --operations-only
python kometa.py --run --playlists-only
```

### Run Tests

```bash
pytest
```

The test suite is small; most validation is done via Docker test builds and community testing (see CI/CD).

### Lint / Format (Developer Tooling)

```bash
# Format code
black modules/ tests/ *.py

# Sort imports
isort --profile black modules/ tests/ *.py

# Lint
flake8 modules/ tests/ *.py --max-line-length=256 --extend-ignore=E203,W503

# Type check (optional; currently best-effort)
mypy modules/

# Security scan
bandit -r modules/ -c pyproject.toml
```

There is also a convenience wrapper `prek` installed from `dev-requirements.txt`:

```bash
prek run --all-files --show-diff-on-failure
```

### Build Documentation

```bash
pip install -r docs/requirements.txt
mkdocs serve    # Local preview
mkdocs build    # Static site output
```

---

## Code Style Guidelines

- **Formatter**: Black, line length **256**.
- **Import sorting**: isort with `profile = "black"`.
- **Linting**: flake8, max line length 256, ignoring `E203`, `W503`.
- **Type hints**: Encouraged but not enforced; mypy is run in CI as informational only (`continue-on-error: true`).
- **Security**: bandit scans the repo; `B101` (assert statements) is skipped. Tests, `config/`, and virtual-env directories are excluded.
- **No `src/` layout**: The project uses a flat root layout (`kometa.py` + `modules/` package).

---

## Testing Instructions

- Tests live in `tests/` and use `pytest`.
- The existing tests rely heavily on mocking (fake Plex libraries, fake episodes, fake logger) because Kometa requires a live Plex server and API keys for most real code paths.
- When adding new builder sources or utility modules, add corresponding unit tests with mocks.
- Integration testing is primarily done via Docker image builds on PRs and by community testers on the Discord server.

---

## CI/CD and Deployment

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `validate-pull.yml` | `pull_request_target` | Ensures PRs target `nightly`, spell-checks docs, and optionally builds a Docker test image for branches labeled `docker` or `tester` |
| `docker-version.yml` | Tag push (`v*`) | Builds and pushes multi-arch Docker images for releases (`linux/amd64`, `linux/arm64`, `linux/arm/v7`) |
| `docker-develop.yml` | Push to `develop` | Develop branch Docker image |
| `docker-nightly.yml` | Push to `nightly` | Nightly branch Docker image |
| `docker-latest.yml` | Push to `master` | Latest Docker image |
| `release-master.yml` | Manual (`workflow_dispatch`) | Bumps `VERSION`, tags release, syncs `nightly` → `develop` → `master` |
| `release-develop.yml` | Manual | Develop branch release tasks |
| `increment-build.yml` | Various | Increments the `PART` build counter |
| `lint.yml` | **Disabled** | Was meant to run black/isort/flake8/mypy/bandit |
| `spellcheck.yml` | PR / push | Markdown spell checking |

### Docker

- Image: `kometateam/kometa:<tag>`
- `Dockerfile` uses `tini` as PID 1 and sets `ENTRYPOINT ["/tini", "-s", "python3", "kometa.py", "--"]`.
- The `/config` directory is a volume for persistent user configuration, logs, and caches.

### Branches

| Branch | Stability | Audience |
|--------|-----------|----------|
| `master` | Stable | General users |
| `develop` | Documented beta | Users wanting recent fixes |
| `nightly` | Bleeding edge | Testers and contributors; may break at any time |

**All Pull Requests must target `nightly`.** PRs to `master` or `develop` are rejected by CI.

---

## Security Considerations

- **Secrets**: API keys and tokens live in the YAML config or environment variables (`KOMETA_*`). The CLI redacts known secrets from logged command lines.
- **SSL verification**: `--no-verify-ssl` disables global SSL verification (not recommended for production).
- **Bandit**: Runs on `modules/` in CI; skips `B101` (assert used outside tests).
- **Cloudscraper**: Used to bypass Cloudflare protection on some scraping targets (IMDb, etc.); keep this dependency up to date.
- **Input validation**: `pathvalidate` sanitizes filenames before writing overlays and reports to disk.

---

## Contributing Checklist

When making changes:

1. Target the **`nightly`** branch.
2. Update **`CHANGELOG`** if the change is more than a minor tweak.
3. Update **documentation** (`docs/`) if user-facing behavior changes.
4. Add or update **tests** in `tests/` where feasible.
5. Run the formatter and linter locally:
   ```bash
   black modules/ tests/ *.py
   isort --profile black modules/ tests/ *.py
   flake8 modules/ tests/ *.py --max-line-length=256 --extend-ignore=E203,W503
   ```
6. Keep PRs small and focused when possible.

---

## Useful References

- User Wiki: <https://kometa.wiki>
- Discord: <https://kometa.wiki/en/latest/discord/>
- Docker Hub: <https://hub.docker.com/r/kometateam/kometa>
- JSON Schema: `json-schema/config-schema.json` (validate user configs)
- Default templates: `defaults/` directory
