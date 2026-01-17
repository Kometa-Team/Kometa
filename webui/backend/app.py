"""
Kometa Web UI - FastAPI Backend

A safe, read-only by default web interface for Kometa.
"""

import os
import json
import asyncio
import subprocess
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import aiosqlite

from backend.config_manager import ConfigManager
from backend.run_manager import RunManager
from backend.overlay_preview import OverlayPreviewManager
from backend.poster_fetcher import PosterFetcher


# Configuration from environment
CONFIG_DIR = Path(os.environ.get("KOMETA_CONFIG_DIR", "/config"))
KOMETA_ROOT = Path(__file__).parent.parent.parent  # Go up from webui/backend to repo root
UI_PORT = int(os.environ.get("KOMETA_UI_PORT", "8080"))
UI_HOST = os.environ.get("KOMETA_UI_HOST", "0.0.0.0")

# Safety: Apply mode kill switch (default: disabled)
APPLY_ENABLED = os.environ.get("KOMETA_UI_APPLY_ENABLED", "false").lower() == "true"

# Optional simple password protection
UI_PASSWORD = os.environ.get("KOMETA_UI_PASSWORD", "")


# Initialize managers
config_manager: Optional[ConfigManager] = None
run_manager: Optional[RunManager] = None
overlay_manager: Optional[OverlayPreviewManager] = None
poster_fetcher: Optional[PosterFetcher] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    global config_manager, run_manager, overlay_manager, poster_fetcher

    # Ensure directories exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    (CONFIG_DIR / "backups").mkdir(exist_ok=True)
    (CONFIG_DIR / "logs" / "runs").mkdir(parents=True, exist_ok=True)

    # Initialize managers
    db_path = CONFIG_DIR / "webui.db"
    config_manager = ConfigManager(CONFIG_DIR)
    run_manager = RunManager(
        config_dir=CONFIG_DIR,
        kometa_root=KOMETA_ROOT,
        db_path=db_path,
        apply_enabled=APPLY_ENABLED
    )
    overlay_manager = OverlayPreviewManager(
        config_dir=CONFIG_DIR,
        kometa_root=KOMETA_ROOT
    )
    poster_fetcher = PosterFetcher(
        config_path=CONFIG_DIR / "config.yml"
    )

    await run_manager.init_db()

    print(f"Kometa Web UI starting on http://{UI_HOST}:{UI_PORT}")
    print(f"Config directory: {CONFIG_DIR}")
    print(f"Apply mode: {'ENABLED (use with caution!)' if APPLY_ENABLED else 'DISABLED (safe mode)'}")

    yield

    # Cleanup
    await run_manager.close()


# Create FastAPI app
app = FastAPI(
    title="Kometa Web UI",
    description="Safe web interface for Kometa metadata automation",
    version="1.0.0",
    lifespan=lifespan
)

# Static files and templates
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")
templates = Jinja2Templates(directory=frontend_dir / "templates")


# Pydantic models
class ConfigSaveRequest(BaseModel):
    content: str


class RunRequest(BaseModel):
    dry_run: bool = True
    libraries: Optional[List[str]] = None
    collections: Optional[List[str]] = None
    run_type: Optional[str] = None  # collections, metadata, overlays, operations, playlists


class ApplyConfirmation(BaseModel):
    confirmation: str
    dry_run: bool = False
    libraries: Optional[List[str]] = None
    collections: Optional[List[str]] = None
    run_type: Optional[str] = None


# ============================================================================
# HTML Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main UI page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "apply_enabled": APPLY_ENABLED
    })


# ============================================================================
# Health Check
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "apply_enabled": APPLY_ENABLED,
        "config_dir": str(CONFIG_DIR),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Configuration Endpoints
# ============================================================================

@app.get("/api/config")
async def get_config():
    """Load the current config.yml."""
    try:
        config_path = CONFIG_DIR / "config.yml"
        if not config_path.exists():
            return {
                "exists": False,
                "content": "",
                "path": str(config_path),
                "message": "No config.yml found. You can create one or import an existing configuration."
            }

        result = config_manager.load_config()
        return {
            "exists": True,
            "content": result["content"],
            "path": str(config_path),
            "parsed": result.get("parsed"),
            "validation": result.get("validation")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def save_config(request: ConfigSaveRequest):
    """Save config.yml with automatic backup."""
    try:
        result = config_manager.save_config(request.content)
        return {
            "success": True,
            "backup_path": result.get("backup_path"),
            "validation": result.get("validation")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/config/validate")
async def validate_config(request: ConfigSaveRequest):
    """Validate YAML without saving."""
    try:
        result = config_manager.validate_yaml(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/config/backups")
async def list_backups():
    """List available config backups."""
    try:
        backups = config_manager.list_backups()
        return {"backups": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/restore/{backup_name}")
async def restore_backup(backup_name: str):
    """Restore config from a backup."""
    try:
        result = config_manager.restore_backup(backup_name)
        return {"success": True, "restored_from": backup_name}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Run Endpoints
# ============================================================================

@app.get("/api/run/plan")
async def get_run_plan():
    """Generate a run plan preview based on current config."""
    try:
        plan = config_manager.generate_run_plan()
        plan["apply_enabled"] = APPLY_ENABLED
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run")
async def start_run(request: RunRequest):
    """Start a Kometa run (dry-run by default)."""
    # Enforce dry-run if apply mode is disabled
    if not APPLY_ENABLED and not request.dry_run:
        raise HTTPException(
            status_code=403,
            detail="Apply mode is disabled. Set KOMETA_UI_APPLY_ENABLED=true to enable."
        )

    # For non-dry-run, require explicit confirmation via the /api/run/apply endpoint
    if not request.dry_run:
        raise HTTPException(
            status_code=400,
            detail="For apply mode, use POST /api/run/apply with confirmation."
        )

    try:
        run_info = await run_manager.start_run(
            dry_run=True,
            libraries=request.libraries,
            collections=request.collections,
            run_type=request.run_type
        )
        return run_info
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run/apply")
async def start_apply_run(request: ApplyConfirmation):
    """Start a Kometa run in APPLY mode (requires confirmation)."""
    # Check kill switch
    if not APPLY_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="Apply mode is disabled by KOMETA_UI_APPLY_ENABLED=false"
        )

    # Require exact confirmation text
    if request.confirmation != "APPLY CHANGES":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation. Type exactly: APPLY CHANGES"
        )

    try:
        run_info = await run_manager.start_run(
            dry_run=False,
            libraries=request.libraries,
            collections=request.collections,
            run_type=request.run_type
        )
        return run_info
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/run/status")
async def get_run_status():
    """Get current run status."""
    status = await run_manager.get_status()
    return status


@app.post("/api/run/stop")
async def stop_run():
    """Stop the current run."""
    try:
        await run_manager.stop_run()
        return {"success": True, "message": "Run stopped"}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/runs")
async def list_runs(limit: int = 50, offset: int = 0):
    """List run history."""
    runs = await run_manager.list_runs(limit=limit, offset=offset)
    return {"runs": runs}


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    """Get details for a specific run."""
    run = await run_manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/api/logs/{run_id}")
async def get_run_logs(run_id: str, tail: int = 1000):
    """Get logs for a specific run."""
    try:
        logs = await run_manager.get_logs(run_id, tail=tail)
        return {"run_id": run_id, "logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Logs not found")


# ============================================================================
# WebSocket for Live Logs
# ============================================================================

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for streaming live logs."""
    await websocket.accept()

    try:
        # Subscribe to log updates
        async for log_line in run_manager.stream_logs():
            await websocket.send_json({"type": "log", "data": log_line})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "data": str(e)})


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """WebSocket endpoint for run status updates."""
    await websocket.accept()

    try:
        while True:
            status = await run_manager.get_status()
            await websocket.send_json(status)
            await asyncio.sleep(2)  # Update every 2 seconds
    except WebSocketDisconnect:
        pass


# ============================================================================
# Overlay Preview Endpoints
# ============================================================================

class OverlayPreviewRequest(BaseModel):
    overlays: List[Dict[str, Any]]
    canvas_type: str = "portrait"  # portrait, landscape, square
    poster_source: Optional[str] = None  # plex, tmdb, or None for sample
    rating_key: Optional[str] = None  # Plex rating key
    tmdb_id: Optional[str] = None  # TMDb ID
    media_type: str = "movie"  # movie, tv


@app.get("/api/overlays")
async def get_available_overlays():
    """Get list of available overlay configurations."""
    try:
        overlays = overlay_manager.get_available_overlays()
        return overlays
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/overlays/images")
async def get_overlay_images():
    """Get list of available overlay images."""
    try:
        images = overlay_manager.get_overlay_images_list()
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/overlays/parse")
async def parse_overlay_file(file_path: str):
    """Parse an overlay YAML file."""
    try:
        result = overlay_manager.parse_overlay_file(file_path)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/overlays/preview")
async def generate_overlay_preview(request: OverlayPreviewRequest):
    """Generate a preview image with overlays applied."""
    try:
        # Fetch poster if a source is specified
        sample_poster = None
        if request.poster_source == "plex" and request.rating_key:
            poster_data = poster_fetcher.fetch_poster_image(
                rating_key=request.rating_key
            )
            if poster_data:
                # Save to temp file for overlay manager
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(poster_data)
                    sample_poster = f.name
        elif request.poster_source == "tmdb" and request.tmdb_id:
            poster_data = poster_fetcher.fetch_poster_image(
                tmdb_id=request.tmdb_id,
                media_type=request.media_type
            )
            if poster_data:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(poster_data)
                    sample_poster = f.name

        result = overlay_manager.generate_preview(
            overlays=request.overlays,
            canvas_type=request.canvas_type,
            sample_poster=sample_poster
        )

        # Clean up temp file
        if sample_poster:
            import os
            try:
                os.unlink(sample_poster)
            except:
                pass

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/overlays/defaults")
async def get_default_overlays():
    """Get list of default overlay configurations with details."""
    try:
        overlays = overlay_manager.get_available_overlays()
        detailed = []

        for overlay_file in overlays.get("default", []):
            try:
                parsed = overlay_manager.parse_overlay_file(overlay_file["path"])
                detailed.append({
                    "name": overlay_file["name"],
                    "path": overlay_file["path"],
                    "overlay_count": len(parsed.get("overlays", [])),
                    "queue_count": len(parsed.get("queues", [])),
                    "overlays": parsed.get("overlays", [])[:5]  # First 5 for preview
                })
            except Exception:
                detailed.append({
                    "name": overlay_file["name"],
                    "path": overlay_file["path"],
                    "error": "Failed to parse"
                })

        return {"defaults": detailed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Media Search & Poster Endpoints (for overlay preview)
# ============================================================================

@app.get("/api/media/status")
async def get_media_sources_status():
    """Get status of available media sources (Plex, TMDb)."""
    try:
        status = poster_fetcher.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/libraries")
async def get_plex_libraries():
    """Get list of Plex libraries."""
    try:
        libraries = poster_fetcher.get_plex_libraries()
        return {"libraries": libraries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/search")
async def search_media(
    query: str,
    source: str = "plex",  # plex or tmdb
    media_type: str = "movie",  # movie or tv
    library: Optional[str] = None,
    limit: int = 20
):
    """Search for media items in Plex or TMDb."""
    try:
        if source == "plex":
            results = poster_fetcher.search_plex(query, library=library, limit=limit)
        elif source == "tmdb":
            results = poster_fetcher.search_tmdb(query, media_type=media_type, limit=limit)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

        return {"results": results, "source": source, "query": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/recent")
async def get_recent_media(library_key: str, limit: int = 20):
    """Get recently added media from a Plex library."""
    try:
        items = poster_fetcher.get_recent_items(library_key, limit=limit)
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/poster")
async def get_poster(
    rating_key: Optional[str] = None,
    tmdb_id: Optional[str] = None,
    media_type: str = "movie",
    width: Optional[int] = None,
    height: Optional[int] = None
):
    """Fetch a poster image and return as base64 data URI."""
    try:
        resize = None
        if width and height:
            resize = (width, height)

        result = poster_fetcher.fetch_poster_base64(
            rating_key=rating_key,
            tmdb_id=tmdb_id,
            media_type=media_type,
            resize=resize
        )

        if not result:
            raise HTTPException(status_code=404, detail="Poster not found")

        return {"poster": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=UI_HOST, port=UI_PORT)
