"""Shared library targets keep configuration and state independent."""

import pytest

from modules.library_config import expand_libraries
from modules.util import Failed


def test_expands_inherits_and_isolates_targets():
    libraries = {"Movies": {"servers": {"plex": {}, "silo": {"library_name": "Cinema"}}, "collection_files": [{"file": "shared.yml"}]}}
    targets = expand_libraries(libraries, {"plex": object(), "silo": object()})
    assert [name for name, _ in targets] == ["Movies@plex", "Movies@silo"]
    assert [data["library_name"] for _, data in targets] == ["Movies", "Cinema"]
    assert [data["server"] for _, data in targets] == ["plex", "silo"]
    targets[0][1]["collection_files"][0]["file"] = "changed.yml"
    assert targets[1][1]["collection_files"] == libraries["Movies"]["collection_files"]


def test_selection_and_legacy_configuration():
    libraries = {"Movies": {"servers": {"a": {}, "b": {}}}, "Shows": {"server": "a"}}
    servers = {"a": object(), "b": object()}
    assert len(expand_libraries(libraries, servers, ["Movies"])) == 2
    assert [name for name, _ in expand_libraries(libraries, servers, ["Movies@b"])] == ["Movies@b"]
    assert expand_libraries(libraries, servers, ["Shows"]) == [("Shows", {"server": "a"})]


@pytest.mark.parametrize("settings", [{"servers": {}}, {"servers": ["a"]}, {"servers": {"missing": {}}}, {"servers": {"a": None}}, {"server": "a", "servers": {"a": {}}}, {"servers": {"a": {"server": "b"}}}])
def test_rejects_invalid_targets(settings):
    with pytest.raises(Failed):
        expand_libraries({"Movies": settings}, {"a": object()})


def test_rejects_collision_with_explicit_library():
    with pytest.raises(Failed, match="Duplicate library identity"):
        expand_libraries({"Movies": {"servers": {"a": {}}}, "Movies@a": {}}, {"a": object()})


def test_schema_accepts_targets_and_rejects_conflicting_selectors():
    import json
    from pathlib import Path

    from jsonschema import Draft7Validator

    schema = json.loads((Path(__file__).parents[1] / "json-schema" / "config-schema.json").read_text())
    validator = Draft7Validator({"$ref": "#/definitions/library-section", "definitions": schema["definitions"]})
    valid = {"Movies": {"servers": {"a": {}, "b": {"library_name": "Cinema"}}}}
    assert not list(validator.iter_errors(valid))
    for invalid in ({"servers": {}}, {"server": "a", "servers": {"a": {}}}, {"servers": {"a": {"server": "b"}}}):
        assert list(validator.iter_errors({"Movies": invalid}))
