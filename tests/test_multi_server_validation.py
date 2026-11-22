"""Fixture-driven checks through the real config parser; no live APIs."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from jsonschema import Draft7Validator
from ruamel.yaml import YAML

import modules.builder  # noqa: F401 - breaks circular imports
import modules.config as config_module
from modules.builder import CollectionBuilder
from modules.library import Library
from modules.library_config import expand_libraries
from modules.plex import Plex
from modules.util import Failed
from scripts import validate_multi_server as harness
from tests.factories import make_builder
from tests.test_config import _patch_everything, make_config  # noqa: F401 - reuse API isolation fixture

FIXTURES = Path(__file__).parent / "fixtures" / "multi_server"


def load(name):
    return YAML(typ="safe").load((FIXTURES / name).read_text())


@pytest.mark.parametrize("filename", ["playlists.yml", "playlists-cross-server.yml"])
def test_playlist_fixture_search_builds_valid_plex_filter(filename):
    from modules.builder import custom_sort_builders

    definition = next(iter(load(filename)["playlists"].values()))
    library = Plex.__new__(Plex)
    library.is_movie, library.is_show, library.is_music = True, False, False
    builder = make_builder(library=library, playlist=True, Type="Playlist")
    assert "plex_all" not in definition
    assert "plex_search" in custom_sort_builders
    _, _, url = builder.build_filter("plex_search", definition["plex_search"])
    assert "sort=titleSort" in url
    assert "1800" in url


def dump(data):
    from io import StringIO

    stream = StringIO()
    YAML().dump(data, stream)
    return stream.getvalue()


@pytest.fixture
def adapters(monkeypatch):
    seen = []

    def constructor(kind):
        def connect(config, params):
            seen.append((kind, params))
            if params["server"].url == "http://127.0.0.1:1":
                raise Failed("Deliberately unavailable validation server")
            library = MagicMock()
            library.original_mapping_name = params["mapping_name"]
            library.name = params["name"]
            library.server = params["server"]
            library.type = "Movie"
            library.collections = []
            library.collection_files = params["collection_files"] or ["validation.yml"]
            return library

        return connect

    for kind in ("Plex", "Silo", "Emby", "Jellyfin"):
        monkeypatch.setattr(config_module, kind, constructor(kind))
    return seen


def test_real_parser_dispatch_and_remote_names(tmp_path, adapters):
    config = make_config(tmp_path, config_yaml=dump(load("shared.yml")))
    assert [(kind, params["name"]) for kind, params in adapters] == [("Plex", "Movies"), ("Silo", "Cinema"), ("Emby", "Films")]
    assert list(config.library_map) == ["Movies@my-plex", "Movies@my-silo", "Movies@my-emby"]
    assert len({id(library) for library in config.libraries}) == 3
    assert all(library.scan_files.call_count == 1 for library in config.libraries)
    assert not config.general["plex"]["url"]


def test_real_parser_shelf_option_accepts_per_server_override(tmp_path, adapters):
    data = load("shared.yml")
    data["libraries"]["Movies"]["silo_shelves"] = True
    data["libraries"]["Movies"]["servers"]["my-plex"]["silo_shelves"] = False
    make_config(tmp_path, config_yaml=dump(data))
    assert [params["silo_shelves"] for _, params in adapters] == [False, True, True]


@pytest.mark.parametrize("selection,expected", [("Movies", ["Plex", "Silo", "Emby"]), ("Movies@my-silo", ["Silo"]), ("Movies@my-plex|Movies@my-emby", ["Plex", "Emby"])])
def test_real_parser_selection(tmp_path, adapters, selection, expected):
    make_config(tmp_path, config_yaml=dump(load("shared.yml")), attrs={"libraries": selection})
    assert [kind for kind, _ in adapters] == expected


def test_connection_failure_does_not_stop_later_targets(tmp_path, adapters):
    data = load("shared.yml")
    data["media_servers"]["my-plex"]["url"] = "http://127.0.0.1:1"
    config = make_config(tmp_path, config_yaml=dump(data))
    assert [kind for kind, _ in adapters] == ["Plex", "Silo", "Emby"]
    assert list(config.library_map) == ["Movies@my-silo", "Movies@my-emby"]
    assert any("Movies@my-plex" in message and "Connection Failed" in message for message in config_module.logger.info_messages)


@pytest.mark.parametrize("stage", ["overlays", "operations"])
def test_stage_configs_reach_real_parser_with_isolated_paths(tmp_path, adapters, monkeypatch, stage):
    directory = tmp_path / "run"
    directory.mkdir()
    harness.write_yaml(directory / "config.yml", load("shared.yml"))

    def fake_run(command, **kwargs):
        path = Path(command[command.index("--config") + 1])
        make_config(tmp_path, config_yaml=path.read_text())
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(harness.subprocess, "run", fake_run)
    # No completion output: this test checks config dispatch, not smoke success.
    assert harness.live(SimpleNamespace(directory=directory, case=[stage], target="my-silo", timeout=10)) == 1
    assert [kind for kind, _ in adapters] == ["Plex", "Silo", "Emby"]
    for (_, params), target in zip(adapters, ("my-plex", "my-silo", "my-emby")):
        if stage == "operations":
            assert params["metadata_backup"]["path"] == str(directory / stage / f"Movies@{target}_Metadata_Backup.yml")
            assert not params["overlay_files"]
        else:
            assert params["overlay_files"]
            assert not params["metadata_backup"]


def test_real_library_default_paths_and_cache_names_are_isolated(tmp_path, adapters):
    config = make_config(tmp_path, config_yaml=dump(load("shared.yml")))
    cache_names = []
    config.Cache = MagicMock()

    def table(name):
        cache_names.append(name)
        return f"image_map_{len(cache_names)}"

    config.Cache.get_image_table_name.side_effect = table
    libraries = []
    for _, params in adapters:
        library = Plex.__new__(Plex)
        Library.__init__(library, config, params)
        libraries.append(library)
    for attribute in ("mapping_name", "overlay_backup", "report_path", "image_table_name"):
        assert len({getattr(library, attribute) for library in libraries}) == 3
    assert cache_names == list(config.library_map)
    assert len({id(library.report_data) for library in libraries}) == 3


@pytest.mark.parametrize("name,settings", list(load("invalid.yml").items()))
def test_invalid_fixture_cases(name, settings):
    with pytest.raises(Failed):
        expand_libraries({name: settings}, load("shared.yml")["media_servers"])


def test_playlist_target_names_resolve_and_shared_name_is_not_ambiguous(tmp_path, adapters):
    config = make_config(tmp_path, config_yaml=dump(load("shared.yml")))
    definition = next(iter(load("playlists.yml")["playlists"].values()))
    names = CollectionBuilder._playlist_libraries(config, definition, {key: key for key in definition})
    assert [config.library_map[name].server.type_name for name in names] == ["plex"]
    assert "Movies" not in config.library_map
    config.run_libraries = config.libraries
    assert CollectionBuilder._playlist_libraries(config, {}, {}) == list(config.library_map)


@pytest.mark.xfail(strict=True, reason="Per-server override schema still accepts arbitrary objects")
@pytest.mark.parametrize("name,settings", list(load("invalid-overrides.yml").items()))
def test_override_schema_gap(name, settings):
    schema = json.loads((FIXTURES.parents[2] / "json-schema" / "config-schema.json").read_text())
    validator = Draft7Validator({"$ref": "#/definitions/library-section", "definitions": schema["definitions"]})
    assert not validator.is_valid({"Movies": settings}), name


@pytest.mark.parametrize(
    "filename,schema_name",
    [
        ("collections.yml", "collection-schema.json"),
        ("playlists.yml", "playlist-schema.json"),
        ("playlists-cross-server.yml", "playlist-schema.json"),
        ("overlays.yml", "overlay-schema.json"),
        ("shelves.yml", "collection-schema.json"),
        ("shelves-default.yml", "collection-schema.json"),
        ("shelves-earlier.yml", "collection-schema.json"),
    ],
)
def test_definition_fixtures_match_schema(filename, schema_name):
    schema = json.loads((FIXTURES.parents[2] / "json-schema" / schema_name).read_text())
    Draft7Validator(schema).validate(load(filename))
