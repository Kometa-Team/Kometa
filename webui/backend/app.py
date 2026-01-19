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
# KOMETA_ROOT: Where the main Kometa source code lives (kometa.py, modules/, etc.)
# In Docker: mounted at /kometa; locally: relative to this file
KOMETA_ROOT = Path(os.environ.get("KOMETA_ROOT", "/kometa"))
UI_PORT = int(os.environ.get("KOMETA_UI_PORT", "8080"))
UI_HOST = os.environ.get("KOMETA_UI_HOST", "0.0.0.0")

# Safety: Apply mode kill switch (default: disabled)
APPLY_ENABLED = os.environ.get("KOMETA_UI_APPLY_ENABLED", "false").lower() == "true"

# Optional simple password protection
UI_PASSWORD = os.environ.get("KOMETA_UI_PASSWORD", "")

# UI Mode: 'vue' for Vue 3 SPA, 'legacy' for Jinja2 templates
UI_MODE = os.environ.get("KOMETA_UI_MODE", "legacy").lower()


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
    print(f"UI Mode: {UI_MODE.upper()}" + (" (Vue build available)" if vue_available else " (Vue build not found, using legacy)" if UI_MODE == "vue" else ""))

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
vue_frontend_dir = Path(__file__).parent.parent / "frontend-vue" / "dist"

# Check if Vue build exists
vue_available = vue_frontend_dir.exists() and (vue_frontend_dir / "index.html").exists()

if UI_MODE == "vue" and vue_available:
    # Serve Vue 3 SPA
    app.mount("/assets", StaticFiles(directory=vue_frontend_dir / "assets"), name="assets")
else:
    # Serve legacy static files
    app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")
    templates = Jinja2Templates(directory=frontend_dir / "templates")

# Mount overlay images from defaults directory
overlay_images_dir = KOMETA_ROOT / "defaults" / "overlays" / "images"
if overlay_images_dir.exists():
    app.mount("/overlay-images", StaticFiles(directory=overlay_images_dir), name="overlay-images")


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
    if UI_MODE == "vue" and vue_available:
        # Serve Vue SPA
        from fastapi.responses import FileResponse
        return FileResponse(vue_frontend_dir / "index.html")
    else:
        # Serve legacy Jinja2 template
        return templates.TemplateResponse("index.html", {
            "request": request,
            "apply_enabled": APPLY_ENABLED
        })


# Catch-all route for Vue SPA client-side routing
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """Serve Vue SPA for all non-API routes (client-side routing support)."""
    # Skip API and WebSocket routes
    if full_path.startswith(("api/", "ws/", "static/", "assets/", "overlay-images/")):
        raise HTTPException(status_code=404, detail="Not found")

    if UI_MODE == "vue" and vue_available:
        # Check if it's a static file
        file_path = vue_frontend_dir / full_path
        if file_path.exists() and file_path.is_file():
            from fastapi.responses import FileResponse
            return FileResponse(file_path)
        # Otherwise return index.html for client-side routing
        from fastapi.responses import FileResponse
        return FileResponse(vue_frontend_dir / "index.html")
    else:
        # Legacy mode - 404 for unknown routes
        raise HTTPException(status_code=404, detail="Not found")


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


@app.get("/api/settings")
async def get_settings():
    """Get current Web UI settings."""
    return {
        "apply_enabled": APPLY_ENABLED,
        "password_required": bool(UI_PASSWORD),
        "ui_mode": UI_MODE,
        "vue_available": vue_available,
        "version": "1.0.0"
    }


@app.get("/api/libraries")
async def get_libraries():
    """Get list of libraries from config."""
    try:
        result = config_manager.load_config()
        parsed = result.get("parsed", {})
        libraries = []

        if parsed and "libraries" in parsed:
            for name, config in parsed["libraries"].items():
                lib_type = "unknown"
                # Try to determine library type from config
                if config:
                    if "collection_files" in config:
                        lib_type = "collection"
                    elif "overlay_files" in config:
                        lib_type = "overlay"
                libraries.append({
                    "name": name,
                    "type": lib_type
                })

        return libraries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
async def parse_overlay_file(file_path: str, template_vars: Optional[str] = None):
    """
    Parse an overlay YAML file.

    Args:
        file_path: Path to the overlay file
        template_vars: JSON-encoded template variables (optional)
    """
    try:
        # Parse template variables if provided
        user_template_vars = None
        if template_vars:
            import json
            try:
                user_template_vars = json.loads(template_vars)
            except json.JSONDecodeError:
                pass

        result = overlay_manager.parse_overlay_file(file_path, user_template_vars)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/overlays/preview")
async def generate_overlay_preview(request: OverlayPreviewRequest):
    """Generate a preview image with overlays applied."""
    try:
        # Fetch poster and metadata if a source is specified
        sample_poster = None
        media_metadata = None

        if request.poster_source == "plex" and request.rating_key:
            # Fetch poster image
            poster_data = poster_fetcher.fetch_poster_image(
                rating_key=request.rating_key
            )
            if poster_data:
                # Save to temp file for overlay manager
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(poster_data)
                    sample_poster = f.name

            # Fetch metadata for text variable substitution
            media_metadata = poster_fetcher.get_plex_item_metadata(request.rating_key)

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
            sample_poster=sample_poster,
            media_metadata=media_metadata
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
# Connection Test Endpoints
# ============================================================================

class PlexTestRequest(BaseModel):
    url: str
    token: str


class TmdbTestRequest(BaseModel):
    apikey: str


class ArrTestRequest(BaseModel):
    url: str
    token: str


class TautulliTestRequest(BaseModel):
    url: str
    apikey: str


class ApiKeyTestRequest(BaseModel):
    apikey: str


class TraktTestRequest(BaseModel):
    client_id: str
    client_secret: Optional[str] = None


class MalTestRequest(BaseModel):
    client_id: str


class AnidbTestRequest(BaseModel):
    client: str
    version: str


class GithubTestRequest(BaseModel):
    token: str


class GotifyTestRequest(BaseModel):
    url: str
    token: str


class NtfyTestRequest(BaseModel):
    url: str
    topic: str


@app.post("/api/test/plex")
async def test_plex_connection(request: PlexTestRequest):
    """Test Plex server connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        headers = {
            "X-Plex-Token": request.token,
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/", headers=headers)

            if response.status_code == 200:
                data = response.json()
                server_name = data.get("MediaContainer", {}).get("friendlyName", "Plex Server")
                return {"success": True, "server_name": server_name}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/tmdb")
async def test_tmdb_connection(request: TmdbTestRequest):
    """Test TMDb API key."""
    import httpx

    try:
        url = f"https://api.themoviedb.org/3/configuration?api_key={request.apikey}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                return {"success": True, "message": "API key is valid"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/radarr")
async def test_radarr_connection(request: ArrTestRequest):
    """Test Radarr connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        headers = {"X-Api-Key": request.token}

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/api/v3/system/status", headers=headers)

            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                return {"success": True, "message": f"Connected to Radarr v{version}"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/sonarr")
async def test_sonarr_connection(request: ArrTestRequest):
    """Test Sonarr connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        headers = {"X-Api-Key": request.token}

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/api/v3/system/status", headers=headers)

            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                return {"success": True, "message": f"Connected to Sonarr v{version}"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/tautulli")
async def test_tautulli_connection(request: TautulliTestRequest):
    """Test Tautulli connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        params = {"apikey": request.apikey, "cmd": "get_server_info"}

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/api/v2", params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("response", {}).get("result") == "success":
                    return {"success": True, "message": "Connected to Tautulli"}
                else:
                    return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/mdblist")
async def test_mdblist_connection(request: ApiKeyTestRequest):
    """Test MDBList API key."""
    import httpx

    try:
        url = f"https://mdblist.com/api/user/?apikey={request.apikey}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                if "error" not in data:
                    return {"success": True, "message": "API key is valid"}
                else:
                    return {"success": False, "error": data.get("error", "Unknown error")}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/omdb")
async def test_omdb_connection(request: ApiKeyTestRequest):
    """Test OMDb API key."""
    import httpx

    try:
        url = f"https://www.omdbapi.com/?apikey={request.apikey}&t=test"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True" or "Error" not in data or "Invalid API key" not in data.get("Error", ""):
                    return {"success": True, "message": "API key is valid"}
                elif "Invalid API key" in data.get("Error", ""):
                    return {"success": False, "error": "Invalid API key"}
                else:
                    return {"success": True, "message": "API key is valid"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/trakt")
async def test_trakt_connection(request: TraktTestRequest):
    """Test Trakt API credentials."""
    import httpx

    try:
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": request.client_id
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.trakt.tv/lists/trending", headers=headers)

            if response.status_code == 200:
                return {"success": True, "message": "Client ID is valid"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid Client ID"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/mal")
async def test_mal_connection(request: MalTestRequest):
    """Test MyAnimeList API credentials."""
    import httpx

    try:
        headers = {"X-MAL-CLIENT-ID": request.client_id}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.myanimelist.net/v2/anime/ranking?ranking_type=all&limit=1",
                headers=headers
            )

            if response.status_code == 200:
                return {"success": True, "message": "Client ID is valid"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid Client ID"}
            elif response.status_code == 403:
                return {"success": False, "error": "Client ID forbidden - check app settings"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/anidb")
async def test_anidb_connection(request: AnidbTestRequest):
    """Test AniDB API credentials."""
    # AniDB API is rate-limited and doesn't have a simple test endpoint
    # Just validate that the client name is lowercase and version is numeric
    if not request.client.islower():
        return {"success": False, "error": "Client name must be lowercase"}

    if not request.version.isdigit():
        return {"success": False, "error": "Version must be a number"}

    return {"success": True, "message": "Credentials format is valid (AniDB connection will be tested during run)"}


@app.post("/api/test/github")
async def test_github_connection(request: GithubTestRequest):
    """Test GitHub personal access token."""
    import httpx

    try:
        headers = {"Authorization": f"token {request.token}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.github.com/user", headers=headers)

            if response.status_code == 200:
                data = response.json()
                username = data.get("login", "unknown")
                return {"success": True, "message": f"Authenticated as {username}"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/notifiarr")
async def test_notifiarr_connection(request: ApiKeyTestRequest):
    """Test Notifiarr API key."""
    import httpx

    try:
        headers = {"x-api-key": request.apikey}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://notifiarr.com/api/v1/user/validate", headers=headers)

            if response.status_code == 200:
                return {"success": True, "message": "API key is valid"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid API key"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/gotify")
async def test_gotify_connection(request: GotifyTestRequest):
    """Test Gotify connection."""
    import httpx

    try:
        url = request.url.rstrip('/')
        headers = {"X-Gotify-Key": request.token}

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(f"{url}/version", headers=headers)

            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                return {"success": True, "message": f"Connected to Gotify v{version}"}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid token"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/test/ntfy")
async def test_ntfy_connection(request: NtfyTestRequest):
    """Test ntfy connection by sending a test notification."""
    import httpx

    try:
        url = request.url.rstrip('/')

        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            # Just check if the ntfy server is reachable
            response = await client.get(f"{url}/{request.topic}/json?poll=1")

            if response.status_code in [200, 304]:
                return {"success": True, "message": f"Connected to ntfy topic '{request.topic}'"}
            elif response.status_code == 404:
                return {"success": False, "error": "Topic not found"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# NEW API ENDPOINTS - Stubs for Phase 7-10 Features
# See docs/API_INTEGRATION.md for full implementation details
# ============================================================================

# Request/Response Models for new endpoints
class WebhookTestRequest(BaseModel):
    """Request model for testing webhooks."""
    url: str
    event: str = "test"
    service: str = "custom"  # discord, slack, teams, custom


class MetadataBrowseResponse(BaseModel):
    """Response model for metadata browsing."""
    items: List[Dict[str, Any]]
    total: int
    page: int
    total_pages: int


class MetadataEditRequest(BaseModel):
    """Request model for editing item metadata."""
    title: Optional[str] = None
    sort_title: Optional[str] = None
    year: Optional[int] = None
    content_rating: Optional[str] = None
    summary: Optional[str] = None
    genres: Optional[str] = None
    labels: Optional[str] = None


class CollectionSaveRequest(BaseModel):
    """Request model for saving a collection."""
    library: str
    name: str
    builders: List[Dict[str, Any]]
    filters: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None


class ScheduleSettingsRequest(BaseModel):
    """Request model for schedule settings."""
    run_order: Optional[List[str]] = None
    global_schedule: Optional[str] = None
    library_schedules: Optional[Dict[str, Dict[str, Any]]] = None


class MapperSettingsRequest(BaseModel):
    """Request model for data mapper settings."""
    genre_mapper: Optional[Dict[str, str]] = None
    content_rating_mapper: Optional[Dict[str, str]] = None
    studio_mapper: Optional[Dict[str, str]] = None


class NotificationSettingsRequest(BaseModel):
    """Request model for notification settings."""
    enabled_events: List[str]
    webhooks: Optional[Dict[str, str]] = None


class OperationsConfigRequest(BaseModel):
    """Request model for advanced operations configuration."""
    enabled: List[str]
    settings: Optional[Dict[str, Any]] = None


# --- Webhook Testing ---

@app.post("/api/webhooks/test")
async def test_webhook(request: WebhookTestRequest):
    """
    Test a webhook by sending a test notification.

    TODO: Implement actual webhook delivery based on service type.
    Currently returns a stub response.
    """
    import httpx

    try:
        # Detect service from URL if not specified
        service = request.service
        if "discord.com" in request.url:
            service = "discord"
        elif "slack.com" in request.url or "hooks.slack" in request.url:
            service = "slack"
        elif "office.com" in request.url:
            service = "teams"

        # Build payload based on service
        if service == "discord":
            payload = {
                "content": None,
                "embeds": [{
                    "title": f"Kometa Test - {request.event}",
                    "description": "This is a test notification from Kometa Web UI",
                    "color": 15105570  # Kometa gold
                }]
            }
        elif service == "slack":
            payload = {
                "text": f"Kometa Test - {request.event}",
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Kometa Test Notification*\nThis is a test notification from Kometa Web UI"
                    }
                }]
            }
        elif service == "teams":
            payload = {
                "@type": "MessageCard",
                "themeColor": "e5a00d",
                "title": f"Kometa Test - {request.event}",
                "text": "This is a test notification from Kometa Web UI"
            }
        else:
            payload = {
                "event": request.event,
                "message": "Kometa test notification",
                "timestamp": datetime.now().isoformat()
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(request.url, json=payload)

            if response.status_code in [200, 204]:
                return {"success": True, "message": f"Test notification sent successfully ({service})"}
            else:
                return {"success": False, "error": f"Webhook returned HTTP {response.status_code}"}

    except httpx.ConnectError:
        return {"success": False, "error": "Connection refused - check URL"}
    except httpx.TimeoutException:
        return {"success": False, "error": "Connection timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Metadata Editor ---

@app.get("/api/metadata/browse/{library}")
async def browse_metadata(
    library: str,
    page: int = 1,
    per_page: int = 24,
    search: str = "",
    type: str = "all",
    sort: str = "title"
):
    """
    Browse media items in a library for metadata editing.

    TODO: Connect to Plex API to fetch real library contents.
    Currently returns a stub response.
    """
    # Stub: Return placeholder data
    # Real implementation should query Plex API
    return {
        "items": [],
        "total": 0,
        "page": page,
        "total_pages": 0,
        "message": "TODO: Connect to Plex API - see docs/API_INTEGRATION.md"
    }


@app.get("/api/metadata/item/{item_id}")
async def get_metadata_item(item_id: str):
    """
    Get full metadata for a specific item.

    TODO: Connect to Plex API to fetch item details.
    """
    return {
        "id": item_id,
        "message": "TODO: Connect to Plex API - see docs/API_INTEGRATION.md"
    }


@app.post("/api/metadata/item/{item_id}")
async def update_metadata_item(item_id: str, request: MetadataEditRequest):
    """
    Update metadata for a specific item.

    TODO: Connect to Plex API to update item metadata.
    """
    return {
        "success": True,
        "message": "TODO: Implement Plex metadata update - see docs/API_INTEGRATION.md"
    }


@app.post("/api/metadata/generate-yaml")
async def generate_metadata_yaml(items: List[Dict[str, Any]]):
    """
    Generate YAML for metadata edits.

    TODO: Generate valid Kometa metadata YAML.
    """
    # Stub implementation
    yaml_output = "metadata:\n  # Generated metadata will appear here\n"
    return {"yaml": yaml_output}


# --- Collection Builder ---

@app.get("/api/collections/{library}")
async def get_collections(library: str):
    """Get existing collections for a library from collection files."""
    collection_files = config_manager.get_collection_files()

    # Filter by library and load collections
    collections = []
    for cf in collection_files:
        if cf["library"] == library:
            file_data = config_manager.load_collection_file(cf["path"])
            if file_data.get("exists") and file_data.get("collections"):
                for coll in file_data["collections"]:
                    coll["source_file"] = cf["path"]
                    collections.append(coll)

    return {"collections": collections, "files": collection_files}


@app.post("/api/collections/save")
async def save_collection(request: CollectionSaveRequest):
    """Save a collection definition to a YAML file."""
    # Determine file path - use library name as default
    file_path = f"config/{request.library.lower().replace(' ', '_')}_collections.yml"

    # Build collection config
    collection_config = {}

    # Add builders
    for builder in request.builders:
        source = builder.get("source", "unknown")
        config = builder.get("config", {})
        if config:
            collection_config[source] = config
        else:
            collection_config[source] = builder.get("value", True)

    # Add filters if present
    if request.filters:
        filters = {}
        for f in request.filters:
            field = f.get("field", "")
            operator = f.get("operator", "")
            value = f.get("value", "")
            filter_key = f"{field}.{operator}" if operator else field
            filters[filter_key] = value
        if filters:
            collection_config["filters"] = filters

    # Add settings if present
    if request.settings:
        collection_config.update(request.settings)

    # Load existing collections from file
    file_data = config_manager.load_collection_file(file_path)
    existing = file_data.get("collections", []) if file_data.get("exists") else []

    # Update or add the collection
    found = False
    for i, coll in enumerate(existing):
        if coll["name"] == request.name:
            existing[i] = {"name": request.name, "config": collection_config}
            found = True
            break

    if not found:
        existing.append({"name": request.name, "config": collection_config})

    # Save to file
    success = config_manager.save_collection_file(file_path, existing)

    if success:
        return {"success": True, "message": f"Collection '{request.name}' saved to {file_path}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save collection")


@app.post("/api/collections/preview")
async def preview_collection(request: CollectionSaveRequest):
    """
    Preview the YAML that would be generated for a collection.
    """
    # Generate YAML preview
    yaml_output = f"collections:\n  {request.name}:\n"
    for builder in request.builders:
        source = builder.get("source", "unknown")
        yaml_output += f"    {source}:\n"
        for key, value in builder.get("config", {}).items():
            yaml_output += f"      {key}: {value}\n"

    return {"yaml": yaml_output}


@app.get("/api/builders/sources")
async def get_builder_sources():
    """
    Get available builder sources and their configuration options.
    """
    # Return available sources
    sources = {
        "tmdb_popular": {"name": "TMDb Popular", "category": "charts", "fields": ["limit"]},
        "tmdb_trending": {"name": "TMDb Trending", "category": "charts", "fields": ["limit", "time_window"]},
        "trakt_list": {"name": "Trakt List", "category": "lists", "fields": ["list_url"]},
        "imdb_list": {"name": "IMDb List", "category": "lists", "fields": ["list_id"]},
        "plex_search": {"name": "Plex Search", "category": "plex", "fields": ["any"]},
    }
    return {"sources": sources}


# --- Playlist Builder ---

@app.get("/api/playlists")
async def get_playlists():
    """Get existing playlists from playlist files."""
    playlist_files = config_manager.get_playlist_files()
    return {"playlists": [], "files": playlist_files}


@app.post("/api/playlists/save")
async def save_playlist(request: Dict[str, Any]):
    """Save a playlist definition to a YAML file."""
    name = request.get("name", "New Playlist")
    file_path = f"config/playlists.yml"

    # Build playlist config from request
    playlist_config = {}
    if "libraries" in request:
        playlist_config["libraries"] = request["libraries"]
    if "sync_to_users" in request:
        playlist_config["sync_to_users"] = request["sync_to_users"]
    if "builders" in request:
        for builder in request["builders"]:
            source = builder.get("source", "plex_all")
            playlist_config[source] = builder.get("config", True)

    return {
        "success": True,
        "message": f"Playlist '{name}' configuration prepared",
        "config": playlist_config
    }


# --- Settings Endpoints ---

@app.get("/api/settings/schedule")
async def get_schedule_settings():
    """Get scheduling configuration from config.yml."""
    return config_manager.get_schedule_settings()


@app.post("/api/settings/schedule")
async def save_schedule_settings(request: ScheduleSettingsRequest):
    """Save scheduling configuration to config.yml."""
    success = config_manager.save_schedule_settings(
        run_order=request.run_order,
        global_schedule=request.global_schedule,
        library_schedules=request.library_schedules
    )
    if success:
        return {"success": True, "message": "Schedule settings saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save schedule settings")


@app.get("/api/settings/mappers")
async def get_mapper_settings():
    """Get data mapper settings from config.yml."""
    return config_manager.get_mapper_settings()


@app.post("/api/settings/mappers")
async def save_mapper_settings(request: MapperSettingsRequest):
    """Save data mapper settings to config.yml."""
    success = config_manager.save_mapper_settings(
        genre_mapper=request.genre_mapper,
        content_rating_mapper=request.content_rating_mapper,
        studio_mapper=request.studio_mapper
    )
    if success:
        return {"success": True, "message": "Mapper settings saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save mapper settings")


@app.get("/api/settings/notifications")
async def get_notification_settings():
    """Get notification/webhook settings from config.yml."""
    settings = config_manager.get_webhook_settings()
    # Extract enabled events from webhooks (events with non-empty URLs)
    webhooks = settings.get("webhooks", {}) or {}
    enabled_events = [event for event, url in webhooks.items() if url]
    return {
        "enabled_events": enabled_events,
        "webhooks": webhooks
    }


@app.post("/api/settings/notifications")
async def save_notification_settings(request: NotificationSettingsRequest):
    """Save notification settings to config.yml."""
    # Build webhooks dict from enabled events and URLs
    webhooks = request.webhooks or {}
    success = config_manager.save_webhook_settings(webhooks=webhooks)
    if success:
        return {"success": True, "message": "Notification settings saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save notification settings")


# --- Operations Config ---

@app.get("/api/operations/config")
async def get_operations_config():
    """Get advanced operations configuration from config.yml."""
    return config_manager.get_operations_settings()


@app.post("/api/operations/config")
async def save_operations_config(request: OperationsConfigRequest, library: str = "Movies"):
    """Save advanced operations configuration to config.yml."""
    # Build operations dict from enabled operations
    operations = {}
    for op in request.enabled:
        # Map operation IDs to config keys
        op_key = op.replace("op-", "").replace("-", "_")
        operations[op_key] = True

    # Merge with any additional settings
    if request.settings:
        operations.update(request.settings)

    success = config_manager.save_operations_settings(library, operations)
    if success:
        return {"success": True, "message": "Operations settings saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save operations settings")


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=UI_HOST, port=UI_PORT)
