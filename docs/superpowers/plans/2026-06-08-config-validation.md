# Config Validation Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `--validate` / `--validate-schema` runtime flags that parse and validate `config.yml` and all linked YAML files, then exit with a structured report and gap analysis for JSON schema authoring.

**Architecture:** A new `modules/validator.py` houses a `ConfigValidator` class with three depth levels (syntax, structure, full) and an optional JSON schema pass. `kometa.py` gains four new CLI flags and a short-circuit branch in `start()` that calls the validator and exits without running collections.

**Tech Stack:** Python 3.10+, `ruamel.yaml` (already a dependency), `jsonschema==4.26.0` (new), `pytest` (existing test runner).

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `modules/validator.py` | `ConfigValidator` class — all validation logic |
| Create | `tests/test_validator.py` | pytest tests for all validator behaviour |
| Modify | `kometa.py` (lines 66–96, 429–431) | Add 4 CLI flags; add validation branch in `start()` |
| Modify | `requirements.txt` | Add `jsonschema==4.26.0` |

---

## Task 1: Add jsonschema dependency

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add jsonschema to requirements.txt**

Insert after the `lxml` line (keep alphabetical order is not required — just add it):

```
jsonschema==4.26.0
```

Full resulting requirements.txt (add the one line):

```
apprise>=1.9.0
arrapi==1.4.14
cloudscraper==1.2.71
letterboxdpy==6.5.5
GitPython==3.1.50
jsonschema==4.26.0
lxml==6.1.1
num2words==0.5.14
packaging==26.2
pathvalidate==3.3.1
pillow==12.2.0
PlexAPI==4.18.1
psutil==7.2.2
python-dateutil==2.9.0.post0
python-dotenv==1.2.2
pywin32==311; sys_platform == 'win32'
requests==2.34.2
ruamel.yaml==0.19.1
schedule==1.2.2
setuptools==82.0.1
tenacity==9.1.4
tmdbapis==1.2.30
```

- [ ] **Step 2: Verify import**

```bash
python3 -c "import jsonschema; from jsonschema import Draft6Validator; print('ok')"
```

Expected output: `ok`

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "feat: add jsonschema dependency for config validation"
```

---

## Task 2: Add CLI flags to kometa.py

**Files:**
- Modify: `kometa.py` (the `arguments` dict, lines 66–96)

- [ ] **Step 1: Add four new entries to the `arguments` dict**

In `kometa.py`, the `arguments` dict ends with `"low-priority"`. Add four new entries **before** the closing `}` of that dict:

```python
    "validate": {"args": ["va", "validate-config"], "type": "bool", "help": "Validate config.yml and all linked YAML files without running"},
    "validate-level": {"args": "vl", "type": "str", "default": "structure", "help": "Validation depth: syntax | structure | full (Default: structure)"},
    "validate-schema": {"args": ["vs", "validate-schemas"], "type": "bool", "help": "Also validate each YAML file against its corresponding JSON schema"},
    "schema-path": {"args": "sp", "type": "str", "default": None, "help": "Path to the json-schema/ directory (default: ./json-schema/ next to kometa.py)"},
```

- [ ] **Step 2: Verify flags appear in --help**

```bash
python3 kometa.py --help | grep -E "validate|schema"
```

Expected: lines for `--validate`, `--validate-level`, `--validate-schema`, `--schema-path`.

- [ ] **Step 3: Commit**

```bash
git add kometa.py
git commit -m "feat: add --validate and --validate-schema CLI flags"
```

---

## Task 3: Write syntax-level tests (TDD — red phase)

**Files:**
- Create: `tests/test_validator.py`

- [ ] **Step 1: Create tests/test_validator.py with a FakeLogger and syntax tests**

```python
import os
import pytest
import modules.validator as validator_module
from modules.validator import ConfigValidator


class FakeLogger:
    def __init__(self):
        self.info_msgs = []
        self.warning_msgs = []
        self.error_msgs = []

    def info(self, msg=""):
        self.info_msgs.append(str(msg))

    def warning(self, msg=""):
        self.warning_msgs.append(str(msg))

    def error(self, msg=""):
        self.error_msgs.append(str(msg))

    def separator(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def make_validator(tmp_path, config_content, level="syntax",
                   validate_schema=False, schema_path=None, extra_files=None):
    """Write config.yml to tmp_path and return a ConfigValidator."""
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content, encoding="utf-8")
    if extra_files:
        for rel_path, content in extra_files.items():
            p = tmp_path / rel_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    attrs = {"config_file": str(config_file)}
    return ConfigValidator(
        requests=None,
        default_dir=str(tmp_path),
        attrs=attrs,
        secret_args={},
        level=level,
        validate_schema=validate_schema,
        schema_path=schema_path,
    )


# ── Syntax tests ──────────────────────────────────────────────────────────────

def test_syntax_valid_config_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "libraries:\n  Movies:\n    collection_files: []\n")
    passed, errors, warnings = v.validate()
    assert passed
    assert errors == []


def test_syntax_invalid_yaml_in_config_reports_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "libraries:\n  bad:\n\tinvalid_tab: true\n")
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("YAML Error" in e for e in errors)


def test_syntax_invalid_yaml_in_linked_file_reports_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - file: collections/bad.yml\n"
    )
    v = make_validator(
        tmp_path, config,
        extra_files={"collections/bad.yml": "key: [\n  unclosed\n"}
    )
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("bad.yml" in e for e in errors)


def test_syntax_missing_linked_file_is_not_an_error_at_syntax_level(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - file: collections/missing.yml\n"
    )
    v = make_validator(tmp_path, config)
    passed, errors, warnings = v.validate()
    assert passed
    assert errors == []


def test_syntax_url_references_are_skipped(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - url: https://example.com/collections.yml\n"
    )
    v = make_validator(tmp_path, config)
    passed, errors, warnings = v.validate()
    assert passed


def test_syntax_git_references_are_skipped(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - git: some/path\n"
    )
    v = make_validator(tmp_path, config)
    passed, errors, warnings = v.validate()
    assert passed


def test_syntax_playlist_files_are_checked(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "playlist_files:\n  - file: playlists/bad.yml\n"
    v = make_validator(
        tmp_path, config,
        extra_files={"playlists/bad.yml": "key: [\n  unclosed\n"}
    )
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("bad.yml" in e for e in errors)
```

- [ ] **Step 2: Run tests — expect FAIL (module not found)**

```bash
pytest tests/test_validator.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'modules.validator'`

---

## Task 4: Implement syntax-level validation (TDD — green phase)

**Files:**
- Create: `modules/validator.py`

- [ ] **Step 1: Create modules/validator.py**

```python
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


class ConfigValidator:
    def __init__(self, requests, default_dir, attrs, secret_args,
                 level="structure", validate_schema=False, schema_path=None):
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
                    for yml in (glob.glob(os.path.join(entry["folder"], "*.yml")) +
                                glob.glob(os.path.join(entry["folder"], "*.yaml"))):
                        yield yml, f"folder: {yml}"

    def _collect_linked_files(self, config_data):
        """Load all local YAML files referenced in libraries and playlist_files."""
        for lib_name, lib_data in (config_data.get("libraries") or {}).items():
            if not isinstance(lib_data, dict):
                continue
            for key in FILE_KEYS:
                for path, _ in self._iter_local_paths(lib_data.get(key)):
                    if not os.path.exists(path):
                        continue
                    label = f"library '{lib_name}' {key}: {os.path.basename(path)}"
                    file_data = self._load_yaml(path, label)
                    if file_data is not None and self.validate_schema and key != "image_files":
                        self._files_for_schema.append((file_data, key, label))

        for path, _ in self._iter_local_paths(config_data.get("playlist_files")):
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
        raise NotImplementedError

    def _validate_full(self):
        raise NotImplementedError

    def _run_schema_validation(self):
        raise NotImplementedError

    def _print_report(self):
        sep = "=" * 62
        logger.info("")
        logger.info(sep)
        label = f"structure+schema" if self.level == "structure" and self.validate_schema else \
                f"{self.level}+schema" if self.validate_schema else self.level
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
```

- [ ] **Step 2: Run syntax tests — expect PASS**

```bash
pytest tests/test_validator.py -v 2>&1 | tail -20
```

Expected: all `test_syntax_*` tests pass.

- [ ] **Step 3: Commit**

```bash
git add modules/validator.py tests/test_validator.py
git commit -m "feat: add ConfigValidator with syntax-level validation"
```

---

## Task 5: Structure-level validation (TDD)

**Files:**
- Modify: `tests/test_validator.py` (add tests)
- Modify: `modules/validator.py` (implement `_validate_structure`)

- [ ] **Step 1: Add structure tests to tests/test_validator.py**

Append to the end of the file:

```python
# ── Structure tests ───────────────────────────────────────────────────────────

def test_structure_missing_libraries_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "tmdb:\n  apikey: abc\n", level="structure")
    passed, errors, warnings = v.validate()
    assert passed
    assert any("libraries" in w for w in warnings)


def test_structure_missing_tmdb_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "libraries:\n  Movies:\n    collection_files: []\n", level="structure")
    passed, errors, warnings = v.validate()
    assert passed
    assert any("tmdb" in w for w in warnings)


def test_structure_deprecated_metadata_path_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    metadata_path:\n"
        "      - file: collections/test.yml\n"
    )
    v = make_validator(tmp_path, config, level="structure")
    passed, errors, warnings = v.validate()
    assert any("metadata_path" in w and "deprecated" in w for w in warnings)


def test_structure_deprecated_overlay_path_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    overlay_path:\n"
        "      - file: overlays/test.yml\n"
    )
    v = make_validator(tmp_path, config, level="structure")
    passed, errors, warnings = v.validate()
    assert any("overlay_path" in w and "deprecated" in w for w in warnings)


def test_structure_missing_file_path_is_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - file: collections/missing.yml\n"
    )
    v = make_validator(tmp_path, config, level="structure")
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("missing.yml" in e and "not found" in e for e in errors)


def test_structure_existing_file_path_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - file: collections/good.yml\n"
    )
    v = make_validator(
        tmp_path, config, level="structure",
        extra_files={"collections/good.yml": "collections:\n  My Collection:\n    tmdb_popular: true\n"}
    )
    passed, errors, warnings = v.validate()
    assert errors == []


def test_structure_library_with_no_content_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = "libraries:\n  Movies:\n    plex:\n      url: http://localhost\n"
    v = make_validator(tmp_path, config, level="structure")
    passed, errors, warnings = v.validate()
    assert any("Movies" in w and "no" in w.lower() for w in warnings)


def test_structure_yaml_error_in_config_is_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(tmp_path, "bad:\n\ttabs: not allowed\n", level="structure")
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("YAML Error" in e for e in errors)
```

- [ ] **Step 2: Run new tests — expect FAIL**

```bash
pytest tests/test_validator.py -k "structure" -v 2>&1 | tail -15
```

Expected: `NotImplementedError`

- [ ] **Step 3: Implement `_validate_structure` in modules/validator.py**

Replace the `raise NotImplementedError` stub for `_validate_structure`:

```python
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
                    self._warnings.append(
                        f"library '{lib_name}': '{old_key}' is deprecated, use '{replacement}'"
                    )

            if not any(lib_data.get(k) for k in FILE_KEYS + ["operations"]):
                self._warnings.append(
                    f"library '{lib_name}': no collection_files, metadata_files, overlay_files, image_files, or operations defined"
                )

            for key in FILE_KEYS:
                for path, _ in self._iter_local_paths(lib_data.get(key)):
                    if not os.path.exists(path):
                        self._errors.append(
                            f"library '{lib_name}' {key}: path not found: {path}"
                        )

        for path, _ in self._iter_local_paths(data.get("playlist_files")):
            if not os.path.exists(path):
                self._errors.append(f"playlist_files: path not found: {path}")
```

- [ ] **Step 4: Run structure tests — expect PASS**

```bash
pytest tests/test_validator.py -v 2>&1 | tail -25
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/validator.py tests/test_validator.py
git commit -m "feat: add structure-level validation"
```

---

## Task 6: Full-level validation (TDD)

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `modules/validator.py`

- [ ] **Step 1: Add full-level tests to tests/test_validator.py**

Append to the end of the file:

```python
# ── Full-level tests ──────────────────────────────────────────────────────────

def test_full_passes_when_config_file_init_succeeds(tmp_path, monkeypatch):
    import modules.validator as vm
    monkeypatch.setattr(vm, "logger", FakeLogger())

    class FakeConfigFile:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(vm, "_ConfigFile", FakeConfigFile)

    v = make_validator(tmp_path, "libraries: {}\n", level="full")
    passed, errors, warnings = v.validate()
    assert passed
    assert errors == []


def test_full_reports_error_when_config_file_init_raises(tmp_path, monkeypatch):
    import modules.validator as vm
    monkeypatch.setattr(vm, "logger", FakeLogger())

    class BadConfigFile:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Plex connection refused")

    monkeypatch.setattr(vm, "_ConfigFile", BadConfigFile)

    v = make_validator(tmp_path, "libraries: {}\n", level="full")
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("Plex connection refused" in e for e in errors)
```

- [ ] **Step 2: Run new tests — expect FAIL**

```bash
pytest tests/test_validator.py -k "full" -v 2>&1 | tail -15
```

Expected: `NotImplementedError`

- [ ] **Step 3: Add `_ConfigFile` alias and implement `_validate_full` in modules/validator.py**

Add this import alias near the top of the file, just after the module-level constants (after `DEPRECATED_KEYS`):

```python
# Alias to allow monkeypatching in tests
def _get_config_file_class():
    from modules.config import ConfigFile
    return ConfigFile

_ConfigFile = None  # set lazily; overridable in tests
```

Then replace the `raise NotImplementedError` stub for `_validate_full`:

```python
    def _validate_full(self):
        """Run full ConfigFile initialisation (connects to Plex/APIs). Does not call run_config()."""
        if self.validate_schema:
            self._config_data = self._load_yaml(self.config_path, "config.yml")
            if self._config_data is not None:
                self._files_for_schema.append((self._config_data, "config", "config.yml"))
        try:
            cls = _ConfigFile if _ConfigFile is not None else _get_config_file_class()
            cls(self.requests, self.default_dir, self.attrs, self.secret_args)
        except Exception as e:
            self._errors.append(f"Full validation error: {e}")
```

- [ ] **Step 4: Run all tests — expect PASS**

```bash
pytest tests/test_validator.py -v 2>&1 | tail -30
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/validator.py tests/test_validator.py
git commit -m "feat: add full-level validation"
```

---

## Task 7: Schema validation and gap report (TDD)

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `modules/validator.py`

- [ ] **Step 1: Add schema validation tests to tests/test_validator.py**

Append to the end of the file. These tests use the real schema files from `json-schema/`:

```python
# ── Schema validation tests ───────────────────────────────────────────────────

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCHEMA_DIR = os.path.join(REPO_ROOT, "json-schema")


def test_schema_valid_collection_file_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - file: collections/good.yml\n"
    )
    collection_content = "collections:\n  My Collection:\n    tmdb_popular: true\n"
    v = make_validator(
        tmp_path, config, level="syntax",
        validate_schema=True, schema_path=SCHEMA_DIR,
        extra_files={"collections/good.yml": collection_content},
    )
    passed, errors, warnings = v.validate()
    assert errors == [], f"Unexpected errors: {errors}"


def test_schema_missing_schema_dir_warns_and_does_not_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    v = make_validator(
        tmp_path, "libraries: {}\n", level="syntax",
        validate_schema=True, schema_path="/nonexistent/schema/dir",
    )
    passed, errors, warnings = v.validate()
    assert passed
    assert any("not found" in w or "Schema" in w for w in warnings)


def test_schema_additionalproperties_violation_goes_to_gap_not_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - file: collections/extra.yml\n"
    )
    # unknown_key_xyz is not in collection-schema.json
    collection_content = "collections:\n  Test:\n    tmdb_popular: true\nunknown_key_xyz: true\n"
    v = make_validator(
        tmp_path, config, level="syntax",
        validate_schema=True, schema_path=SCHEMA_DIR,
        extra_files={"collections/extra.yml": collection_content},
    )
    passed, errors, warnings = v.validate()
    # additionalProperties violations are warnings/gaps, not errors
    assert errors == [], f"additionalProperties should not be in errors: {errors}"
    assert "collection-schema.json" in v._schema_gaps
    assert any("unknown_key_xyz" in k for k in v._schema_gaps["collection-schema.json"])


def test_schema_type_error_is_an_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - file: collections/typed.yml\n"
    )
    # visible is a bool in the schema; passing a list makes it a type error
    collection_content = "collections:\n  Test:\n    tmdb_popular: true\n    visible_home: [not, a, bool]\n"
    v = make_validator(
        tmp_path, config, level="syntax",
        validate_schema=True, schema_path=SCHEMA_DIR,
        extra_files={"collections/typed.yml": collection_content},
    )
    passed, errors, warnings = v.validate()
    assert not passed
    assert any("visible_home" in e or "typed.yml" in e for e in errors)


def test_schema_gap_report_deduplicates_across_files(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    config = (
        "libraries:\n"
        "  Movies:\n"
        "    collection_files:\n"
        "      - file: collections/a.yml\n"
        "      - file: collections/b.yml\n"
    )
    content = "collections:\n  Test:\n    tmdb_popular: true\nunknown_key_xyz: true\n"
    v = make_validator(
        tmp_path, config, level="syntax",
        validate_schema=True, schema_path=SCHEMA_DIR,
        extra_files={"collections/a.yml": content, "collections/b.yml": content},
    )
    v.validate()
    gaps = v._schema_gaps.get("collection-schema.json", Counter())
    assert any("unknown_key_xyz" in k for k in gaps)
    # seen in both files → count is 2
    gap_key = next(k for k in gaps if "unknown_key_xyz" in k)
    assert gaps[gap_key] == 2
```

- [ ] **Step 2: Run schema tests — expect FAIL**

```bash
pytest tests/test_validator.py -k "schema" -v 2>&1 | tail -15
```

Expected: `NotImplementedError` from `_run_schema_validation`.

- [ ] **Step 3: Implement `_run_schema_validation` in modules/validator.py**

Replace the `raise NotImplementedError` stub for `_run_schema_validation`:

```python
    def _run_schema_validation(self):
        """Validate collected files against JSON schemas; populate _schema_gaps."""
        import jsonschema

        if not self.schema_path or not os.path.isdir(self.schema_path):
            self._warnings.append(
                f"Schema directory not found, skipping schema validation: {self.schema_path}"
            )
            return

        for data, schema_key, label in self._files_for_schema:
            schema_filename = SCHEMA_MAP.get(schema_key)
            if not schema_filename:
                continue
            schema_file = os.path.join(self.schema_path, schema_filename)
            if not os.path.exists(schema_file):
                self._warnings.append(f"Schema file not found, skipping: {schema_file}")
                continue
            self._schemas_checked.add(schema_filename)
            try:
                with open(schema_file, encoding="utf-8") as f:
                    schema = json.load(f)
            except Exception as e:
                self._warnings.append(f"Could not load {schema_filename}: {e}")
                continue

            validator_cls = jsonschema.Draft6Validator(schema)
            for error in validator_cls.iter_errors(data):
                if error.validator == "additionalProperties":
                    props = re.findall(r"'([^']+)'", error.message)
                    normalized = []
                    for p in error.absolute_path:
                        if isinstance(p, int):
                            if normalized:
                                normalized[-1] += "[*]"
                        else:
                            normalized.append(str(p))
                    base = ".".join(normalized)
                    counter = self._schema_gaps.setdefault(schema_filename, Counter())
                    for prop in props:
                        key = f"{base}.{prop}" if base else prop
                        counter[key] += 1
                else:
                    path_str = " -> ".join(str(p) for p in error.absolute_path) or "(root)"
                    self._errors.append(
                        f"{label} [{schema_filename}] at {path_str}: {error.message}"
                    )

        # Kitchen sink regression files
        for ks_name in ("kitchen_sink_config.yml", "prototype_config.yml"):
            ks_path = os.path.join(self.schema_path, ks_name)
            if not os.path.exists(ks_path):
                continue
            ks_data = self._load_yaml(ks_path, ks_name)
            if ks_data is None:
                continue
            schema_file = os.path.join(self.schema_path, "config-schema.json")
            if not os.path.exists(schema_file):
                continue
            with open(schema_file, encoding="utf-8") as f:
                schema = json.load(f)
            for error in jsonschema.Draft6Validator(schema).iter_errors(ks_data):
                if error.validator != "additionalProperties":
                    path_str = " -> ".join(str(p) for p in error.absolute_path) or "(root)"
                    self._errors.append(
                        f"{ks_name} [config-schema.json] at {path_str}: {error.message}"
                    )
```

- [ ] **Step 4: Update `_print_report` to include gap report section**

Replace the existing `_print_report` method in `modules/validator.py`:

```python
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
```

- [ ] **Step 5: Run all tests — expect PASS**

```bash
pytest tests/test_validator.py -v 2>&1 | tail -35
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add modules/validator.py tests/test_validator.py
git commit -m "feat: add schema validation and gap report"
```

---

## Task 8: Wire validation into kometa.py start()

**Files:**
- Modify: `kometa.py` (inside `start()`, around line 429–431)

- [ ] **Step 1: Add the validation branch to start()**

In `kometa.py`, locate this exact block (around line 429):

```python
        logger.separator(debug=True)

        logger.separator(f"Starting {start_type}Run")
```

Insert the validation branch between those two lines:

```python
        logger.separator(debug=True)

        if run_args["validate"]:
            level = run_args["validate-level"]
            if level not in ("syntax", "structure", "full"):
                logger.error(f"--validate-level must be syntax, structure, or full. Got: {level!r}")
                sys.exit(1)
            from modules.validator import ConfigValidator
            schema_dir = run_args["schema-path"] or os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "json-schema"
            )
            validator = ConfigValidator(
                my_requests, default_dir, attrs, secret_args,
                level=level,
                validate_schema=run_args["validate-schema"],
                schema_path=schema_dir,
            )
            passed, _errors, _warnings = validator.validate()
            sys.exit(0 if passed else 1)

        logger.separator(f"Starting {start_type}Run")
```

- [ ] **Step 2: Verify the flag appears in help and the branch is reachable**

```bash
python3 kometa.py --help | grep -A1 "validate"
```

Expected: descriptions for `--validate`, `--validate-level`, `--validate-schema`, `--schema-path`.

- [ ] **Step 3: Smoke test against a real config (read-only)**

If a real `config/config.yml` exists in the repo, run:

```bash
python3 kometa.py --validate --validate-level syntax 2>&1 | tail -15
```

Expected: a "Validation Report (syntax)" block with `Result: PASSED` or a list of YAML errors. No Plex connection is made.

- [ ] **Step 4: Smoke test schema validation**

```bash
python3 kometa.py --validate --validate-level syntax --validate-schema 2>&1 | tail -20
```

Expected: validation report plus either a Schema Gap Report or "no gaps" for each schema type checked.

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v 2>&1 | tail -20
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add kometa.py
git commit -m "feat: wire --validate into kometa.py start()"
```

---

## Self-Review Notes

**Spec coverage check:**
- ✅ `--validate` / `-va` / `--validate-config` — Task 2
- ✅ `--validate-level` / `-vl` — Task 2
- ✅ `--validate-schema` / `-vs` — Task 2
- ✅ `--schema-path` / `-sp` — Task 2
- ✅ Syntax level: YAML parse, linked file walk, skip url/git — Tasks 3–4
- ✅ Structure level: required keys, deprecated keys, path existence, empty library warning — Task 5
- ✅ Full level: ConfigFile init, no run_config() — Task 6
- ✅ Schema validation: file→schema mapping, `additionalProperties` → gap, other errors → error list — Task 7
- ✅ Gap report: deduplicated, per-schema, count of files — Task 7
- ✅ Kitchen sink regression files — Task 7
- ✅ Print report with warnings/errors/gap report — Tasks 4, 7
- ✅ Exit 0 on pass / exit 1 on fail — Task 8
- ✅ `jsonschema==4.26.0` added — Task 1
- ✅ KOMETA_VALIDATE / KOMETA_VALIDATE_LEVEL / KOMETA_VALIDATE_SCHEMA / KOMETA_SCHEMA_PATH env vars — automatic via existing `get_env()` machinery (Task 2)
