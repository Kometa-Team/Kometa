# Kometa API Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a FastAPI server to Kometa that exposes control-plane and config-management APIs while preserving the existing scheduler and run logic unchanged.

**Architecture:** A new `server.py` entry point starts FastAPI+Uvicorn alongside a scheduler thread (wrapping the existing `schedule` library) and a job worker thread. Auth is enforced via `X-API-Key` header. Jobs are tracked in a new SQLite database (`kometa_server.db`). Kometa runs are triggered by importing `kometa` and calling `kometa.start(attrs)` in the worker thread, with a custom log handler capturing output into the job record in real time.

**Tech Stack:** Python 3.10+, FastAPI ≥ 0.115.0, Uvicorn ≥ 0.34.0, SQLite (stdlib), ruamel.yaml (existing dep), httpx ≥ 0.28.0 (test client via FastAPI TestClient)

**Spec:** `docs/superpowers/specs/2026-06-28-api-server-design.md`

## Global Constraints

- Python 3.10+ required
- Line length 256 characters (per `pyproject.toml`)
- All new API routes prefixed `/api/`
- `X-API-Key` header required on all routes except `GET /api/health`
- One Kometa run per Plex server name at a time (per-server `threading.Lock`)
- Config write endpoints return `423 Locked` if any run is in progress
- Job database: `kometa_server.db` — separate from `cache.db`
- New deps: `fastapi>=0.115.0`, `uvicorn[standard]>=0.34.0` in `requirements.txt`; `httpx>=0.28.0` in `dev-requirements.txt`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `requirements.txt` | Modify | Add fastapi, uvicorn |
| `dev-requirements.txt` | Modify | Add httpx |
| `api/__init__.py` | Create | Package marker |
| `api/app.py` | Create | FastAPI app factory (`create_app`) |
| `api/auth.py` | Create | `require_api_key` FastAPI dependency |
| `api/jobs.py` | Create | `JobStore` (SQLite), `JobWorker` (thread), `_JobLogHandler`, `JOB_STATUS` |
| `api/scheduler.py` | Create | `KometaScheduler` background thread |
| `api/config_io.py` | Create | YAML read/write utilities, secret masking |
| `api/routers/__init__.py` | Create | Package marker |
| `api/routers/health.py` | Create | `GET /api/health`, `GET /api/status` |
| `api/routers/runs.py` | Create | `POST/GET/DELETE /api/runs` |
| `api/routers/config_router.py` | Create | `GET/PUT /api/config`, `GET/PUT /api/schedule` |
| `api/routers/libraries.py` | Create | `GET /api/libraries`, collection CRUD |
| `frontend/dist/index.html` | Create | Placeholder SPA shell |
| `server.py` | Create | Entry point: starts all three threads + uvicorn |
| `tests/test_api_smoke.py` | Create | Import smoke test + health check |
| `tests/test_api_auth.py` | Create | Auth acceptance/rejection tests |
| `tests/test_jobs.py` | Create | `JobStore` unit tests |
| `tests/test_job_worker.py` | Create | `JobWorker` thread tests |
| `tests/test_api_scheduler.py` | Create | `KometaScheduler` tests |
| `tests/test_api_runs.py` | Create | Runs router tests |
| `tests/test_api_config.py` | Create | Config router tests |
| `tests/test_api_collections.py` | Create | Libraries/collections router tests |
| `tests/test_server_entrypoint.py` | Create | Frontend serving + integration smoke |

---

### Task 1: Add dependencies and scaffold the API package

**Files:**
- Modify: `requirements.txt`
- Modify: `dev-requirements.txt`
- Create: `api/__init__.py`
- Create: `api/routers/__init__.py`
- Create: `frontend/dist/index.html`
- Create: `tests/test_api_smoke.py`

**Interfaces:**
- Produces: `api` package importable from tests

- [ ] **Step 1: Add production dependencies to `requirements.txt`**

Append to `requirements.txt`:
```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
```

- [ ] **Step 2: Add test dependency to `dev-requirements.txt`**

Append to `dev-requirements.txt`:
```
httpx>=0.28.0
```

- [ ] **Step 3: Install new dependencies**

```bash
pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.34.0" "httpx>=0.28.0"
```

Expected: successful install with no conflicts

- [ ] **Step 4: Create `api/__init__.py`** (empty file)

- [ ] **Step 5: Create `api/routers/__init__.py`** (empty file)

- [ ] **Step 6: Create `frontend/dist/index.html`**

```html
<!DOCTYPE html>
<html>
<head><title>Kometa</title></head>
<body><h1>Kometa API Server</h1><p>Frontend not yet installed.</p></body>
</html>
```

- [ ] **Step 7: Write smoke test**

Create `tests/test_api_smoke.py`:
```python
def test_api_package_imports():
    import api  # noqa: F401
```

- [ ] **Step 8: Run test**

```bash
pytest tests/test_api_smoke.py -v
```

Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add requirements.txt dev-requirements.txt api/__init__.py api/routers/__init__.py frontend/dist/index.html tests/test_api_smoke.py
git commit -m "feat(api): scaffold API package and add FastAPI/uvicorn dependencies"
```

---

### Task 2: FastAPI app factory and health endpoint

**Files:**
- Create: `api/routers/health.py`
- Create: `api/app.py`
- Modify: `tests/test_api_smoke.py`

**Interfaces:**
- Produces: `create_app() -> FastAPI` in `api/app.py`
- Produces: `GET /api/health` → `{"status": "ok"}`

- [ ] **Step 1: Write failing test**

Append to `tests/test_api_smoke.py`:
```python
from fastapi.testclient import TestClient
from api.app import create_app

def test_health_returns_ok():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest tests/test_api_smoke.py::test_health_returns_ok -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'api.app'`

- [ ] **Step 3: Create `api/routers/health.py`**

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}

@router.get("/status")
def status() -> dict:
    return {"running": False, "server": None, "next_run": None, "active_job_id": None}
```

- [ ] **Step 4: Create `api/app.py`**

```python
from fastapi import FastAPI
from api.routers import health as health_router

def create_app() -> FastAPI:
    app = FastAPI(title="Kometa API", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc")
    app.include_router(health_router.router)
    return app
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_api_smoke.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add api/app.py api/routers/health.py tests/test_api_smoke.py
git commit -m "feat(api): add FastAPI app factory and health endpoint"
```

---

### Task 3: API key authentication

**Files:**
- Create: `api/auth.py`
- Create: `tests/test_api_auth.py`
- Modify: `api/routers/health.py` (protect `/api/status`)

**Interfaces:**
- Produces: `require_api_key` dependency in `api/auth.py` — raises `HTTPException(401)` on bad/missing key
- Consumes: `KOMETA_API_KEY` environment variable

- [ ] **Step 1: Write failing tests**

Create `tests/test_api_auth.py`:
```python
import pytest
from fastapi.testclient import TestClient
from api.app import create_app

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("KOMETA_API_KEY", "test-secret-key")
    return TestClient(create_app())

def test_health_needs_no_auth(client):
    assert client.get("/api/health").status_code == 200

def test_valid_key_accepted(client):
    assert client.get("/api/status", headers={"X-API-Key": "test-secret-key"}).status_code == 200

def test_invalid_key_rejected(client):
    assert client.get("/api/status", headers={"X-API-Key": "wrong"}).status_code == 401

def test_missing_key_rejected(client):
    assert client.get("/api/status").status_code == 401

def test_unconfigured_server_key_returns_error(monkeypatch):
    monkeypatch.delenv("KOMETA_API_KEY", raising=False)
    client = TestClient(create_app())
    assert client.get("/api/status").status_code in (401, 500)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_api_auth.py -v
```

Expected: multiple FAILs (`test_invalid_key_rejected` passes vacuously since no auth exists yet)

- [ ] **Step 3: Create `api/auth.py`**

```python
import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(key: str | None = Security(_key_header)) -> str:
    expected = os.environ.get("KOMETA_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="KOMETA_API_KEY is not configured")
    if not key or key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return key
```

- [ ] **Step 4: Protect `/api/status` in `api/routers/health.py`**

```python
from fastapi import APIRouter, Depends
from api.auth import require_api_key

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}

@router.get("/status", dependencies=[Depends(require_api_key)])
def status() -> dict:
    return {"running": False, "server": None, "next_run": None, "active_job_id": None}
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_api_auth.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add api/auth.py api/routers/health.py tests/test_api_auth.py
git commit -m "feat(api): add X-API-Key authentication dependency"
```

---

### Task 4: SQLite job store

**Files:**
- Create: `api/jobs.py`
- Create: `tests/test_jobs.py`

**Interfaces:**
- Produces: `JOB_STATUS` class with class-level string constants: `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`
- Produces: `JobStore(db_path: str)` with methods:
  - `create(server_name: str, triggered_by: str, attrs: dict) -> str`
  - `get(job_id: str) -> dict | None`
  - `list(limit: int = 50) -> list[dict]`
  - `update_status(job_id: str, status: str, *, started: bool = False, finished: bool = False) -> None`
  - `append_log(job_id: str, lines: list[str]) -> None`
  - `get_log_from_offset(job_id: str, offset: int = 0) -> list[str]`
  - `cancel(job_id: str) -> bool`
  - `prune(days: int = 30) -> None`

- [ ] **Step 1: Write failing tests**

Create `tests/test_jobs.py`:
```python
import datetime
import sqlite3
import pytest
from api.jobs import JobStore, JOB_STATUS

@pytest.fixture
def store(tmp_path):
    return JobStore(str(tmp_path / "test.db"))

def test_create_and_get(store):
    job_id = store.create("Main", "api", {"libraries": ["Movies"]})
    job = store.get(job_id)
    assert job is not None
    assert job["status"] == JOB_STATUS.QUEUED
    assert job["server_name"] == "Main"
    assert job["triggered_by"] == "api"
    assert job["log"] == ""
    assert job["started_at"] is None
    assert job["finished_at"] is None

def test_list_returns_most_recent_first(store):
    id1 = store.create("Main", "scheduler", {})
    id2 = store.create("Main", "api", {})
    jobs = store.list(limit=10)
    assert jobs[0]["id"] == id2
    assert jobs[1]["id"] == id1

def test_update_status(store):
    job_id = store.create("Main", "api", {})
    store.update_status(job_id, JOB_STATUS.RUNNING)
    assert store.get(job_id)["status"] == JOB_STATUS.RUNNING

def test_update_status_records_started_at(store):
    job_id = store.create("Main", "api", {})
    store.update_status(job_id, JOB_STATUS.RUNNING, started=True)
    assert store.get(job_id)["started_at"] is not None

def test_update_status_records_finished_at(store):
    job_id = store.create("Main", "api", {})
    store.update_status(job_id, JOB_STATUS.COMPLETED, finished=True)
    assert store.get(job_id)["finished_at"] is not None

def test_append_log(store):
    job_id = store.create("Main", "api", {})
    store.append_log(job_id, ["line one", "line two"])
    job = store.get(job_id)
    assert job["log"] == "line one\nline two\n"
    assert job["log_lines"] == 2

def test_append_log_incremental(store):
    job_id = store.create("Main", "api", {})
    store.append_log(job_id, ["a"])
    store.append_log(job_id, ["b", "c"])
    assert store.get(job_id)["log_lines"] == 3

def test_get_log_from_offset(store):
    job_id = store.create("Main", "api", {})
    store.append_log(job_id, ["line 1", "line 2", "line 3"])
    assert store.get_log_from_offset(job_id, offset=1) == ["line 2", "line 3"]

def test_get_log_from_offset_zero_returns_all(store):
    job_id = store.create("Main", "api", {})
    store.append_log(job_id, ["a", "b"])
    assert store.get_log_from_offset(job_id, offset=0) == ["a", "b"]

def test_cancel_queued_job(store):
    job_id = store.create("Main", "api", {})
    assert store.cancel(job_id) is True
    assert store.get(job_id)["status"] == JOB_STATUS.CANCELLED

def test_cancel_running_job_returns_false(store):
    job_id = store.create("Main", "api", {})
    store.update_status(job_id, JOB_STATUS.RUNNING)
    assert store.cancel(job_id) is False

def test_prune_removes_old_jobs(store):
    job_id = store.create("Main", "api", {})
    store.update_status(job_id, JOB_STATUS.COMPLETED)
    old_time = (datetime.datetime.utcnow() - datetime.timedelta(days=40)).isoformat()
    with sqlite3.connect(store.db_path) as conn:
        conn.execute("UPDATE jobs SET created_at = ? WHERE id = ?", (old_time, job_id))
    store.prune(days=30)
    assert store.get(job_id) is None

def test_prune_keeps_recent_jobs(store):
    job_id = store.create("Main", "api", {})
    store.prune(days=30)
    assert store.get(job_id) is not None
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_jobs.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'api.jobs'`

- [ ] **Step 3: Create `api/jobs.py`**

```python
import datetime
import json
import sqlite3
import uuid
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    server_name TEXT NOT NULL DEFAULT 'default',
    triggered_by TEXT NOT NULL,
    attrs TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'queued',
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    log TEXT NOT NULL DEFAULT '',
    log_lines INTEGER NOT NULL DEFAULT 0
);
"""


class JOB_STATUS:
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["attrs"] = json.loads(d["attrs"])
    return d


class JobStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, server_name: str, triggered_by: str, attrs: dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        now = datetime.datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO jobs (id, server_name, triggered_by, attrs, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (job_id, server_name, triggered_by, json.dumps(attrs), JOB_STATUS.QUEUED, now),
            )
        return job_id

    def get(self, job_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def list(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [_row_to_dict(r) for r in rows]

    def update_status(self, job_id: str, status: str, *, started: bool = False, finished: bool = False) -> None:
        now = datetime.datetime.utcnow().isoformat()
        with self._connect() as conn:
            if started:
                conn.execute("UPDATE jobs SET status = ?, started_at = ? WHERE id = ?", (status, now, job_id))
            elif finished:
                conn.execute("UPDATE jobs SET status = ?, finished_at = ? WHERE id = ?", (status, now, job_id))
            else:
                conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))

    def append_log(self, job_id: str, lines: list[str]) -> None:
        text = "".join(line + "\n" for line in lines)
        with self._connect() as conn:
            conn.execute(
                "UPDATE jobs SET log = log || ?, log_lines = log_lines + ? WHERE id = ?",
                (text, len(lines), job_id),
            )

    def get_log_from_offset(self, job_id: str, offset: int = 0) -> list[str]:
        job = self.get(job_id)
        if not job:
            return []
        return job["log"].splitlines()[offset:]

    def cancel(self, job_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE jobs SET status = ? WHERE id = ? AND status = ?",
                (JOB_STATUS.CANCELLED, job_id, JOB_STATUS.QUEUED),
            )
        return cur.rowcount > 0

    def prune(self, days: int = 30) -> None:
        cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()
        with self._connect() as conn:
            conn.execute("DELETE FROM jobs WHERE created_at < ?", (cutoff,))
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_jobs.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add api/jobs.py tests/test_jobs.py
git commit -m "feat(api): add SQLite-backed job store"
```

---

### Task 5: Job worker thread and log capture

**Files:**
- Modify: `api/jobs.py` (append `_JobLogHandler` and `JobWorker`)
- Create: `tests/test_job_worker.py`

**Interfaces:**
- Consumes: `JobStore` from Task 4
- Produces: `JobWorker(store: JobStore, run_fn: Callable, logger_instance: Any)` with:
  - `.start() -> None`
  - `.stop() -> None`
  - `.submit(server_name: str, triggered_by: str, attrs: dict) -> str` — raises `ValueError` if server already running
  - `.is_running(server_name: str) -> bool`

The `logger_instance` is a `MyLogger` object (from `modules/logs.py`). The worker accesses its underlying Python logger via `logger_instance._logger` and adds a `_JobLogHandler` that writes captured log lines into the job store in real time. Remove the handler after the run completes.

- [ ] **Step 1: Write failing tests**

Create `tests/test_job_worker.py`:
```python
import time
import threading
import pytest
from unittest.mock import MagicMock
from api.jobs import JobStore, JobWorker, JOB_STATUS

@pytest.fixture
def store(tmp_path):
    return JobStore(str(tmp_path / "test.db"))

@pytest.fixture
def worker(store):
    mock_logger = MagicMock()
    mock_logger._logger = MagicMock()
    run_fn = MagicMock()
    w = JobWorker(store=store, run_fn=run_fn, logger_instance=mock_logger)
    w.start()
    yield w, run_fn
    w.stop()

def test_submit_creates_queued_job(worker, store):
    w, _ = worker
    job_id = w.submit("Main", "api", {})
    assert store.get(job_id) is not None

def test_job_runs_to_completion(worker, store):
    w, run_fn = worker
    job_id = w.submit("Main", "api", {})
    for _ in range(30):
        if store.get(job_id)["status"] == JOB_STATUS.COMPLETED:
            break
        time.sleep(0.1)
    assert store.get(job_id)["status"] == JOB_STATUS.COMPLETED
    run_fn.assert_called_once()

def test_failed_run_marks_job_failed(tmp_path):
    store = JobStore(str(tmp_path / "f.db"))
    mock_logger = MagicMock()
    mock_logger._logger = MagicMock()
    def boom(attrs):
        raise RuntimeError("intentional failure")
    w = JobWorker(store=store, run_fn=boom, logger_instance=mock_logger)
    w.start()
    job_id = w.submit("Main", "api", {})
    for _ in range(30):
        if store.get(job_id)["status"] in (JOB_STATUS.FAILED, JOB_STATUS.COMPLETED):
            break
        time.sleep(0.1)
    w.stop()
    assert store.get(job_id)["status"] == JOB_STATUS.FAILED

def test_concurrent_same_server_rejected(worker):
    w, _ = worker
    gate = threading.Event()
    original_run = w._run_fn
    def slow(attrs):
        gate.wait(timeout=2)
    w._run_fn = slow
    w.submit("Main", "api", {})
    time.sleep(0.05)
    with pytest.raises(ValueError, match="already running"):
        w.submit("Main", "api", {})
    gate.set()

def test_different_servers_can_both_be_submitted(worker):
    w, _ = worker
    id1 = w.submit("ServerA", "api", {})
    id2 = w.submit("ServerB", "api", {})
    assert id1 != id2
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_job_worker.py -v
```

Expected: FAIL with `ImportError` (`JobWorker` not defined yet)

- [ ] **Step 3: Append `_JobLogHandler` and `JobWorker` to `api/jobs.py`**

```python
import logging
import queue
import threading
from typing import Callable


class _JobLogHandler(logging.Handler):
    def __init__(self, job_id: str, store: "JobStore") -> None:
        super().__init__()
        self._job_id = job_id
        self._store = store

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._store.append_log(self._job_id, [self.format(record)])
        except Exception:
            self.handleError(record)


class JobWorker:
    def __init__(self, store: JobStore, run_fn: Callable, logger_instance: Any) -> None:
        self._store = store
        self._run_fn = run_fn
        self._logger = logger_instance
        self._queue: queue.Queue[dict] = queue.Queue()
        self._server_locks: dict[str, threading.Lock] = {}
        self._locks_mutex = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def _get_lock(self, server_name: str) -> threading.Lock:
        with self._locks_mutex:
            if server_name not in self._server_locks:
                self._server_locks[server_name] = threading.Lock()
            return self._server_locks[server_name]

    def is_running(self, server_name: str) -> bool:
        lock = self._get_lock(server_name)
        acquired = lock.acquire(blocking=False)
        if acquired:
            lock.release()
        return not acquired

    def submit(self, server_name: str, triggered_by: str, attrs: dict) -> str:
        if self.is_running(server_name):
            raise ValueError(f"A run for server '{server_name}' is already running")
        job_id = self._store.create(server_name, triggered_by, attrs)
        self._queue.put({"job_id": job_id, "server_name": server_name, "attrs": attrs})
        return job_id

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                item = self._queue.get(timeout=1)
            except queue.Empty:
                continue
            self._execute(item)

    def _execute(self, item: dict) -> None:
        job_id = item["job_id"]
        server_name = item["server_name"]
        attrs = item["attrs"]
        lock = self._get_lock(server_name)
        lock.acquire()
        handler = _JobLogHandler(job_id, self._store)
        self._logger._logger.addHandler(handler)
        self._store.update_status(job_id, JOB_STATUS.RUNNING, started=True)
        try:
            self._run_fn(attrs)
            self._store.update_status(job_id, JOB_STATUS.COMPLETED, finished=True)
        except Exception as exc:
            self._store.append_log(job_id, [f"ERROR: {exc}"])
            self._store.update_status(job_id, JOB_STATUS.FAILED, finished=True)
        finally:
            self._logger._logger.removeHandler(handler)
            lock.release()
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_job_worker.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add api/jobs.py tests/test_job_worker.py
git commit -m "feat(api): add job worker thread with per-server locking and log capture"
```

---

### Task 6: Runs API router

**Files:**
- Create: `api/routers/runs.py`
- Create: `tests/test_api_runs.py`
- Modify: `api/app.py` (accept `store` and `worker`, register runs router)

**Interfaces:**
- Consumes: `JobWorker.submit(server_name, triggered_by, attrs) -> str` (Task 5), `JobStore` (Task 4), `require_api_key` (Task 3)
- Produces:
  - `POST /api/runs` body `{server?, libraries?, collections?}` → `202 {"job_id": str}`
  - `GET /api/runs?limit=N` → `200 list[dict]`
  - `GET /api/runs/{job_id}?offset=N` → `200 dict` with `"log": list[str]`
  - `DELETE /api/runs/{job_id}` → `200 {"cancelled": bool}`
  - `POST /api/runs` when server busy → `409`

- [ ] **Step 1: Write failing tests**

Create `tests/test_api_runs.py`:
```python
import time
import threading
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.app import create_app
from api.jobs import JobStore, JobWorker, JOB_STATUS

HEADERS = {"X-API-Key": "test-key"}

@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("KOMETA_API_KEY", "test-key")
    store = JobStore(str(tmp_path / "test.db"))
    mock_logger = MagicMock()
    mock_logger._logger = MagicMock()
    worker = JobWorker(store=store, run_fn=MagicMock(), logger_instance=mock_logger)
    worker.start()
    app = create_app(store=store, worker=worker)
    yield TestClient(app), store, worker
    worker.stop()

def test_trigger_run(setup):
    c, store, _ = setup
    resp = c.post("/api/runs", json={"server": "Main"}, headers=HEADERS)
    assert resp.status_code == 202
    assert "job_id" in resp.json()

def test_trigger_run_without_auth(setup):
    c, _, _ = setup
    assert c.post("/api/runs", json={}).status_code == 401

def test_trigger_run_empty_body(setup):
    c, _, _ = setup
    resp = c.post("/api/runs", json={}, headers=HEADERS)
    assert resp.status_code == 202

def test_list_runs(setup):
    c, _, _ = setup
    c.post("/api/runs", json={}, headers=HEADERS)
    resp = c.get("/api/runs", headers=HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

def test_get_run_status(setup):
    c, _, _ = setup
    job_id = c.post("/api/runs", json={}, headers=HEADERS).json()["job_id"]
    resp = c.get(f"/api/runs/{job_id}", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == job_id
    assert "status" in data
    assert "log" in data

def test_get_run_with_log_offset(setup):
    c, store, _ = setup
    job_id = c.post("/api/runs", json={}, headers=HEADERS).json()["job_id"]
    time.sleep(0.2)
    store.append_log(job_id, ["a", "b", "c"])
    resp = c.get(f"/api/runs/{job_id}?offset=1", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["log"] == ["b", "c"]

def test_get_nonexistent_run(setup):
    c, _, _ = setup
    assert c.get("/api/runs/does-not-exist", headers=HEADERS).status_code == 404

def test_cancel_queued_run(setup):
    c, store, _ = setup
    job_id = store.create("Main", "api", {})
    resp = c.delete(f"/api/runs/{job_id}", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["cancelled"] is True

def test_concurrent_same_server_rejected(setup):
    c, store, worker = setup
    gate = threading.Event()
    def slow(attrs):
        gate.wait(timeout=2)
    worker._run_fn = slow
    c.post("/api/runs", json={"server": "Main"}, headers=HEADERS)
    time.sleep(0.05)
    resp = c.post("/api/runs", json={"server": "Main"}, headers=HEADERS)
    assert resp.status_code == 409
    gate.set()
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_api_runs.py -v
```

Expected: FAIL (`create_app` doesn't accept `store`/`worker` yet)

- [ ] **Step 3: Create `api/routers/runs.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.auth import require_api_key
from api.jobs import JobStore, JobWorker

class RunRequest(BaseModel):
    server: str = "default"
    libraries: list[str] = []
    collections: list[str] = []

def make_router(store: JobStore, worker: JobWorker) -> APIRouter:
    router = APIRouter(prefix="/api/runs", tags=["runs"])

    @router.post("", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(require_api_key)])
    def trigger_run(req: RunRequest) -> dict:
        attrs = {
            "server": req.server,
            "run-libraries": "|".join(req.libraries) if req.libraries else None,
            "run-collections": "|".join(req.collections) if req.collections else None,
        }
        try:
            job_id = worker.submit(req.server, "api", attrs)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        return {"job_id": job_id}

    @router.get("", dependencies=[Depends(require_api_key)])
    def list_runs(limit: int = 50) -> list[dict]:
        return store.list(limit=limit)

    @router.get("/{job_id}", dependencies=[Depends(require_api_key)])
    def get_run(job_id: str, offset: int = 0) -> dict:
        job = store.get(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        log_lines = store.get_log_from_offset(job_id, offset=offset)
        return {**job, "log": log_lines}

    @router.delete("/{job_id}", dependencies=[Depends(require_api_key)])
    def cancel_run(job_id: str) -> dict:
        if store.get(job_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return {"cancelled": store.cancel(job_id)}

    return router
```

- [ ] **Step 4: Update `api/app.py`**

```python
from fastapi import FastAPI
from api.jobs import JobStore, JobWorker
from api.routers import health as health_router
from api.routers import runs as runs_router

def create_app(store: JobStore | None = None, worker: JobWorker | None = None) -> FastAPI:
    app = FastAPI(title="Kometa API", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc")
    app.include_router(health_router.router)
    if store is not None and worker is not None:
        app.include_router(runs_router.make_router(store, worker))
    return app
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_api_runs.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add api/routers/runs.py api/app.py tests/test_api_runs.py
git commit -m "feat(api): add runs router (trigger, list, get, cancel)"
```

---

### Task 7: Scheduler thread

**Files:**
- Create: `api/scheduler.py`
- Create: `tests/test_api_scheduler.py`

**Interfaces:**
- Consumes: `JobWorker.submit(server_name, triggered_by, attrs)` (Task 5)
- Produces: `KometaScheduler(worker: JobWorker, run_times: list[str])` with:
  - `.start() -> None`
  - `.stop() -> None`
  - `.next_run() -> str | None` — ISO8601 timestamp of next scheduled run, or None
  - `.set_times(times: list[str]) -> None` — replaces the current schedule

- [ ] **Step 1: Write failing tests**

Create `tests/test_api_scheduler.py`:
```python
import time
import pytest
from unittest.mock import MagicMock
from api.scheduler import KometaScheduler

@pytest.fixture
def worker():
    mock_logger = MagicMock()
    mock_logger._logger = MagicMock()
    w = MagicMock()
    w.submit = MagicMock()
    return w

def test_scheduler_reports_next_run(worker):
    sched = KometaScheduler(worker=worker, run_times=["23:59"])
    sched.start()
    assert sched.next_run() is not None
    sched.stop()

def test_scheduler_no_times_returns_none_next_run(worker):
    sched = KometaScheduler(worker=worker, run_times=[])
    sched.start()
    assert sched.next_run() is None
    sched.stop()

def test_set_times_updates_schedule(worker):
    sched = KometaScheduler(worker=worker, run_times=["23:59"])
    sched.start()
    sched.set_times(["00:01", "12:00"])
    assert sched.next_run() is not None
    sched.stop()

def test_set_times_empty_clears_schedule(worker):
    sched = KometaScheduler(worker=worker, run_times=["23:59"])
    sched.start()
    sched.set_times([])
    assert sched.next_run() is None
    sched.stop()
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_api_scheduler.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'api.scheduler'`

- [ ] **Step 3: Create `api/scheduler.py`**

```python
import threading
import schedule as schedule_lib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.jobs import JobWorker


class KometaScheduler:
    def __init__(self, worker: "JobWorker", run_times: list[str]) -> None:
        self._worker = worker
        self._scheduler = schedule_lib.Scheduler()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._set_schedule(run_times)

    def _set_schedule(self, run_times: list[str]) -> None:
        self._scheduler.clear()
        for t in run_times:
            self._scheduler.every().day.at(t).do(self._trigger)

    def _trigger(self) -> None:
        try:
            self._worker.submit("default", "scheduler", {})
        except ValueError:
            pass  # run already in progress for this server

    def next_run(self) -> str | None:
        next_job = self._scheduler.next_run
        return next_job.isoformat() if next_job else None

    def set_times(self, run_times: list[str]) -> None:
        self._set_schedule(run_times)

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            self._scheduler.run_pending()
            self._stop_event.wait(timeout=30)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_api_scheduler.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add api/scheduler.py tests/test_api_scheduler.py
git commit -m "feat(api): add KometaScheduler background thread"
```

---

### Task 8: Config YAML reader/writer

**Files:**
- Create: `api/config_io.py`
- Create: `tests/test_config_io.py`

**Interfaces:**
- Produces:
  - `SECRET_KEYS: set[str]` — set of substrings that mark a key as a secret
  - `read_config(path: str) -> dict` — loads config.yml, masks secrets
  - `write_config(path: str, patch: dict) -> None` — deep-merges patch into YAML and writes back
  - `read_collections(meta_file_path: str) -> dict` — returns the `collections:` section as a plain dict
  - `write_collections(meta_file_path: str, collections: dict) -> None` — replaces `collections:` section, preserves other YAML sections

All YAML I/O uses `ruamel.yaml` with `preserve_quotes=True` so hand-edited configs survive round-trips. Secrets: any config key whose name (lowercased, underscores normalised) contains one of `{"token", "password", "api_key", "apikey", "client_id", "client_secret", "access_token"}` is replaced with `"***"` on read. Secrets are written through unchanged on `write_config` — the `"***"` value is never written back.

- [ ] **Step 1: Write failing tests**

Create `tests/test_config_io.py`:
```python
import pytest
from ruamel.yaml import YAML
from api.config_io import read_config, write_config, read_collections, write_collections

SAMPLE_CONFIG = """
plex:
  url: http://localhost:32400
  token: my-secret-token
tmdb:
  apikey: abc123
libraries:
  Movies:
    metadata_path:
      - file: config/movies.yml
"""

SAMPLE_META = """
collections:
  Best of 2024:
    tmdb_popular: 20
    sort_title: "!!Best of 2024"
  Action Movies:
    plex_search:
      genre: Action
"""

@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "config.yml"
    p.write_text(SAMPLE_CONFIG)
    return str(p)

@pytest.fixture
def meta_file(tmp_path):
    p = tmp_path / "movies.yml"
    p.write_text(SAMPLE_META)
    return str(p)

def test_read_config_returns_dict(config_file):
    data = read_config(config_file)
    assert data["plex"]["url"] == "http://localhost:32400"

def test_read_config_masks_token(config_file):
    assert read_config(config_file)["plex"]["token"] == "***"

def test_read_config_masks_apikey(config_file):
    assert read_config(config_file)["tmdb"]["apikey"] == "***"

def test_write_config_merges_patch(config_file):
    write_config(config_file, {"plex": {"url": "http://newhost:32400"}})
    assert read_config(config_file)["plex"]["url"] == "http://newhost:32400"

def test_write_config_preserves_untouched_keys(config_file):
    write_config(config_file, {"plex": {"url": "http://newhost:32400"}})
    yaml = YAML()
    with open(config_file) as f:
        raw = yaml.load(f)
    assert raw["plex"]["token"] == "my-secret-token"
    assert raw["tmdb"]["apikey"] == "abc123"

def test_write_config_accepts_new_secret_value(config_file):
    write_config(config_file, {"plex": {"token": "new-token"}})
    yaml = YAML()
    with open(config_file) as f:
        raw = yaml.load(f)
    assert raw["plex"]["token"] == "new-token"

def test_write_config_ignores_masked_sentinel(config_file):
    write_config(config_file, {"plex": {"token": "***"}})
    yaml = YAML()
    with open(config_file) as f:
        raw = yaml.load(f)
    assert raw["plex"]["token"] == "my-secret-token"

def test_read_collections(meta_file):
    colls = read_collections(meta_file)
    assert "Best of 2024" in colls
    assert "Action Movies" in colls

def test_write_collections_creates_new_entry(meta_file):
    colls = read_collections(meta_file)
    colls["New Collection"] = {"tmdb_popular": 10}
    write_collections(meta_file, colls)
    assert "New Collection" in read_collections(meta_file)

def test_write_collections_deletes_entry(meta_file):
    colls = read_collections(meta_file)
    del colls["Action Movies"]
    write_collections(meta_file, colls)
    assert "Action Movies" not in read_collections(meta_file)

def test_write_collections_preserves_other_yaml_sections(meta_file):
    colls = read_collections(meta_file)
    write_collections(meta_file, colls)
    yaml = YAML()
    with open(meta_file) as f:
        raw = yaml.load(f)
    assert "collections" in raw
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_config_io.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'api.config_io'`

- [ ] **Step 3: Create `api/config_io.py`**

```python
from __future__ import annotations
import copy
from ruamel.yaml import YAML

SECRET_KEYS: set[str] = {"token", "password", "api_key", "apikey", "client_id", "client_secret", "access_token"}

def _is_secret(key: str) -> bool:
    key_norm = key.lower().replace("-", "_")
    return any(s in key_norm for s in SECRET_KEYS)

def _mask_secrets(data: dict) -> dict:
    result: dict = {}
    for k, v in data.items():
        if isinstance(v, dict):
            result[k] = _mask_secrets(v)
        elif _is_secret(str(k)) and isinstance(v, str):
            result[k] = "***"
        else:
            result[k] = v
    return result

def _deep_merge(base: dict, patch: dict, *, skip_masked: bool = False) -> dict:
    result = copy.deepcopy(base)
    for k, v in patch.items():
        if skip_masked and isinstance(v, str) and v == "***":
            continue
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v, skip_masked=skip_masked)
        else:
            result[k] = v
    return result

def _load_yaml(path: str) -> dict:
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(path, encoding="utf-8") as f:
        return yaml.load(f) or {}

def _save_yaml(path: str, data: dict) -> None:
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

def read_config(path: str) -> dict:
    return _mask_secrets(dict(_load_yaml(path)))

def write_config(path: str, patch: dict) -> None:
    raw = _load_yaml(path)
    merged = _deep_merge(dict(raw), patch, skip_masked=True)
    _save_yaml(path, merged)

def read_collections(meta_file_path: str) -> dict:
    raw = _load_yaml(meta_file_path)
    return dict(raw.get("collections") or {})

def write_collections(meta_file_path: str, collections: dict) -> None:
    raw = _load_yaml(meta_file_path)
    raw["collections"] = collections
    _save_yaml(meta_file_path, raw)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_config_io.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add api/config_io.py tests/test_config_io.py
git commit -m "feat(api): add YAML config reader/writer with secret masking"
```

---

### Task 9: Config and schedule API router

**Files:**
- Create: `api/routers/config_router.py`
- Create: `tests/test_api_config.py`
- Modify: `api/app.py` (add `config_path` and `scheduler` params, register router)

**Interfaces:**
- Consumes: `read_config`, `write_config` from Task 8; `KometaScheduler.next_run()`, `.set_times()` from Task 7; `JobStore.list()`, `JOB_STATUS` from Task 4
- Produces:
  - `GET /api/config` → masked config dict
  - `PUT /api/config` body is a partial config dict (same shape as config.yml) → `{"ok": true}` or `423`
  - `GET /api/schedule` → `{"times": list[str], "next_run": str | None}`
  - `PUT /api/schedule` body `{"times": ["HH:MM", ...]}` → `{"ok": true}`

- [ ] **Step 1: Write failing tests**

Create `tests/test_api_config.py`:
```python
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.app import create_app
from api.jobs import JobStore, JobWorker, JOB_STATUS

SAMPLE_CONFIG = "plex:\n  url: http://localhost:32400\n  token: secret-token\n"
HEADERS = {"X-API-Key": "test-key"}

@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("KOMETA_API_KEY", "test-key")
    cfg_path = tmp_path / "config.yml"
    cfg_path.write_text(SAMPLE_CONFIG)
    store = JobStore(str(tmp_path / "test.db"))
    mock_logger = MagicMock()
    mock_logger._logger = MagicMock()
    worker = JobWorker(store=store, run_fn=MagicMock(), logger_instance=mock_logger)
    worker.start()
    scheduler = MagicMock()
    scheduler.next_run.return_value = "2026-07-01T05:00:00"
    app = create_app(store=store, worker=worker, config_path=str(cfg_path), scheduler=scheduler)
    yield TestClient(app), store, worker, scheduler, cfg_path
    worker.stop()

def test_get_config_masks_secrets(setup):
    c, *_ = setup
    resp = c.get("/api/config", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["plex"]["token"] == "***"
    assert resp.json()["plex"]["url"] == "http://localhost:32400"

def test_put_config_updates_field(setup):
    c, _, _, _, cfg_path = setup
    resp = c.put("/api/config", json={"plex": {"url": "http://newhost:32400"}}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert c.get("/api/config", headers=HEADERS).json()["plex"]["url"] == "http://newhost:32400"

def test_put_config_locked_during_run(setup):
    c, store, *_ = setup
    job_id = store.create("default", "api", {})
    store.update_status(job_id, JOB_STATUS.RUNNING, started=True)
    assert c.put("/api/config", json={"plex": {"url": "x"}}, headers=HEADERS).status_code == 423

def test_get_schedule(setup):
    c, *_ = setup
    resp = c.get("/api/schedule", headers=HEADERS)
    assert resp.status_code == 200
    assert "times" in resp.json()
    assert resp.json()["next_run"] == "2026-07-01T05:00:00"

def test_put_schedule(setup):
    c, _, _, scheduler, _ = setup
    resp = c.put("/api/schedule", json={"times": ["06:00", "18:00"]}, headers=HEADERS)
    assert resp.status_code == 200
    scheduler.set_times.assert_called_once_with(["06:00", "18:00"])

def test_config_requires_auth(setup):
    c, *_ = setup
    assert c.get("/api/config").status_code == 401
    assert c.put("/api/config", json={}).status_code == 401
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_api_config.py -v
```

Expected: FAIL (`create_app` doesn't accept `config_path`/`scheduler` yet)

- [ ] **Step 3: Create `api/routers/config_router.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.auth import require_api_key
from api.config_io import read_config, write_config
from api.jobs import JobStore, JOB_STATUS
from api.scheduler import KometaScheduler


class ScheduleRequest(BaseModel):
    times: list[str]


def _has_active_run(store: JobStore) -> bool:
    return any(j["status"] == JOB_STATUS.RUNNING for j in store.list(limit=100))


def make_router(config_path: str, store: JobStore, scheduler: KometaScheduler) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["config"])

    @router.get("/config", dependencies=[Depends(require_api_key)])
    def get_config() -> dict:
        return read_config(config_path)

    @router.put("/config", dependencies=[Depends(require_api_key)])
    def put_config(patch: dict) -> dict:
        if _has_active_run(store):
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="A run is in progress; config cannot be modified")
        write_config(config_path, patch)
        return {"ok": True}

    @router.get("/schedule", dependencies=[Depends(require_api_key)])
    def get_schedule() -> dict:
        return {"times": [], "next_run": scheduler.next_run()}

    @router.put("/schedule", dependencies=[Depends(require_api_key)])
    def put_schedule(req: ScheduleRequest) -> dict:
        scheduler.set_times(req.times)
        write_config(config_path, {"settings": {"times": ",".join(req.times)}})
        return {"ok": True}

    return router
```

- [ ] **Step 4: Update `api/app.py`**

```python
from fastapi import FastAPI
from api.jobs import JobStore, JobWorker
from api.scheduler import KometaScheduler
from api.routers import health as health_router
from api.routers import runs as runs_router
from api.routers import config_router as config_router_module


def create_app(
    store: JobStore | None = None,
    worker: JobWorker | None = None,
    config_path: str | None = None,
    scheduler: KometaScheduler | None = None,
) -> FastAPI:
    app = FastAPI(title="Kometa API", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc")
    app.include_router(health_router.router)
    if store is not None and worker is not None:
        app.include_router(runs_router.make_router(store, worker))
    if config_path is not None and store is not None and scheduler is not None:
        app.include_router(config_router_module.make_router(config_path, store, scheduler))
    return app
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_api_config.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add api/routers/config_router.py api/app.py tests/test_api_config.py
git commit -m "feat(api): add config and schedule endpoints"
```

---

### Task 10: Libraries and collections router

**Files:**
- Create: `api/routers/libraries.py`
- Create: `tests/test_api_collections.py`
- Modify: `api/app.py` (register libraries router when `config_path` is set)

**Interfaces:**
- Consumes: `read_collections`, `write_collections`, `_load_yaml` from Task 8
- Produces:
  - `GET /api/libraries` → `list[{"name": str, "metadata_path": list}]`
  - `GET /api/libraries/{lib}/collections` → `dict` keyed by collection name
  - `POST /api/libraries/{lib}/collections` body `{"name": str, "definition": dict}` → `201 {"ok": true}`
  - `GET /api/libraries/{lib}/collections/{name}` → `dict`
  - `PUT /api/libraries/{lib}/collections/{name}` body is the new definition dict → `200 {"ok": true}`
  - `DELETE /api/libraries/{lib}/collections/{name}` → `200 {"ok": true}`

Collection names may contain spaces; use `{name:path}` in FastAPI route to capture them.

- [ ] **Step 1: Write failing tests**

Create `tests/test_api_collections.py`:
```python
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.app import create_app
from api.jobs import JobStore, JobWorker

SAMPLE_META = "collections:\n  Best of 2024:\n    tmdb_popular: 20\n"
HEADERS = {"X-API-Key": "test-key"}

@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("KOMETA_API_KEY", "test-key")
    meta_path = tmp_path / "movies.yml"
    meta_path.write_text(SAMPLE_META)
    cfg_path = tmp_path / "config.yml"
    cfg_path.write_text(f"libraries:\n  Movies:\n    metadata_path:\n      - file: {meta_path}\n")
    store = JobStore(str(tmp_path / "test.db"))
    mock_logger = MagicMock()
    mock_logger._logger = MagicMock()
    worker = JobWorker(store=store, run_fn=MagicMock(), logger_instance=mock_logger)
    worker.start()
    scheduler = MagicMock()
    scheduler.next_run.return_value = None
    app = create_app(store=store, worker=worker, config_path=str(cfg_path), scheduler=scheduler)
    yield TestClient(app)
    worker.stop()

def test_list_libraries(setup):
    resp = setup.get("/api/libraries", headers=HEADERS)
    assert resp.status_code == 200
    assert any(lib["name"] == "Movies" for lib in resp.json())

def test_list_collections(setup):
    resp = setup.get("/api/libraries/Movies/collections", headers=HEADERS)
    assert resp.status_code == 200
    assert "Best of 2024" in resp.json()

def test_get_collection(setup):
    resp = setup.get("/api/libraries/Movies/collections/Best of 2024", headers=HEADERS)
    assert resp.status_code == 200
    assert "tmdb_popular" in resp.json()

def test_create_collection(setup):
    resp = setup.post("/api/libraries/Movies/collections", json={"name": "Action Movies", "definition": {"plex_search": {"genre": "Action"}}}, headers=HEADERS)
    assert resp.status_code == 201
    assert "Action Movies" in setup.get("/api/libraries/Movies/collections", headers=HEADERS).json()

def test_create_duplicate_collection_rejected(setup):
    setup.post("/api/libraries/Movies/collections", json={"name": "Dupe", "definition": {}}, headers=HEADERS)
    resp = setup.post("/api/libraries/Movies/collections", json={"name": "Dupe", "definition": {}}, headers=HEADERS)
    assert resp.status_code == 409

def test_update_collection(setup):
    setup.put("/api/libraries/Movies/collections/Best of 2024", json={"tmdb_popular": 50}, headers=HEADERS)
    resp = setup.get("/api/libraries/Movies/collections/Best of 2024", headers=HEADERS)
    assert resp.json()["tmdb_popular"] == 50

def test_delete_collection(setup):
    setup.delete("/api/libraries/Movies/collections/Best of 2024", headers=HEADERS)
    assert setup.get("/api/libraries/Movies/collections/Best of 2024", headers=HEADERS).status_code == 404

def test_nonexistent_library_returns_404(setup):
    assert setup.get("/api/libraries/Nope/collections", headers=HEADERS).status_code == 404

def test_nonexistent_collection_returns_404(setup):
    assert setup.get("/api/libraries/Movies/collections/Ghost", headers=HEADERS).status_code == 404

def test_libraries_require_auth(setup):
    assert setup.get("/api/libraries").status_code == 401
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_api_collections.py -v
```

Expected: FAIL (no libraries router)

- [ ] **Step 3: Create `api/routers/libraries.py`**

```python
import os
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.auth import require_api_key
from api.config_io import _load_yaml, read_collections, write_collections


class CreateCollectionRequest(BaseModel):
    name: str
    definition: dict


def _resolve_meta_path(entry: dict | str, config_dir: str) -> str:
    if isinstance(entry, dict):
        p = entry.get("file", "")
    else:
        p = entry
    return p if os.path.isabs(p) else os.path.join(config_dir, p)


def _get_library_config(config_path: str, lib_name: str) -> dict:
    raw = _load_yaml(config_path)
    libraries = raw.get("libraries") or {}
    if lib_name not in libraries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Library '{lib_name}' not found")
    return dict(libraries[lib_name] or {})


def _first_meta_path(lib_config: dict, config_dir: str) -> str:
    entries = lib_config.get("metadata_path") or []
    if not entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No metadata_path configured for this library")
    return _resolve_meta_path(entries[0], config_dir)


def make_router(config_path: str) -> APIRouter:
    config_dir = os.path.dirname(os.path.abspath(config_path))
    router = APIRouter(prefix="/api/libraries", tags=["libraries"])

    @router.get("", dependencies=[Depends(require_api_key)])
    def list_libraries() -> list[dict]:
        raw = _load_yaml(config_path)
        libs = raw.get("libraries") or {}
        return [{"name": name, "metadata_path": list((lib or {}).get("metadata_path") or [])} for name, lib in libs.items()]

    @router.get("/{lib_name}/collections", dependencies=[Depends(require_api_key)])
    def list_collections(lib_name: str) -> dict:
        lib = _get_library_config(config_path, lib_name)
        return read_collections(_first_meta_path(lib, config_dir))

    @router.post("/{lib_name}/collections", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_api_key)])
    def create_collection(lib_name: str, req: CreateCollectionRequest) -> dict:
        lib = _get_library_config(config_path, lib_name)
        meta_path = _first_meta_path(lib, config_dir)
        colls = read_collections(meta_path)
        if req.name in colls:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Collection '{req.name}' already exists")
        colls[req.name] = req.definition
        write_collections(meta_path, colls)
        return {"ok": True}

    @router.get("/{lib_name}/collections/{name:path}", dependencies=[Depends(require_api_key)])
    def get_collection(lib_name: str, name: str) -> dict:
        lib = _get_library_config(config_path, lib_name)
        colls = read_collections(_first_meta_path(lib, config_dir))
        if name not in colls:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection '{name}' not found")
        return dict(colls[name] or {})

    @router.put("/{lib_name}/collections/{name:path}", dependencies=[Depends(require_api_key)])
    def update_collection(lib_name: str, name: str, definition: dict) -> dict:
        lib = _get_library_config(config_path, lib_name)
        meta_path = _first_meta_path(lib, config_dir)
        colls = read_collections(meta_path)
        if name not in colls:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection '{name}' not found")
        colls[name] = definition
        write_collections(meta_path, colls)
        return {"ok": True}

    @router.delete("/{lib_name}/collections/{name:path}", dependencies=[Depends(require_api_key)])
    def delete_collection(lib_name: str, name: str) -> dict:
        lib = _get_library_config(config_path, lib_name)
        meta_path = _first_meta_path(lib, config_dir)
        colls = read_collections(meta_path)
        if name not in colls:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Collection '{name}' not found")
        del colls[name]
        write_collections(meta_path, colls)
        return {"ok": True}

    return router
```

- [ ] **Step 4: Register libraries router in `api/app.py`**

```python
from fastapi import FastAPI
from api.jobs import JobStore, JobWorker
from api.scheduler import KometaScheduler
from api.routers import health as health_router
from api.routers import runs as runs_router
from api.routers import config_router as config_router_module
from api.routers import libraries as libraries_router


def create_app(
    store: JobStore | None = None,
    worker: JobWorker | None = None,
    config_path: str | None = None,
    scheduler: KometaScheduler | None = None,
) -> FastAPI:
    app = FastAPI(title="Kometa API", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc")
    app.include_router(health_router.router)
    if store is not None and worker is not None:
        app.include_router(runs_router.make_router(store, worker))
    if config_path is not None and store is not None and scheduler is not None:
        app.include_router(config_router_module.make_router(config_path, store, scheduler))
        app.include_router(libraries_router.make_router(config_path))
    return app
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_api_collections.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add api/routers/libraries.py api/app.py tests/test_api_collections.py
git commit -m "feat(api): add libraries and collections CRUD endpoints"
```

---

### Task 11: Frontend static serving and `server.py` entry point

**Files:**
- Modify: `api/app.py` (add `frontend_dir` param, mount static files, SPA catch-all)
- Create: `server.py`
- Create: `tests/test_server_entrypoint.py`

**Interfaces:**
- Consumes: `JobStore`, `JobWorker`, `KometaScheduler`, `create_app` — all from prior tasks
- Consumes: `kometa.start` and `kometa.logger` from `kometa.py` (imported at server startup)
- Produces: `server.py` — `python server.py [--config PATH] [--host HOST] [--port PORT] [--times HH:MM,...] [--db PATH] [--debug]`

**Note on `import kometa`:** `kometa.py` runs `argparse.parse_known_args()` at import time. This is safe — `parse_known_args` silently ignores `--host`, `--port`, and other server-specific flags. The `run_args` dict is populated from environment variables and the remaining recognised args. Set any Kometa env vars (`KOMETA_DEBUG`, `KOMETA_TIMEOUT`, etc.) in the shell environment before starting `server.py`; they will be picked up at import time.

- [ ] **Step 1: Write failing tests**

Create `tests/test_server_entrypoint.py`:
```python
import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.app import create_app
from api.jobs import JobStore, JobWorker

HEADERS = {"X-API-Key": "test-key"}

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("KOMETA_API_KEY", "test-key")
    frontend_dir = tmp_path / "frontend" / "dist"
    frontend_dir.mkdir(parents=True)
    (frontend_dir / "index.html").write_text("<html><body>Kometa UI</body></html>")
    store = JobStore(str(tmp_path / "test.db"))
    mock_logger = MagicMock()
    mock_logger._logger = MagicMock()
    worker = JobWorker(store=store, run_fn=MagicMock(), logger_instance=mock_logger)
    worker.start()
    scheduler = MagicMock()
    scheduler.next_run.return_value = None
    cfg_path = tmp_path / "config.yml"
    cfg_path.write_text("plex:\n  url: http://localhost:32400\n")
    app = create_app(store=store, worker=worker, config_path=str(cfg_path), scheduler=scheduler, frontend_dir=str(frontend_dir))
    yield TestClient(app, raise_server_exceptions=False)
    worker.stop()

def test_frontend_root_served(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Kometa UI" in resp.text

def test_spa_catchall_returns_index(client):
    resp = client.get("/some/deep/client/route")
    assert resp.status_code == 200
    assert "Kometa UI" in resp.text

def test_api_routes_not_swallowed_by_catchall(client):
    assert client.get("/api/health").json() == {"status": "ok"}

def test_all_existing_tests_still_pass():
    pass  # enforced by running the full test suite in the next step
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_server_entrypoint.py::test_frontend_root_served -v
```

Expected: FAIL (`create_app` doesn't accept `frontend_dir`)

- [ ] **Step 3: Update `api/app.py` to add static serving and catch-all**

```python
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.jobs import JobStore, JobWorker
from api.scheduler import KometaScheduler
from api.routers import health as health_router
from api.routers import runs as runs_router
from api.routers import config_router as config_router_module
from api.routers import libraries as libraries_router


def create_app(
    store: JobStore | None = None,
    worker: JobWorker | None = None,
    config_path: str | None = None,
    scheduler: KometaScheduler | None = None,
    frontend_dir: str | None = None,
) -> FastAPI:
    app = FastAPI(title="Kometa API", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc")
    app.include_router(health_router.router)
    if store is not None and worker is not None:
        app.include_router(runs_router.make_router(store, worker))
    if config_path is not None and store is not None and scheduler is not None:
        app.include_router(config_router_module.make_router(config_path, store, scheduler))
        app.include_router(libraries_router.make_router(config_path))

    if frontend_dir and os.path.isdir(frontend_dir):
        index_path = os.path.join(frontend_dir, "index.html")
        assets_dir = os.path.join(frontend_dir, "assets")
        if os.path.isdir(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa_catchall(full_path: str) -> FileResponse:
            return FileResponse(index_path)

    return app
```

- [ ] **Step 4: Create `server.py`**

```python
#!/usr/bin/env python3
import argparse
import os
import sys

if sys.version_info < (3, 10):
    print(f"Python {sys.version_info[0]}.{sys.version_info[1]} is not supported. Kometa requires Python 3.10+.")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "config", ".env"))

parser = argparse.ArgumentParser(description="Kometa API Server")
parser.add_argument("--config", "-c", default=os.path.join(os.path.dirname(__file__), "config", "config.yml"), help="Path to config.yml")
parser.add_argument("--host", default=os.environ.get("KOMETA_HOST", "0.0.0.0"), help="Bind host (default: 0.0.0.0)")
parser.add_argument("--port", "-p", type=int, default=int(os.environ.get("KOMETA_PORT", "7777")), help="Bind port (default: 7777)")
parser.add_argument("--db", default=os.path.join(os.path.dirname(__file__), "config", "kometa_server.db"), help="Path to job database")
parser.add_argument("--times", "-t", default=os.environ.get("KOMETA_TIMES", "05:00"), help="Comma-separated run times HH:MM (default: 05:00)")
parser.add_argument("--debug", action="store_true", default=False, help="Enable debug logging")
server_args, _ = parser.parse_known_args()

import kometa  # noqa: E402  (imported after dotenv and server arg parsing so env vars are set first)
import uvicorn  # noqa: E402
from api.app import create_app  # noqa: E402
from api.jobs import JobStore, JobWorker  # noqa: E402
from api.scheduler import KometaScheduler  # noqa: E402


def main() -> None:
    if not os.environ.get("KOMETA_API_KEY"):
        print("ERROR: KOMETA_API_KEY environment variable must be set before starting the server.")
        sys.exit(1)

    store = JobStore(server_args.db)
    store.prune(days=30)

    worker = JobWorker(store=store, run_fn=kometa.start, logger_instance=kometa.logger)
    worker.start()

    run_times = [t.strip() for t in server_args.times.split(",") if t.strip()]
    scheduler = KometaScheduler(worker=worker, run_times=run_times)
    scheduler.start()

    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
    app = create_app(
        store=store,
        worker=worker,
        config_path=server_args.config,
        scheduler=scheduler,
        frontend_dir=frontend_dir,
    )

    print(f"Kometa API server starting on http://{server_args.host}:{server_args.port}")
    print(f"  API docs: http://{server_args.host}:{server_args.port}/api/docs")
    print(f"  Scheduled run times: {', '.join(run_times) if run_times else 'none'}")

    try:
        uvicorn.run(app, host=server_args.host, port=server_args.port, log_level="debug" if server_args.debug else "info")
    finally:
        scheduler.stop()
        worker.stop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run new tests**

```bash
pytest tests/test_server_entrypoint.py -v
```

Expected: all PASS

- [ ] **Step 6: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all tests PASS (no regressions in existing tests)

- [ ] **Step 7: Commit**

```bash
git add api/app.py server.py tests/test_server_entrypoint.py
git commit -m "feat(api): add frontend static serving and server.py entry point"
```
