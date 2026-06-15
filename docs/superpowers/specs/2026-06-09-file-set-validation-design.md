# File-Set Validation Design Spec

**Date:** 2026-06-09
**Branch:** schema-improvements
**Status:** Approved

---

## Overview

Extend Kometa's validation mode to validate standalone YAML files and entire directory trees — without requiring a full `config.yml`. The primary use case is feeding a collection of real-world configs and YAML files (Discord attachments, community configs repo) through schema validation to produce an aggregate gap report for improving the JSON schemas in `json-schema/`.

---

## New CLI Flags

Two new entries in the `arguments` dict in `kometa.py`:

```python
"validate-file": {
    "args": ["vf", "validate-files"],
    "type": "str",
    "default": None,
    "help": "Validate a single YAML file against its auto-detected schema"
},
"validate-dir": {
    "args": ["vd", "validate-directory"],
    "type": "str",
    "default": None,
    "help": "Validate all YAML files in a directory against their auto-detected schemas"
},
```

**Flag aliases:**
- `--validate-file` / `-vf` / `--validate-files`
- `--validate-dir` / `-vd` / `--validate-directory`

**Environment variable equivalents** (automatic via existing `get_env()` machinery):
- `KOMETA_VALIDATE_FILE`
- `KOMETA_VALIDATE_DIR`

**Implied behaviour:**
- Both flags imply `--validate-schema` — the gap report is the primary purpose; no need to pass it explicitly
- Both flags trigger an immediate run (added to the scheduler-bypass condition at line 1273 of `kometa.py`)
- `--schema-path` works the same as with `--validate` — defaults to `./json-schema/` next to `kometa.py`

**Example usage:**
```bash
python kometa.py --validate-file /downloads/discord/my_collection.yml
python kometa.py --validate-dir /repos/community-configs
python kometa.py --validate-dir /downloads/discord-attachments --schema-path /custom/json-schema
```

---

## Schema Type Detection

A new module-level function `detect_schema_type(data: dict) -> str | None` in `modules/validator.py` inspects the root keys of a loaded YAML file and returns the `SCHEMA_MAP` key to use for schema validation.

| Root key(s) present | Detected type |
|---|---|
| `collections` or `dynamic_collections` | `collection_files` |
| `overlays` | `overlay_files` |
| `playlists` | `playlist_files` |
| `metadata` | `metadata_files` |
| `libraries`, `plex`, `tmdb`, or `settings` | `config` |
| only `templates` / `external_templates`, nothing type-specific | `None` |

**Detection rules:**
- Type-specific keys take priority; `templates:` and `external_templates:` appear in collection, overlay, and playlist files and are not used as discriminators
- All detected types — including `config` — are validated against their corresponding JSON schema only. The existing `ConfigValidator` structural checks (required keys, deprecated keys, linked file existence) are not run; the goal here is schema gap discovery, not full structural validation
- Files returning `None` are recorded as skipped with a warning (`cannot determine file type`) — not counted as errors, not counted as passes

**Out of scope:** Standalone template-only files (root key `templates:` with no other type-specific key) cannot be typed automatically. Validation of these is deferred to a future spec.

---

## `--validate-file` Behaviour

1. Resolve the path; error and exit 1 if the file does not exist
2. Load the YAML file; record parse error and exit 1 if it fails
3. Call `detect_schema_type(data)`
4. If type is `None`: exit 1 with "cannot determine file type" message
5. Validate against the corresponding JSON schema (all types including `config`), collect errors and gaps
6. Print compact report; exit 0 (no errors) or 1 (any errors)

---

## `--validate-dir` Behaviour

1. Walk the path recursively; collect all `.yml` and `.yaml` files via `collect_yaml_files(path)`
2. For each file:
   - Load YAML; if parse fails, record as file error
   - Call `detect_schema_type(data)`; if `None`, record as skipped
   - Validate against detected schema (all types including `config`), collect errors and gaps
3. **Output:**
   - Files that are clean (no errors, no gaps): silent
   - Files with errors: print path + error list
   - After all files: one aggregate gap report across all **passing** files, ranked by frequency
   - Final summary: `X files checked, Y skipped (unknown type), Z with errors, N schema gaps found`
4. Exit 0 if no file had errors; exit 1 if any file had errors
5. The aggregate gap report draws only from files with no hard errors — gaps from broken files are excluded as noise

---

## Code Structure

### `modules/validator.py` additions

**`detect_schema_type(data: dict) -> str | None`** — module-level function implementing the detection table above.

**`collect_yaml_files(path: str) -> list[str]`** — module-level helper; if `path` is a file, returns `[path]`; if a directory, walks recursively and returns all `.yml` and `.yaml` files sorted by path.

**`FileSetValidator` class:**

```python
class FileSetValidator:
    def __init__(self, paths: list[str], schema_path: str):
        # paths: list of resolved file paths to validate
        # schema_path: path to json-schema/ directory

    def validate(self) -> tuple[bool, dict[str, list[str]], dict[str, Counter]]:
        # Returns (passed, per_file_errors, aggregate_gaps)
        # per_file_errors: {file_path: [error_strings]}
        # aggregate_gaps: {schema_filename: Counter{key: count}}

    def _print_report(self) -> None:
        # Per-file error blocks for files with errors
        # Aggregate gap report across passing files
        # Summary line
```

`FileSetValidator` reuses the existing `_load_yaml`, `_run_schema_validation`, and gap-tracking logic from `ConfigValidator` — extracted into module-level helpers or called via composition.

### `kometa.py` additions

New branch in `start()`, alongside the existing `if run_args["validate"]:` block:

```python
if run_args["validate-file"] or run_args["validate-dir"]:
    from modules.validator import FileSetValidator, collect_yaml_files
    source = run_args["validate-file"] or run_args["validate-dir"]
    schema_dir = run_args["schema-path"] or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "json-schema"
    )
    paths = collect_yaml_files(source)
    validator = FileSetValidator(paths, schema_dir)
    passed, *_ = validator.validate()
    sys.exit(0 if passed else 1)
```

Added to the immediate-run condition at line 1273 alongside `run_args["validate"]`.

---

## Output Format

**`--validate-file` (single file, errors):**
```
================================================================
 File Validation Report (syntax+schema)
================================================================
 File:   /downloads/my_collection.yml
 Schema: collection-schema.json

 Errors (1):
   [collection-schema.json] at collections -> My Collection -> visible_home: [not, a, bool] is not valid

 Result: FAILED
================================================================
```

**`--validate-dir` (batch, mixed results):**
```
================================================================
 File: /repos/community-configs/users/alice/collections.yml
 Schema: collection-schema.json
 Errors (1):
   [collection-schema.json] at collections -> Bad Collection -> tmdb_popular: "yes" is not of type 'integer'
================================================================

 Schema Gap Report (across 47 passing files)
================================================================
 Keys found in your files that are not in the schema:

 collection-schema.json:
   - smart_label          (seen in 31 files)
   - builder_options      (seen in 12 files)
   - minimum_items        (seen in 4 files)

 No gaps in: overlay, metadata, playlist schemas

================================================================
 Summary: 51 files checked, 3 skipped (unknown type), 1 with errors, 3 schema gaps found
 Result: FAILED
================================================================
```

---

## Testing

New tests in `tests/test_validator.py`:

- `test_detect_schema_type_collection` — `collections:` root key → `collection_files`
- `test_detect_schema_type_overlay` — `overlays:` root key → `overlay_files`
- `test_detect_schema_type_templates_only` — only `templates:` → `None`
- `test_detect_schema_type_config` — `libraries:` root key → `config`
- `test_collect_yaml_files_single_file` — single path returns one-element list
- `test_collect_yaml_files_directory` — directory returns all `.yml`/`.yaml` files recursively
- `test_fileset_validator_clean_file_passes` — valid collection file, no errors, gap reported
- `test_fileset_validator_parse_error` — broken YAML → file error, not in aggregate gaps
- `test_fileset_validator_unknown_type` — unrecognised root key → skipped, not an error
- `test_fileset_validator_aggregate_gaps` — same gap key across two files → count is 2

---

## Out of Scope

- Standalone template-only files (root key `templates:` with no type-specific key) — deferred
- Network-fetched files (`url:`, `git:`, `repo:` references within walked config files)
- Type inference for gap report (observing value types to suggest schema additions) — separate future spec
- Schema patch generation — separate future spec
