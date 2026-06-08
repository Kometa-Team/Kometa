# Config Validation Mode — Design Spec

**Date:** 2026-06-08  
**Branch:** schema-improvements  
**Status:** Approved

---

## Overview

Add a `--validate` runtime flag to Kometa that reads and validates `config.yml` and all YAML files linked from it, then exits with a structured report — without performing a normal run. Three depth levels are supported: `syntax`, `structure`, and `full`.

---

## CLI Flags

Two new entries in the `arguments` dict in `kometa.py`:

```python
"validate": {
    "args": ["va", "validate-config"],
    "type": "bool",
    "help": "Validate config.yml and all linked YAML files without running"
},
"validate-level": {
    "args": "vl",
    "type": "str",
    "default": "structure",
    "help": "Validation depth: syntax | structure | full (Default: structure)"
},
```

**Flag aliases:**
- `--validate` / `-va` / `--validate-config`
- `--validate-level` / `-vl`

**Environment variable equivalents** (automatic via existing `get_env()` machinery):
- `KOMETA_VALIDATE`
- `KOMETA_VALIDATE_LEVEL`

When `--validate` is set, Kometa performs validation and exits — the scheduler loop does not run.

---

## Validation Levels

### `syntax`
- Loads `config.yml` with `YAML()` (ruamel.yaml).
- Walks all file references in:
  - `libraries[*].collection_files`
  - `libraries[*].metadata_files`
  - `libraries[*].overlay_files`
  - `libraries[*].image_files`
  - `playlist_files`
- For each reference with `file:` or bare string path, loads the file with `YAML()` and collects any `Failed` (YAML parse) errors.
- References with `url:`, `git:`, `default:`, `repo:` are skipped (no network access at this level).
- Catches all errors; does not abort on first failure.

### `structure`
- Runs everything in `syntax` first.
- Additionally checks:
  - Required top-level keys are present: `libraries`, `tmdb` (warns if absent rather than errors, since some setups omit tmdb).
  - Each library entry has at least one of: `collection_files`, `metadata_files`, `overlay_files`, `image_files`, or `operations`.
  - Local `file:` paths exist on disk (missing path = error).
  - Known deprecated keys (`metadata_path`, `overlay_path`) are flagged as warnings.

### `full`
- Calls `ConfigFile(requests, default_dir, attrs, secret_args)` exactly as the normal `start()` does.
- Any exception from `ConfigFile.__init__` is collected as an error.
- Does **not** call `run_config()` — no collections, overlays, or operations are executed, and no writes are made to Plex.
- Connects to Plex and all configured external APIs (this is the intended behaviour at this level).

---

## New Module: `modules/validator.py`

```python
class ConfigValidator:
    def __init__(self, requests, config_path, default_dir, attrs, secret_args, level="structure"):
        ...

    def validate(self) -> tuple[bool, list[str], list[str]]:
        """Returns (passed, errors, warnings)."""
        ...

    def _validate_syntax(self): ...
    def _validate_structure(self): ...
    def _validate_full(self): ...
```

**Dependencies used from existing code:**
- `modules.request.YAML` — YAML loading/parsing
- `modules.util.load_files` — resolves file reference dicts to `(file_type, path)` tuples
- `modules.config.ConfigFile` — used only for the `full` level
- `modules.util.Failed` — caught to collect errors without aborting

The module has no new external dependencies.

---

## Integration in `kometa.py`

In `start()`, before the existing `ConfigFile` construction:

```python
if run_args["validate"]:
    from modules.validator import ConfigValidator
    level = run_args["validate-level"]
    if level not in ("syntax", "structure", "full"):
        logger.error(f"--validate-level must be syntax, structure, or full. Got: {level!r}")
        sys.exit(1)
    validator = ConfigValidator(my_requests, config_path, default_dir, attrs, secret_args, level)
    passed, errors, warnings = validator.validate()
    sys.exit(0 if passed else 1)
```

The existing `start()` run path is **completely unchanged**. The validation branch exits before reaching it.

---

## Output Format

Uses Kometa's existing `logger` methods (`logger.separator`, `logger.info`, `logger.warning`, `logger.error`) to match log style.

Example output:

```
|============================================================|
| Validation Report (structure)                              |
|============================================================|
| Config:         /config/config.yml                         |
| Files checked:  14                                         |
|                                                            |
| Warnings (2):                                              |
|   config.yml: metadata_path is deprecated, use            |
|               collection_files / metadata_files            |
|   Movies/collections.yml: unknown key "sync_mod" ignored   |
|                                                            |
| Errors (1):                                                |
|   Shows/overlays.yml: YAML Error: found character '\t'     |
|                                                            |
| Result: FAILED                                             |
|============================================================|
```

- Warnings do **not** cause a non-zero exit code.
- Any error causes exit code 1.
- Clean validation (zero errors) exits with code 0.

---

## Error Handling

- Each file is validated independently; a failure in one file does not abort validation of the remaining files.
- `Failed` exceptions from `YAML()` and `load_files()` are caught per-file and added to the errors list.
- For the `full` level, any exception from `ConfigFile.__init__` is caught, added to errors, and validation reports FAILED.

---

## Out of Scope

- Semantic validation of collection/overlay builder keys (e.g., checking that `tmdb_popular` is a valid builder) — this belongs to the run-time builder validation already in `builder.py`.
- Validating URL/git/repo-referenced files in `syntax` or `structure` modes (requires network; use `full` for that).
- A machine-readable report file output — console + exit code is sufficient.
