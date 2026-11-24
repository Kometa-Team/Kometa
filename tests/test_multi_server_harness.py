"""The smoke runner must not report success just because Kometa exits zero."""

import os
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import validate_multi_server as harness


def prepare_config(tmp_path):
    output = tmp_path / "run"
    harness.prepare(Namespace(source=harness.FIXTURES / "shared.yml", output=output, plex="my-plex", silo="my-silo", emby="my-emby", library=["my-silo=Cinema", "my-emby=Films"]))
    return output


def test_prepare_is_isolated_and_does_not_overwrite(tmp_path):
    output = prepare_config(tmp_path)
    config = harness.read_yaml(output / "config.yml")
    assert config["libraries"]["Movies"]["servers"]["my-silo"]["library_name"] == "Cinema"
    assert Path(config["libraries"]["Movies"]["collection_files"][0]["file"]).is_absolute()
    assert set(config) == {"settings", "tmdb", "media_servers", "libraries"}
    with pytest.raises(FileExistsError):
        prepare_config(tmp_path)


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits are not enforced on Windows")
def test_prepare_uses_private_posix_permissions(tmp_path):
    output = prepare_config(tmp_path)
    assert output.stat().st_mode & 0o777 == 0o700
    assert (output / "config.yml").stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("omit_finish,extra_error,returncode,expected", [(False, False, 0, 0), (True, False, 0, 1), (False, True, 0, 1), (False, False, 1, 1)])
def test_live_assertions_on_mocked_process(tmp_path, monkeypatch, omit_finish, extra_error, returncode, expected):
    output = prepare_config(tmp_path)

    def fake_run(command, *, stdout, **kwargs):
        assert "--collections-only" in command
        assert "--read-only-config" in command
        for target in ("my-plex", "my-silo", "my-emby"):
            stdout.write(f"Movies (Movies@{target}) Library Connection Successful\n")
            stdout.write(f"Movies (Movies@{target}) Summary\n")
            if not omit_finish:
                stdout.write("Finished Kometa Multi-Server Validation Collection\n")
        if extra_error:
            stdout.write("Collection Error: Failed to create collection\n")
        return SimpleNamespace(returncode=returncode)

    monkeypatch.setattr(harness.subprocess, "run", fake_run)
    assert harness.live(Namespace(directory=output, case=["shared"], target="my-silo", timeout=10)) == expected
    assert (output / "results.json").exists()


def test_live_failure_case_requires_surviving_targets(tmp_path, monkeypatch):
    output = prepare_config(tmp_path)

    def fake_run(command, *, stdout, **kwargs):
        config = harness.read_yaml(Path(command[command.index("--config") + 1]))
        assert list(config["libraries"]["Movies"]["servers"])[0] == "unavailable"
        stdout.write("Movies (Movies@unavailable) Library Connection Failed\n")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(harness.subprocess, "run", fake_run)
    assert harness.live(Namespace(directory=output, case=["failure"], target="my-silo", timeout=10)) == 1


@pytest.mark.parametrize("stage", ["overlays", "operations"])
@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("problem", [None, "missing_completion", "missing_artifact", "error", "invalid_backup", "missing_upload"])
def test_stage_cases_require_completions_artifacts_and_no_errors(tmp_path, monkeypatch, stage, selected, problem):
    output = prepare_config(tmp_path)
    case = stage + ("-selected" if selected else "")
    targets = ["my-silo"] if selected else ["my-plex", "my-silo", "my-emby"]

    def fake_run(command, *, stdout, **kwargs):
        assert f"--{stage}-only" in command
        assert ("--libraries" in command) == selected
        if selected:
            assert command[command.index("--libraries") + 1] == "Movies@my-silo"
        path = Path(command[command.index("--config") + 1])
        library = harness.read_yaml(path)["libraries"]["Movies"]
        assert "collection_files" not in library
        for target in targets:
            overrides = library["servers"][target]
            stdout.write(f"Movies (Movies@{target}) Library Connection Successful\n")
            stdout.write(f"Movies (Movies@{target}) Summary\n")
            if problem != "missing_completion":
                stdout.write(f"Finished Movies Library {stage.title()}\n")
            if stage == "operations":
                assert "overlay_files" not in overrides
                assert set(overrides["operations"]) == {"metadata_backup"}
                backup = Path(overrides["operations"]["metadata_backup"]["path"])
                assert backup.parent == path.parent
                if problem != "missing_artifact":
                    backup.write_text("metadata: [" if problem == "invalid_backup" else "metadata:\n  Test Movie:\n    title: Test Movie\n")
            else:
                assert "operations" not in overrides
                assert Path(overrides["overlay_files"][0]["file"]).is_absolute()
                if problem != "missing_upload":
                    stdout.write("Overlays Applied: text(MULTI SERVER TEST)\n")
                if problem != "missing_artifact":
                    backup_dir = path.parent / "overlays" / f"Movies@{target} Original Posters"
                    backup_dir.mkdir(parents=True)
                    (backup_dir / "123.jpg").write_bytes(b"poster")
        if problem == "error":
            logs = path.parent / "logs"
            logs.mkdir()
            (logs / "meta.log").write_text("[ERROR] Stage failed\n")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(harness.subprocess, "run", fake_run)
    passed = problem is None or (stage == "overlays" and problem == "invalid_backup") or (stage == "operations" and problem == "missing_upload")
    assert harness.live(Namespace(directory=output, case=[case], target="my-silo", timeout=10)) == (0 if passed else 1)


@pytest.mark.parametrize("status", ["Assigned", "Unchanged", "missing", "wrong-server", "missing-order"])
def test_shelves_case_requires_each_collection_to_be_assigned_on_silo(tmp_path, monkeypatch, status):
    output = prepare_config(tmp_path)

    def fake_run(command, *, stdout, **kwargs):
        config = harness.read_yaml(Path(command[command.index("--config") + 1]))
        library = config["libraries"]["Movies"]
        assert library["silo_shelves"] is True
        assert {Path(entry["file"]).name for entry in library["collection_files"]} == {"shelves.yml", "shelves-default.yml", "shelves-earlier.yml"}
        for target in ("my-plex", "my-silo", "my-emby"):
            stdout.write(f"Movies (Movies@{target}) Library Connection Successful\nMovies (Movies@{target}) Summary\n")
            for title in ("Custom One", "Custom Two", "Automatic", "Earlier"):
                name = f"Kometa Multi-Server Shelf {title}"
                shelf = "Kometa Multi-Server Earlier Shelf" if title == "Earlier" else "Kometa Multi-Server Validation Shelf"
                stdout.write(f"Finished {name} Collection\n")
                if target == "my-silo" and status != "missing":
                    alias = "my-plex" if status == "wrong-server" else target
                    stdout.write(f"Silo Shelf: Movies@{alias} | {shelf} | {name} | {'Assigned' if status == 'missing-order' else status}\n")
        if status != "missing-order":
            stdout.write("Silo Shelf Order: Movies@my-silo | 20,60\n")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(harness.subprocess, "run", fake_run)
    assert harness.live(Namespace(directory=output, case=["shelves"], target="my-silo", timeout=10)) == (0 if status in ("Assigned", "Unchanged") else 1)


@pytest.mark.parametrize("case", ["visibility", "visibility-disabled"])
@pytest.mark.parametrize("status", ["Updated", "Unchanged", "missing", "wrong-server"])
def test_visibility_case_requires_silo_promotion_confirmations(tmp_path, monkeypatch, case, status):
    output = prepare_config(tmp_path)

    def fake_run(command, *, stdout, **kwargs):
        assert command[command.index("--libraries") + 1] == "Movies@my-silo"
        config = harness.read_yaml(Path(command[command.index("--config") + 1]))
        assert Path(config["libraries"]["Movies"]["collection_files"][0]["file"]).name == f"{case}.yml"
        stdout.write("Movies (Movies@my-silo) Library Connection Successful\nMovies (Movies@my-silo) Summary\n")
        for title in ("Library", "Home", "Shared"):
            name = f"Kometa Multi-Server Visibility {title}"
            stdout.write(f"Finished {name} Collection\n")
            if status != "missing":
                target = "my-emby" if status == "wrong-server" else "my-silo"
                flags = ", ".join(f"visible_{key}={str(case == 'visibility' and key == title.lower()).lower()}" for key in ("library", "home", "shared"))
                stdout.write(f"Silo Visibility: Movies@{target} | {name} | {flags} | {status}\n")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(harness.subprocess, "run", fake_run)
    assert harness.live(Namespace(directory=output, case=[case], target="my-silo", timeout=10)) == (0 if status in ("Updated", "Unchanged") else 1)
