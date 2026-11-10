"""Exercise the runtime dependency verifier without Docker."""

import importlib.util
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_runtime_dependencies.py"
SHA = "1b34bb2ddee12df12bfd19c88d95d489a0bcd483"
GIT_PIN = f"serializd-py @ git+https://github.com/Velocidensity/serializd-py.git@{SHA}"


@pytest.fixture(scope="module")
def verifier():
    spec = importlib.util.spec_from_file_location("verify_runtime_dependencies", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def installed(verifier, monkeypatch):
    versions = {}
    commits = {}

    def version(name):
        if name not in versions:
            raise metadata.PackageNotFoundError(name)
        return versions[name]

    monkeypatch.setattr(verifier.metadata, "version", version)
    monkeypatch.setattr(verifier, "installed_commit", commits.get)
    return versions, commits


def problems_for(verifier, text):
    return verifier.find_problems(verifier.locked_requirements(text))


def test_matching_versions_pass(verifier, installed):
    installed[0].update({"anyio": "4.15.1", "ruamel-yaml": "0.19.1"})
    assert problems_for(verifier, "# header\nanyio==4.15.1\n    # via httpx\nruamel-yaml==0.19.1\n\n") == []


def test_version_mismatch_and_missing_are_reported(verifier, installed):
    installed[0]["anyio"] = "4.0.0"
    problems = problems_for(verifier, "anyio==4.15.1\nlxml==6.1.3\n")
    assert problems == ["anyio: installed 4.0.0, locked ==4.15.1", "lxml: not installed"]


def test_names_are_normalised(verifier, installed):
    installed[0]["ruamel-yaml"] = "0.19.1"
    assert problems_for(verifier, "ruamel.yaml==0.19.1\n") == []


def test_markers_select_what_applies(verifier, installed):
    text = "skipped==1.0 ; python_version < '3'\nrequired==1.0 ; python_version >= '3'\n"
    assert problems_for(verifier, text) == ["required: not installed"]
    installed[0]["required"] = "1.0"
    assert problems_for(verifier, text) == []


def test_git_pin_compares_the_installed_commit(verifier, installed):
    versions, commits = installed
    versions["serializd-py"] = "0.1.0"
    commits["serializd-py"] = SHA
    assert problems_for(verifier, GIT_PIN + "\n") == []
    commits["serializd-py"] = "f" * 40
    assert problems_for(verifier, GIT_PIN + "\n") == [f"serializd-py: installed commit {'f' * 40}, locked {SHA}"]
    del commits["serializd-py"]
    assert problems_for(verifier, GIT_PIN + "\n") == [f"serializd-py: installed commit None, locked {SHA}"]


def test_repo_requirements_file_is_fully_pinned(verifier):
    requirements = list(verifier.locked_requirements((ROOT / "requirements.txt").read_text()))
    assert len(requirements) > 50
    for requirement in requirements:
        assert requirement.url or [spec.operator for spec in requirement.specifier] == ["=="], requirement
    assert any(requirement.url and requirement.url.endswith("@" + SHA) for requirement in requirements)


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_cli_exit_codes(tmp_path):
    locked = tmp_path / "requirements.txt"
    locked.write_text(f"pytest=={metadata.version('pytest')}\npackaging=={metadata.version('packaging')}\n")
    result = run_cli(str(locked))
    assert result.returncode == 0, result.stderr
    assert "Verified 2 locked runtime dependencies" in result.stdout

    locked.write_text("pytest==0.0.1\n")
    result = run_cli(str(locked))
    assert result.returncode == 1
    assert "do not match" in result.stderr
    assert "pytest: installed" in result.stderr

    assert run_cli().returncode == 2


def test_dockerfile_verifies_after_the_source_copy():
    dockerfile = (ROOT / "Dockerfile").read_text()
    command = "RUN /.venv/bin/python3 scripts/verify_runtime_dependencies.py requirements.txt"
    assert dockerfile.index("COPY . /") < dockerfile.index(command) < dockerfile.index("ENTRYPOINT")
