"""Schema validation tests.

Two kinds of checks:

1. ``test_all_schemas_are_valid_jsonschema`` — every ``*.json`` file in
   ``json-schema/`` must itself be a valid JSON Schema document.  Catches
   "I broke the schema while editing it" regressions.

2. ``test_all_defaults_are_valid_yaml`` — every ``*.yml`` / ``*.yaml`` file
   under ``defaults/`` must parse as valid YAML.  Strict schema-level
   validation is intentionally skipped because the defaults contain
   Kometa-specific ``<<placeholder>>`` template syntax that would fail any
   raw JSON-Schema check.

If you want stricter validation of a specific shipped default, add a
focused test for it (see ``test_collection_schema.py`` for the pattern).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator, SchemaError

# ── Locations ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "json-schema"
DEFAULTS_DIR = REPO_ROOT / "defaults"

# Schema files in this directory are JSON Schema documents themselves.
# Other .json files (e.g. example configs) are skipped here.
SCHEMA_FILES = sorted(p for p in SCHEMA_DIR.glob("*.json") if p.name.endswith("-schema.json"))

# Every YAML file shipped under defaults/.
DEFAULT_YAML_FILES = sorted(list(DEFAULTS_DIR.rglob("*.yml")) + list(DEFAULTS_DIR.rglob("*.yaml")))


# ── 1. Schemas themselves must be valid JSON Schema ───────────────────────────


@pytest.mark.parametrize("schema_path", SCHEMA_FILES, ids=lambda p: p.name)
def test_schema_file_is_valid_jsonschema(schema_path: Path) -> None:
    """Each *-schema.json file must be loadable AND a valid Draft-7 schema."""
    with schema_path.open() as fh:
        schema = json.load(fh)

    # check_schema() raises SchemaError on a malformed schema definition.
    try:
        Draft7Validator.check_schema(schema)
    except SchemaError as e:
        pytest.fail(f"{schema_path.name} is not a valid JSON Schema: {e.message}")


def test_at_least_one_schema_exists() -> None:
    """Defensive: catch a layout change that hides all schemas from us."""
    assert SCHEMA_FILES, f"no *-schema.json files found in {SCHEMA_DIR}"


# ── 2. Defaults must be parseable YAML ────────────────────────────────────────


@pytest.mark.parametrize("yaml_path", DEFAULT_YAML_FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_default_file_is_valid_yaml(yaml_path: Path) -> None:
    """Each YAML file under defaults/ must parse without errors."""
    with yaml_path.open() as fh:
        try:
            doc = yaml.safe_load(fh)
        except yaml.YAMLError as e:
            pytest.fail(f"{yaml_path.name} is not valid YAML: {e}")

    # Empty files would silently parse to None; flag them so they're caught.
    assert doc is not None, f"{yaml_path.name} parsed to None (empty file?)"


def test_at_least_one_default_exists() -> None:
    """Defensive: catch a layout change that hides all defaults from us."""
    assert DEFAULT_YAML_FILES, f"no YAML files found under {DEFAULTS_DIR}"
