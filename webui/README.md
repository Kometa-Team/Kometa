# Kometa Web UI

A **safe, read-only by default** web interface for [Kometa](https://kometa.wiki) - the Plex metadata automation tool.

## Features

- **Safe by Default**: Runs in dry-run mode - no changes to Plex without explicit confirmation
- **Config Editor**: Import, edit, and validate your `config.yml` with syntax highlighting
- **Run Plan Preview**: See exactly what Kometa will do before running
- **Live Logs**: Real-time log streaming during runs
- **Run History**: Track all past runs with status and logs
- **Docker Ready**: Simple deployment for Unraid and other Docker hosts

## Quick Start

### Using VS Code (Recommended for Development)

1. Open the Kometa repo in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Select "Tasks: Run Task"
4. Choose "Kometa UI: Start Dev Container"
5. Open http://localhost:8080 in your browser

### Using Docker Compose

```bash
cd webui
docker-compose up -d
```

Access the UI at: http://localhost:8080

### Manual Docker Build

```bash
# Build the image
docker build -t kometa-ui ./webui

# Run the container
docker run -d \
  --name kometa-ui \
  -p 8080:8080 \
  -v /path/to/config:/config \
  -e KOMETA_UI_APPLY_ENABLED=false \
  kometa-ui
```

## Safety Architecture

The Web UI implements a **three-layer safety model**:

### Layer 1: Docker Kill Switch

```bash
# Default: Apply mode is disabled
KOMETA_UI_APPLY_ENABLED=false

# To enable apply mode (use with caution!)
KOMETA_UI_APPLY_ENABLED=true
```

When `KOMETA_UI_APPLY_ENABLED=false`, the Apply button is completely disabled in the UI.

### Layer 2: UI Safety Controls

Even when apply mode is enabled:
1. Default mode is always **DRY RUN**
2. Switching to Apply mode requires clicking a toggle
3. Starting an Apply run requires typing `APPLY CHANGES`
4. An **ARMED** banner is prominently displayed

### Layer 3: Write Guard

The `modules/write_guard.py` module intercepts all Plex write operations when dry-run mode is active:
- Logs what would have been changed
- Does not actually modify Plex
- Provides a summary at the end of the run

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KOMETA_CONFIG_DIR` | `/config` | Path to Kometa config directory |
| `KOMETA_UI_PORT` | `8080` | Port for the Web UI |
| `KOMETA_UI_HOST` | `0.0.0.0` | Host to bind the UI |
| `KOMETA_UI_APPLY_ENABLED` | `false` | Enable/disable apply mode |
| `KOMETA_UI_PASSWORD` | (none) | Optional password protection |
| `TZ` | `America/New_York` | Timezone |

### Volumes

| Path | Description |
|------|-------------|
| `/config` | Kometa config directory (config.yml, logs, cache) |

## API Endpoints

### Configuration

- `GET /api/config` - Load current config.yml
- `POST /api/config` - Save config.yml (creates backup)
- `POST /api/config/validate` - Validate YAML syntax
- `GET /api/config/backups` - List available backups
- `POST /api/config/restore/{name}` - Restore from backup

### Runs

- `POST /api/run` - Start a dry-run
- `POST /api/run/apply` - Start an apply run (requires confirmation)
- `GET /api/run/status` - Get current run status
- `POST /api/run/stop` - Stop current run
- `GET /api/run/plan` - Get run plan preview
- `GET /api/runs` - List run history
- `GET /api/logs/{id}` - Get logs for a run

### WebSocket

- `/ws/logs` - Live log streaming
- `/ws/status` - Run status updates

## Development

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- VS Code (recommended)

### Local Development (without Docker)

```bash
# Install dependencies
cd webui
pip install -r backend/requirements.txt

# Run the backend
KOMETA_CONFIG_DIR=../config python -m uvicorn backend.app:app --reload --port 8080
```

### Project Structure

```
webui/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── config_manager.py   # YAML parsing and validation
│   ├── run_manager.py      # Kometa run execution
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── templates/
│   │   └── index.html      # Main UI template
│   └── static/
│       ├── css/style.css   # Styles
│       └── js/app.js       # Frontend logic
├── Dockerfile
├── docker-compose.yml
├── DESIGN_NOTES.md         # Architecture documentation
└── README.md               # This file
```

## Backups

The UI automatically creates a backup every time you save the config:

```
/config/backups/
├── config.yml.20240115-143022
├── config.yml.20240115-152341
└── config.yml.20240116-091500
```

Backups can be restored from the UI or by copying the file manually.

## Run Reports

Each run creates a log file:

```
/config/logs/runs/
├── run_20240115_143022.log
├── run_20240115_152341.log
└── run_20240116_091500.log
```

Run history is stored in `/config/webui.db` (SQLite).

## Troubleshooting

### UI won't start

Check Docker logs:
```bash
docker-compose -f webui/docker-compose.yml logs
```

### Can't connect to Plex

1. Verify your Plex URL and token in config.yml
2. Ensure the container can reach your Plex server
3. Check if Plex is running

### Apply mode is disabled

Set the environment variable:
```bash
KOMETA_UI_APPLY_ENABLED=true docker-compose up -d
```

## License

This Web UI is part of the Kometa project. See the main [LICENSE](../LICENSE) for details.
