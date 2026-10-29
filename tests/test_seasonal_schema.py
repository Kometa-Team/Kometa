"""Full-config seasonal schema contracts, derived from the shipped templates."""

import copy
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "json-schema"
SUFFIXES = ("years", "valentine", "halloween")

# Public inputs consumed by holiday/shared/arr/separator, and the custom
# dynamic-collection machinery. Generated template variables are excluded below.
GLOBAL_VALUES = {
    "collection_section": "090",
    "name_mapping": "<<key_name>>",
    "sort_prefix": "!",
    "sort_title": "<<collection_section>>_<<title>>",
    "pre": "_",
    "order": 1,
    "sort": "<<title>>",
    "schedule": ["daily", "range(12/26-01/04)"],
    "visible_home": True,
    "visible_library": False,
    "visible_shared": "weekly(friday)",
    "url_poster": "https://example.com/poster.jpg",
    "file_poster": "/config/poster.jpg",
    "url_background": "https://example.com/background.jpg",
    "file_background": "/config/background.jpg",
    "url_logo": "https://example.com/logo.png",
    "file_logo": "/config/logo.png",
    "url_square_art": "https://example.com/square.jpg",
    "file_square_art": "/config/square.jpg",
    "minimum_items": 1,
    "hub_priority": 2,
    "ignore_ids": [550, "603"],
    "ignore_imdb_ids": ["tt0133093"],
    "limit": 20,
    "radarr_add_missing": False,
    "radarr_folder": "/movies",
    "radarr_tag": ["seasonal"],
    "radarr_monitor": True,
    "radarr_monitor_existing": False,
    "radarr_search": True,
    "radarr_upgrade_existing": False,
    "sonarr_add_missing": False,
    "sonarr_folder": "/shows",
    "sonarr_tag": ["seasonal"],
    "sonarr_monitor": "all",
    "sonarr_monitor_existing": False,
    "sonarr_search": True,
    "sonarr_upgrade_existing": False,
    "item_radarr_tag": ["holiday"],
    "item_sonarr_tag": ["holiday"],
    "delete_collections_named": ["Old Holiday Movies"],
    "image": "seasonal/years",
    "translation_key": "seasonal",
    "dynamic": True,
    "sync_mode": "sync",
    "collection_mode": "hide",
    "use_all": True,
    "placeholder_imdb_id": "tt0133093",
    "placeholder_tmdb_movie": 603,
    "placeholder_tvdb_show": 81189,
    "sep_style": "orig",
    "use_separator": False,
    "name_separator": "Seasonal",
    "summary_separator": "Holiday collections",
    "url_poster_separator": "https://example.com/separator.jpg",
    "sort_by": ["title.asc", "year.desc"],
    "name_format": "<<key_name>> Movies",
    "summary_format": "Movies for <<key_name>>",
    "language": "en",
    "emoji": "\U0001f389 ",
    "allowed_libraries": ["movie"],
    "data": {"years": "New Year's Day", "valentine": "Valentine's Day"},
    "append_data": {"apes": "Planet of the Apes Day"},
    "remove_data": ["halloween"],
    "exclude": ["christmas"],
    "append_exclude": ["easter"],
    "remove_exclude": ["christmas"],
    "include": ["years", "valentine"],
    "append_include": ["halloween"],
    "remove_include": ["valentine"],
    "addons": {"years": ["valentine"]},
    "append_addons": {"years": "halloween"},
    "remove_addons": {"years": ["valentine"]},
    "custom_keys": True,
    "title_format": "<<key_name>> Movies",
    "title_override": {"years": "New Year Movies"},
    "key_name_override": {"years": "New Year"},
    "remove_prefix": ["The "],
    "remove_suffix": [" Day"],
    "other_name": "Other Holidays",
    "test": False,
    "sync": False,
}
KEYED_VALUES = {
    "name": "New Year's Movies",
    "summary": "Movies celebrating the new year",
    "emoji": "\U0001f389 ",
    "sync_mode": "append",
    "sort_by": ["title.asc", "year.desc"],
    "limit": 10,
    "schedule": ["daily", "range(12/26-01/04)"],
    "visible_home": "range(12/26-01/04)",
    "visible_library": False,
    "visible_shared": ["weekly(friday)", "range(12/26-01/04)"],
    "use": True,
    "order": "001",
    "minimum_items": 1,
    "hub_priority": 3,
    "url_poster": "https://example.com/poster.jpg",
    "file_poster": "/config/poster.jpg",
    "url_background": "https://example.com/background.jpg",
    "file_background": "/config/background.jpg",
    "url_logo": "https://example.com/logo.png",
    "file_logo": "/config/logo.png",
    "url_square_art": "https://example.com/square.jpg",
    "file_square_art": "/config/square.jpg",
    "radarr_add_missing": False,
    "radarr_folder": "/movies",
    "radarr_tag": ["seasonal"],
    "radarr_monitor": True,
    "radarr_monitor_existing": False,
    "radarr_search": True,
    "radarr_upgrade_existing": False,
    "sonarr_add_missing": False,
    "sonarr_folder": "/shows",
    "sonarr_tag": ["seasonal"],
    "sonarr_monitor": "future",
    "sonarr_monitor_existing": False,
    "sonarr_search": True,
    "sonarr_upgrade_existing": False,
    "item_radarr_tag": ["holiday"],
    "item_sonarr_tag": ["holiday"],
    "delete_collections_named": ["Old Holiday Movies", "Another Holiday Movies"],
}
BUILDER_VALUES = {
    "tmdb_collection": [185103, "11716", "https://www.themoviedb.org/collection/8091", [185103, "11716"]],
    "tmdb_movie": [603, "550", "https://www.themoviedb.org/movie/603", [603, "550"]],
    "imdb_list": [
        "https://www.imdb.com/list/ls066838460/",
        {"list_id": "ls066838460", "sort_by": "custom.asc", "limit": 0},
        {"url": "https://www.imdb.com/list/ls066838460/", "limit": 20},
        ["ls066838460", {"list_id": "ls023525790", "limit": 10}],
    ],
    "imdb_search": [
        {"list.any": ["ls066838460", "ls023525790"], "limit": 500},
        {"keyword.any": ["holiday", "new-year"], "type": ["movie", "tv_movie"], "sort_by": "rating.desc"},
        [{"list.any": "ls066838460"}, {"keyword.any": "holiday"}],
        {"content_rating": [{"region": "US", "rating": "PG"}], "title": "Holiday"},
    ],
    "mdblist_list": [
        "https://mdblist.com/lists/k0meta/christmas-extravaganza",
        {"url": "https://mdblist.com/lists/k0meta/christmas-extravaganza", "limit": 0, "sort_by": "score"},
        ["https://mdblist.com/lists/k0meta/christmas-extravaganza", {"url": "https://mdblist.com/lists/k0meta/asian-american-pacific-islander-heritage-month", "limit": 10}],
    ],
    "letterboxd_list": [
        "https://letterboxd.com/patrickb15/list/christmas/",
        {"url": "https://letterboxd.com/patrickb15/list/christmas/", "limit": 0, "note": "holiday", "year": "2000-2025", "rating": "5-10"},
        ["https://letterboxd.com/patrickb15/list/christmas/", {"url": "https://letterboxd.com/mardarrius/list/black-is-beautiful/", "limit": 10, "rating": 8}],
    ],
}
POSITIVE_CASES = list(GLOBAL_VALUES.items()) + [(f"{key}_{suffix}", value) for suffix in SUFFIXES for key, value in KEYED_VALUES.items()]
POSITIVE_CASES += [(key + suffix, value) for key, values in BUILDER_VALUES.items() for suffix in ("", "_years", "_valentine", "_halloween") for value in values]
NEGATIVE_CASES = [
    ("name_years", 1),
    ("summary_valentine", []),
    ("emoji_halloween", False),
    ("sync_mode_years", "replace"),
    ("sync_mode_years", True),
    ("limit_halloween", 0),
    ("limit_years", "ten"),
    ("schedule_years", []),
    ("schedule_years", ["daily", 1]),
    ("schedule_years", {}),
    ("schedule_years", True),
    ("sort_by", {}),
    ("sort_by_halloween", [1]),
    ("minimum_items_years", 0),
    ("hub_priority_valentine", False),
    ("order_years", []),
    ("file_logo_years", {}),
    ("url_square_art_valentine", False),
    ("tmdb_collection_years", {"id": 185103}),
    ("tmdb_movie_valentine", [603, {}]),
    ("tmdb_movie", True),
    ("imdb_list_years", {"list_id": "invalid"}),
    ("imdb_list_years", {"url": "https://www.imdb.com/list/ls066838460/", "unknown": 1}),
    ("imdb_search_years", "https://www.imdb.com/search/title/"),
    ("imdb_search_years", {"unknown": "holiday"}),
    ("imdb_search_years", {"sort_by": "nonsense"}),
    ("imdb_search_years", {"list.any": [1]}),
    ("imdb_search_years", [{}]),
    ("mdblist_list_years", {"limit": 10}),
    ("mdblist_list_years", {"url": "https://mdblist.com/lists/k0meta/test", "limit": -1}),
    ("letterboxd_list_years", {"url": "https://letterboxd.com/test/list/test/", "rating": {}}),
    ("letterboxd_list_years", {"url": "https://letterboxd.com/test/list/test/", "unknown": True}),
    ("delete_collections_named_years", [False]),
    ("radarr_monitor_years", "collection"),
    ("sonarr_monitor_years", True),
    ("sonarr_monitor_years", "everything"),
    ("sonarr_monitor_existing_years", "future"),
    ("sonarr_tag_years", [False]),
    ("data", []),
    ("append_data", {"apes": []}),
    ("remove_addons", ["years"]),
    ("title_override", {"years": []}),
    ("allowed_libraries", {}),
    ("custom_keys", []),
    ("sync", {}),
    ("remove_prefix", {}),
    ("visible_home_years", {}),
    ("visible_shared_valentine", [True]),
    ("unknown", True),
    ("name_", "Empty suffix"),
    ("collection_order_years", "custom"),
    ("trakt_list_years", "https://trakt.tv/users/test/lists/holidays"),
    ("image_years", "seasonal/years"),
    ("translation_key_years", "seasonal"),
    ("cache_builders_years", 0),
    ("tmdb_show_years", 1399),
    ("key", "years"),
    ("smart_label", "Holiday"),
]


def full_config(variables, default="seasonal"):
    return {"plex": {"url": "http://localhost:32400", "token": "test"}, "tmdb": {"apikey": "test"}, "libraries": {"Movies": {"collection_files": [{"default": default, "template_variables": variables}]}}}


@pytest.fixture(scope="module")
def schema():
    return json.loads((SCHEMA_DIR / "config-schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator(schema):
    return Draft7Validator(schema)


@pytest.mark.parametrize("key,value", POSITIVE_CASES, ids=[f"{key}-{index}" for index, (key, _) in enumerate(POSITIVE_CASES)])
def test_supported_seasonal_override_in_full_config(validator, key, value):
    errors = list(validator.iter_errors(full_config({key: value})))
    assert not errors, [error.message for error in errors]


@pytest.mark.parametrize("key,value", NEGATIVE_CASES, ids=[f"{key}-{index}" for index, (key, _) in enumerate(NEGATIVE_CASES)])
def test_invalid_or_unsupported_seasonal_override_is_rejected(validator, key, value):
    assert list(validator.iter_errors(full_config({key: value})))


def test_seasonal_overrides_work_together(validator):
    variables = copy.deepcopy(GLOBAL_VALUES)
    for suffix in SUFFIXES:
        variables.update({f"{key}_{suffix}": value for key, value in KEYED_VALUES.items()})
        variables.update({f"{key}_{suffix}": values[0] for key, values in BUILDER_VALUES.items()})
    validator.validate(full_config(variables))


def test_documented_custom_season_example(validator):
    validator.validate(full_config({"append_data": {"apes": "Planet of the Apes Day"}, "schedule_apes": ["daily", "range(11/24-11/26)"], "imdb_list_apes": "https://www.imdb.com/list/ls005126084/", "emoji_apes": "\U0001f435 "}))


def test_every_inherited_template_input_has_a_schema_contract(validator):
    """New public inputs in a shipped seasonal template must gain schema coverage."""
    seasonal = yaml.safe_load((ROOT / "defaults/movie/seasonal.yml").read_text(encoding="utf-8"))
    shared = yaml.safe_load((ROOT / "defaults/templates.yml").read_text(encoding="utf-8"))["templates"]
    # These describe generated keys, template identity or intermediate conditions,
    # rather than public seasonal overrides. key_name_override is the public API
    # for key_name; data/append_data configure keys.
    internal = {"key", "key_name", "mapping_name", "smart_label", "title", "separator", "final_use", "use_blank"}
    contracts = dict(POSITIVE_CASES)
    missing = set()
    templates = [("holiday", seasonal["templates"]["holiday"]), *[(name, shared[name]) for name in ("shared", "arr", "separator")]]
    for name, template in templates:
        inputs = set(template.get("default", {})) | set(template.get("optional", []))
        inputs.update(re.findall(r"<<([a-z_]+)>>", json.dumps(template)))
        for variable in inputs - internal:
            variable = variable.replace("<<key>>", "separator" if name == "separator" else "years")
            if variable not in contracts:
                missing.add(variable)
            else:
                validator.validate(full_config({variable: contracts[variable]}))
    assert not missing, f"Classify and cover new seasonal template inputs: {sorted(missing)}"


def test_runtime_radarr_and_sonarr_monitor_types():
    from modules.builder import CollectionBuilder

    builder = SimpleNamespace(Type="Collection", radarr_details={}, sonarr_details={})
    CollectionBuilder._radarr(builder, "radarr_monitor", False)
    CollectionBuilder._sonarr(builder, "sonarr_monitor", "future")
    assert builder.radarr_details["monitor"] is False
    assert builder.sonarr_details["monitor"] == "future"


def test_runtime_imdb_search_accepts_structured_lists():
    from modules.builder import CollectionBuilder

    builder = SimpleNamespace(Type="Collection", builders=[])
    CollectionBuilder._imdb(builder, "imdb_search", BUILDER_VALUES["imdb_search"][0])
    assert builder.builders[0][1]["list.any"] == ["ls066838460", "ls023525790"]


def test_seasonal_schema_stays_closed_and_visibility_definitions_are_preserved(schema):
    seasonal = schema["definitions"]["seasonal-template-vars"]
    assert seasonal["additionalProperties"] is False
    general = schema["definitions"]["template-variables-collections"]
    for visibility in ("home", "library", "shared"):
        pattern = f"^visible_{visibility}_.+$"
        assert seasonal["patternProperties"][pattern] == general["patternProperties"][pattern]


def test_supported_property_patterns_do_not_conflict(schema):
    seasonal = schema["definitions"]["seasonal-template-vars"]
    for key, value in POSITIVE_CASES:
        for pattern, declaration in seasonal["patternProperties"].items():
            if re.search(pattern, key):
                Draft7Validator({"definitions": schema["definitions"], **declaration}).validate(value)


@pytest.mark.parametrize("default", ["imdb", "genre", "oscars"])
def test_nonseasonal_defaults_keep_existing_overrides(validator, default):
    validator.validate(full_config({"name_format": "<<key_name>> Movies", "use_all": True, "visible_home": True, "schedule": ["daily"], "minimum_items": 1}, default))


def test_imdb_search_schema_keys_follow_the_runtime(schema):
    from modules.imdb import imdb_search_attributes

    assert set(schema["definitions"]["seasonal-imdb-search"]["properties"]) == set(imdb_search_attributes)
