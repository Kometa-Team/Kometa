import glob
import os

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
        """Resolve a possibly-relative path against default_dir."""
        if os.path.isabs(path):
            return path
        return os.path.join(self.default_dir, path)

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
        raise NotImplementedError

    def _run_schema_validation(self):
        raise NotImplementedError

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
        logger.info("")
        logger.info(sep)
        result = "FAILED" if self._errors else ("PASSED" + (f" with {len(self._warnings)} warning(s)" if self._warnings else ""))
        logger.info(f" Result: {result}")
        logger.info(sep)
        logger.info("")
