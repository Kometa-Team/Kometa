"""
Run Manager for Kometa Web UI

Handles executing Kometa via subprocess, tracking runs, and managing logs.
"""

import os
import sys
import json
import asyncio
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, AsyncGenerator
import aiosqlite


class RunManager:
    """Manages Kometa run execution and history."""

    def __init__(
        self,
        config_dir: Path,
        kometa_root: Path,
        db_path: Path,
        apply_enabled: bool = False
    ):
        self.config_dir = Path(config_dir)
        self.kometa_root = Path(kometa_root)
        self.db_path = Path(db_path)
        self.apply_enabled = apply_enabled

        self.logs_dir = self.config_dir / "logs" / "runs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Current run state
        self._current_process: Optional[subprocess.Popen] = None
        self._current_run_id: Optional[str] = None
        self._current_log_path: Optional[Path] = None
        self._log_queue: asyncio.Queue = asyncio.Queue()

        # Database connection
        self._db: Optional[aiosqlite.Connection] = None

    async def init_db(self):
        """Initialize the SQLite database."""
        self._db = await aiosqlite.connect(self.db_path)
        self._db.row_factory = aiosqlite.Row

        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER,
                dry_run INTEGER NOT NULL,
                status TEXT NOT NULL,
                exit_code INTEGER,
                libraries TEXT,
                collections TEXT,
                run_type TEXT,
                log_path TEXT,
                error_message TEXT
            )
        """)
        await self._db.commit()

    async def close(self):
        """Close database connection."""
        if self._db:
            await self._db.close()

    def _generate_run_id(self) -> str:
        """Generate a unique run ID."""
        return f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    async def start_run(
        self,
        dry_run: bool = True,
        libraries: Optional[List[str]] = None,
        collections: Optional[List[str]] = None,
        run_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new Kometa run."""
        # Check if a run is already in progress
        if self._current_process and self._current_process.poll() is None:
            raise RuntimeError("A run is already in progress")

        # Generate run ID and log path
        run_id = self._generate_run_id()
        log_path = self.logs_dir / f"{run_id}.log"

        # Build command
        cmd = self._build_command(
            dry_run=dry_run,
            libraries=libraries,
            collections=collections,
            run_type=run_type
        )

        # Record start time
        start_time = datetime.utcnow()

        # Insert run record
        await self._db.execute("""
            INSERT INTO runs (id, start_time, dry_run, status, libraries, collections, run_type, log_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            start_time.isoformat(),
            1 if dry_run else 0,
            "running",
            "|".join(libraries) if libraries else None,
            "|".join(collections) if collections else None,
            run_type,
            str(log_path)
        ))
        await self._db.commit()

        # Open log file
        log_file = open(log_path, "w", encoding="utf-8")

        # Start subprocess
        env = os.environ.copy()
        env["KOMETA_CONFIG"] = str(self.config_dir / "config.yml")

        # Set dry-run environment variable for Write Guard
        if dry_run:
            env["KOMETA_DRY_RUN"] = "true"

        self._current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            cwd=str(self.kometa_root),
            env=env
        )

        self._current_run_id = run_id
        self._current_log_path = log_path

        # Start log reader task
        asyncio.create_task(self._read_process_output(log_file))

        return {
            "run_id": run_id,
            "dry_run": dry_run,
            "status": "running",
            "start_time": start_time.isoformat(),
            "log_path": str(log_path),
            "command": " ".join(cmd)
        }

    def _build_command(
        self,
        dry_run: bool,
        libraries: Optional[List[str]],
        collections: Optional[List[str]],
        run_type: Optional[str]
    ) -> List[str]:
        """Build the Kometa command line."""
        python_exe = sys.executable
        kometa_script = self.kometa_root / "kometa.py"

        cmd = [python_exe, str(kometa_script)]

        # Always run immediately (not scheduled)
        cmd.extend(["--run"])

        # Config path
        cmd.extend(["--config", str(self.config_dir / "config.yml")])

        # Dry-run flag (this will be checked by the Write Guard)
        if dry_run:
            cmd.extend(["--dry-run"])

        # Filter by libraries
        if libraries:
            cmd.extend(["--run-libraries", "|".join(libraries)])

        # Filter by collections
        if collections:
            cmd.extend(["--run-collections", "|".join(collections)])

        # Run type filter
        if run_type:
            type_flag_map = {
                "collections": "--collections-only",
                "metadata": "--metadata-only",
                "overlays": "--overlays-only",
                "operations": "--operations-only",
                "playlists": "--playlists-only"
            }
            if run_type in type_flag_map:
                cmd.append(type_flag_map[run_type])

        return cmd

    async def _read_process_output(self, log_file):
        """Read process output and write to log file."""
        try:
            while True:
                if self._current_process is None:
                    break

                line = await asyncio.get_event_loop().run_in_executor(
                    None, self._current_process.stdout.readline
                )

                if not line:
                    # Process has finished
                    break

                # Write to log file
                log_file.write(line)
                log_file.flush()

                # Put in queue for WebSocket streaming
                await self._log_queue.put(line.rstrip())

            # Process finished
            exit_code = self._current_process.wait()
            await self._finalize_run(exit_code)

        except Exception as e:
            await self._finalize_run(-1, error_message=str(e))
        finally:
            log_file.close()

    async def _finalize_run(self, exit_code: int, error_message: str = None):
        """Finalize a completed run."""
        if not self._current_run_id:
            return

        end_time = datetime.utcnow()

        # Get start time from database
        async with self._db.execute(
            "SELECT start_time FROM runs WHERE id = ?",
            (self._current_run_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                start_time = datetime.fromisoformat(row["start_time"])
                duration = int((end_time - start_time).total_seconds())
            else:
                duration = 0

        status = "success" if exit_code == 0 else "failed"

        await self._db.execute("""
            UPDATE runs
            SET end_time = ?, duration_seconds = ?, status = ?, exit_code = ?, error_message = ?
            WHERE id = ?
        """, (
            end_time.isoformat(),
            duration,
            status,
            exit_code,
            error_message,
            self._current_run_id
        ))
        await self._db.commit()

        # Signal end of log stream
        await self._log_queue.put(None)

        # Clear current run state
        self._current_process = None
        self._current_run_id = None
        self._current_log_path = None

    async def stop_run(self):
        """Stop the current run."""
        if not self._current_process or self._current_process.poll() is not None:
            raise RuntimeError("No run is currently in progress")

        # Send SIGTERM for graceful shutdown
        self._current_process.terminate()

        # Wait a bit for graceful shutdown
        try:
            self._current_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            # Force kill if not responding
            self._current_process.kill()
            self._current_process.wait()

        await self._finalize_run(-15, error_message="Stopped by user")

    async def get_status(self) -> Dict[str, Any]:
        """Get current run status."""
        if self._current_process and self._current_process.poll() is None:
            # Run in progress
            async with self._db.execute(
                "SELECT * FROM runs WHERE id = ?",
                (self._current_run_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "running": True,
                        "run_id": row["id"],
                        "dry_run": bool(row["dry_run"]),
                        "start_time": row["start_time"],
                        "libraries": row["libraries"].split("|") if row["libraries"] else None,
                        "collections": row["collections"].split("|") if row["collections"] else None,
                        "run_type": row["run_type"]
                    }

        return {"running": False, "run_id": None}

    async def list_runs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List run history."""
        runs = []
        async with self._db.execute(
            """
            SELECT * FROM runs
            ORDER BY start_time DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        ) as cursor:
            async for row in cursor:
                runs.append({
                    "id": row["id"],
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "duration_seconds": row["duration_seconds"],
                    "dry_run": bool(row["dry_run"]),
                    "status": row["status"],
                    "exit_code": row["exit_code"],
                    "libraries": row["libraries"].split("|") if row["libraries"] else None,
                    "collections": row["collections"].split("|") if row["collections"] else None,
                    "run_type": row["run_type"],
                    "log_path": row["log_path"],
                    "error_message": row["error_message"]
                })
        return runs

    async def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific run."""
        async with self._db.execute(
            "SELECT * FROM runs WHERE id = ?",
            (run_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None

            return {
                "id": row["id"],
                "start_time": row["start_time"],
                "end_time": row["end_time"],
                "duration_seconds": row["duration_seconds"],
                "dry_run": bool(row["dry_run"]),
                "status": row["status"],
                "exit_code": row["exit_code"],
                "libraries": row["libraries"].split("|") if row["libraries"] else None,
                "collections": row["collections"].split("|") if row["collections"] else None,
                "run_type": row["run_type"],
                "log_path": row["log_path"],
                "error_message": row["error_message"]
            }

    async def get_logs(self, run_id: str, tail: int = 1000) -> List[str]:
        """Get logs for a specific run."""
        run = await self.get_run(run_id)
        if not run:
            raise FileNotFoundError(f"Run not found: {run_id}")

        log_path = Path(run["log_path"])
        if not log_path.exists():
            raise FileNotFoundError(f"Log file not found: {log_path}")

        # Read last N lines
        lines = log_path.read_text(encoding="utf-8").splitlines()
        if tail and len(lines) > tail:
            lines = lines[-tail:]

        return lines

    async def stream_logs(self) -> AsyncGenerator[str, None]:
        """Stream logs in real-time."""
        while True:
            line = await self._log_queue.get()
            if line is None:
                # End of stream
                break
            yield line
