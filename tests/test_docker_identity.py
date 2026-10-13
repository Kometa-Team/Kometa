"""Exercise the Dockerfile's build-time identity validation without Docker."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "commit, version, expected_error",
    [
        ("a" * 40, "2.5.2-build6", None),
        (None, "2.5.2-build6", "KOMETA_GIT_SHA"),
        ("", "2.5.2-build6", "KOMETA_GIT_SHA"),
        ("a" * 7, "2.5.2-build6", "KOMETA_GIT_SHA"),
        ("g" * 40, "2.5.2-build6", "KOMETA_GIT_SHA"),
        ("a" * 40, None, "KOMETA_VERSION"),
        ("a" * 40, "", "KOMETA_VERSION"),
        ("a" * 40, "2.5.2-build5", "KOMETA_VERSION"),
    ],
)
def test_docker_build_identity(tmp_path, commit, version, expected_error):
    dockerfile = (Path(__file__).resolve().parents[1] / "Dockerfile").read_text()
    validation = dockerfile.split("RUN /.venv/bin/python3 - <<'PY'\n", 1)[1].split("\nPY", 1)[0]
    (tmp_path / "VERSION").write_text("2.5.2-build6\n")
    # A source-supplied hint must be replaced by the build's validated SHA.
    hint = tmp_path / ".kometa_sha"
    hint.write_text("stale hint")
    env = {key: value for key, value in os.environ.items() if key not in {"KOMETA_GIT_SHA", "KOMETA_VERSION"}}
    if commit is not None:
        env["KOMETA_GIT_SHA"] = commit
    if version is not None:
        env["KOMETA_VERSION"] = version
    result = subprocess.run([sys.executable, "-c", validation], cwd=tmp_path, env=env, capture_output=True, text=True)
    if expected_error:
        assert result.returncode == 0, result.stderr
        assert "WARNING:" in result.stderr
        assert expected_error in result.stderr
        assert not hint.exists()
    else:
        assert result.returncode == 0, result.stderr
        assert hint.read_text() == commit + "\n"
