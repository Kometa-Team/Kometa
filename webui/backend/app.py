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
# Main entry point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=UI_HOST, port=UI_PORT)
