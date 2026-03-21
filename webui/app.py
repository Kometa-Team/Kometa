import os
import sys
import glob
import signal
import subprocess
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

# Path to kometa root
KOMETA_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_DIR = KOMETA_ROOT / "config"

app = Flask(__name__)

# Global state
run_state = {
    "pid": None,
    "process": None,
    "running": False,
    "start_time": None,
    "log_lines": [],
    "history": [],
    "last_exit_code": None,
}
log_lock = threading.Lock()
log_subscribers = []
subscribers_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_config_files():
    """Return list of .yml files in the config directory (and subdirs)."""
    patterns = [
        str(CONFIG_DIR / "*.yml"),
        str(CONFIG_DIR / "*.yaml"),
        str(CONFIG_DIR / "**" / "*.yml"),
        str(CONFIG_DIR / "**" / "*.yaml"),
    ]
    found = set()
    for pat in patterns:
        for f in glob.glob(pat, recursive=True):
            # Exclude template files
            if ".template" not in f:
                found.add(str(Path(f).resolve()))
    return sorted(found)


def push_log_line(line: str):
    """Append a log line to the buffer and notify all SSE subscribers."""
    with log_lock:
        run_state["log_lines"].append(line)
        # Keep only last 5000 lines
        if len(run_state["log_lines"]) > 5000:
            run_state["log_lines"] = run_state["log_lines"][-5000:]

    with subscribers_lock:
        dead = []
        for q in log_subscribers:
            try:
                q.append(line)
            except Exception:
                dead.append(q)
        for q in dead:
            log_subscribers.remove(q)


def _stream_output(proc):
    """Read stdout/stderr from subprocess and push to SSE."""
    try:
        for line in iter(proc.stdout.readline, ""):
            if line:
                push_log_line(line.rstrip())
    except Exception as e:
        push_log_line(f"[WebUI] Stream error: {e}")
    finally:
        proc.stdout.close()
        exit_code = proc.wait()
        with log_lock:
            run_state["running"] = False
            run_state["pid"] = None
            run_state["last_exit_code"] = exit_code
            end_time = datetime.now()
            run_state["history"].insert(0, {
                "start": run_state["start_time"].isoformat() if run_state["start_time"] else None,
                "end": end_time.isoformat(),
                "exit_code": exit_code,
                "args": run_state.get("last_args", []),
            })
            # Keep only last 20 history entries
            run_state["history"] = run_state["history"][:20]
            run_state["process"] = None

        push_log_line(f"[WebUI] Kometa exited with code {exit_code}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    with log_lock:
        return jsonify({
            "running": run_state["running"],
            "pid": run_state["pid"],
            "start_time": run_state["start_time"].isoformat() if run_state["start_time"] else None,
            "last_exit_code": run_state["last_exit_code"],
            "history": run_state["history"][:5],
        })


@app.route("/api/configs")
def api_configs():
    files = find_config_files()
    # Return relative paths for display, absolute for value
    result = []
    for f in files:
        try:
            rel = str(Path(f).relative_to(KOMETA_ROOT))
        except ValueError:
            rel = f
        result.append({"label": rel, "value": f})
    return jsonify(result)


@app.route("/api/logs")
def api_logs():
    with log_lock:
        return jsonify(run_state["log_lines"][-500:])


@app.route("/api/run", methods=["POST"])
def api_run():
    if run_state["running"]:
        return jsonify({"error": "Kometa is already running"}), 409

    data = request.get_json(force=True)
    args = build_args(data)

    cmd = [sys.executable, str(KOMETA_ROOT / "kometa.py")] + args

    with log_lock:
        run_state["log_lines"] = []
        run_state["running"] = True
        run_state["start_time"] = datetime.now()
        run_state["last_args"] = args
        run_state["last_exit_code"] = None

    push_log_line(f"[WebUI] Starting Kometa: {' '.join(cmd)}")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(KOMETA_ROOT),
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        run_state["process"] = proc
        run_state["pid"] = proc.pid

        thread = threading.Thread(target=_stream_output, args=(proc,), daemon=True)
        thread.start()

        return jsonify({"ok": True, "pid": proc.pid, "cmd": cmd})
    except Exception as e:
        with log_lock:
            run_state["running"] = False
        return jsonify({"error": str(e)}), 500


@app.route("/api/stop", methods=["POST"])
def api_stop():
    proc = run_state.get("process")
    if not proc or not run_state["running"]:
        return jsonify({"error": "No running process"}), 409

    push_log_line("[WebUI] Stop requested — sending SIGTERM")
    try:
        proc.terminate()
        # Give it 10 seconds then force kill
        def _force_kill():
            time.sleep(10)
            if run_state["running"]:
                push_log_line("[WebUI] Force killing process (SIGKILL)")
                proc.kill()
        threading.Thread(target=_force_kill, daemon=True).start()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/logs/stream")
def api_logs_stream():
    """Server-Sent Events endpoint for real-time log streaming."""
    my_queue = []

    with subscribers_lock:
        log_subscribers.append(my_queue)

    def generate():
        # First, send existing buffered lines
        with log_lock:
            existing = list(run_state["log_lines"])
        for line in existing:
            yield f"data: {json.dumps(line)}\n\n"

        # Then stream new lines as they arrive
        while True:
            if my_queue:
                line = my_queue.pop(0)
                yield f"data: {json.dumps(line)}\n\n"
            else:
                # Heartbeat every 15 seconds
                yield ": heartbeat\n\n"
                time.sleep(0.1)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Argument builder
# ---------------------------------------------------------------------------

def build_args(data: dict) -> list:
    """Convert form data to kometa.py CLI arguments."""
    args = []

    # Config file
    config = data.get("config", "").strip()
    if config:
        args += ["--config", config]

    # Run mode (mutually exclusive-ish)
    if data.get("run"):
        args.append("--run")
    if data.get("test"):
        args.append("--tests")

    # Resume
    resume = data.get("resume", "").strip()
    if resume:
        args += ["--resume", resume]

    # What to run
    if data.get("collections_only"):
        args.append("--collections-only")
    if data.get("metadata_only"):
        args.append("--metadata-only")
    if data.get("overlays_only"):
        args.append("--overlays-only")
    if data.get("playlists_only"):
        args.append("--playlists-only")
    if data.get("operations_only"):
        args.append("--operations-only")

    # Filters
    run_libraries = data.get("run_libraries", "").strip()
    if run_libraries:
        args += ["--run-libraries", run_libraries]

    run_collections = data.get("run_collections", "").strip()
    if run_collections:
        args += ["--run-collections", run_collections]

    run_files = data.get("run_files", "").strip()
    if run_files:
        args += ["--run-files", run_files]

    # Schedule
    times = data.get("times", "").strip()
    if times:
        args += ["--times", times]

    # Debug
    if data.get("debug"):
        args.append("--debug")
    if data.get("trace"):
        args.append("--trace")

    # Misc flags
    if data.get("delete_collections"):
        args.append("--delete-collections")
    if data.get("delete_labels"):
        args.append("--delete-labels")
    if data.get("ignore_schedules"):
        args.append("--ignore-schedules")
    if data.get("no_verify_ssl"):
        args.append("--no-verify-ssl")
    if data.get("no_countdown"):
        args.append("--no-countdown")

    # Timeout
    timeout = data.get("timeout", "").strip()
    if timeout:
        args += ["--timeout", timeout]

    # Width
    width = data.get("width", "").strip()
    if width:
        args += ["--width", width]

    return args


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kometa Web UI")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=7799, help="Bind port (default: 7799)")
    parser.add_argument("--debug", action="store_true", help="Flask debug mode")
    opts = parser.parse_args()

    print(f"Starting Kometa WebUI on http://{opts.host}:{opts.port}")
    app.run(host=opts.host, port=opts.port, debug=opts.debug, threaded=True)
