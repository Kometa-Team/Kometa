"""
Config Manager for Kometa Web UI

Handles YAML parsing, validation, backups, and run plan generation.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError


class ConfigManager:
    """Manages Kometa configuration files."""

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.config_path = self.config_dir / "config.yml"
        self.backup_dir = self.config_dir / "backups"

        # Initialize ruamel.yaml with comment preservation
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 100000  # Prevent line wrapping
        self.yaml.indent(mapping=2, sequence=2, offset=2)

    def load_config(self) -> Dict[str, Any]:
        """Load and parse config.yml."""
        if not self.config_path.exists():
            return {
                "exists": False,
                "content": "",
                "parsed": None,
                "validation": {"valid": False, "errors": ["Config file not found"]}
            }

        content = self.config_path.read_text(encoding="utf-8")

        # Parse YAML
        parsed = None
        validation = self.validate_yaml(content)

        if validation["valid"]:
            try:
                from io import StringIO
                parsed = self.yaml.load(StringIO(content))
            except Exception as e:
                parsed = None

        return {
            "exists": True,
            "content": content,
            "parsed": self._serialize_for_json(parsed) if parsed else None,
            "validation": validation
        }

    def save_config(self, content: str) -> Dict[str, Any]:
        """Save config.yml with automatic backup."""
        # Validate first
        validation = self.validate_yaml(content)

        # Create backup of existing config
        backup_path = None
        if self.config_path.exists():
            backup_path = self._create_backup()

        # Save new config
        self.config_path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "backup_path": str(backup_path) if backup_path else None,
            "validation": validation
        }

    def validate_yaml(self, content: str) -> Dict[str, Any]:
        """Validate YAML content without saving."""
        errors = []
        warnings = []

        # Check if empty
        if not content or not content.strip():
            return {
                "valid": False,
                "errors": ["Config is empty"],
                "warnings": []
            }

        # Try to parse YAML
        try:
            from io import StringIO
            parsed = self.yaml.load(StringIO(content))
        except YAMLError as e:
            return {
                "valid": False,
                "errors": [f"YAML syntax error: {str(e)}"],
                "warnings": []
            }

        if parsed is None:
            return {
                "valid": False,
                "errors": ["Config is empty or invalid"],
                "warnings": []
            }

        # Validate structure
        if not isinstance(parsed, dict):
            return {
                "valid": False,
                "errors": ["Config must be a YAML mapping (dictionary)"],
                "warnings": []
            }

        # Check for required sections
        if "libraries" not in parsed:
            warnings.append("No 'libraries' section found - Kometa won't process any libraries")

        # Validate plex section if present
        if "plex" in parsed:
            plex = parsed["plex"]
            if isinstance(plex, dict):
                if "url" not in plex:
                    errors.append("plex.url is required")
                if "token" not in plex:
                    errors.append("plex.token is required")
        else:
            warnings.append("No 'plex' section found")

        # Validate libraries section
        if "libraries" in parsed and parsed["libraries"]:
            libraries = parsed["libraries"]
            if isinstance(libraries, dict):
                for lib_name, lib_config in libraries.items():
                    if lib_config is None:
                        warnings.append(f"Library '{lib_name}' has no configuration")
                    elif isinstance(lib_config, dict):
                        # Check for at least one content file
                        has_content = any(
                            key in lib_config
                            for key in ["collection_files", "metadata_files", "overlay_files", "operations"]
                        )
                        if not has_content:
                            warnings.append(f"Library '{lib_name}' has no collection, metadata, or overlay files")

        # Validate TMDb if present
        if "tmdb" in parsed:
            tmdb = parsed["tmdb"]
            if isinstance(tmdb, dict):
                if "apikey" not in tmdb:
                    warnings.append("tmdb.apikey not set - TMDb features will be limited")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "sections_found": list(parsed.keys()) if isinstance(parsed, dict) else []
        }

    def _create_backup(self) -> Path:
        """Create a timestamped backup of the current config."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"config.yml.{timestamp}"
        backup_path = self.backup_dir / backup_name

        # Copy current config to backup
        content = self.config_path.read_text(encoding="utf-8")
        backup_path.write_text(content, encoding="utf-8")

        return backup_path

    def list_backups(self) -> List[Dict[str, Any]]:
        """List available config backups."""
        backups = []

        if not self.backup_dir.exists():
            return backups

        for backup_file in sorted(self.backup_dir.glob("config.yml.*"), reverse=True):
            stat = backup_file.stat()
            backups.append({
                "name": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return backups

    def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """Restore config from a backup."""
        backup_path = self.backup_dir / backup_name

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")

        # Create backup of current config before restoring
        if self.config_path.exists():
            self._create_backup()

        # Restore
        content = backup_path.read_text(encoding="utf-8")
        self.config_path.write_text(content, encoding="utf-8")

        return {"restored_from": backup_name}

    def generate_run_plan(self) -> Dict[str, Any]:
        """Generate a run plan preview based on current config."""
        plan = {
            "valid": False,
            "libraries": [],
            "collection_files": [],
            "metadata_files": [],
            "overlay_files": [],
            "integrations": {},
            "paths": {},
            "warnings": []
        }

        if not self.config_path.exists():
            plan["warnings"].append("No config.yml found")
            return plan

        try:
            from io import StringIO
            content = self.config_path.read_text(encoding="utf-8")
            config = self.yaml.load(StringIO(content))
        except Exception as e:
            plan["warnings"].append(f"Failed to parse config: {e}")
            return plan

        if not config:
            plan["warnings"].append("Config is empty")
            return plan

        plan["valid"] = True

        # Extract libraries
        if "libraries" in config and config["libraries"]:
            for lib_name, lib_config in config["libraries"].items():
                lib_info = {"name": lib_name, "files": []}

                if lib_config and isinstance(lib_config, dict):
                    # Collection files
                    if "collection_files" in lib_config:
                        files = lib_config["collection_files"]
                        if isinstance(files, list):
                            for f in files:
                                if isinstance(f, str):
                                    lib_info["files"].append({"type": "collection", "path": f})
                                    plan["collection_files"].append(f)
                                elif isinstance(f, dict) and "file" in f:
                                    lib_info["files"].append({"type": "collection", "path": f["file"]})
                                    plan["collection_files"].append(f["file"])

                    # Metadata files
                    if "metadata_files" in lib_config:
                        files = lib_config["metadata_files"]
                        if isinstance(files, list):
                            for f in files:
                                if isinstance(f, str):
                                    lib_info["files"].append({"type": "metadata", "path": f})
                                    plan["metadata_files"].append(f)
                                elif isinstance(f, dict) and "file" in f:
                                    lib_info["files"].append({"type": "metadata", "path": f["file"]})
                                    plan["metadata_files"].append(f["file"])

                    # Overlay files
                    if "overlay_files" in lib_config:
                        files = lib_config["overlay_files"]
                        if isinstance(files, list):
                            for f in files:
                                if isinstance(f, str):
                                    lib_info["files"].append({"type": "overlay", "path": f})
                                    plan["overlay_files"].append(f)
                                elif isinstance(f, dict) and "file" in f:
                                    lib_info["files"].append({"type": "overlay", "path": f["file"]})
                                    plan["overlay_files"].append(f["file"])

                plan["libraries"].append(lib_info)

        # Extract integrations
        integration_keys = ["tmdb", "trakt", "mal", "anidb", "radarr", "sonarr", "tautulli", "webhooks"]
        for key in integration_keys:
            if key in config and config[key]:
                int_config = config[key]
                if isinstance(int_config, dict):
                    # Check if it has required keys (varies by integration)
                    has_config = bool(int_config)
                    plan["integrations"][key] = {
                        "configured": has_config,
                        "details": self._summarize_integration(key, int_config)
                    }
                else:
                    plan["integrations"][key] = {"configured": False}

        # Extract paths
        plan["paths"]["config"] = str(self.config_path)
        plan["paths"]["logs"] = str(self.config_dir / "logs")

        if "settings" in config and config["settings"]:
            settings = config["settings"]
            if isinstance(settings, dict):
                if "cache" in settings:
                    plan["paths"]["cache"] = settings["cache"]
                if "asset_directory" in settings:
                    plan["paths"]["assets"] = settings["asset_directory"]

        return plan

    def _summarize_integration(self, name: str, config: Dict) -> str:
        """Generate a human-readable summary of an integration."""
        if name == "plex":
            url = config.get("url", "Not set")
            return f"URL: {url}"
        elif name == "tmdb":
            return "API key configured" if "apikey" in config else "API key missing"
        elif name == "trakt":
            return "Configured" if "client_id" in config else "Client ID missing"
        elif name in ["radarr", "sonarr"]:
            url = config.get("url", "Not set")
            return f"URL: {url}"
        else:
            return "Configured"

    def _serialize_for_json(self, obj: Any) -> Any:
        """Convert ruamel.yaml objects to JSON-serializable types."""
        if obj is None:
            return None
        elif isinstance(obj, dict):
            return {str(k): self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_for_json(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        else:
            return str(obj)

    # =========================================================================
    # Settings Management Methods
    # =========================================================================

    def _load_parsed_config(self) -> Optional[Dict]:
        """Load and parse config.yml, returning the parsed dict."""
        if not self.config_path.exists():
            return None
        try:
            from io import StringIO
            content = self.config_path.read_text(encoding="utf-8")
            return self.yaml.load(StringIO(content))
        except Exception:
            return None

    def _save_parsed_config(self, config: Dict) -> bool:
        """Save a parsed config dict back to config.yml with backup."""
        try:
            from io import StringIO
            # Create backup first
            if self.config_path.exists():
                self._create_backup()
            # Write config
            stream = StringIO()
            self.yaml.dump(config, stream)
            self.config_path.write_text(stream.getvalue(), encoding="utf-8")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_schedule_settings(self) -> Dict[str, Any]:
        """Get scheduling settings from config."""
        config = self._load_parsed_config()
        if not config:
            return {
                "run_order": ["operations", "metadata", "collections", "overlays"],
                "global_schedule": None,
                "library_schedules": {}
            }

        settings = config.get("settings", {}) or {}
        libraries = config.get("libraries", {}) or {}

        # Extract library schedules
        library_schedules = {}
        for lib_name, lib_config in libraries.items():
            if lib_config and isinstance(lib_config, dict):
                lib_schedule = {}
                if "schedule" in lib_config:
                    lib_schedule["schedule"] = lib_config["schedule"]
                if "schedule_overlays" in lib_config:
                    lib_schedule["schedule_overlays"] = lib_config["schedule_overlays"]
                if lib_schedule:
                    library_schedules[lib_name] = lib_schedule

        return {
            "run_order": settings.get("run_order", ["operations", "metadata", "collections", "overlays"]),
            "global_schedule": settings.get("schedule"),
            "library_schedules": library_schedules
        }

    def save_schedule_settings(self, run_order: List[str] = None,
                                global_schedule: str = None,
                                library_schedules: Dict = None) -> bool:
        """Save scheduling settings to config."""
        config = self._load_parsed_config()
        if not config:
            config = {}

        # Ensure settings section exists
        if "settings" not in config:
            config["settings"] = {}

        if run_order is not None:
            config["settings"]["run_order"] = run_order

        if global_schedule is not None:
            config["settings"]["schedule"] = global_schedule

        # Update library schedules
        if library_schedules is not None and "libraries" in config:
            for lib_name, schedule_config in library_schedules.items():
                if lib_name in config["libraries"]:
                    if config["libraries"][lib_name] is None:
                        config["libraries"][lib_name] = {}
                    for key, value in schedule_config.items():
                        config["libraries"][lib_name][key] = value

        return self._save_parsed_config(config)

    def get_mapper_settings(self) -> Dict[str, Any]:
        """Get data mapper settings from config."""
        config = self._load_parsed_config()
        if not config:
            return {
                "genre_mapper": {},
                "content_rating_mapper": {},
                "studio_mapper": {}
            }

        settings = config.get("settings", {}) or {}

        return {
            "genre_mapper": self._serialize_for_json(settings.get("genre_mapper", {})) or {},
            "content_rating_mapper": self._serialize_for_json(settings.get("content_rating_mapper", {})) or {},
            "studio_mapper": self._serialize_for_json(settings.get("studio_mapper", {})) or {}
        }

    def save_mapper_settings(self, genre_mapper: Dict = None,
                              content_rating_mapper: Dict = None,
                              studio_mapper: Dict = None) -> bool:
        """Save data mapper settings to config."""
        config = self._load_parsed_config()
        if not config:
            config = {}

        if "settings" not in config:
            config["settings"] = {}

        if genre_mapper is not None:
            if genre_mapper:
                config["settings"]["genre_mapper"] = genre_mapper
            elif "genre_mapper" in config["settings"]:
                del config["settings"]["genre_mapper"]

        if content_rating_mapper is not None:
            if content_rating_mapper:
                config["settings"]["content_rating_mapper"] = content_rating_mapper
            elif "content_rating_mapper" in config["settings"]:
                del config["settings"]["content_rating_mapper"]

        if studio_mapper is not None:
            if studio_mapper:
                config["settings"]["studio_mapper"] = studio_mapper
            elif "studio_mapper" in config["settings"]:
                del config["settings"]["studio_mapper"]

        return self._save_parsed_config(config)

    def get_webhook_settings(self) -> Dict[str, Any]:
        """Get webhook/notification settings from config."""
        config = self._load_parsed_config()
        if not config:
            return {"webhooks": {}, "notifiarr": None, "gotify": None}

        webhooks = config.get("webhooks", {}) or {}

        return {
            "webhooks": self._serialize_for_json(webhooks),
            "notifiarr": self._serialize_for_json(config.get("notifiarr")),
            "gotify": self._serialize_for_json(config.get("gotify"))
        }

    def save_webhook_settings(self, webhooks: Dict = None) -> bool:
        """Save webhook settings to config."""
        config = self._load_parsed_config()
        if not config:
            config = {}

        if webhooks is not None:
            if webhooks:
                config["webhooks"] = webhooks
            elif "webhooks" in config:
                del config["webhooks"]

        return self._save_parsed_config(config)

    def get_operations_settings(self) -> Dict[str, Any]:
        """Get operations settings from libraries."""
        config = self._load_parsed_config()
        if not config:
            return {"operations": {}}

        # Operations can be at library level or in settings
        settings = config.get("settings", {}) or {}
        libraries = config.get("libraries", {}) or {}

        # Get global operations from settings if any
        global_ops = {}

        # Get per-library operations
        library_ops = {}
        for lib_name, lib_config in libraries.items():
            if lib_config and isinstance(lib_config, dict) and "operations" in lib_config:
                library_ops[lib_name] = self._serialize_for_json(lib_config["operations"])

        return {
            "global_operations": global_ops,
            "library_operations": library_ops,
            "settings": self._serialize_for_json(settings)
        }

    def save_operations_settings(self, library_name: str, operations: Dict) -> bool:
        """Save operations settings for a specific library."""
        config = self._load_parsed_config()
        if not config:
            config = {}

        if "libraries" not in config:
            config["libraries"] = {}

        if library_name not in config["libraries"]:
            config["libraries"][library_name] = {}

        if config["libraries"][library_name] is None:
            config["libraries"][library_name] = {}

        if operations:
            config["libraries"][library_name]["operations"] = operations
        elif "operations" in config["libraries"][library_name]:
            del config["libraries"][library_name]["operations"]

        return self._save_parsed_config(config)

    # =========================================================================
    # Collection/Playlist File Management
    # =========================================================================

    def get_collection_files(self) -> List[Dict[str, Any]]:
        """Get list of collection files referenced in config."""
        config = self._load_parsed_config()
        if not config:
            return []

        collection_files = []
        libraries = config.get("libraries", {}) or {}

        for lib_name, lib_config in libraries.items():
            if lib_config and isinstance(lib_config, dict):
                files = lib_config.get("collection_files", [])
                if isinstance(files, list):
                    for f in files:
                        if isinstance(f, str):
                            collection_files.append({
                                "library": lib_name,
                                "path": f,
                                "file_path": self._resolve_path(f)
                            })
                        elif isinstance(f, dict) and "file" in f:
                            collection_files.append({
                                "library": lib_name,
                                "path": f["file"],
                                "file_path": self._resolve_path(f["file"]),
                                "template_variables": f.get("template_variables", {})
                            })

        return collection_files

    def _resolve_path(self, path: str) -> str:
        """Resolve a config path to absolute path."""
        if path.startswith("/"):
            return path
        if path.startswith("config/"):
            return str(self.config_dir / path[7:])
        return str(self.config_dir / path)

    def load_collection_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse a collection file."""
        resolved_path = Path(self._resolve_path(file_path))

        if not resolved_path.exists():
            return {"exists": False, "collections": [], "error": "File not found"}

        try:
            from io import StringIO
            content = resolved_path.read_text(encoding="utf-8")
            parsed = self.yaml.load(StringIO(content))

            collections = []
            if parsed and "collections" in parsed:
                for name, config in parsed["collections"].items():
                    collections.append({
                        "name": name,
                        "config": self._serialize_for_json(config)
                    })

            return {
                "exists": True,
                "path": str(resolved_path),
                "collections": collections,
                "raw_content": content
            }
        except Exception as e:
            return {"exists": True, "collections": [], "error": str(e)}

    def save_collection_file(self, file_path: str, collections: List[Dict]) -> bool:
        """Save collections to a YAML file."""
        resolved_path = Path(self._resolve_path(file_path))

        # Ensure directory exists
        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        # Build collections dict
        collections_dict = {}
        for coll in collections:
            collections_dict[coll["name"]] = coll.get("config", {})

        # Write file
        try:
            from io import StringIO
            stream = StringIO()
            self.yaml.dump({"collections": collections_dict}, stream)
            resolved_path.write_text(stream.getvalue(), encoding="utf-8")
            return True
        except Exception as e:
            print(f"Error saving collection file: {e}")
            return False

    def get_playlist_files(self) -> List[Dict[str, Any]]:
        """Get list of playlist files referenced in config."""
        config = self._load_parsed_config()
        if not config:
            return []

        playlist_files = []
        libraries = config.get("libraries", {}) or {}

        for lib_name, lib_config in libraries.items():
            if lib_config and isinstance(lib_config, dict):
                files = lib_config.get("playlist_files", [])
                if isinstance(files, list):
                    for f in files:
                        if isinstance(f, str):
                            playlist_files.append({
                                "library": lib_name,
                                "path": f,
                                "file_path": self._resolve_path(f)
                            })
                        elif isinstance(f, dict) and "file" in f:
                            playlist_files.append({
                                "library": lib_name,
                                "path": f["file"],
                                "file_path": self._resolve_path(f["file"])
                            })

        return playlist_files

