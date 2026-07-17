# Kometa API Server Design

**Date:** 2026-06-28
**Status:** Approved

## Overview

Convert Kometa from a CLI script into a long-running server that exposes an HTTP API for both control-plane operations (triggering runs, checking status, viewing logs) and config management (CRUD on collections, overlays, and global config). The server replaces `kometa.py` as the primary entry point and serves a frontend UI from the same process.

## Goals

- Replace the existing `kometa.py` entry point with a `server.py` that runs Kometa's scheduler and processing logic alongside a FastAPI web server.
- Expose all Kometa config (global settings, libraries, collections, overlays, playlists) as structured JSON via a REST API — broad enough to eventually absorb the functionality of the separate Quickstart config editor tool.
- Provide a job system for async run execution with log polling.
- Serve a frontend SPA from the same process.
- Leave all existing modules (`modules/`) untouched.

## Non-Goals

- Concurrent multi-server runs (designed for, not implemented in this phase).
- Full runtime validation of config on write (handled at run time, as today).
- Prescribing a frontend framework.
- WebSocket log streaming (polling is sufficient for now).

## Architecture

A new `server.py` entry point starts three things in one process:

1. **FastAPI + Uvicorn** — serves the HTTP API and static frontend.
2. **Scheduler thread** — the existing `schedule` library loop in a background thread, unchanged from `kometa.py`.
3. **Job worker thread** — picks jobs off a SQLite queue and calls existing Kometa run functions.

```
server.py                  ← new entry point (replaces kometa.py as primary)
kometa.py                  ← retained as legacy CLI fallback
api/
  app.py                   ← FastAPI app, mounts routers + static files
  auth.py                  ← X-API-Key dependency
  jobs.py                  ← SQLite-backed job queue + worker thread
  scheduler.py             ← wraps schedule library in background thread
  routers/
    runs.py                ← POST/GET /api/runs
    libraries.py           ← GET /api/libraries
    collections.py         ← CRUD /api/libraries/{lib}/collections
    config.py              ← GET/PUT /api/config, GET/PUT /api/schedule
modules/                   ← unchanged
frontend/
  dist/                    ← built frontend assets, served at /
```

**New dependencies:** `fastapi`, `uvicorn[standard]`. SQLite is stdlib.

## API Surface

All routes require `X-API-Key` header except `GET /api/health`.

### Control Plane

```
GET    /api/health                                    — liveness, no auth
GET    /api/status                                    — current run status, next scheduled run

POST   /api/runs                                      — trigger a run
GET    /api/runs                                      — list recent runs
GET    /api/runs/{job_id}                             — job status + log output
GET    /api/runs/{job_id}?offset=N                    — log lines since offset N
DELETE /api/runs/{job_id}                             — cancel a queued run

GET    /api/schedule                                  — configured run times
PUT    /api/schedule                                  — update run times (writes config.yml)
```

`POST /api/runs` body (all fields optional):
```json
{
  "server": "Main",
  "libraries": ["Movies"],
  "collections": ["Best of 2024"]
}
```

### Config Management

```
GET    /api/config                                             — global config (secrets masked)
PUT    /api/config                                             — update global config

GET    /api/libraries                                          — list configured libraries
GET    /api/libraries/{lib}/collections                        — list collections
POST   /api/libraries/{lib}/collections                        — create collection
GET    /api/libraries/{lib}/collections/{name}                 — read collection
PUT    /api/libraries/{lib}/collections/{name}                 — update collection
DELETE /api/libraries/{lib}/collections/{name}                 — delete collection
```

### Constraints

- `POST /api/runs` returns `409 Conflict` if a run is already active for the specified server.
- Config write endpoints return `423 Locked` if a run is in progress (prevents mid-run mutation).
- `GET /api/config` replaces secret values (tokens, passwords) with `"***"` in the response.

## Job System

Jobs are stored in a `jobs` table in a new `kometa_server.db` SQLite file, separate from the existing `cache.db` to keep concerns isolated.

**Job record:**

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `server_name` | string | Plex server this run targets |
| `triggered_by` | string | `"api"` or `"scheduler"` |
| `attrs` | JSON | Run attrs (library/collection filters, flags) |
| `status` | string | `queued` / `running` / `completed` / `failed` / `cancelled` |
| `created_at` | timestamp | |
| `started_at` | timestamp | Null until picked up |
| `finished_at` | timestamp | Null until complete |
| `log` | text | Accumulated log output, appended in real time |

**Log capture:** A log handler is attached to `MyLogger` for the duration of each job, writing lines into the `log` field. `GET /api/runs/{job_id}?offset=N` returns only lines after line number N, enabling the frontend to poll incrementally without re-fetching the full log.

**Concurrency:** A `threading.Lock` is held per server name. The scheduler thread and API handler both acquire the appropriate lock before enqueuing. This is designed so that in a future phase, runs against different Plex servers can proceed concurrently — only same-server runs are serialised.

**Retention:** Jobs older than a configurable period (default 30 days) are pruned on startup.

## Config Management Detail

YAML files are the source of truth. The API reads and writes them via `ruamel.yaml` (already a dependency), which preserves comments and formatting so hand-edited configs remain intact.

- `GET /api/config` parses `config.yml` and returns the global section as JSON.
- `PUT /api/config` merges the incoming JSON patch and writes the file.
- Collection CRUD targets the individual metadata YAML files referenced in `config.yml`. Create appends, update replaces in place, delete removes — all via `ruamel.yaml`.
- The API does not validate the full Kometa config schema on write; structural JSON correctness only. Runtime validation happens at run time, as today.
- Secrets are accepted on write but masked (`"***"`) on read.

### Quickstart Integration (Future)

The separate [Kometa-Team/Quickstart](https://github.com/Kometa-Team/Quickstart) tool is an interactive config editor. It currently does not expose all `config.yml` settings and does not support external YAML files (collections, overlays, metadata). This API is intentionally broad — covering all config — so that Quickstart's functionality can eventually be reimplemented as a frontend consuming this API, rather than maintained as a standalone tool.

## Authentication

- API key set via `KOMETA_API_KEY` environment variable, or a field in `config.yml` as fallback.
- All routes (except `/api/health`) require `X-API-Key: <key>` header.
- Missing or invalid key returns `401 Unauthorized`.
- The key is never returned by any API response.

## Frontend Serving

- `frontend/dist/` is mounted as a `StaticFiles` directory by FastAPI, served at `/`.
- A catch-all route returns `index.html` for any non-`/api/` path, enabling client-side routing.
- Framework choice is deferred — plain HTML/JS is sufficient for an initial phase; React/Vue/etc. can replace it without changing the serving mechanism.
- CORS is disabled by default (same-origin). Optionally enabled via config for development.

## Testing

New test files follow the existing pytest pattern in `tests/`:

| File | Coverage |
|---|---|
| `tests/test_api_runs.py` | Trigger runs, poll status, 409 on concurrent same-server run, per-server lock |
| `tests/test_api_collections.py` | CRUD operations, YAML round-trip correctness |
| `tests/test_api_config.py` | Read/write global config, secret masking, 423 lock during active run |
| `tests/test_jobs.py` | Job lifecycle, log accumulation, retention pruning |

FastAPI's `TestClient` is used for route tests. The SQLite job store uses an in-memory database in tests. Kometa run functions are mocked — these tests cover the API layer only.

## Decision Summary

| Concern | Decision |
|---|---|
| Entry point | New `server.py`; `kometa.py` kept as legacy CLI |
| Web framework | FastAPI + Uvicorn |
| Job storage | SQLite, per-server lock |
| Log access | Poll `GET /api/runs/{id}?offset=N` |
| Config storage | YAML files via `ruamel.yaml`, unchanged format |
| Auth | `X-API-Key` header, `KOMETA_API_KEY` env var |
| Frontend | Served from `frontend/dist/` at `/`, framework TBD |
| Concurrency | One run per Plex server at a time (multi-server concurrent: future) |
| New deps | `fastapi`, `uvicorn[standard]` |
| Future | Quickstart absorbed into config management API |
