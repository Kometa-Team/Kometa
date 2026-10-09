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

import ast
import json
import re
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
SCHEDULE_SCHEMA_FILES = [SCHEMA_DIR / name for name in ("config-schema.json", "collection-schema.json", "overlay-schema.json", "playlist-schema.json")]

# Every YAML file shipped under defaults/.
DEFAULT_YAML_FILES = sorted(list(DEFAULTS_DIR.rglob("*.yml")) + list(DEFAULTS_DIR.rglob("*.yaml")))


def _scheduled_visibility_declarations(schema):
    declarations = []

    def find_visibility_properties(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if re.fullmatch(r"\^?visible_(?:library|home|shared)(?:_\.\+\$)?", key) and isinstance(child, dict):
                    declarations.append(child)
                find_visibility_properties(child)
        elif isinstance(value, list):
            for child in value:
                find_visibility_properties(child)

    find_visibility_properties(schema)
    return declarations


# ── 1. Schemas themselves must be valid JSON Schema ───────────────────────────


@pytest.mark.parametrize("schema_path", SCHEMA_FILES, ids=lambda p: p.name)
def test_schema_file_is_valid_jsonschema(schema_path: Path) -> None:
    """Each *-schema.json file must be loadable AND a valid Draft-7 schema."""
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)

    # check_schema() raises SchemaError on a malformed schema definition.
    try:
        Draft7Validator.check_schema(schema)
    except SchemaError as e:
        pytest.fail(f"{schema_path.name} is not a valid JSON Schema: {e.message}")


def test_at_least_one_schema_exists() -> None:
    """Defensive: catch a layout change that hides all schemas from us."""
    assert SCHEMA_FILES, f"no *-schema.json files found in {SCHEMA_DIR}"


@pytest.mark.parametrize("operation", ["mass_content_rating_update", "mass_original_title_update"])
@pytest.mark.parametrize("value", ["reset", ["reset", "remove"]], ids=["scalar", "list"])
def test_legacy_mass_metadata_operations_accept_scalar_and_list(operation: str, value: str | list[str]) -> None:
    with (SCHEMA_DIR / "config-schema.json").open(encoding="utf-8") as fh:
        schema = json.load(fh)

    operation_schema = schema["definitions"]["operations"]["oneOf"][0]["properties"][operation]
    assert list(Draft7Validator(operation_schema).iter_errors(value)) == []


@pytest.mark.parametrize("schema_path", SCHEDULE_SCHEMA_FILES, ids=lambda p: p.name)
@pytest.mark.parametrize("schedule", ["weekly(monday)", ["non_existing", "range(10/05-10/31)"]])
def test_schedule_schema_accepts_string_or_list(schema_path: Path, schedule) -> None:
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)

    assert list(Draft7Validator(schema["definitions"]["schedule"]).iter_errors(schedule)) == []


@pytest.mark.parametrize("schema_path", SCHEDULE_SCHEMA_FILES, ids=lambda p: p.name)
@pytest.mark.parametrize("schedule", [[], ["daily", 1], [True], None, 1, {}])
def test_schedule_schema_rejects_invalid_values(schema_path: Path, schedule) -> None:
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)

    assert list(Draft7Validator(schema["definitions"]["schedule"]).iter_errors(schedule))


@pytest.mark.parametrize("schema_path", SCHEDULE_SCHEMA_FILES, ids=lambda p: p.name)
def test_schedule_properties_use_shared_definition(schema_path: Path) -> None:
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)

    declarations = []

    def find_schedule_properties(value, path=()):
        if isinstance(value, dict):
            for key, child in value.items():
                if path != ("definitions",) and key in {"schedule", "schedule_overlays", "^schedule_.*$"} and isinstance(child, dict):
                    declarations.append(child)
                find_schedule_properties(child, (*path, key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                find_schedule_properties(child, (*path, index))

    find_schedule_properties(schema)

    assert declarations

    def references_shared_schedule(declaration):
        if declaration.get("$ref") == "#/definitions/schedule":
            return True
        return any(item.get("$ref") == "#/definitions/schedule" for item in declaration.get("allOf", []))

    assert all(references_shared_schedule(declaration) for declaration in declarations)


@pytest.mark.parametrize("schema_path", [SCHEMA_DIR / "config-schema.json", SCHEMA_DIR / "collection-schema.json"], ids=lambda p: p.name)
def test_scheduled_visibility_uses_shared_schedule_definition(schema_path: Path) -> None:
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)

    declarations = _scheduled_visibility_declarations(schema)

    assert declarations
    assert all({"type": "boolean"} in declaration.get("oneOf", []) and any(item.get("$ref") == "#/definitions/schedule" for item in declaration.get("oneOf", [])) for declaration in declarations)


@pytest.mark.parametrize("schema_path", [SCHEMA_DIR / "config-schema.json", SCHEMA_DIR / "collection-schema.json"], ids=lambda p: p.name)
@pytest.mark.parametrize("value", [True, False, "weekly(monday)", ["non_existing", "range(10/05-10/31)"]])
def test_scheduled_visibility_accepts_boolean_or_schedule(schema_path: Path, value) -> None:
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)

    for declaration in _scheduled_visibility_declarations(schema):
        scheduled_boolean = {"definitions": schema["definitions"], **declaration}
        assert list(Draft7Validator(scheduled_boolean).iter_errors(value)) == []


@pytest.mark.parametrize("schema_path", [SCHEMA_DIR / "config-schema.json", SCHEMA_DIR / "collection-schema.json"], ids=lambda p: p.name)
@pytest.mark.parametrize("value", [[], ["daily", 1], [True], None, 1, {}])
def test_scheduled_visibility_rejects_invalid_values(schema_path: Path, value) -> None:
    with schema_path.open(encoding="utf-8") as fh:
        schema = json.load(fh)

    for declaration in _scheduled_visibility_declarations(schema):
        scheduled_boolean = {"definitions": schema["definitions"], **declaration}
        assert list(Draft7Validator(scheduled_boolean).iter_errors(value))


def test_metadata_schema_accepts_movie_and_show_themes() -> None:
    with (SCHEMA_DIR / "metadata-schema.json").open(encoding="utf-8") as fh:
        schema = json.load(fh)

    metadata = {
        "metadata": {
            "Movie": {"url_theme": "https://example.com/movie-theme.mp3"},
            "Show": {"file_theme": "/config/themes/show-theme.mp3"},
        }
    }

    assert list(Draft7Validator(schema).iter_errors(metadata)) == []


def test_metadata_schema_rejects_season_themes() -> None:
    with (SCHEMA_DIR / "metadata-schema.json").open(encoding="utf-8") as fh:
        schema = json.load(fh)

    metadata = {"metadata": {"Show": {"seasons": {1: {"url_theme": "https://example.com/season-theme.mp3"}}}}}
    errors = list(Draft7Validator(schema).iter_errors(metadata))

    assert any("url_theme" in error.message for error in errors)


# ── 2. Defaults must be parseable YAML ────────────────────────────────────────


@pytest.mark.parametrize("yaml_path", DEFAULT_YAML_FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_default_file_is_valid_yaml(yaml_path: Path) -> None:
    """Each YAML file under defaults/ must parse without errors."""
    with yaml_path.open(encoding="utf-8") as fh:
        try:
            doc = yaml.safe_load(fh)
        except yaml.YAMLError as e:
            pytest.fail(f"{yaml_path.name} is not valid YAML: {e}")

    # Empty files would silently parse to None; flag them so they're caught.
    assert doc is not None, f"{yaml_path.name} parsed to None (empty file?)"


def test_at_least_one_default_exists() -> None:
    """Defensive: catch a layout change that hides all defaults from us."""
    assert DEFAULT_YAML_FILES, f"no YAML files found under {DEFAULTS_DIR}"


def test_rating_overlay_schema_matches_runtime_and_default() -> None:
    """Rating overlay completions must reflect sources supported by code and ratings.yml."""
    with (DEFAULTS_DIR / "overlays" / "ratings.yml").open(encoding="utf-8") as fh:
        ratings_default = yaml.safe_load(fh)
    direct_sources = ratings_default["templates"]["Rating"]["conditionals"]["plex_all"]["conditions"][0]["rating<<rating_num>>"]

    overlay_tree = ast.parse((REPO_ROOT / "modules" / "overlay.py").read_text(encoding="utf-8"))
    rating_sources = next(ast.literal_eval(node.value) for node in overlay_tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "rating_sources" for target in node.targets))
    runtime_sources = [source.removesuffix("_rating") for source in rating_sources]
    assert set(direct_sources) <= set(runtime_sources)

    with (SCHEMA_DIR / "config-schema.json").open(encoding="utf-8") as fh:
        config_schema = json.load(fh)

    rating_groups = []

    def find_rating_groups(value):
        if isinstance(value, dict):
            if all(key in value for key in ("rating1", "rating2", "rating3")):
                rating_groups.append(value)
            for child in value.values():
                find_rating_groups(child)
        elif isinstance(value, list):
            for child in value:
                find_rating_groups(child)

    find_rating_groups(config_schema)
    assert len(rating_groups) == 1
    expected = ["critic", "audience", "user", *direct_sources]
    for key in ("rating1", "rating2", "rating3"):
        assert rating_groups[0][key]["enum"] == expected


def test_seasonal_template_variables_accept_per_collection_use_flags() -> None:
    with (SCHEMA_DIR / "config-schema.json").open(encoding="utf-8") as fh:
        schema = json.load(fh)

    seasonal_schema = schema["definitions"]["seasonal-template-vars"]
    validator = Draft7Validator(seasonal_schema)
    variables = {
        "use_all": False,
        "use_christmas": True,
        "use_easter": True,
        "use_father": True,
        "use_halloween": True,
        "use_mother": True,
        "use_years": True,
        "use_valentine": True,
        "sort_by": "random",
    }

    assert list(validator.iter_errors(variables)) == []


def test_tracearr_default_uses_short_trending_window_without_raw_history_and_sets_logos() -> None:
    with (DEFAULTS_DIR / "chart" / "tracearr.yml").open(encoding="utf-8") as fh:
        tracearr_default = yaml.safe_load(fh)

    collections = tracearr_default["collections"]
    tracearr_template = tracearr_default["templates"]["tracearr"]
    assert tracearr_template["default"]["list_minimum"] == 0
    assert tracearr_template["default"]["list_minimum_<<key>>"] == "<<list_minimum>>"
    assert tracearr_template["tracearr_<<type>>"]["list_minimum"] == "<<list_minimum_<<key>>>>"
    assert collections["Tracearr Trending"]["variables"]["list_days"] == 7
    assert "Tracearr History" not in collections
    expected_logo = "https://raw.githubusercontent.com/Kometa-Team/Default-Images/master/chart/logos/tracearr.png"
    for collection in collections.values():
        shared_template = next(template for template in collection["template"] if template["name"] == "shared")
        assert shared_template["url_logo"] == expected_logo


@pytest.mark.parametrize("value", ["config/collections", ["config/collections", "config/shared"], None])
@pytest.mark.parametrize("level", ["global", "library", "file", "collection"])
def test_collection_asset_directory_schema_levels(value, level):
    if level == "collection":
        schema = json.loads((SCHEMA_DIR / "collection-schema.json").read_text())
        document = {"collections": {"Test": {"plex_all": True, "asset_directory": {"Movies": value, "collections": value}}}}
    else:
        schema = json.loads((SCHEMA_DIR / "config-schema.json").read_text())
        document = {"libraries": {"Movies": {"collection_files": []}}, "plex": {"url": "http://localhost:32400", "token": "test"}, "tmdb": {"apikey": "test"}}
        if level == "global":
            document["settings"] = {"asset_directory": {"Movies": value, "collections": value}}
        elif level == "library":
            document["libraries"]["Movies"]["settings"] = {"asset_directory": {"Movies": value, "collections": value}}
        else:
            document["libraries"]["Movies"]["collection_files"] = [{"file": "config/collections.yml", "asset_directory": {"Movies": value, "collections": value}}]
    errors = list(Draft7Validator(schema).iter_errors(document))
    assert not errors, [error.message for error in errors]
