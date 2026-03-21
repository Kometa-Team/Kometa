# Kometa Web UI

A lightweight browser-based interface for running Kometa with full control over settings and real-time log output.

## Features

- **Config selector** – pick any `.yml` file from your `config/` directory (or use the default `config/config.yml`)
- **Run controls** – Run Once, Test Mode, Scheduled mode with custom times
- **Scope filters** – limit runs to Collections, Metadata, Overlays, Playlists, or Operations only
- **Library / Collection / File filters** – pipe-separated target filters
- **Logging options** – Debug and Trace modes
- **Danger zone** – Delete collections/labels before run, skip SSL verification
- **Advanced** – custom timeout, console width
- **Command preview** – shows the exact CLI command that will be executed
- **Live log viewer** – streamed via Server-Sent Events with color-coded lines
- **Run history** – last 20 runs with exit code and timestamp
- **Start / Stop** – graceful SIGTERM with 10-second SIGKILL fallback

## Requirements

```
pip install flask
```

Or install from this directory:
```
pip install -r webui/requirements.txt
```

## Running

From the Kometa root directory:

```bash
python webui/app.py
```

Then open **http://localhost:7799** in your browser.

### Options

```
python webui/app.py --host 0.0.0.0 --port 7799 --debug
```

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `0.0.0.0` | Interface to bind to |
| `--port` | `7799` | Port to listen on |
| `--debug` | off | Enable Flask debug mode (auto-reload) |
