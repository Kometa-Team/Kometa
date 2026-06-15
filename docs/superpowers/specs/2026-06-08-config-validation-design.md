# Config Validation Mode — Design Spec

**Date:** 2026-06-08  
**Branch:** schema-improvements  
**Status:** Approved

---

## Overview

Add a `--validate` runtime flag to Kometa that reads and validates `config.yml` and all YAML files linked from it, then exits with a structured report — without performing a normal run. Three depth levels are supported: `syntax`, `structure`, and `full`. An optional `--validate-schema` flag additionally validates each file against its corresponding JSON schema and emits a schema gap report useful for schema authoring.

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

Two additional entries for schema validation:

```python
"validate-schema": {
    "args": ["vs", "validate-schemas"],
    "type": "bool",
    "help": "Also validate each YAML file against its corresponding JSON schema"
},
"schema-path": {
    "args": "sp",
    "type": "str",
    "default": None,
    "help": "Path to the json-schema/ directory (default: ./json-schema/ relative to kometa.py)"
},
```

**Flag aliases:**
- `--validate` / `-va` / `--validate-config`
- `--validate-level` / `-vl`
- `--validate-schema` / `-vs` / `--validate-schemas`
- `--schema-path` / `-sp`

**Environment variable equivalents** (automatic via existing `get_env()` machinery):
- `KOMETA_VALIDATE`
- `KOMETA_VALIDATE_LEVEL`
- `KOMETA_VALIDATE_SCHEMA`
- `KOMETA_SCHEMA_PATH`

`--validate-schema` is independent of `--validate-level` — it can be combined with any level. You can run schema validation alone (`--validate --validate-schema --validate-level syntax`) or alongside structural/full checks.

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

## Schema Validation (`--validate-schema`)

### Purpose

Validates each YAML file against its corresponding JSON schema using the `jsonschema` Python library. This provides a bidirectional feedback loop for schema authoring:

- **Schema too strict**: files that run fine in Kometa but fail schema validation → schema is missing keys or has wrong types.
- **Schema too loose**: files that pass schema but would fail at runtime → `required` / `type` constraints need tightening.

### File → Schema mapping

| File role | Schema file |
|-----------|-------------|
| `config.yml` | `json-schema/config-schema.json` |
| `collection_files` entries | `json-schema/collection-schema.json` |
| `metadata_files` entries | `json-schema/metadata-schema.json` |
| `overlay_files` entries | `json-schema/overlay-schema.json` |
| `playlist_files` entries | `json-schema/playlist-schema.json` |

The schema directory is resolved from `--schema-path` if provided, otherwise defaults to `./json-schema/` relative to `kometa.py`. If the directory or a specific schema file is not found, that schema check is skipped with a warning.

### Schema gap report

When `--validate-schema` is active, the validator collects all `additionalProperties` violations across every checked file and deduplicates them into a **gap report** appended after the main validation summary:

```
|============================================================|
| Schema Gap Report                                          |
|============================================================|
| Keys found in your files that are not in the schema:      |
|                                                            |
| collection-schema.json:                                    |
|   - collections[*].smart_label       (seen in 2 files)    |
|   - collections[*].builder_options   (seen in 1 file)     |
|                                                            |
| config-schema.json:                                        |
|   - settings.cache_expiration        (seen in 4 files)    |
|                                                            |
| No gaps found in: metadata, overlay, playlist schemas      |
|============================================================|
```

Gap report entries are **warnings**, not errors — an undocumented key is a schema authoring gap, not necessarily a broken config. They do not affect the exit code.

Schema validation errors (type mismatches, failed `required` checks, etc.) are **errors** and do cause exit code 1.

### Built-in kitchen sink test cases

When `--validate-schema` is set and the `json-schema/` directory contains `kitchen_sink_config.yml` or `prototype_config.yml`, the validator automatically includes them as additional config-schema test cases. This makes them a regression suite: if a schema edit breaks them, the next `--validate --validate-schema` run will catch it.

### New dependency

`jsonschema` must be added to `requirements.txt`. The schemas use JSON Schema draft-06; `jsonschema>=4.0` supports this via `Draft6Validator`.

---

## New Module: `modules/validator.py`

```python
class ConfigValidator:
    def __init__(self, requests, config_path, default_dir, attrs, secret_args,
                 level="structure", validate_schema=False, schema_path=None):
        ...

    def validate(self) -> tuple[bool, list[str], list[str]]:
        """Returns (passed, errors, warnings)."""
        ...

    def _validate_syntax(self): ...
    def _validate_structure(self): ...
    def _validate_full(self): ...
    def _validate_against_schema(self, data, schema_file, label): ...
    def _build_gap_report(self) -> list[str]: ...
```

**Internal state for schema validation:**
- `self._schema_gaps`: `dict[str, Counter[str]]` — maps schema filename → key path → count of files where that gap was seen.
- `self._files_checked`: list of `(data, schema_file, label)` tuples accumulated during the level pass, then consumed by `_validate_against_schema`.

**Dependencies used from existing code:**
- `modules.request.YAML` — YAML loading/parsing
- `modules.util.load_files` — resolves file reference dicts to `(file_type, path)` tuples
- `modules.config.ConfigFile` — used only for the `full` level
- `modules.util.Failed` — caught to collect errors without aborting

**New external dependency:**
- `jsonschema>=4.0` — JSON Schema draft-06 validation via `Draft6Validator`

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
    schema_dir = run_args["schema-path"] or os.path.join(os.path.dirname(os.path.abspath(__file__)), "json-schema")
    validator = ConfigValidator(
        my_requests, config_path, default_dir, attrs, secret_args,
        level=level,
        validate_schema=run_args["validate-schema"],
        schema_path=schema_dir,
    )
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
| Warnings (1):                                              |
|   config.yml: metadata_path is deprecated, use            |
|               collection_files / metadata_files            |
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
- Typo/did-you-mean suggestions for unknown keys — gap report surfaces the unknown keys; fixing the schema is the human's job.
