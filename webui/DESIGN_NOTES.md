# Kometa Web UI - Design Notes

## Overview

This document describes the architecture, safety guarantees, and design decisions for the Kometa Web UI.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Frontend (HTML/JS) - Port 8080                          │   │
│  │  - Config Editor (YAML + Form views)                     │   │
│  │  - Run Plan Preview                                       │   │
│  │  - Log Viewer (live streaming)                           │   │
│  │  - Run History                                            │   │
│  │  - Safety Controls (DRY RUN / APPLY toggle)              │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP/WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│  Backend (FastAPI)                                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Endpoints                                            │   │
│  │  - GET /api/config - Load config.yml                     │   │
│  │  - POST /api/config - Save config.yml (with backup)      │   │
│  │  - POST /api/config/validate - Validate YAML             │   │
│  │  - POST /api/run - Start Kometa run                      │   │
│  │  - GET /api/run/status - Get run status                  │   │
│  │  - GET /api/run/plan - Generate run plan preview         │   │
│  │  - GET /api/runs - List run history                      │   │
│  │  - GET /api/logs/{run_id} - Get run logs                 │   │
│  │  - WS /ws/logs - Live log streaming                      │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │  Run Manager                                              │   │
│  │  - Subprocess execution of kometa.py                     │   │
│  │  - PID tracking and lock files                           │   │
│  │  - Log capture and streaming                             │   │
│  │  - Run state persistence (SQLite)                        │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │ subprocess
┌───────────────────────────▼─────────────────────────────────────┐
│  Kometa CLI (kometa.py)                                          │
│  - Existing CLI unchanged                                        │
│  - New --dry-run flag for safe preview mode                     │
│  - Write Guard intercepts Plex writes when dry-run enabled      │
└─────────────────────────────────────────────────────────────────┘
```

## Safety Architecture

### Three-Layer Safety Model

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Docker Environment Kill Switch                    │
│  KOMETA_UI_APPLY_ENABLED=false (default)                    │
│  → When false, apply mode is completely disabled            │
│  → Cannot be overridden from UI                             │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  Layer 2: UI Safety Controls                                 │
│  - Default to DRY RUN mode                                  │
│  - Apply mode requires:                                      │
│    1. Explicit toggle switch                                │
│    2. Typed confirmation ("APPLY CHANGES")                  │
│    3. Visible ARMED banner                                  │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  Layer 3: Kometa Write Guard                                 │
│  - modules/write_guard.py                                   │
│  - Wraps all Plex write operations                          │
│  - Checks DRY_RUN flag before any write                     │
│  - Logs what WOULD have been written                        │
└─────────────────────────────────────────────────────────────┘
```

### Safety Rules

1. **Default is SAFE**: All runs default to dry-run mode
2. **Explicit Arming Required**: Apply mode requires conscious user action
3. **Docker Override**: Operators can disable apply mode entirely via environment
4. **Visible State**: Current mode is always visible (banner + status indicators)
5. **CLI Unchanged**: Existing CLI behavior is preserved (no dry-run by default for backwards compatibility)

## Write Guard Implementation

The Write Guard is a minimal, isolated module that intercepts Plex write operations.

### Guarded Operations

| Operation | Plex Method | Guard Action |
|-----------|-------------|--------------|
| Edit metadata | `item.edit()`, `item.editAdvanced()` | Log changes, skip write |
| Upload images | `item.uploadPoster()`, `item.uploadArt()` | Log URL/path, skip upload |
| Collection add | `addCollection()`, `batchMultiEdits()` | Log items, skip modification |
| Collection remove | `removeCollection()` | Log items, skip modification |
| Create playlist | `createPlaylist()` | Log name/items, skip creation |
| Delete objects | `obj.delete()` | Log object, skip deletion |

### Integration Points

The Write Guard uses a **feature flag pattern** that only activates when:
1. Running via the Web UI subprocess, AND
2. `--dry-run` flag is passed

CLI usage remains completely unaffected.

## Configuration Management

### Config Import Flow

```
User selects "Start from existing config.yml"
    │
    ▼
Load /config/config.yml (or user-specified path)
    │
    ▼
Parse YAML with ruamel.yaml (preserves comments)
    │
    ▼
Validate structure against schema
    │
    ├── Valid ──► Populate form fields
    │             Show raw YAML editor
    │
    └── Invalid ─► Show validation errors
                   Still allow raw YAML editing
                   Partial field population where possible
```

### Config Backup Strategy

```
/config/
├── config.yml                    # Active config
└── backups/
    ├── config.yml.20240115-143022
    ├── config.yml.20240115-152341
    └── config.yml.20240116-091500
```

- Backups created on every save via UI
- Timestamp format: YYYYMMDD-HHMMSS
- No automatic cleanup (user manages backups)

## Run Management

### Run State Machine

```
┌──────────┐    start()    ┌──────────┐
│  IDLE    │ ─────────────►│ RUNNING  │
└──────────┘               └────┬─────┘
     ▲                          │
     │                          │ complete/error
     │      ┌───────────────────┘
     │      ▼
     │ ┌──────────┐
     └─│ FINISHED │
       └──────────┘
```

### Run Report Structure

```json
{
  "id": "run_20240115_143022",
  "start_time": "2024-01-15T14:30:22Z",
  "end_time": "2024-01-15T14:45:33Z",
  "duration_seconds": 911,
  "dry_run": true,
  "status": "success",
  "libraries": ["Movies", "TV Shows"],
  "collections_processed": 42,
  "overlays_processed": 15,
  "log_path": "/config/logs/runs/run_20240115_143022.log",
  "exit_code": 0
}
```

## Run Plan Preview

Before any run (dry-run or apply), the UI generates a preview showing:

```
┌─────────────────────────────────────────────────────────────┐
│  RUN PLAN PREVIEW                                            │
│                                                              │
│  Mode: DRY RUN (no changes will be made)                    │
│  ────────────────────────────────────────                   │
│                                                              │
│  Libraries:                                                  │
│    • Movies (1,234 items)                                   │
│    • TV Shows (567 items)                                   │
│                                                              │
│  Collection Files:                                          │
│    • Movies.yml (15 collections)                            │
│    • Charts.yml (8 collections)                             │
│                                                              │
│  Overlay Files:                                             │
│    • resolution.yml                                         │
│    • ratings.yml                                            │
│                                                              │
│  Integrations:                                              │
│    • TMDb: Configured                                       │
│    • Trakt: Configured                                      │
│    • Radarr: Not configured                                 │
│                                                              │
│  Paths:                                                      │
│    • Config: /config/config.yml                             │
│    • Logs: /config/logs/                                    │
│    • Cache: /config/cache.db                                │
│                                                              │
│  ⚠️  DRY RUN: Kometa will analyze your library and log      │
│      what it WOULD do, but NO changes will be made.         │
│                                                              │
│                    [Start Dry Run]                          │
└─────────────────────────────────────────────────────────────┘
```

## Security Considerations

### Local-Only by Default

- UI binds to `0.0.0.0:8080` (configurable)
- No authentication by default (assumes trusted network)
- Optional: `KOMETA_UI_PASSWORD` environment variable for basic auth

### File Access

- UI can only access files within `/config` directory
- Config path validation prevents directory traversal
- No shell command injection possible (uses subprocess with explicit args)

## API Endpoints

### Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config` | Load current config.yml |
| POST | `/api/config` | Save config.yml (creates backup) |
| POST | `/api/config/validate` | Validate YAML without saving |
| GET | `/api/config/backups` | List available backups |
| POST | `/api/config/restore/{backup}` | Restore from backup |

### Runs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/run` | Start a new run |
| GET | `/api/run/status` | Get current run status |
| POST | `/api/run/stop` | Stop current run (SIGTERM) |
| GET | `/api/run/plan` | Generate run plan preview |
| GET | `/api/runs` | List run history |
| GET | `/api/runs/{id}` | Get specific run details |
| GET | `/api/logs/{id}` | Get logs for a run |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/logs` | Real-time log streaming |
| `/ws/status` | Run status updates |

## Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backend | FastAPI | Modern, async, excellent WebSocket support |
| Frontend | Vanilla HTML/JS | Simple, no build step, minimal dependencies |
| YAML | ruamel.yaml | Preserves comments, already used by Kometa |
| Database | SQLite | Simple, file-based, sufficient for run history |
| Process Mgmt | subprocess | Standard library, reliable |

## Extension Points

### Adding New Config Sections

1. Update JSON schema in `/json-schema/`
2. Add form fields in frontend
3. Update validation in backend

### Adding New Integrations

1. Add checkbox in integrations panel
2. Map to config.yml structure
3. Include in run plan preview

### Custom Overlays

1. Upload overlay images via UI
2. Preview overlay positioning
3. Generate overlay YAML

## Tradeoffs

| Decision | Benefit | Cost |
|----------|---------|------|
| Subprocess vs import | Isolation, no code changes | Slower startup, separate process |
| SQLite vs JSON | Query capability | Additional dependency |
| No build step | Simple deployment | Less polished UI |
| Write Guard wrapper | Safety, reversibility | Slight overhead, maintenance |

## Future Considerations

- WebSocket for real-time log streaming
- Multi-user support with authentication
- Scheduled run management via UI
- Visual overlay editor
- Config diff viewer
- Backup rotation policy
