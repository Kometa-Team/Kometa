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
