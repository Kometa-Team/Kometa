# kometa-spec Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `kometa-spec` package (single source of truth for config.yml rules) and wire Kometa to consume it, per `docs/superpowers/specs/2026-07-06-kometa-spec-design.md`.

**Architecture:** A new data-only repo `kometa-spec` holds YAML spec files plus a thin loader/meta-schema/emitter. Kometa keeps `check_for_attribute` untouched; call-site kwargs move into the spec. A parity test proves spec kwargs ≡ literal kwargs before any call site converts. `json-schema/config-schema.json` becomes a generated file (skeleton + spec-emitted sections).

**Tech Stack:** Python ≥3.12, ruamel.yaml, pytest, hatchling (spec repo), AST parsing (extraction), GitHub Actions.

## Global Constraints

- **Behavior preservation is absolute:** `check_for_attribute` in `modules/config.py` is never edited. Only its inputs move.
- Spec repo path: `/Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec` (referred to as `$SPEC`). Kometa repo: `/Volumes/Samsung_SSD/dev/Kometa-Team/Kometa` (referred to as `$KOMETA`).
- Kometa work happens on branch `feat/kometa-spec`, created from `origin/nightly` (NOT from `fix/security-perf-hardening`, which has an open PR).
- Python floor `>=3.12` in both repos. YAML via `ruamel.yaml` (repo convention — no PyYAML).
- Kometa-side Python code must pass `black .`, `isort .`, `flake8 --max-line-length=256 --extend-ignore=E203,W503,E501` (pre-commit enforces these).
- Spec field names mirror `check_for_attribute` parameter names exactly (`save`, `do_print`, `req_default`, …), with two readability renames handled by `AttributeSpec`: spec `type` → engine `var_type`, spec `allowed` → engine `test_list`. No other renames.
- `test_list` values in config.py are dicts of `value → human description` (e.g. `sync_modes`). The spec's `allowed` preserves those descriptions.
- The 9 valid `type` values (from config.py:546-603): `str`, `bool`, `int`, `url`, `path`, `list`, `lower_list`, `int_list`, `list_path`.
- Human gates (cannot be done by the executor alone) are marked **HUMAN GATE** — pause and ask the user.

---

## Phase 1 — the kometa-spec package

### Task 1: Scaffold the kometa-spec repo

**Files:**
- Create: `$SPEC/pyproject.toml`
- Create: `$SPEC/src/kometa_spec/__init__.py`
- Create: `$SPEC/src/kometa_spec/spec/config/.gitkeep`
- Create: `$SPEC/tests/__init__.py` (empty)
- Create: `$SPEC/.gitignore`

**Interfaces:**
- Produces: importable package `kometa_spec`; spec data dir `src/kometa_spec/spec/config/` (packaged with the wheel). Note: the design doc sketched `spec/` at repo root; it lives inside the package instead so `importlib.resources` finds it identically in editable installs, wheels, and git installs.

- [ ] **Step 1: Create the repo and files**

```bash
mkdir -p /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec/src/kometa_spec/spec/config
mkdir -p /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec/tests
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec && git init -b main
```

`$SPEC/pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "kometa-spec"
version = "0.1.0"
description = "Single source of truth for Kometa YAML configuration rules"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
dependencies = ["ruamel.yaml>=0.17"]

[project.optional-dependencies]
dev = ["pytest>=8"]

[tool.hatch.build.targets.wheel]
packages = ["src/kometa_spec"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`$SPEC/src/kometa_spec/__init__.py`:

```python
__version__ = "0.1.0"
```

`$SPEC/.gitignore`:

```
__pycache__/
*.egg-info/
dist/
.pytest_cache/
```

`$SPEC/src/kometa_spec/spec/config/.gitkeep`: empty file.
`$SPEC/tests/__init__.py`: empty file.
`$SPEC/README.md`: one line for now: `# kometa-spec` (Task 6 fills it in).

- [ ] **Step 2: Verify it installs and pytest runs**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
python -m venv .venv && .venv/bin/pip install -q -e ".[dev]"
.venv/bin/python -c "import kometa_spec; print(kometa_spec.__version__)"
.venv/bin/pytest -q
```

Expected: `0.1.0`, then `no tests ran`.

- [ ] **Step 3: Commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git commit -m "chore: scaffold kometa-spec package"
```

---

### Task 2: AttributeSpec model with kwargs mapping

**Files:**
- Create: `$SPEC/src/kometa_spec/model.py`
- Test: `$SPEC/tests/test_model.py`

**Interfaces:**
- Produces: `AttributeSpec` frozen dataclass; `AttributeSpec.kwargs() -> dict` (engine kwargs that differ from engine defaults); `AttributeSpec.full_kwargs() -> dict` (all 11 engine kwargs, defaults applied — the parity-comparison form); constants `VAR_TYPES: list[str]`, `ENGINE_DEFAULTS: dict`.

- [ ] **Step 1: Write the failing tests**

`$SPEC/tests/test_model.py`:

```python
from kometa_spec.model import ENGINE_DEFAULTS, AttributeSpec


def test_full_kwargs_applies_engine_defaults():
    entry = AttributeSpec(section="settings", name="cache")
    assert entry.full_kwargs() == ENGINE_DEFAULTS


def test_kwargs_omits_engine_defaults():
    entry = AttributeSpec(section="settings", name="asset_depth", type="int", default=0)
    assert entry.kwargs() == {"var_type": "int", "default": 0}


def test_allowed_maps_to_test_list_preserving_descriptions():
    allowed = {"append": "Only Add Items", "sync": "Add & Remove Items"}
    entry = AttributeSpec(section="settings", name="sync_mode", default="append", allowed=allowed)
    assert entry.kwargs() == {"default": "append", "test_list": allowed}
    assert entry.full_kwargs()["test_list"] == allowed


def test_spec_only_fields_never_reach_engine_kwargs():
    entry = AttributeSpec(section="plex", name="token", secret=True, description="Plex token", group="Connection")
    assert "secret" not in entry.full_kwargs()
    assert "description" not in entry.full_kwargs()


def test_frozen():
    import dataclasses

    import pytest

    entry = AttributeSpec(section="settings", name="cache")
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.type = "bool"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd $SPEC && .venv/bin/pytest tests/test_model.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'kometa_spec.model'`

- [ ] **Step 3: Implement the model**

`$SPEC/src/kometa_spec/model.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

VAR_TYPES = ["str", "bool", "int", "url", "path", "list", "lower_list", "int_list", "list_path"]

# Parameter defaults of Kometa's check_for_attribute engine. full_kwargs()
# must always produce exactly these keys so the parity test compares like
# with like.
ENGINE_DEFAULTS = {
    "var_type": "str",
    "default": None,
    "default_is_none": False,
    "test_list": None,
    "translations": None,
    "throw": False,
    "save": True,
    "do_print": True,
    "req_default": False,
    "int_min": 0,
    "int_max": None,
}


@dataclass(frozen=True)
class AttributeSpec:
    section: str | None
    name: str
    # engine-facing facts (names mirror check_for_attribute, except
    # type -> var_type and allowed -> test_list, mapped in full_kwargs)
    type: str = "str"
    default: object = None
    default_is_none: bool = False
    allowed: dict | None = None
    translations: dict | None = None
    throw: bool = False
    save: bool = True
    do_print: bool = True
    req_default: bool = False
    int_min: int = 0
    int_max: int | None = None
    # spec-only metadata (consumed by QuickStart / schema emitter, never the engine)
    description: str = ""
    group: str | None = None
    secret: bool = False
    since: str | None = None
    deprecated: str | None = None

    def full_kwargs(self) -> dict:
        return {
            "var_type": self.type,
            "default": self.default,
            "default_is_none": self.default_is_none,
            "test_list": dict(self.allowed) if self.allowed is not None else None,
            "translations": dict(self.translations) if self.translations is not None else None,
            "throw": self.throw,
            "save": self.save,
            "do_print": self.do_print,
            "req_default": self.req_default,
            "int_min": self.int_min,
            "int_max": self.int_max,
        }

    def kwargs(self) -> dict:
        return {k: v for k, v in self.full_kwargs().items() if v != ENGINE_DEFAULTS[k]}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd $SPEC && .venv/bin/pytest tests/test_model.py -q`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git commit -m "feat: AttributeSpec model with engine kwargs mapping"
```

---

### Task 3: Meta-schema — the spec validates itself

**Files:**
- Create: `$SPEC/src/kometa_spec/metaschema.py`
- Test: `$SPEC/tests/test_metaschema.py`

**Interfaces:**
- Consumes: `VAR_TYPES` from `kometa_spec.model`.
- Produces: `validate_entry(section: str | None, name: str, raw: dict, source: str) -> None` (raises `SpecError` with file/section/attr context on any violation); `SpecError(Exception)`.

- [ ] **Step 1: Write the failing tests**

`$SPEC/tests/test_metaschema.py`:

```python
import pytest

from kometa_spec.metaschema import SpecError, validate_entry


def ok(**raw):
    validate_entry("settings", "sync_mode", raw, "settings.yml")


def err(match, **raw):
    with pytest.raises(SpecError, match=match):
        validate_entry("settings", "sync_mode", raw, "settings.yml")


def test_minimal_entry_is_valid():
    ok()
    ok(type="bool", default=True, description="x")


def test_unknown_key_rejected():
    err("unknown key 'colour'", colour="red")


def test_bad_type_rejected():
    err("invalid type 'integer'", type="integer")


def test_bool_fields_must_be_bool():
    err("must be a boolean", default_is_none="yes")
    err("must be a boolean", secret=1)


def test_int_bounds_must_be_int():
    err("must be an integer", int_min="0")
    err("must be an integer", int_max="10")


def test_allowed_must_be_mapping_of_descriptions():
    err("must be a mapping", allowed=["append", "sync"])
    err("must be a string", allowed={"append": 1})


def test_default_must_be_in_allowed_when_both_set():
    err("not in allowed", default="both", allowed={"append": "a", "sync": "s"})
    ok(default="sync", allowed={"append": "a", "sync": "s"})
    ok(allowed={"append": "a", "sync": "s"})  # no default is fine


def test_error_message_carries_context():
    with pytest.raises(SpecError, match=r"settings\.yml.*settings.*sync_mode"):
        validate_entry("settings", "sync_mode", {"colour": "red"}, "settings.yml")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd $SPEC && .venv/bin/pytest tests/test_metaschema.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'kometa_spec.metaschema'`

- [ ] **Step 3: Implement the meta-schema**

`$SPEC/src/kometa_spec/metaschema.py`:

```python
from __future__ import annotations

from kometa_spec.model import VAR_TYPES


class SpecError(Exception):
    pass


BOOL_KEYS = ["default_is_none", "throw", "save", "do_print", "req_default", "secret"]
INT_KEYS = ["int_min", "int_max"]
STR_KEYS = ["description", "group", "since", "deprecated"]
ALL_KEYS = {"type", "default", "allowed", "translations", *BOOL_KEYS, *INT_KEYS, *STR_KEYS}


def _fail(source: str, section: str | None, name: str, message: str) -> None:
    where = f"{source}: section {section!r} attribute {name!r}"
    raise SpecError(f"{where}: {message}")


def validate_entry(section: str | None, name: str, raw: dict, source: str) -> None:
    if not isinstance(raw, dict):
        _fail(source, section, name, f"entry must be a mapping, got {type(raw).__name__}")
    for key in raw:
        if key not in ALL_KEYS:
            _fail(source, section, name, f"unknown key {key!r}")
    if "type" in raw and raw["type"] not in VAR_TYPES:
        _fail(source, section, name, f"invalid type {raw['type']!r}; must be one of {VAR_TYPES}")
    for key in BOOL_KEYS:
        if key in raw and not isinstance(raw[key], bool):
            _fail(source, section, name, f"{key!r} must be a boolean")
    for key in INT_KEYS:
        if key in raw and not isinstance(raw[key], int):
            _fail(source, section, name, f"{key!r} must be an integer")
    for key in STR_KEYS:
        if key in raw and not isinstance(raw[key], str):
            _fail(source, section, name, f"{key!r} must be a string")
    for key in ["allowed", "translations"]:
        if key in raw:
            if not isinstance(raw[key], dict):
                _fail(source, section, name, f"{key!r} must be a mapping")
            if key == "allowed":
                for value, desc in raw[key].items():
                    if not isinstance(desc, str):
                        _fail(source, section, name, f"allowed[{value!r}] description must be a string")
    if raw.get("default") is not None and "allowed" in raw and raw["default"] not in raw["allowed"]:
        _fail(source, section, name, f"default {raw['default']!r} is not in allowed values")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd $SPEC && .venv/bin/pytest tests/test_metaschema.py -q`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git commit -m "feat: meta-schema validation for spec entries"
```

---

### Task 4: Loader

**Files:**
- Create: `$SPEC/src/kometa_spec/loader.py`
- Modify: `$SPEC/src/kometa_spec/__init__.py`
- Test: `$SPEC/tests/test_loader.py`

**Interfaces:**
- Consumes: `AttributeSpec`, `validate_entry`, `SpecError`.
- Produces: `kometa_spec.load(domain="config") -> Spec` (reads packaged spec files; raises `SpecError` on any invalid file); `Spec.sections: dict[str | None, dict[str, AttributeSpec]]`; `Spec.lookup(parent: str | None, attribute: str) -> AttributeSpec` (raises `SpecError` if missing); `load_dir(path) -> Spec` for tests and tooling.
- Convention: one YAML file per section, filename stem = section name (`settings.yml` → parent `"settings"`); the reserved filename `_root.yml` holds parent-less (top-level) attributes under section `None`.

- [ ] **Step 1: Write the failing tests**

`$SPEC/tests/test_loader.py`:

```python
import pytest

import kometa_spec
from kometa_spec.loader import Spec, load_dir
from kometa_spec.metaschema import SpecError


@pytest.fixture
def spec_dir(tmp_path):
    (tmp_path / "settings.yml").write_text(
        "sync_mode:\n"
        "  default: append\n"
        "  allowed:\n"
        "    append: Only Add\n"
        "    sync: Add & Remove\n"
        "asset_depth:\n"
        "  type: int\n"
        "  default: 0\n"
    )
    (tmp_path / "_root.yml").write_text("libraries:\n  type: list\n")
    return tmp_path


def test_load_dir_builds_sections(spec_dir):
    spec = load_dir(spec_dir)
    assert isinstance(spec, Spec)
    assert spec.lookup("settings", "sync_mode").default == "append"
    assert spec.lookup("settings", "asset_depth").type == "int"
    assert spec.lookup(None, "libraries").type == "list"


def test_lookup_missing_raises_with_context(spec_dir):
    spec = load_dir(spec_dir)
    with pytest.raises(SpecError, match="no spec entry for settings.nope"):
        spec.lookup("settings", "nope")


def test_invalid_entry_fails_load(tmp_path):
    (tmp_path / "settings.yml").write_text("sync_mode:\n  colour: red\n")
    with pytest.raises(SpecError, match="unknown key 'colour'"):
        load_dir(tmp_path)


def test_empty_attribute_body_means_all_defaults(tmp_path):
    (tmp_path / "settings.yml").write_text("cache:\n")
    spec = load_dir(tmp_path)
    assert spec.lookup("settings", "cache").type == "str"


def test_packaged_load_config_smoke():
    # Passes trivially while spec/config is empty; guards packaging once seeded.
    spec = kometa_spec.load("config")
    assert isinstance(spec, Spec)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd $SPEC && .venv/bin/pytest tests/test_loader.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'kometa_spec.loader'`

- [ ] **Step 3: Implement the loader**

`$SPEC/src/kometa_spec/loader.py`:

```python
from __future__ import annotations

from importlib import resources
from pathlib import Path

import ruamel.yaml

from kometa_spec.metaschema import SpecError, validate_entry
from kometa_spec.model import AttributeSpec


class Spec:
    def __init__(self, sections: dict[str | None, dict[str, AttributeSpec]]):
        self.sections = sections

    def lookup(self, parent: str | None, attribute: str) -> AttributeSpec:
        try:
            return self.sections[parent][attribute]
        except KeyError:
            raise SpecError(f"no spec entry for {parent or '(root)'}.{attribute}") from None


def _load_file(path: Path) -> tuple[str | None, dict[str, AttributeSpec]]:
    section = None if path.stem == "_root" else path.stem
    yaml = ruamel.yaml.YAML(typ="safe")
    data = yaml.load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SpecError(f"{path.name}: file must be a mapping of attribute entries")
    entries = {}
    for name, raw in data.items():
        raw = raw or {}
        validate_entry(section, name, raw, path.name)
        entries[name] = AttributeSpec(section=section, name=name, **raw)
    return section, entries


def load_dir(path) -> Spec:
    sections: dict[str | None, dict[str, AttributeSpec]] = {}
    for file in sorted(Path(path).glob("*.yml")):
        section, entries = _load_file(file)
        sections[section] = entries
    return Spec(sections)


def load(domain: str = "config") -> Spec:
    base = resources.files("kometa_spec") / "spec" / domain
    with resources.as_file(base) as path:
        return load_dir(path)
```

Update `$SPEC/src/kometa_spec/__init__.py`:

```python
from kometa_spec.loader import Spec, load, load_dir
from kometa_spec.metaschema import SpecError
from kometa_spec.model import ENGINE_DEFAULTS, VAR_TYPES, AttributeSpec

__version__ = "0.1.0"
__all__ = ["AttributeSpec", "ENGINE_DEFAULTS", "Spec", "SpecError", "VAR_TYPES", "load", "load_dir"]
```

- [ ] **Step 4: Run all spec-repo tests**

Run: `cd $SPEC && .venv/bin/pytest -q`
Expected: all pass (model 5 + metaschema 8 + loader 5)

- [ ] **Step 5: Commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git commit -m "feat: spec loader with packaged data and _root convention"
```

---

### Task 5: JSON Schema emitter

**Files:**
- Create: `$SPEC/src/kometa_spec/emit_jsonschema.py`
- Test: `$SPEC/tests/test_emit_jsonschema.py`

**Interfaces:**
- Consumes: `Spec`, `AttributeSpec`.
- Produces: `property_node(entry: AttributeSpec) -> dict` (one JSON-Schema property); `emit(spec: Spec, skeleton: dict, section_defs: dict[str, str]) -> dict` — deep-copies `skeleton`, and for each spec section named in `section_defs` (spec section → skeleton `definitions` key) replaces that definition's `properties` entirely with generated nodes. Sections absent from `section_defs` are ignored (skeleton-owned).

- [ ] **Step 1: Write the failing tests**

`$SPEC/tests/test_emit_jsonschema.py`:

```python
from kometa_spec.emit_jsonschema import emit, property_node
from kometa_spec.loader import Spec
from kometa_spec.model import AttributeSpec


def test_property_node_scalar_types():
    assert property_node(AttributeSpec(None, "x", type="str", description="d")) == {"type": "string", "description": "d"}
    assert property_node(AttributeSpec(None, "x", type="bool")) == {"type": "boolean"}
    assert property_node(AttributeSpec(None, "x", type="url")) == {"type": "string"}


def test_property_node_int_bounds():
    node = property_node(AttributeSpec(None, "x", type="int", int_min=0, int_max=10))
    assert node == {"type": "integer", "minimum": 0, "maximum": 10}


def test_property_node_enum_from_allowed():
    node = property_node(AttributeSpec(None, "x", allowed={"append": "a", "sync": "s"}))
    assert node == {"enum": ["append", "sync"]}


def test_property_node_list_types_accept_string_or_array():
    node = property_node(AttributeSpec(None, "x", type="list"))
    assert node == {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]}


def test_emit_replaces_owned_sections_and_preserves_rest():
    skeleton = {
        "$schema": "http://json-schema.org/draft-06/schema#",
        "properties": {"settings": {"$ref": "#/definitions/settings"}},
        "definitions": {
            "settings": {"type": "object", "properties": {"stale": {"type": "string"}}},
            "untouched": {"type": "object", "properties": {"keep": {"type": "string"}}},
        },
    }
    spec = Spec({"settings": {"cache": AttributeSpec("settings", "cache", type="bool", default=True)}})
    out = emit(spec, skeleton, {"settings": "settings"})
    assert out["definitions"]["settings"]["properties"] == {"cache": {"type": "boolean"}}
    assert out["definitions"]["untouched"]["properties"] == {"keep": {"type": "string"}}
    assert skeleton["definitions"]["settings"]["properties"] == {"stale": {"type": "string"}}  # input not mutated


def test_emit_ignores_sections_not_in_mapping():
    spec = Spec({"mystery": {"a": AttributeSpec("mystery", "a")}})
    skeleton = {"definitions": {}}
    out = emit(spec, skeleton, {})
    assert out == {"definitions": {}}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd $SPEC && .venv/bin/pytest tests/test_emit_jsonschema.py -q`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement the emitter**

`$SPEC/src/kometa_spec/emit_jsonschema.py`:

```python
from __future__ import annotations

from copy import deepcopy

from kometa_spec.loader import Spec
from kometa_spec.model import AttributeSpec

_SCALAR = {"str": "string", "url": "string", "path": "string", "bool": "boolean", "int": "integer"}
_LIST_ITEM = {"list": "string", "lower_list": "string", "list_path": "string", "int_list": "integer"}


def property_node(entry: AttributeSpec) -> dict:
    node: dict = {}
    if entry.allowed is not None:
        node["enum"] = list(entry.allowed)
    elif entry.type in _SCALAR:
        node["type"] = _SCALAR[entry.type]
        if entry.type == "int":
            node["minimum"] = entry.int_min
            if entry.int_max is not None:
                node["maximum"] = entry.int_max
    else:
        item = _LIST_ITEM[entry.type]
        node["anyOf"] = [{"type": item}, {"type": "array", "items": {"type": item}}]
    if entry.description:
        node["description"] = entry.description
    return node


def emit(spec: Spec, skeleton: dict, section_defs: dict[str, str]) -> dict:
    out = deepcopy(skeleton)
    for section, def_name in section_defs.items():
        if section not in spec.sections:
            continue
        target = out["definitions"].setdefault(def_name, {"type": "object"})
        target["properties"] = {name: property_node(e) for name, e in spec.sections[section].items()}
    return out
```

Note: an `int` node always includes `minimum` because the engine enforces `int_min=0` even when no bound is given — the existing hand schema does the same (see `asset_depth`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd $SPEC && .venv/bin/pytest -q`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git commit -m "feat: JSON Schema emitter (skeleton + owned-section merge)"
```

---

### Task 6: README, publish workflow, and GitHub repo

**Files:**
- Create: `$SPEC/README.md`
- Create: `$SPEC/.github/workflows/tests.yml`
- Create: `$SPEC/.github/workflows/publish.yml`

**Interfaces:**
- Produces: CI (pytest on push/PR) and tag-triggered PyPI publishing via trusted publishing.

- [ ] **Step 1: Write the README**

`$SPEC/README.md`:

```markdown
# kometa-spec

Single source of truth for what is legal in [Kometa](https://github.com/Kometa-Team/Kometa) YAML configuration.

The spec lives in `src/kometa_spec/spec/config/` — one YAML file per config.yml
section, one entry per attribute. Every entry is a datum, never logic: type,
default, allowed values (with descriptions), translations, int bounds, and
UI-facing metadata (`description`, `group`, `secret`).

## Consumers

- **Kometa** derives `check_for_attribute` parameters and emits
  `json-schema/config-schema.json` from this spec.
- **QuickStart** drives config-editor form generation from the same entries.

## Rules

- To change what is legal in config.yml, change it here. Kometa CI enforces
  parity between this spec and its call sites.
- Semver: patch = metadata only; minor = additive (new attributes/values);
  major = removals, renames, type or default changes, or spec-format changes.

## Usage

    import kometa_spec
    spec = kometa_spec.load("config")
    entry = spec.lookup("settings", "sync_mode")
    entry.kwargs()      # engine kwargs for Kometa
    entry.description   # UI metadata for QuickStart
```

- [ ] **Step 2: Write the workflows**

`$SPEC/.github/workflows/tests.yml`:

```yaml
name: Tests
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: pytest -q
```

`$SPEC/.github/workflows/publish.yml`:

```yaml
name: Publish
on:
  push:
    tags: ["v*"]
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build && python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 3: Commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git commit -m "docs+ci: README, test and publish workflows"
```

- [ ] **Step 4: HUMAN GATE — create the GitHub repo and push**

Ask the user to confirm the repo name/org, then:

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
gh repo create Kometa-Team/kometa-spec --public --source . --push
```

PyPI trusted-publisher registration (project `kometa-spec` → repo `Kometa-Team/kometa-spec`, workflow `publish.yml`, environment `pypi`) must be done by a human on pypi.org. Not needed until the first tagged release; Kometa consumes via git URL until then.

---

## Phase 2 — Kometa integration

### Task 7: Branch + call-site extractor

**Files:**
- Create: `$KOMETA/scripts/spec_tools/__init__.py` (empty)
- Create: `$KOMETA/scripts/spec_tools/extract.py`
- Test: `$KOMETA/tests/test_spec_extract.py`

**Interfaces:**
- Produces: `CallSite` dataclass with fields `lineno: int`, `parent: str | None`, `attribute: str`, `ordinal: int` (0-based index among sites sharing `(parent, attribute)`, in file order), `kwargs: dict` (full engine kwargs, defaults applied — same shape as `AttributeSpec.full_kwargs()`), `unresolved: list[str]` (kwarg names whose values could not be resolved to literals); `extract_call_sites(config_py_path) -> list[CallSite]` (static sites only); `count_dynamic_sites(config_py_path) -> int` (sites whose `attribute` or `parent` is not a literal). Also `site.key` property = `"{parent or '_root'}.{attribute}#{ordinal}"`.

- [ ] **Step 1: Create the Kometa branch**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
git fetch origin && git checkout -b feat/kometa-spec origin/nightly
```

(Working tree must be clean first; `docs/superpowers/` untracked files can stay.)

- [ ] **Step 2: Write the failing tests**

`$KOMETA/tests/test_spec_extract.py`:

```python
import textwrap

import pytest

from scripts.spec_tools.extract import count_dynamic_sites, extract_call_sites

SAMPLE = textwrap.dedent(
    """
    sync_modes = {"append": "Only Add", "sync": "Add & Remove"}

    class ConfigFile:
        def __init__(self):
            self.general = {
                "cache": check_for_attribute(self.data, "cache", parent="settings", var_type="bool", default=True),
                "sync_mode": check_for_attribute(self.data, "sync_mode", parent="settings", default="append", test_list=sync_modes),
                "asset_depth": check_for_attribute(self.data, "asset_depth", parent="settings", var_type="int", default=0),
                "cache": check_for_attribute(lib, "cache", parent="settings", var_type="bool", default=True, save=False),
            }
            dyn = check_for_attribute(self.data, attr_name, parent="settings")
    """
)


@pytest.fixture
def sample(tmp_path):
    p = tmp_path / "config.py"
    p.write_text(SAMPLE)
    return p


def test_extracts_static_sites_with_full_kwargs(sample):
    sites = extract_call_sites(sample)
    assert [s.attribute for s in sites] == ["cache", "sync_mode", "asset_depth", "cache"]
    cache = sites[0]
    assert cache.parent == "settings"
    assert cache.kwargs["var_type"] == "bool"
    assert cache.kwargs["default"] is True
    assert cache.kwargs["save"] is True  # engine default applied
    assert cache.unresolved == []


def test_resolves_module_level_name_references(sample):
    sync = extract_call_sites(sample)[1]
    assert sync.kwargs["test_list"] == {"append": "Only Add", "sync": "Add & Remove"}


def test_duplicate_sites_get_ordinals(sample):
    sites = extract_call_sites(sample)
    assert sites[0].ordinal == 0 and sites[0].key == "settings.cache#0"
    assert sites[3].ordinal == 1 and sites[3].key == "settings.cache#1"
    assert sites[3].kwargs["save"] is False


def test_unresolvable_value_is_flagged_not_fatal(tmp_path):
    p = tmp_path / "config.py"
    p.write_text('x = check_for_attribute(d, "a", parent="p", test_list=make_list())\n')
    (site,) = extract_call_sites(p)
    assert site.unresolved == ["test_list"]


def test_dynamic_attribute_counted_separately(sample):
    assert count_dynamic_sites(sample) == 1


def test_real_config_py_extracts_many_sites():
    sites = extract_call_sites("modules/config.py")
    assert len(sites) > 180
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd $KOMETA && python -m pytest tests/test_spec_extract.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.spec_tools'`

- [ ] **Step 4: Implement the extractor**

`$KOMETA/scripts/spec_tools/extract.py`:

```python
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

ENGINE_DEFAULTS = {
    "var_type": "str",
    "default": None,
    "default_is_none": False,
    "test_list": None,
    "translations": None,
    "throw": False,
    "save": True,
    "do_print": True,
    "req_default": False,
    "int_min": 0,
    "int_max": None,
}
ENGINE_PARAMS = list(ENGINE_DEFAULTS)


@dataclass
class CallSite:
    lineno: int
    parent: str | None
    attribute: str
    ordinal: int
    kwargs: dict
    unresolved: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.parent or '_root'}.{self.attribute}#{self.ordinal}"


def _module_constants(tree: ast.Module) -> dict:
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                consts[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError):
                pass
    return consts


def _resolve(node: ast.expr, consts: dict):
    """Return (value, ok). Literals and module-constant names resolve; anything else does not."""
    if isinstance(node, ast.Name) and node.id in consts:
        return consts[node.id], True
    try:
        return ast.literal_eval(node), True
    except (ValueError, TypeError, SyntaxError):
        return None, False


def _iter_calls(tree: ast.Module):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "check_for_attribute":
            yield node


def _split(path) -> tuple[list, dict]:
    source = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    return list(_iter_calls(tree)), _module_constants(tree)


def extract_call_sites(path) -> list[CallSite]:
    calls, consts = _split(path)
    sites: list[CallSite] = []
    seen: dict[tuple, int] = {}
    for call in calls:
        if len(call.args) < 2 or not isinstance(call.args[1], ast.Constant):
            continue
        attribute = call.args[1].value
        parent = None
        kwargs = dict(ENGINE_DEFAULTS)
        unresolved = []
        dynamic_parent = False
        for kw in call.keywords:
            if kw.arg == "parent":
                value, ok = _resolve(kw.value, consts)
                if ok:
                    parent = value
                else:
                    dynamic_parent = True
            elif kw.arg in ENGINE_PARAMS:
                value, ok = _resolve(kw.value, consts)
                if ok:
                    kwargs[kw.arg] = value
                else:
                    unresolved.append(kw.arg)
        if dynamic_parent:
            continue
        ordinal = seen.get((parent, attribute), 0)
        seen[(parent, attribute)] = ordinal + 1
        sites.append(CallSite(call.lineno, parent, attribute, ordinal, kwargs, unresolved))
    return sites


def count_dynamic_sites(path) -> int:
    calls, consts = _split(path)
    count = 0
    for call in calls:
        if len(call.args) < 2 or not isinstance(call.args[1], ast.Constant):
            count += 1
            continue
        for kw in call.keywords:
            if kw.arg == "parent" and not _resolve(kw.value, consts)[1]:
                count += 1
                break
    return count
```

Also create empty `$KOMETA/scripts/spec_tools/__init__.py` and `$KOMETA/scripts/__init__.py` (so `from scripts.spec_tools...` imports work from the repo root, matching how tests import).

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd $KOMETA && python -m pytest tests/test_spec_extract.py -q`
Expected: 6 passed. Note the count from `test_real_config_py_extracts_many_sites` — record the actual number for Task 9.

- [ ] **Step 6: Run linters and commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
black scripts/ tests/test_spec_extract.py && isort scripts/ tests/test_spec_extract.py
flake8 scripts/ tests/test_spec_extract.py --max-line-length=256 --extend-ignore=E203,W503,E501
git add scripts/ tests/test_spec_extract.py
git commit -m "feat: AST extractor for check_for_attribute call sites"
```

---

### Task 8: Seeder — generate the initial spec content

**Files:**
- Create: `$KOMETA/scripts/spec_tools/seed.py`
- Create (generated): `$SPEC/src/kometa_spec/spec/config/*.yml`

**Interfaces:**
- Consumes: `extract_call_sites`; existing `$KOMETA/json-schema/config-schema.json` (for descriptions).
- Produces: seeded spec files; `$SPEC/seed_report.txt` listing (a) duplicate `(parent, attribute)` sites whose kwargs differ from ordinal #0 (these become parity exceptions in Task 9) and (b) unresolved kwargs needing hand entry.
- `SECTION_DEFS` mapping (spec section → schema `definitions` key) is defined here and reused by Task 10; keep it in `seed.py` and import it from there.

- [ ] **Step 1: Write the seeder**

`$KOMETA/scripts/spec_tools/seed.py`:

```python
"""One-off: seed kometa-spec files from config.py call sites + existing schema descriptions.

Usage: python -m scripts.spec_tools.seed ../kometa-spec
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import ruamel.yaml

from scripts.spec_tools.extract import ENGINE_DEFAULTS, extract_call_sites

# spec section -> definitions key in json-schema/config-schema.json
SECTION_DEFS = {
    "plex": "plex-server",
    "tmdb": "tmdb-api",
    "tautulli": "tautulli-api",
    "webhooks": "webhooks",
    "omdb": "omdb-api",
    "mdblist": "mdblist-api",
    "notifiarr": "notifiarr-api",
    "gotify": "gotify-api",
    "ntfy": "ntfy-api",
    "anidb": "anidb-api",
    "sonarr": "sonarr-api",
    "radarr": "radarr-api",
    "settings": "settings",
    "mal": "mal-api",
    "trakt": "trakt-api",
    "github": "github-api",
}

SPEC_KEY_ORDER = ["type", "default", "default_is_none", "allowed", "translations", "int_min", "int_max", "throw", "save", "do_print", "req_default", "description"]


def _descriptions(schema_path: Path) -> dict:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    out = {}
    for section, def_name in SECTION_DEFS.items():
        props = schema.get("definitions", {}).get(def_name, {}).get("properties", {})
        out[section] = {name: node.get("description", "") for name, node in props.items()}
    return out


def _entry(site, description: str) -> dict:
    entry = {}
    for param, value in site.kwargs.items():
        if value == ENGINE_DEFAULTS[param]:
            continue
        key = {"var_type": "type", "test_list": "allowed"}.get(param, param)
        entry[key] = value
    for param in site.unresolved:
        entry[{"var_type": "type", "test_list": "allowed"}.get(param, param)] = f"FIXME unresolved at config.py:{site.lineno}"
    if description:
        entry["description"] = description
    return {k: entry[k] for k in SPEC_KEY_ORDER if k in entry}


def main(spec_repo: str) -> None:
    target = Path(spec_repo) / "src" / "kometa_spec" / "spec" / "config"
    target.mkdir(parents=True, exist_ok=True)
    sites = extract_call_sites("modules/config.py")
    descriptions = _descriptions(Path("json-schema/config-schema.json"))
    report = []

    sections: dict[str, dict] = {}
    for site in sites:
        section = site.parent or "_root"
        if site.ordinal > 0:
            first = next(s for s in sites if (s.parent, s.attribute) == (site.parent, site.attribute) and s.ordinal == 0)
            if site.kwargs != first.kwargs:
                diff = {k: (first.kwargs[k], site.kwargs[k]) for k in site.kwargs if site.kwargs[k] != first.kwargs[k]}
                report.append(f"VARIANT {site.key} (config.py:{site.lineno}) differs from #0: {diff}")
            continue
        if site.unresolved:
            report.append(f"UNRESOLVED {site.key} (config.py:{site.lineno}): {site.unresolved}")
        desc = descriptions.get(site.parent or "", {}).get(site.attribute, "")
        sections.setdefault(section, {})[site.attribute] = _entry(site, desc)

    yaml = ruamel.yaml.YAML()
    yaml.default_flow_style = False
    yaml.width = 4096
    for section, entries in sorted(sections.items()):
        with open(target / f"{section}.yml", "w", encoding="utf-8") as fp:
            yaml.dump(entries, fp)

    report_path = Path(spec_repo) / "seed_report.txt"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote {len(sections)} section files, {len(report)} report lines -> {report_path}")


if __name__ == "__main__":
    main(sys.argv[1])
```

- [ ] **Step 2: Run the seeder**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
python -m scripts.spec_tools.seed ../kometa-spec
```

Expected: `Wrote N section files, M report lines` (N ≈ number of distinct parents, M small).

- [ ] **Step 3: Verify the seeded spec loads**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
.venv/bin/pytest -q && .venv/bin/python -c "
import kometa_spec
spec = kometa_spec.load('config')
total = sum(len(v) for v in spec.sections.values())
print('sections:', len(spec.sections), 'attributes:', total)
"
```

Expected: if `seed_report.txt` listed unresolved kwargs, this load FAILS with a `SpecError` naming each `FIXME` entry in a non-string field (`allowed`, `type`, …) — that failure is the worklist. If there were no unresolved kwargs, it passes immediately.

- [ ] **Step 4: HUMAN GATE — review the seeded spec**

Show the user `seed_report.txt` and a couple of seeded files (e.g. `settings.yml`). Hand-fix any `FIXME` entries (using config.py as reference), then re-run Step 3 until it passes.

- [ ] **Step 5: Commit (both repos)**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git commit -m "feat: seed config spec from Kometa config.py call sites"
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
black scripts/spec_tools/seed.py && isort scripts/spec_tools/seed.py
git add scripts/spec_tools/seed.py && git commit -m "feat: spec seeder script"
```

---

### Task 9: Parity test — the drift alarm

**Files:**
- Create: `$KOMETA/tests/test_spec_parity.py`
- Create: `$KOMETA/tests/spec_parity_exceptions.yml`
- Modify: `$KOMETA/dev-requirements.txt`

**Interfaces:**
- Consumes: `extract_call_sites` / `CallSite.key`; `kometa_spec.load("config")`, `AttributeSpec.full_kwargs()`.
- Produces: permanent CI-enforced parity. Exceptions file format: `{site.key: {engine_param: value}}` — per-site kwarg overrides where a call site legitimately differs from the spec entry (these are exactly the `**overrides` needed at conversion time in Task 11).

- [ ] **Step 1: Add the dependency**

Append to `$KOMETA/dev-requirements.txt`:

```
kometa-spec @ git+https://github.com/Kometa-Team/kometa-spec.git@main
```

For local work, the editable install wins: `pip install -e ../kometa-spec`.

- [ ] **Step 2: Write the failing test**

`$KOMETA/tests/test_spec_parity.py`:

```python
"""Parity gate: every check_for_attribute call site in config.py must match kometa-spec.

If this test fails, either update the spec (the normal case — the spec is the
source of truth) or, for a genuinely site-specific kwarg, add an entry to
tests/spec_parity_exceptions.yml.
"""

from pathlib import Path

import pytest
import ruamel.yaml

import kometa_spec
from scripts.spec_tools.extract import count_dynamic_sites, extract_call_sites

CONFIG_PY = "modules/config.py"
EXCEPTIONS_FILE = Path(__file__).parent / "spec_parity_exceptions.yml"


def _exceptions() -> dict:
    yaml = ruamel.yaml.YAML(typ="safe")
    return yaml.load(EXCEPTIONS_FILE.read_text(encoding="utf-8")) or {}


SITES = extract_call_sites(CONFIG_PY)
SPEC = kometa_spec.load("config")


@pytest.mark.parametrize("site", SITES, ids=lambda s: s.key)
def test_call_site_matches_spec(site):
    exceptions = _exceptions()
    if site.unresolved and site.key not in exceptions:
        pytest.fail(f"{site.key} has unresolved kwargs {site.unresolved}; add an exceptions entry stating their runtime value")
    entry = SPEC.lookup(site.parent, site.attribute)
    expected = entry.full_kwargs() | exceptions.get(site.key, {})
    # Unresolved kwargs can't be compared statically; the exceptions entry is their declared truth.
    actual = site.kwargs | {k: expected[k] for k in site.unresolved}
    assert actual == expected, f"{site.key} (config.py:{site.lineno}) diverges from spec"


def test_no_orphan_spec_entries():
    covered = {(s.parent, s.attribute) for s in SITES}
    orphans = [f"{parent or '_root'}.{name}" for parent, attrs in SPEC.sections.items() for name in attrs if (parent, name) not in covered]
    assert orphans == [], f"spec entries with no call site: {orphans}"


def test_dynamic_site_count_is_pinned():
    # If this grows, a new dynamic call pattern appeared; decide how the spec covers it.
    assert count_dynamic_sites(CONFIG_PY) <= 5
```

`$KOMETA/tests/spec_parity_exceptions.yml` starts as:

```yaml
# Per-call-site kwargs that legitimately differ from the spec entry.
# Key: <parent>.<attribute>#<ordinal>   Value: {engine_param: value}
# Every entry here becomes an explicit **overrides argument when the call
# site is converted to the spec adapter.
{}
```

- [ ] **Step 3: Run and iterate to green**

Run: `cd $KOMETA && python -m pytest tests/test_spec_parity.py -q`

Expected on first run: some failures. Triage each:
1. **Variant sites** (from `seed_report.txt`): add the differing kwargs to `spec_parity_exceptions.yml` under the site's key (e.g. library-level rechecks passing `save: false`).
2. **Unresolved kwargs**: same — exceptions entry with the true runtime meaning, plus a comment.
3. **Seeder bugs**: fix the spec YAML in `$SPEC` (source of truth wins).

Re-run until: all parametrized cases pass, `test_no_orphan_spec_entries` passes, dynamic count pinned. Then run the full Kometa suite:

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa && python -m pytest tests/ -q
```

Expected: everything passes (parity tests add to the existing 749).

- [ ] **Step 4: Commit (both repos)**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git commit -m "fix: spec corrections from Kometa parity test"
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
black tests/test_spec_parity.py && isort tests/test_spec_parity.py
git add tests/test_spec_parity.py tests/spec_parity_exceptions.yml dev-requirements.txt
git commit -m "test: spec parity gate against kometa-spec"
```

---

### Task 10: Schema generation replaces the hand-maintained config-schema.json

**Files:**
- Create: `$KOMETA/json-schema/src/config-skeleton.json` (generated once, then hand-maintained)
- Create: `$KOMETA/scripts/spec_tools/emit_schema.py`
- Modify: `$KOMETA/json-schema/config-schema.json` (regenerated)

**Interfaces:**
- Consumes: `kometa_spec.load`, `kometa_spec.emit_jsonschema.emit`, `SECTION_DEFS` from `scripts.spec_tools.seed`.
- Produces: `python -m scripts.spec_tools.emit_schema` (regenerates the schema in place) and `python -m scripts.spec_tools.emit_schema --check` (exit 1 + diff summary if the committed file differs).

- [ ] **Step 1: Carve the skeleton**

One-off: copy the current schema and empty the owned sections' properties.

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
mkdir -p json-schema/src
python - <<'EOF'
import json
from scripts.spec_tools.seed import SECTION_DEFS

with open("json-schema/config-schema.json") as f:
    schema = json.load(f)
for def_name in SECTION_DEFS.values():
    if def_name in schema.get("definitions", {}):
        schema["definitions"][def_name].pop("properties", None)
with open("json-schema/src/config-skeleton.json", "w") as f:
    json.dump(schema, f, indent=1)
    f.write("\n")
EOF
```

- [ ] **Step 2: Write the emit script**

`$KOMETA/scripts/spec_tools/emit_schema.py`:

```python
"""Regenerate json-schema/config-schema.json from kometa-spec + the skeleton.

Usage:
    python -m scripts.spec_tools.emit_schema           # rewrite the schema
    python -m scripts.spec_tools.emit_schema --check   # exit 1 if committed file is stale
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import kometa_spec
from kometa_spec.emit_jsonschema import emit

from scripts.spec_tools.seed import SECTION_DEFS

SKELETON = Path("json-schema/src/config-skeleton.json")
TARGET = Path("json-schema/config-schema.json")


def generate() -> str:
    skeleton = json.loads(SKELETON.read_text(encoding="utf-8"))
    schema = emit(kometa_spec.load("config"), skeleton, SECTION_DEFS)
    return json.dumps(schema, indent=1) + "\n"


def main() -> int:
    generated = generate()
    if "--check" in sys.argv:
        if TARGET.read_text(encoding="utf-8") != generated:
            print("config-schema.json is stale: regenerate with `python -m scripts.spec_tools.emit_schema`")
            return 1
        print("config-schema.json is up to date")
        return 0
    TARGET.write_text(generated, encoding="utf-8")
    print(f"Wrote {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Generate and review the drift**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
python -m scripts.spec_tools.emit_schema
git diff --stat json-schema/config-schema.json
git diff json-schema/config-schema.json | head -200
```

The diff for owned sections = existing code/schema drift. **HUMAN GATE:** walk through the diff hunks with the user. For each: if the old schema was right and the code/spec is wrong, fix the spec (or file a Kometa bug); if the schema was stale, the generated version stands. Descriptions lost in generation (schema had one, spec doesn't) get copied into the spec's `description` field, not hand-edited into the JSON.

- [ ] **Step 4: Validate the result still works end-to-end**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
python -m pytest tests/test_validator.py tests/test_collection_schema.py -q
python -m scripts.spec_tools.emit_schema --check
```

Expected: validator tests pass against the regenerated schema; `--check` reports up to date.

- [ ] **Step 5: Commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
black scripts/spec_tools/emit_schema.py && isort scripts/spec_tools/emit_schema.py
git add json-schema/ scripts/spec_tools/emit_schema.py
git commit -m "feat: config-schema.json is now generated from kometa-spec"
cd /Volumes/Samsung_SSD/dev/Kometa-Team/kometa-spec
git add -A && git diff --cached --quiet || git commit -m "fix: spec corrections from schema drift review"
```

---

### Task 11: CI enforcement

**Files:**
- Create: `$KOMETA/.github/workflows/spec-check.yml`

**Interfaces:**
- Consumes: parity test (Task 9), `emit_schema --check` (Task 10).

- [ ] **Step 1: Write the workflow**

`$KOMETA/.github/workflows/spec-check.yml`:

```yaml
name: Spec Check
on:
  pull_request:
    paths:
      - "modules/config.py"
      - "json-schema/**"
      - "scripts/spec_tools/**"
      - "tests/test_spec_parity.py"
      - "tests/spec_parity_exceptions.yml"
      - "dev-requirements.txt"
jobs:
  spec-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt -r dev-requirements.txt
      - name: Parity between config.py and kometa-spec
        run: python -m pytest tests/test_spec_parity.py -q
      - name: config-schema.json matches spec emission
        run: python -m scripts.spec_tools.emit_schema --check
```

- [ ] **Step 2: Verify locally (workflow steps run as-is)**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
python -m pytest tests/test_spec_parity.py -q && python -m scripts.spec_tools.emit_schema --check
```

Expected: both green.

- [ ] **Step 3: Commit**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
git add .github/workflows/spec-check.yml
git commit -m "ci: enforce spec parity and schema generation"
```

---

### Task 12: Adapter + call-site conversion

**Files:**
- Modify: `$KOMETA/modules/config.py` (adapter + call sites; `check_for_attribute` body untouched)
- Modify: `$KOMETA/requirements.txt` (kometa-spec becomes a runtime dependency)
- Modify: `$KOMETA/CHANGELOG.md`

**Interfaces:**
- Consumes: `kometa_spec.load`, `Spec.lookup`, `AttributeSpec.kwargs()`; exceptions file from Task 9 (its entries become literal `**overrides`).
- Produces: `check(data, attribute, parent=None, **overrides)` nested function in `ConfigFile.__init__`, defined immediately after `check_for_attribute`.

- [ ] **Step 1: Add the runtime dependency**

Append to `$KOMETA/requirements.txt` (exact pin style matches the file's existing `==` convention; use the git tag until the PyPI release exists — see HUMAN GATE below):

```
kometa-spec @ git+https://github.com/Kometa-Team/kometa-spec.git@v0.1.0
```

**HUMAN GATE:** tag `v0.1.0` in the spec repo first (`cd $SPEC && git tag v0.1.0 && git push --tags`). Once PyPI trusted publishing is configured, replace with `kometa-spec==0.1.0`.

- [ ] **Step 2: Add the adapter**

In `modules/config.py`, at the top with the other imports: `import kometa_spec`. Inside `ConfigFile.__init__`, directly after the `check_for_attribute` function definition ends:

```python
        spec = kometa_spec.load("config")

        def check(data, attribute, parent=None, **overrides):
            entry = spec.lookup(parent, attribute)
            return check_for_attribute(data, attribute, parent=parent, **(entry.kwargs() | overrides))
```

- [ ] **Step 3: Convert the settings section first (the pattern)**

Each settings call site changes from:

```python
"asset_depth": check_for_attribute(self.data, "asset_depth", parent="settings", var_type="int", default=0),
```

to:

```python
"asset_depth": check(self.data, "asset_depth", parent="settings"),
```

Sites listed in `tests/spec_parity_exceptions.yml` keep their divergent kwargs explicitly, e.g. a library-level recheck `settings.cache#1` with `{save: false}` becomes:

```python
check(lib, "cache", parent="settings", save=False)
```

Run after the section:

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa && python -m pytest tests/ -q
```

**Important:** converting call sites removes literal kwargs, which flips those sites' extracted kwargs to all-engine-defaults. The parity test must therefore learn about `check` too — add this to `extract.py`'s `_iter_calls` before converting anything:

```python
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "check":
            yield node
```

With that, a converted `check(...)` site extracts only its explicit overrides, and the parity assertion becomes: overrides ⊆ exceptions entry for that site. Concretely, replace the body of `test_call_site_matches_spec` with:

```python
def test_call_site_matches_spec(site):
    entry = SPEC.lookup(site.parent, site.attribute)
    exceptions = _exceptions().get(site.key, {})
    if site.converted:  # new CallSite field: func name was "check"
        explicit = {k: v for k, v in site.kwargs.items() if k in site.explicit}  # kwargs literally present
        assert explicit == exceptions, f"{site.key}: converted site overrides {explicit} != exceptions {exceptions}"
    else:
        expected = entry.full_kwargs() | exceptions
        assert site.kwargs == expected, f"{site.key} (config.py:{site.lineno}) diverges from spec"
```

with `CallSite` gaining `converted: bool = False` and `explicit: list[str] = field(default_factory=list)` (names of kwargs literally present at the site), set in `extract_call_sites` (`converted = call.func.id == "check"`; `explicit = [kw.arg for kw in call.keywords if kw.arg in ENGINE_PARAMS]`). Update `tests/test_spec_extract.py` with one test:

```python
def test_converted_check_site_extracts_explicit_overrides(tmp_path):
    p = tmp_path / "config.py"
    p.write_text('x = check(d, "cache", parent="settings", save=False)\n')
    (site,) = extract_call_sites(p)
    assert site.converted is True
    assert site.explicit == ["save"]
    assert site.kwargs["save"] is False
```

- [ ] **Step 4: Convert the remaining sections in batches**

Order: `plex`, `tmdb`, then the remaining API sections, then `_root` sites. After each batch:

```bash
python -m pytest tests/test_spec_parity.py tests/ -q
```

Expected after the final batch: `test_no_orphan_spec_entries` still green (every spec entry has a call site), full suite green.

- [ ] **Step 5: Final verification pass**

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
python -m pytest tests/ -q
python -m scripts.spec_tools.emit_schema --check
```

Expected: full suite green, schema check clean. (A true before/after run of `kometa.py` needs a live Plex server; the parity test is the behavioral proof — identical kwargs into an identical, untouched engine.)

- [ ] **Step 6: Update CHANGELOG and commit**

Add under `## [Unreleased]` → `### Changed` in `$KOMETA/CHANGELOG.md`:

```markdown
- config.yml validation rules now come from the shared [kometa-spec](https://github.com/Kometa-Team/kometa-spec) package; `json-schema/config-schema.json` is generated from it and CI enforces parity
```

```bash
cd /Volumes/Samsung_SSD/dev/Kometa-Team/Kometa
black modules/config.py scripts/ tests/ && isort modules/config.py scripts/ tests/
python -m pytest tests/ -q
git add -A ':!docs/superpowers'
git commit -m "feat: drive config.yml validation from kometa-spec"
```

- [ ] **Step 7: HUMAN GATE — PR**

Ask the user before opening the PR to `nightly` (repo template, as with PR #3317). Suggest splitting review: spec-repo link + Kometa branch.

---

## Verification (whole plan)

1. `cd $SPEC && .venv/bin/pytest -q` — all spec-repo tests green.
2. `cd $KOMETA && python -m pytest tests/ -q` — full suite green (749 + new extract/parity tests).
3. `python -m scripts.spec_tools.emit_schema --check` — schema regeneration clean.
4. `git diff origin/nightly --stat` on the Kometa branch shows: no diff to `check_for_attribute`'s body (`git diff origin/nightly -- modules/config.py | grep -A2 "def check_for_attribute"` shows no changes to its implementation lines).
5. Spec repo pushed to GitHub; `pip install "kometa-spec @ git+https://github.com/Kometa-Team/kometa-spec.git@v0.1.0"` works in a clean venv.
