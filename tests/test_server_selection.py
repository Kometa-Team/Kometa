"""CLI server filters compose with library selection before adapter connections."""

import argparse
import ast
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from modules.library_config import expand_libraries
from modules.util import Failed


def resolve_arguments(monkeypatch, flags, environment=None):
    source = ast.parse((Path(__file__).resolve().parents[1] / "kometa.py").read_text())
    start = next(i for i, node in enumerate(source.body) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "arguments" for target in node.targets))
    end = next(i for i, node in enumerate(source.body) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "env_branch" for target in node.targets))
    for key in tuple(os.environ):
        if key.startswith(("KOMETA_", "PMM_")):
            monkeypatch.delenv(key)
    for key, value in (environment or {}).items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, "argv", ["kometa.py", *flags])
    namespace = {"argparse": argparse, "os": os}
    exec(compile(ast.Module(body=source.body[start:end], type_ignores=[]), "kometa-server-arguments", "exec"), namespace)
    return namespace


@pytest.mark.parametrize("kind", ["plex", "silo", "emby", "jellyfin"])
def test_backend_filter_cli_and_environment(monkeypatch, kind):
    for flags, env in [(["-rl", "Movies", f"--{kind}-only"], {}), (["-rl", "Movies"], {f"KOMETA_{kind.upper()}_ONLY": "true"})]:
        result = resolve_arguments(monkeypatch, flags, env)
        assert result["server_only"] == [kind]
        assert result["run_args"]["run-libraries"] == "Movies"
        assert not result["unknown"]


@pytest.mark.parametrize("flags,env", [(["--silo-only", "--plex-only"], {}), (["--silo-only"], {"KOMETA_EMBY_ONLY": "true"}), (["-rs", ""], {}), (["-rs", "my-silo|"], {})])
def test_invalid_cli_server_filters_fail_early(monkeypatch, flags, env):
    with pytest.raises(SystemExit) as error:
        resolve_arguments(monkeypatch, flags, env)
    assert error.value.code == 2


def test_named_server_selection_uses_standard_argument_resolution(monkeypatch):
    result = resolve_arguments(monkeypatch, ["-rs", "silo-one|silo-two", "--silo-only"])
    assert result["run_args"]["run-servers"] == "silo-one|silo-two"
    assert result["server_only"] == ["silo"]
    result = resolve_arguments(monkeypatch, [], {"KOMETA_RUN_SERVERS": "silo-one"})
    assert result["run_args"]["run-servers"] == "silo-one"
    assert "KOMETA_RUN_SERVERS" in result["static_envs"]


def test_backend_filter_combines_with_operation_filter(monkeypatch):
    result = resolve_arguments(monkeypatch, ["-rl", "Movies", "--silo-only", "--overlays-only"])
    assert result["server_only"] == ["silo"]
    assert result["run_args"]["overlays-only"] is True


@pytest.fixture
def connections():
    return {name: SimpleNamespace(type_name=kind) for name, kind in [("plex", "plex"), ("silo-one", "silo"), ("silo-two", "silo"), ("emby", "emby"), ("jellyfin", "jellyfin")]}


@pytest.mark.parametrize("kind", ["plex", "silo", "emby", "jellyfin"])
def test_backend_filter_selects_all_servers_of_that_type(connections, kind):
    libraries = {"Movies": {"servers": {name: {} for name in connections}}}
    results = expand_libraries(libraries, connections, ["Movies"], server_types=[kind])
    assert [identity for identity, _ in results] == [f"Movies@{name}" for name, server in connections.items() if server.type_name == kind]


def test_library_name_server_identity_and_type_filters_intersect(connections):
    libraries = {"Movies": {"servers": {name: {} for name in connections}}, "Shows": {"server": "silo-two"}}
    results = expand_libraries(libraries, connections, ["Movies"], ["silo-two"], ["silo"])
    assert [identity for identity, _ in results] == ["Movies@silo-two"]
    assert [identity for identity, _ in expand_libraries(libraries, connections, ["Movies@silo-one"], server_types=["silo"])] == ["Movies@silo-one"]
    assert [identity for identity, _ in expand_libraries(libraries, connections, requested_servers=["silo-two"])] == ["Movies@silo-two", "Shows"]


def test_plex_filter_includes_legacy_top_level_connection(connections):
    libraries = {"Legacy": {}, "Named": {"server": "plex"}, "Native": {"server": "silo-one"}}
    assert [identity for identity, _ in expand_libraries(libraries, connections, server_types=["plex"])] == ["Legacy", "Named"]
    assert [identity for identity, _ in expand_libraries(libraries, connections, requested_servers=["plex"])] == ["Named"]


@pytest.mark.parametrize("names,kinds", [(["missing"], None), ([""], None), ([], None), (["plex"], ["silo"]), (None, ["unknown"])])
def test_unknown_empty_or_nonmatching_filters_never_select_everything(connections, names, kinds):
    with pytest.raises(Failed):
        expand_libraries({"Movies": {"server": "silo-one"}}, connections, requested_servers=names, server_types=kinds)
