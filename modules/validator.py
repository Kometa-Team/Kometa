import glob
import json
import os
import re
from collections import Counter

import ruamel.yaml as ryaml

from modules import util

logger = util.logger


SCHEMA_MAP = {
    "config": "config-schema.json",
    "collection_files": "collection-schema.json",
    "metadata_files": "metadata-schema.json",
    "overlay_files": "overlay-schema.json",
    "playlist_files": "playlist-schema.json",
}

FILE_KEYS = ["collection_files", "metadata_files", "overlay_files", "image_files"]

DEPRECATED_KEYS = {
    "metadata_path": "collection_files / metadata_files",
    "overlay_path": "overlay_files",
}

# Overridable in tests via monkeypatch
_ConfigFile = None


def _get_config_file_class():
    from modules.config import ConfigFile

    return ConfigFile


def _resolve_ref(node, root):
    """Follow a single $ref within the same document."""
    if not isinstance(node, dict) or "$ref" not in node:
        return node
    ref = node["$ref"]
    if not ref.startswith("#/"):
        return node
    result = root
    for part in ref[2:].split("/"):
        result = result.get(part, {}) if isinstance(result, dict) else {}
    return result


def _normalize_gap_path(absolute_path, schema) -> str:
    """Build a gap key, replacing keys reached via additionalProperties with *."""
    parts = []
    current = schema
    for p in absolute_path:
        current = _resolve_ref(current, schema)
        if isinstance(p, int):
            if parts:
                parts[-1] += "[*]"
            current = _resolve_ref(current.get("items", {}), schema)
        else:
            props = current.get("properties", {}) if isinstance(current, dict) else {}
            add_props = current.get("additionalProperties", False) if isinstance(current, dict) else False
            if p in props:
                parts.append(str(p))
                current = _resolve_ref(props[p], schema)
            elif isinstance(add_props, dict):
                parts.append("*")
                current = _resolve_ref(add_props, schema)
            else:
                parts.append(str(p))
                current = {}
    return ".".join(parts)


def detect_schema_type(data: dict) -> str | None:
    """Infer the SCHEMA_MAP key from a YAML file's root keys."""
    if "collections" in data or "dynamic_collections" in data:
        return "collection_files"
    if "overlays" in data:
        return "overlay_files"
    if "playlists" in data:
        return "playlist_files"
    if "metadata" in data:
        return "metadata_files"
    if any(k in data for k in ("libraries", "plex", "tmdb", "settings")):
        return "config"
    return None


def collect_yaml_files(path: str) -> list[str]:
    """Return sorted list of .yml/.yaml files at path (file) or recursively under path (directory)."""
    if os.path.isfile(path):
        return [path]
    result = []
    for root, _dirs, files in os.walk(path):
        for fname in files:
            if fname.endswith(".yml") or fname.endswith(".yaml"):
                result.append(os.path.join(root, fname))
    return sorted(result)


class FileSetValidator:
    """Validate a list of YAML files against auto-detected JSON schemas."""

    def __init__(self, paths: list[str], schema_path: str):
        self.paths = paths
        self.schema_path = schema_path
        self._results: list[dict] = []
        self._aggregate_gaps: dict[str, Counter] = {}
        self._schemas_checked: set[str] = set()

    def validate(self) -> tuple[bool, dict[str, list[str]], dict[str, Counter]]:
        for path in self.paths:
            result = self._process_file(path)
            self._results.append(result)
            if not result["errors"] and not result["skipped"] and result["schema_validated"]:
                self._schemas_checked.add(result["schema_filename"])
                for k, v in result["gaps"].items():
                    self._aggregate_gaps.setdefault(result["schema_filename"], Counter())[k] += v
        self._print_report()
        per_file_errors = {r["path"]: r["errors"] for r in self._results if r["errors"]}
        return len(per_file_errors) == 0, per_file_errors, self._aggregate_gaps

    def _process_file(self, path: str) -> dict:
        result = {
            "path": path,
            "schema_filename": None,
            "errors": [],
            "gaps": Counter(),
            "skipped": False,
            "schema_validated": False,
        }

        try:
            y = ryaml.YAML()
            with open(path, encoding="utf-8") as fp:
                data = y.load(fp)
            data = data if isinstance(data, dict) else {}
        except ryaml.error.YAMLError as e:
            msg = str(e)
            if "found character '\\t'" in msg:
                result["errors"].append("YAML Error: tabs are not allowed, only spaces")
            else:
                result["errors"].append(f"YAML Error: {msg.splitlines()[0]}")
            return result
        except Exception as e:
            result["errors"].append(f"Error loading file: {e}")
            return result

        schema_key = detect_schema_type(data)
        if schema_key is None:
            result["skipped"] = True
            return result

        schema_filename = SCHEMA_MAP.get(schema_key)
        if not schema_filename:
            result["skipped"] = True
            return result

        result["schema_filename"] = schema_filename

        if not self.schema_path or not os.path.isdir(self.schema_path):
            return result

        schema_file = os.path.join(self.schema_path, schema_filename)
        if not os.path.exists(schema_file):
            return result

        try:
            with open(schema_file, encoding="utf-8") as f:
                schema = json.load(f)
        except Exception as e:
            result["errors"].append(f"Could not load {schema_filename}: {e}")
            return result

        import jsonschema

        result["schema_validated"] = True
        schema_validator = jsonschema.Draft6Validator(schema)

        for error in schema_validator.iter_errors(data):
            if error.validator == "additionalProperties":
                props = re.findall(r"'([^']+)'", error.message)
                base = _normalize_gap_path(error.absolute_path, schema)
                for prop in props:
                    key = f"{base}.{prop}" if base else prop
                    result["gaps"][key] += 1
            else:
                path_str = " -> ".join(str(p) for p in error.absolute_path) or "(root)"
                result["errors"].append(f"[{schema_filename}] at {path_str}: {error.message}")

        return result

    def _print_report(self) -> None:
        sep = "=" * 62
        total = len(self.paths)
        skipped = sum(1 for r in self._results if r["skipped"])
        error_files = sum(1 for r in self._results if r["errors"])
        passing_files = total - skipped - error_files
        total_gap_keys = sum(len(c) for c in self._aggregate_gaps.values())

        for result in self._results:
            if not result["errors"]:
                continue
            logger.info("")
            logger.info(sep)
            logger.info(f" File: {result['path']}")
            if result["schema_filename"]:
                logger.info(f" Schema: {result['schema_filename']}")
            logger.info(f" Errors ({len(result['errors'])}):")
            for e in result["errors"]:
                logger.error(f"   {e}")

        if self._aggregate_gaps:
            logger.info("")
            logger.info(sep)
            logger.info(f" Schema Gap Report (across {passing_files} passing file(s))")
            logger.info(sep)
            logger.info(" Keys found in your files that are not in the schema:")
            for schema_filename, counter in self._aggregate_gaps.items():
                logger.info("")
                logger.info(f" {schema_filename}:")
                for gap_key, count in counter.most_common():
                    noun = "files" if count > 1 else "file"
                    logger.info(f"   - {gap_key}  (seen in {count} {noun})")
            clean = [s for s in self._schemas_checked if s not in self._aggregate_gaps]
            if clean:
                logger.info("")
                logger.info(f" No gaps in: {', '.join(s.replace('-schema.json', '') for s in clean)}")

        logger.info("")
        logger.info(sep)
        logger.info(f" Summary: {total} files checked, {skipped} skipped (unknown type), {error_files} with errors, {total_gap_keys} schema gap(s) found")
        logger.info(f" Result: {'FAILED' if error_files else 'PASSED'}")
        logger.info(sep)
        logger.info("")


class ConfigValidator:
    def __init__(self, requests, default_dir, attrs, secret_args, level="structure", validate_schema=False, schema_path=None):
        self.requests = requests
        self.default_dir = default_dir
        self.attrs = attrs
        self.secret_args = secret_args
        self.level = level
        self.validate_schema = validate_schema
        self.schema_path = schema_path
        self._errors = []
        self._warnings = []
        self._schema_gaps = {}
        self._files_for_schema = []
        self._schemas_checked = set()
        self._config_data = None

        config_file = attrs.get("config_file")
        if config_file and os.path.exists(config_file):
            self.config_path = os.path.abspath(config_file)
        elif os.path.exists(os.path.join(default_dir, "config.yml")):
            self.config_path = os.path.abspath(os.path.join(default_dir, "config.yml"))
        else:
            from modules.util import Failed

            raise Failed(f"Config Error: config.yml not found in {default_dir}")

    def validate(self) -> tuple[bool, list[str], list[str]]:
        if self.level == "syntax":
            self._validate_syntax()
        elif self.level == "structure":
            self._validate_structure()
        elif self.level == "full":
            self._validate_full()

        if self.validate_schema:
            self._run_schema_validation()

        self._print_report()
        return len(self._errors) == 0, self._errors, self._warnings

    def _load_yaml(self, path, label):
        """Load a YAML file; add to self._errors on failure. Returns dict or None."""
        try:
            y = ryaml.YAML()
            with open(path, encoding="utf-8") as fp:
                data = y.load(fp)
            return data if isinstance(data, dict) else {}
        except ryaml.error.YAMLError as e:
            msg = str(e)
            if "found character '\\t'" in msg:
                self._errors.append(f"{label}: YAML Error: tabs are not allowed, only spaces")
            else:
                self._errors.append(f"{label}: YAML Error: {msg.splitlines()[0]}")
            return None
        except Exception as e:
            self._errors.append(f"{label}: Error loading file: {e}")
            return None

    def _iter_local_paths(self, file_list):
        """Yield (path, desc) for local file/folder entries; skip url/git/default/repo."""
        if not file_list:
            return
        entries = file_list if isinstance(file_list, list) else [file_list]
        for entry in entries:
            if isinstance(entry, str):
                yield entry, entry
            elif isinstance(entry, dict):
                if entry.get("file"):
                    yield entry["file"], f"file: {entry['file']}"
                if entry.get("folder") and os.path.isdir(entry["folder"]):
                    for yml in glob.glob(os.path.join(entry["folder"], "*.yml")) + glob.glob(os.path.join(entry["folder"], "*.yaml")):
                        yield yml, f"folder: {yml}"

    def _resolve_path(self, path):
        """Resolve a relative path the same way Kometa does: CWD-relative first, then config-dir-relative."""
        if os.path.isabs(path):
            return path
        cwd_path = os.path.abspath(path)
        if os.path.exists(cwd_path):
            return cwd_path
        default_path = os.path.join(self.default_dir, path)
        if os.path.exists(default_path):
            return default_path
        return cwd_path

    def _collect_linked_files(self, config_data):
        """Load all local YAML files referenced in libraries and playlist_files."""
        for lib_name, lib_data in (config_data.get("libraries") or {}).items():
            if not isinstance(lib_data, dict):
                continue
            for key in FILE_KEYS:
                for raw_path, _ in self._iter_local_paths(lib_data.get(key)):
                    path = self._resolve_path(raw_path)
                    if not os.path.exists(path):
                        continue
                    label = f"library '{lib_name}' {key}: {os.path.basename(path)}"
                    file_data = self._load_yaml(path, label)
                    if file_data is not None and self.validate_schema and key != "image_files":
                        self._files_for_schema.append((file_data, key, label))

        for raw_path, _ in self._iter_local_paths(config_data.get("playlist_files")):
            path = self._resolve_path(raw_path)
            if not os.path.exists(path):
                continue
            label = f"playlist_files: {os.path.basename(path)}"
            file_data = self._load_yaml(path, label)
            if file_data is not None and self.validate_schema:
                self._files_for_schema.append((file_data, "playlist_files", label))

    def _validate_syntax(self):
        """Load config.yml and all local linked YAML files; collect parse errors."""
        self._config_data = self._load_yaml(self.config_path, "config.yml")
        if self._config_data is None:
            return
        if self.validate_schema:
            self._files_for_schema.append((self._config_data, "config", "config.yml"))
        self._collect_linked_files(self._config_data)

    def _validate_structure(self):
        """Syntax checks + structural validation."""
        self._validate_syntax()
        if self._config_data is None:
            return

        data = self._config_data

        if not data.get("libraries"):
            self._warnings.append("config.yml: 'libraries' key is missing or empty")
        if "tmdb" not in data:
            self._warnings.append("config.yml: 'tmdb' key not found — TMDb features will be unavailable")

        for lib_name, lib_data in (data.get("libraries") or {}).items():
            if not isinstance(lib_data, dict):
                continue

            for old_key, replacement in DEPRECATED_KEYS.items():
                if old_key in lib_data:
                    self._warnings.append(f"library '{lib_name}': '{old_key}' is deprecated, use '{replacement}'")

            if not any(lib_data.get(k) for k in FILE_KEYS + ["operations"]):
                self._warnings.append(f"library '{lib_name}': no collection_files, metadata_files, overlay_files, image_files, or operations defined")

            for key in FILE_KEYS:
                for raw_path, _ in self._iter_local_paths(lib_data.get(key)):
                    path = self._resolve_path(raw_path)
                    if not os.path.exists(path):
                        self._errors.append(f"library '{lib_name}' {key}: path not found: {path}")

        for raw_path, _ in self._iter_local_paths(data.get("playlist_files")):
            path = self._resolve_path(raw_path)
            if not os.path.exists(path):
                self._errors.append(f"playlist_files: path not found: {path}")

    def _validate_full(self):
        """Run full ConfigFile initialisation (connects to Plex/APIs). Does not call run_config()."""
        if self.validate_schema:
            self._config_data = self._load_yaml(self.config_path, "config.yml")
            if self._config_data is not None:
                self._files_for_schema.append((self._config_data, "config", "config.yml"))
                self._collect_linked_files(self._config_data)
        try:
            cls = _ConfigFile if _ConfigFile is not None else _get_config_file_class()
            cls(self.requests, self.default_dir, self.attrs, self.secret_args)
        except Exception as e:
            self._errors.append(f"Full validation error: {e}")

    def _run_schema_validation(self):
        """Validate collected files against JSON schemas; populate _schema_gaps."""
        import jsonschema

        if not self.schema_path or not os.path.isdir(self.schema_path):
            self._warnings.append(f"Schema directory not found, skipping schema validation: {self.schema_path}")
            return

        for data, schema_key, label in self._files_for_schema:
            schema_filename = SCHEMA_MAP.get(schema_key)
            if not schema_filename:
                continue
            schema_file = os.path.join(self.schema_path, schema_filename)
            if not os.path.exists(schema_file):
                self._warnings.append(f"Schema file not found, skipping: {schema_file}")
                continue
            try:
                with open(schema_file, encoding="utf-8") as f:
                    schema = json.load(f)
            except Exception as e:
                self._warnings.append(f"Could not load {schema_filename}: {e}")
                continue

            self._schemas_checked.add(schema_filename)
            schema_validator = jsonschema.Draft6Validator(schema)
            for error in schema_validator.iter_errors(data):
                if error.validator == "additionalProperties":
                    props = re.findall(r"'([^']+)'", error.message)
                    base = _normalize_gap_path(error.absolute_path, schema)
                    counter = self._schema_gaps.setdefault(schema_filename, Counter())
                    for prop in props:
                        key = f"{base}.{prop}" if base else prop
                        counter[key] += 1
                else:
                    path_str = " -> ".join(str(p) for p in error.absolute_path) or "(root)"
                    self._errors.append(f"{label} [{schema_filename}] at {path_str}: {error.message}")

    def _print_report(self):
        sep = "=" * 62
        logger.info("")
        logger.info(sep)
        label = f"{self.level}+schema" if self.validate_schema else self.level
        logger.info(f" Validation Report ({label})")
        logger.info(sep)
        logger.info(f" Config: {self.config_path}")
        if self._warnings:
            logger.info("")
            logger.info(f" Warnings ({len(self._warnings)}):")
            for w in self._warnings:
                logger.warning(f"   {w}")
        if self._errors:
            logger.info("")
            logger.info(f" Errors ({len(self._errors)}):")
            for e in self._errors:
                logger.error(f"   {e}")
        if self.validate_schema and self._schema_gaps:
            logger.info("")
            logger.info(sep)
            logger.info(" Schema Gap Report")
            logger.info(sep)
            logger.info(" Keys found in your files that are not in the schema:")
            for schema_filename, counter in self._schema_gaps.items():
                logger.info("")
                logger.info(f" {schema_filename}:")
                for gap_key, count in counter.most_common():
                    noun = "files" if count > 1 else "file"
                    logger.info(f"   - {gap_key}  (seen in {count} {noun})")
            clean = [s for s in self._schemas_checked if s not in self._schema_gaps]
            if clean:
                logger.info("")
                logger.info(f" No gaps in: {', '.join(s.replace('-schema.json', '') for s in clean)}")
        logger.info("")
        logger.info(sep)
        suffix = f" with {len(self._warnings)} warning(s)" if self._warnings else ""
        result = "FAILED" if self._errors else f"PASSED{suffix}"
        logger.info(f" Result: {result}")
        logger.info(sep)
        logger.info("")
