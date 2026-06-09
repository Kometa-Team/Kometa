# File-Set Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `--validate-file` and `--validate-dir` flags that validate standalone YAML files and directory trees against their auto-detected JSON schemas, producing a gap report for schema improvement.

**Architecture:** Two new module-level functions (`detect_schema_type`, `collect_yaml_files`) and a new `FileSetValidator` class are added to `modules/validator.py`. A new branch in `kometa.py`'s `start()` handles both flags. All schema validation logic is self-contained in `FileSetValidator`; it does not depend on `ConfigValidator`.

**Tech Stack:** Python 3.10+, `ruamel.yaml`, `jsonschema==4.26.0`, `pytest`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `modules/validator.py` | Add `detect_schema_type`, `collect_yaml_files`, `FileSetValidator` |
| Modify | `tests/test_validator.py` | Tests for all new functions and the class |
| Modify | `kometa.py` (arguments dict + start()) | Two new CLI flags + validation branch |
| Modify | `docs/kometa/environmental.md` | Document `--validate-file` and `--validate-dir` |

---

## Task 1: `detect_schema_type` and `collect_yaml_files` (TDD)

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `modules/validator.py`

### Background

`detect_schema_type(data: dict) -> str | None` maps a YAML file's root keys to a `SCHEMA_MAP` key. The existing `SCHEMA_MAP` in `modules/validator.py` is:
```python
SCHEMA_MAP = {
    "config": "config-schema.json",
    "collection_files": "collection-schema.json",
    "metadata_files": "metadata-schema.json",
    "overlay_files": "overlay-schema.json",
    "playlist_files": "playlist-schema.json",
}
```

Detection rules (type-specific keys take priority; `templates`/`external_templates` are not discriminators):
- `collections` or `dynamic_collections` present → `"collection_files"`
- `overlays` present → `"overlay_files"`
- `playlists` present → `"playlist_files"`
- `metadata` present → `"metadata_files"`
- `libraries`, `plex`, `tmdb`, or `settings` present → `"config"`
- none of the above → `None`

`collect_yaml_files(path: str) -> list[str]` returns a sorted list of `.yml`/`.yaml` files. If `path` is a file, returns `[path]`. If a directory, walks recursively.

- [ ] **Step 1: Add imports and failing tests to tests/test_validator.py**

Add this import line after `from modules.validator import ConfigValidator`:

```python
from modules.validator import ConfigValidator, FileSetValidator, collect_yaml_files, detect_schema_type
```

Then append to the end of `tests/test_validator.py`:

```python
# ── detect_schema_type tests ──────────────────────────────────────────────────


def test_detect_schema_type_collection():
    assert detect_schema_type({"collections": {}}) == "collection_files"


def test_detect_schema_type_dynamic_collections():
    assert detect_schema_type({"dynamic_collections": {}}) == "collection_files"


def test_detect_schema_type_overlay():
    assert detect_schema_type({"overlays": {}}) == "overlay_files"


def test_detect_schema_type_playlist():
    assert detect_schema_type({"playlists": {}}) == "playlist_files"


def test_detect_schema_type_metadata():
    assert detect_schema_type({"metadata": {}}) == "metadata_files"


def test_detect_schema_type_config():
    assert detect_schema_type({"libraries": {}, "plex": {}}) == "config"


def test_detect_schema_type_templates_only():
    assert detect_schema_type({"templates": {}}) is None


def test_detect_schema_type_templates_with_collections():
    assert detect_schema_type({"templates": {}, "collections": {}}) == "collection_files"


# ── collect_yaml_files tests ──────────────────────────────────────────────────


def test_collect_yaml_files_single_file(tmp_path):
    f = tmp_path / "test.yml"
    f.write_text("key: value", encoding="utf-8")
    assert collect_yaml_files(str(f)) == [str(f)]


def test_collect_yaml_files_directory(tmp_path):
    (tmp_path / "a.yml").write_text("key: a", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("key: b", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.yml").write_text("key: c", encoding="utf-8")
    (tmp_path / "not_yaml.txt").write_text("ignore me", encoding="utf-8")
    result = collect_yaml_files(str(tmp_path))
    assert sorted(result) == sorted([
        str(tmp_path / "a.yml"),
        str(tmp_path / "b.yaml"),
        str(tmp_path / "sub" / "c.yml"),
    ])
```

- [ ] **Step 2: Run new tests — expect FAIL (ImportError)**

```bash
python -m pytest tests/test_validator.py -k "detect_schema_type or collect_yaml_files" -v 2>&1 | tail -15
```

Expected: `ImportError: cannot import name 'detect_schema_type'`

- [ ] **Step 3: Add `detect_schema_type` and `collect_yaml_files` to modules/validator.py**

Add these two functions after `_get_config_file_class()` and before the `ConfigValidator` class definition:

```python
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
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_validator.py -k "detect_schema_type or collect_yaml_files" -v 2>&1 | tail -15
```

Expected: all 10 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/validator.py tests/test_validator.py
git commit -m "feat: add detect_schema_type and collect_yaml_files"
```

---

## Task 2: `FileSetValidator` class (TDD)

**Files:**
- Modify: `tests/test_validator.py`
- Modify: `modules/validator.py`

### Background

`FileSetValidator` validates a list of YAML file paths against their auto-detected schemas. For each file it:
1. Loads the YAML (records parse errors per file)
2. Calls `detect_schema_type` (skips with no error if `None`)
3. Validates against the corresponding JSON schema
4. Routes `additionalProperties` violations to a gaps Counter, all other violations to per-file errors
5. After all files: prints per-file error blocks (silent for clean files), one aggregate gap report across **passing** files only, and a summary line

The `validate()` return signature is `tuple[bool, dict[str, list[str]], dict[str, Counter]]`:
- `bool`: `True` if no file had errors
- `dict[str, list[str]]`: `{file_path: [error_strings]}` for files with errors only
- `dict[str, Counter]`: `{schema_filename: Counter{gap_key: count}}` aggregate gaps

- [ ] **Step 1: Add FileSetValidator tests to tests/test_validator.py**

Append to the end of `tests/test_validator.py`:

```python
# ── FileSetValidator tests ────────────────────────────────────────────────────


def test_fileset_validator_clean_file_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    f = tmp_path / "collections.yml"
    f.write_text("collections:\n  My Collection:\n    tmdb_popular: 5\n", encoding="utf-8")
    v = FileSetValidator([str(f)], SCHEMA_DIR)
    passed, per_file_errors, aggregate_gaps = v.validate()
    assert passed
    assert per_file_errors == {}


def test_fileset_validator_parse_error(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    f = tmp_path / "bad.yml"
    f.write_text("key: [\n  unclosed\n", encoding="utf-8")
    v = FileSetValidator([str(f)], SCHEMA_DIR)
    passed, per_file_errors, aggregate_gaps = v.validate()
    assert not passed
    assert str(f) in per_file_errors
    assert any("YAML" in e for e in per_file_errors[str(f)])
    assert aggregate_gaps == {}


def test_fileset_validator_unknown_type(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    f = tmp_path / "templates_only.yml"
    f.write_text("templates:\n  MyTemplate:\n    test: true\n", encoding="utf-8")
    v = FileSetValidator([str(f)], SCHEMA_DIR)
    passed, per_file_errors, aggregate_gaps = v.validate()
    assert passed
    assert per_file_errors == {}


def test_fileset_validator_aggregate_gaps(tmp_path, monkeypatch):
    monkeypatch.setattr(validator_module, "logger", FakeLogger())
    content = "collections:\n  Test:\n    tmdb_popular: 5\nunknown_key_xyz: true\n"
    f1 = tmp_path / "a.yml"
    f2 = tmp_path / "b.yml"
    f1.write_text(content, encoding="utf-8")
    f2.write_text(content, encoding="utf-8")
    v = FileSetValidator([str(f1), str(f2)], SCHEMA_DIR)
    passed, per_file_errors, aggregate_gaps = v.validate()
    assert passed
    assert "collection-schema.json" in aggregate_gaps
    gap_key = next(k for k in aggregate_gaps["collection-schema.json"] if "unknown_key_xyz" in k)
    assert aggregate_gaps["collection-schema.json"][gap_key] == 2
```

- [ ] **Step 2: Run new tests — expect FAIL (ImportError or NotImplementedError)**

```bash
python -m pytest tests/test_validator.py -k "fileset" -v 2>&1 | tail -15
```

Expected: `ImportError: cannot import name 'FileSetValidator'`

- [ ] **Step 3: Add FileSetValidator to modules/validator.py**

Add the following class at the end of `modules/validator.py` (after `ConfigValidator`):

```python
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
                normalized = []
                for p in error.absolute_path:
                    if isinstance(p, int):
                        if normalized:
                            normalized[-1] += "[*]"
                    else:
                        normalized.append(str(p))
                base = ".".join(normalized)
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
```

- [ ] **Step 4: Run all tests — expect PASS**

```bash
python -m pytest tests/test_validator.py -v 2>&1 | tail -40
```

Expected: all 36 tests pass (22 existing + 10 new from Task 1 + 4 new from Task 2).

- [ ] **Step 5: Commit**

```bash
git add modules/validator.py tests/test_validator.py
git commit -m "feat: add FileSetValidator for standalone and batch YAML validation"
```

---

## Task 3: Wire `--validate-file` and `--validate-dir` into kometa.py

**Files:**
- Modify: `kometa.py`

- [ ] **Step 1: Add two new entries to the `arguments` dict**

In `kometa.py`, the `arguments` dict currently ends with:

```python
    "schema-path": {"args": "sp", "type": "str", "default": None, "help": "Path to the json-schema/ directory (default: ./json-schema/ next to kometa.py)"},
}
```

Replace that closing line with:

```python
    "schema-path": {"args": "sp", "type": "str", "default": None, "help": "Path to the json-schema/ directory (default: ./json-schema/ next to kometa.py)"},
    "validate-file": {"args": ["vf", "validate-files"], "type": "str", "default": None, "help": "Validate a single YAML file against its auto-detected schema"},
    "validate-dir": {"args": ["vd", "validate-directory"], "type": "str", "default": None, "help": "Validate all YAML files in a directory against their auto-detected schemas"},
}
```

- [ ] **Step 2: Add the validation branch in start()**

In `kometa.py`, find the existing `if run_args["validate"]:` block (around line 435):

```python
        if run_args["validate"]:
            ...
            sys.exit(0 if passed else 1)

        logger.separator(f"Starting {start_type}Run")
```

Insert the new branch immediately after `sys.exit(0 if passed else 1)` and before `logger.separator(f"Starting {start_type}Run")`:

```python
        if run_args["validate-file"] or run_args["validate-dir"]:
            from modules.validator import FileSetValidator, collect_yaml_files

            source = run_args["validate-file"] or run_args["validate-dir"]
            schema_dir = run_args["schema-path"] or os.path.join(os.path.dirname(os.path.abspath(__file__)), "json-schema")
            paths = collect_yaml_files(source)
            if not paths:
                logger.error(f"No YAML files found at: {source}")
                sys.exit(1)
            validator = FileSetValidator(paths, schema_dir)
            passed, *_ = validator.validate()
            sys.exit(0 if passed else 1)

```

- [ ] **Step 3: Add to the immediate-run condition**

Find line 1273 (the scheduler-bypass condition):

```python
        if run_args["run"] or run_args["tests"] or run_args["run-collections"] or run_args["run-libraries"] or run_args["run-files"] or run_args["resume"] or run_args["validate"]:
```

Replace with:

```python
        if run_args["run"] or run_args["tests"] or run_args["run-collections"] or run_args["run-libraries"] or run_args["run-files"] or run_args["resume"] or run_args["validate"] or run_args["validate-file"] or run_args["validate-dir"]:
```

- [ ] **Step 4: Verify flags appear in --help**

```bash
python kometa.py --help | grep -E "validate-file|validate-dir"
```

Expected: two lines describing `--validate-file` and `--validate-dir`.

- [ ] **Step 5: Smoke test --validate-file**

```bash
cat > /tmp/test_collection.yml << 'EOF'
collections:
  My Test Collection:
    tmdb_popular: 5
EOF
python kometa.py --validate-file /tmp/test_collection.yml 2>&1 | tail -15
echo "Exit: $?"
```

Expected: report showing `collection-schema.json`, `Result: PASSED`, exit code 0.

- [ ] **Step 6: Smoke test --validate-dir**

```bash
mkdir -p /tmp/test_yaml_dir
cat > /tmp/test_yaml_dir/collections.yml << 'EOF'
collections:
  Test:
    tmdb_popular: 5
unknown_top_level_key: true
EOF
cat > /tmp/test_yaml_dir/overlays.yml << 'EOF'
overlays:
  MyOverlay:
    overlay:
      name: MyOverlay
EOF
python kometa.py --validate-dir /tmp/test_yaml_dir 2>&1 | tail -20
echo "Exit: $?"
```

Expected: report showing files checked, gap for `unknown_top_level_key` in collection-schema.json, `Result: PASSED`, exit code 0.

- [ ] **Step 7: Run full test suite**

```bash
python -m pytest tests/ -v 2>&1 | tail -20
```

Expected: all validator tests pass. Any pre-existing failures in other test files are unrelated.

- [ ] **Step 8: Commit**

```bash
git add kometa.py
git commit -m "feat: add --validate-file and --validate-dir CLI flags"
```

---

## Task 4: Update docs

**Files:**
- Modify: `docs/kometa/environmental.md`

- [ ] **Step 1: Add --validate-file entry**

In `docs/kometa/environmental.md`, find the existing `--validate-dir` entry (it doesn't exist yet). Find the line:

```
??? blank "Config Secrets&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--kometa-***`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_***`<a class="headerlink" href="#kometa-vars" title="Permanent link">¶</a>"
```

Insert before it:

```markdown
??? blank "Validate File&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-vf`/`--validate-files`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_VALIDATE_FILE`<a class="headerlink" href="#validate-file" title="Permanent link">¶</a>"

    <div id="validate-file" />Validate a single YAML file against its auto-detected JSON schema and print a gap report. The schema is inferred from the file's root keys: `collections:` → collection schema, `overlays:` → overlay schema, `playlists:` → playlist schema, `metadata:` → metadata schema, `libraries:`/`plex:`/`tmdb:` → config schema.

    Exits with code `0` if no errors, `1` if any errors. Use [`--schema-path`](#schema-path) to override the schema directory.

    <hr style="margin: 0px;">

    **Accepted Values:** Path to a YAML file

    **Shell Flags:** `-vf`, `--validate-files`, or `--validate-file` (ex. `--validate-file /path/to/collections.yml`)

    **Environment Variable:** `KOMETA_VALIDATE_FILE` (ex. `KOMETA_VALIDATE_FILE=/path/to/collections.yml`)

    !!! example
        === "Local Environment"
            ```
            python kometa.py --validate-file /path/to/collections.yml
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -v "/path/to/files:/files:ro" kometateam/kometa --validate-file /files/collections.yml
            ```

??? blank "Validate Directory&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-vd`/`--validate-directory`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_VALIDATE_DIR`<a class="headerlink" href="#validate-dir" title="Permanent link">¶</a>"

    <div id="validate-dir" />Walk a directory recursively, validate every `.yml` and `.yaml` file found against its auto-detected JSON schema, and print a combined report. Files with an unrecognised structure are skipped with a warning (not an error). Clean files are silent; only files with errors are reported individually.

    After all files, a single aggregate gap report is printed showing keys present in your files but missing from the schemas, ranked by how many files contain each key. This is the primary tool for improving the `json-schema/` files.

    Exits with code `0` if no file had errors, `1` if any file had errors. Use [`--schema-path`](#schema-path) to override the schema directory.

    <hr style="margin: 0px;">

    **Accepted Values:** Path to a directory

    **Shell Flags:** `-vd`, `--validate-directory`, or `--validate-dir` (ex. `--validate-dir /path/to/configs`)

    **Environment Variable:** `KOMETA_VALIDATE_DIR` (ex. `KOMETA_VALIDATE_DIR=/path/to/configs`)

    !!! example
        === "Local Environment"
            ```
            python kometa.py --validate-dir /path/to/community-configs
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -v "/path/to/configs:/data:ro" kometateam/kometa --validate-dir /data
            ```

```

- [ ] **Step 2: Commit**

```bash
git add docs/kometa/environmental.md
git commit -m "docs: add --validate-file and --validate-dir to environmental.md"
```

---

## Self-Review Notes

**Spec coverage:**
- ✅ `--validate-file` / `-vf` / `--validate-files` / `KOMETA_VALIDATE_FILE` — Task 3
- ✅ `--validate-dir` / `-vd` / `--validate-directory` / `KOMETA_VALIDATE_DIR` — Task 3
- ✅ Both imply `--validate-schema` (built into `FileSetValidator`, no flag needed) — Task 2
- ✅ Both trigger immediate run — Task 3 step 3
- ✅ `detect_schema_type` with correct detection table — Task 1
- ✅ `templates`/`external_templates` not used as discriminators — Task 1 (test_detect_schema_type_templates_only)
- ✅ `collect_yaml_files` for file and directory — Task 1
- ✅ Per-file errors + aggregate gap report from passing files only — Task 2
- ✅ Summary line format — Task 2
- ✅ Unknown type → skipped, not error — Task 2 (test_fileset_validator_unknown_type)
- ✅ Parse error → file error, not in gaps — Task 2 (test_fileset_validator_parse_error)
- ✅ Gap deduplication across files — Task 2 (test_fileset_validator_aggregate_gaps)
- ✅ Empty directory → error message + exit 1 — Task 3 step 2
- ✅ Docs updated — Task 4
