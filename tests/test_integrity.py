"""Source integrity diagnostics must never turn unavailable data into trust."""

import base64
import io
import json
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from modules import integrity

SHIPPED = {
    "kometa.py": b"# upstream\n",
    "VERSION": b"2.5.2-build3\n",
    "PART": b"\n",
    "requirements.txt": b"requests\n",
    "modules/builder.py": b"# builder\n",
    "defaults/overlays/images/rating.png": b"image",
    "fonts/font.ttf": b"font",
    "docs/kometa/logs.md": b"logs",
    "config/config.yml.template": b"config",
}


def archive_and_proof(files=SHIPPED):
    entries = [{"path": path, "mode": "100644", "sha": integrity._git_hash("blob", content)} for path, content in files.items()]
    tree = integrity._tree_hashes(entries)[""]
    raw = f"tree {tree}\nauthor Test <test@example.com> 1 +0000\ncommitter Test <test@example.com> 1 +0000\n\nUpstream\n".encode()
    commit = integrity._git_hash("commit", raw)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(f"Kometa-{commit}/{name}", content)
    return buffer.getvalue(), commit, raw, entries


@pytest.fixture
def installation(tmp_path, monkeypatch):
    root = tmp_path / "kometa"
    config = root / "config"
    for name, content in SHIPPED.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    zipped, commit, raw, entries = archive_and_proof()
    monkeypatch.delenv("KOMETA_GIT_SHA", raising=False)
    monkeypatch.setattr(integrity.timings, "git_sha", lambda *args, **kwargs: commit)
    client = MagicMock()
    client.baseline.side_effect = lambda requested, profile: integrity.manifest_from_zip(zipped, requested, profile, raw, entries)
    return root, config, commit, client


def check(installation, profile="source"):
    root, config, _, client = installation
    return integrity.check_integrity(root, config, profile, client)


def cache_path(installation):
    root, config, commit, _ = installation
    return config / integrity.CACHE_DIR / f"Kometa-Team-Kometa-{commit}-source-v1.json"


def test_pristine_and_cached_offline(installation):
    assert check(installation)["state"] == "Verified"
    installation[3].baseline.side_effect = requests.ConnectionError("offline")
    assert check(installation)["state"] == "Verified"
    assert installation[3].baseline.call_count == 1
    assert integrity.format_integrity(check(installation)) == ["Source Integrity: Verified"]


@pytest.mark.parametrize("path", [name for name in SHIPPED if not name.startswith("config/")])
def test_modified_distributed_files(installation, path):
    assert check(installation)["state"] == "Verified"
    (installation[0] / path).write_bytes(b"modified")
    before = cache_path(installation).read_bytes()
    report = check(installation)
    assert report["state"] == "Modified"
    assert report["modified"] == [path]
    assert cache_path(installation).read_bytes() == before


def test_missing_and_added(installation):
    (installation[0] / "fonts/font.ttf").unlink()
    (installation[0] / "modules/test_patch.py").write_bytes(b"extra")
    report = check(installation)
    assert report["state"] == "Modified"
    assert report["missing"] == ["fonts/font.ttf"]
    assert report["added"] == ["modules/test_patch.py"]
    assert integrity.format_integrity(report) == ["Source Integrity: MODIFIED", "Missing:", "  fonts/font.ttf", "Added:", "  modules/test_patch.py"]


@pytest.mark.parametrize(
    "name",
    [
        "config/config.yml",
        "config/logs/meta.log",
        "config/cache.db",
        "logs/meta.log",
        ".git/HEAD",
        ".venv/bin/python",
        "venv/pyvenv.cfg",
        "kometa-venv/bin/python",
        "modules/__pycache__/builder.pyc",
        "modules/builder.pyc",
        ".kometa_sha",
        ".kometa_integrity.json",
    ],
)
def test_excluded_runtime_content(installation, name):
    target = installation[0] / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"runtime")
    assert check(installation)["state"] == "Verified"


def test_custom_config_directory_is_excluded(installation):
    root, _, commit, client = installation
    config = root / "user-settings"
    config.mkdir()
    (config / "config.yml").write_text("secret", encoding="utf-8")
    assert integrity.check_integrity(root, config, upstream=client)["state"] == "Verified"


def test_missing_cache_downloads_pristine_not_local_files(installation):
    (installation[0] / "kometa.py").write_bytes(b"modified before first run")
    report = check(installation)
    assert report["state"] == "Modified"
    assert report["modified"] == ["kometa.py"]
    assert installation[3].baseline.call_count == 1


@pytest.mark.parametrize("corruption", ["json", "commit", "repository", "profile", "schema", "hash", "path", "omitted_file", "tree", "commit_object"])
def test_invalid_cache_rebuilt_only_from_upstream(installation, corruption):
    check(installation)
    path = cache_path(installation)
    manifest = json.loads(path.read_text())
    if corruption == "json":
        path.write_text("invalid JSON", encoding="utf-8")
    else:
        if corruption == "hash":
            manifest["files"]["kometa.py"] = "bad"
        elif corruption == "path":
            manifest["files"]["../outside"] = "a" * 64
        elif corruption == "omitted_file":
            del manifest["files"]["modules/builder.py"]
        elif corruption == "tree":
            manifest["entries"][0]["sha"] = "a" * 40
        elif corruption == "commit_object":
            manifest["commit_object"] = base64.b64encode(b"changed").decode()
        else:
            key = "schema_version" if corruption == "schema" else corruption
            manifest[key] = "wrong"
        path.write_text(json.dumps(manifest), encoding="utf-8")
    installation[3].baseline.side_effect = requests.ConnectionError("offline")
    report = check(installation)
    assert report["state"] == "Not Verified"
    assert report["reason"] == "authoritative manifest unavailable"


def test_cache_edit_cannot_bless_modified_file(installation):
    check(installation)
    path = cache_path(installation)
    manifest = json.loads(path.read_text())
    modified = b"custom code"
    (installation[0] / "kometa.py").write_bytes(modified)
    manifest["files"]["kometa.py"] = integrity.hashlib.sha256(modified).hexdigest()
    path.write_text(json.dumps(manifest), encoding="utf-8")
    report = check(installation)
    assert report["state"] == "Not Verified"


def test_valid_looking_wrong_digest_is_not_modified(installation):
    check(installation)
    path = cache_path(installation)
    manifest = json.loads(path.read_text())
    manifest["files"]["kometa.py"] = "0" * 64
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert check(installation)["state"] == "Not Verified"


def test_network_failure_is_not_modified(installation):
    installation[3].baseline.side_effect = requests.ConnectionError("offline")
    assert check(installation)["state"] == "Not Verified"
    assert not cache_path(installation).exists()


def test_changed_commit_cannot_reuse_cache(installation, monkeypatch):
    check(installation)
    monkeypatch.setattr(integrity.timings, "git_sha", lambda *args, **kwargs: "b" * 40)
    installation[3].baseline.side_effect = requests.ConnectionError("offline")
    assert check(installation)["state"] == "Not Verified"
    assert installation[3].baseline.call_args.args[0] == "b" * 40


def test_branch_movement_keeps_pinned_baseline(installation, monkeypatch):
    check(installation)
    monkeypatch.setenv("BRANCH_NAME", "new-branch")
    installation[3].baseline.side_effect = AssertionError("must not refresh branch HEAD")
    assert check(installation)["state"] == "Verified"
    assert installation[3].baseline.call_count == 1


def test_arbitrary_local_git_commit_is_not_upstream(installation, monkeypatch):
    root = installation[0]
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "kometa.py"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--quiet", "-m", "Unofficial"], check=True)
    commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    monkeypatch.setattr(integrity.timings, "git_sha", lambda *args, **kwargs: commit)
    client = integrity.Upstream()
    monkeypatch.setattr(client, "_json", lambda path: {"merge_base_commit": {"sha": "a" * 40}})
    monkeypatch.setattr(integrity.subprocess, "run", lambda *args, **kwargs: pytest.fail("unofficial commit must not be fetched"))
    report = integrity.check_integrity(root, installation[1], upstream=client)
    client.close()
    assert report["state"] == "Not Verified"
    assert report["reason"] == "upstream commit could not be validated"


@pytest.mark.parametrize("hint", ["env", "sha_file", "none", "invalid", "conflict"])
def test_identity_hints(installation, monkeypatch, hint):
    root, config, commit, client = installation
    monkeypatch.setattr(integrity.timings, "git_sha", lambda *args, **kwargs: commit if hint == "conflict" else None)
    if hint in {"env", "invalid", "conflict"}:
        monkeypatch.setenv("KOMETA_GIT_SHA", commit if hint == "env" else "b" * 40 if hint == "conflict" else "invalid")
    elif hint == "sha_file":
        (root / ".kometa_sha").write_text(commit)
    report = integrity.check_integrity(root, config, upstream=client)
    assert report["state"] == ("Verified" if hint in {"env", "sha_file"} else "Not Verified")
    assert client.baseline.call_count == (1 if hint in {"env", "sha_file"} else 0)


@pytest.mark.parametrize("directory", [False, True])
def test_symlink_never_reads_outside_root(installation, tmp_path, monkeypatch, directory):
    root = installation[0]
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "builder.py").write_bytes(b"secret")
    target = root / "modules" if directory else root / "modules/builder.py"
    (root / "modules/builder.py").unlink()
    if directory:
        target.rmdir()
    try:
        target.symlink_to(outside if directory else outside / "builder.py", target_is_directory=directory)
    except OSError:
        pytest.skip("symlinks unavailable")
    original = Path.open

    def guarded(path, *args, **kwargs):
        if "builder.py" in str(path):
            pytest.fail("must not open symlink target")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    report = check(installation)
    assert report["state"] == "Modified"
    assert "modules/builder.py" in report["modified"]


def test_unreadable_file_and_walk_failure_are_not_modified(installation, monkeypatch):
    from contextlib import contextmanager

    original = integrity._open_local

    @contextmanager
    def denied(root, relative):
        if relative.as_posix() == "kometa.py":
            raise PermissionError("denied")
        with original(root, relative) as stream:
            yield stream

    monkeypatch.setattr(integrity, "_open_local", denied)
    assert check(installation)["state"] == "Not Verified"


def test_docker_excludes_operating_system_and_missing_package_files(installation):
    root = installation[0]
    (root / "docs/kometa/logs.md").unlink()
    for name in ["etc/passwd", "usr/bin/python", "proc/status", ".venv/bin/python"]:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"container")
    assert check(installation, "docker")["state"] == "Verified"
    (root / "modules/test_patch.py").write_bytes(b"added")
    assert check(installation, "docker")["added"] == ["modules/test_patch.py"]


@pytest.mark.parametrize("name", ["../escape.py", "modules/../../escape", "/absolute", "C:/escape", "modules\\escape"])
def test_unsafe_archive_paths_are_rejected(name):
    zipped, commit, raw, entries = archive_and_proof()
    buffer = io.BytesIO(zipped)
    with zipfile.ZipFile(buffer, "a") as archive:
        archive.writestr(f"Kometa-{commit}/{name}", b"bad")
    with pytest.raises(ValueError):
        integrity.manifest_from_zip(buffer.getvalue(), commit, "source", raw, entries)


def test_corrupt_archive_and_symlink_cache_are_not_verified(installation):
    check(installation)
    path = cache_path(installation)
    path.unlink()
    path.symlink_to(installation[0] / "VERSION")
    assert check(installation)["state"] == "Not Verified"


@pytest.mark.parametrize("state", ["Verified", "Modified", "Not Verified", "exception"])
def test_integrity_failure_does_not_prevent_startup(installation, monkeypatch, state):
    events = []
    logger = MagicMock()
    logger.info.side_effect = lambda line: events.append(line)
    if state == "exception":
        monkeypatch.setattr(integrity, "check_integrity", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("unexpected")))
    else:
        monkeypatch.setattr(integrity, "check_integrity", lambda *args, **kwargs: {"state": state, "reason": "authoritative manifest unavailable", "modified": ["modules/builder.py"] if state == "Modified" else [], "missing": [], "added": []})
    integrity.log_integrity(installation[0], installation[1], logger)
    events.append("normal startup continued")
    assert events[-1] == "normal startup continued"
    assert events[0].startswith("Source Integrity:")


def test_output_bounded_and_escaped():
    report = {"state": "Modified", "modified": ["bad\nInjected"] + [str(index) for index in range(30)], "missing": [], "added": []}
    lines = integrity.format_integrity(report)
    assert all("\n" not in line for line in lines)
    assert lines[-1] == "  11 more"
    assert lines[2] == "  bad\\nInjected"


def test_startup_does_not_wait_for_network(installation, monkeypatch):
    import threading

    entered, release, completed = threading.Event(), threading.Event(), threading.Event()
    root, config, _, client = installation
    original = integrity.check_integrity

    def slow_baseline(commit, profile):
        entered.set()
        assert release.wait(3)
        zipped, expected, raw, entries = archive_and_proof()
        return integrity.manifest_from_zip(zipped, expected, profile, raw, entries)

    client.baseline.side_effect = slow_baseline

    def checker(root, config, profile, allow_network=True):
        try:
            return original(root, config, profile, client, allow_network=allow_network)
        finally:
            if allow_network:
                completed.set()

    monkeypatch.setattr(integrity, "check_integrity", checker)
    logger = MagicMock()
    integrity.log_integrity(root, config, logger)
    assert entered.wait(1)
    logger.info.assert_called_with("Source Integrity: Not Verified (authoritative manifest unavailable)")
    assert not completed.is_set()
    release.set()
    assert completed.wait(3)


def test_cached_startup_never_starts_background_download(installation, monkeypatch):
    check(installation)
    monkeypatch.setattr(integrity, "_start_background_check", lambda *args: pytest.fail("warm cache must not start a download"))
    logger = MagicMock()
    integrity.log_integrity(installation[0], installation[1], logger)
    logger.info.assert_called_once_with("Source Integrity: Verified")


def test_authoritative_download_is_pinned_and_tls_verified(monkeypatch):
    from types import SimpleNamespace

    zipped, commit, raw, entries = archive_and_proof()
    client = integrity.Upstream()
    calls = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def raise_for_status(self):
            pass

        def iter_content(self, size):
            yield zipped

        def json(self):
            if "compare/" in calls[-1][0]:
                return {"merge_base_commit": {"sha": commit}}
            return {"sha": integrity._tree_hashes(entries)[""], "truncated": False, "tree": [{**entry, "type": "blob"} for entry in entries]}

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr(client.session, "get", get)
    monkeypatch.setattr(integrity.subprocess, "run", lambda args, **kwargs: SimpleNamespace(stdout=raw if "cat-file" in args else b""))
    manifest = client.baseline(commit, "source")
    client.close()
    assert manifest["commit"] == commit
    assert calls[-1][0] == f"https://codeload.github.com/{integrity.REPOSITORY}/zip/{commit}"
    assert all(kwargs["verify"] is True for _, kwargs in calls)
    assert calls[0][0].endswith(f"compare/{commit}...nightly")


def test_archive_cannot_change_upstream_files():
    zipped, commit, raw, entries = archive_and_proof()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in SHIPPED.items():
            archive.writestr(f"Kometa-{commit}/{name}", b"modified" if name == "kometa.py" else content)
    with pytest.raises(ValueError, match="upstream tree"):
        integrity.manifest_from_zip(buffer.getvalue(), commit, "source", raw, entries)


def test_walk_permission_failure_is_not_modified(installation, monkeypatch):
    def denied(*args, **kwargs):
        kwargs["onerror"](PermissionError("denied"))
        return []

    monkeypatch.setattr(integrity.os, "walk", denied)
    assert check(installation)["state"] == "Not Verified"


def test_custom_virtual_environment_is_excluded(installation):
    target = installation[0] / "test_venv"
    target.mkdir()
    (target / "pyvenv.cfg").write_text("home = python", encoding="utf-8")
    (target / "package.py").write_text("generated", encoding="utf-8")
    assert check(installation)["state"] == "Verified"


def test_stat_permission_error_is_not_missing(installation, monkeypatch):
    original = Path.lstat

    def denied(path, *args, **kwargs):
        if path == installation[0] / "modules/builder.py":
            raise PermissionError("denied")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", denied)
    report = check(installation)
    assert report["state"] == "Not Verified"
    assert report["missing"] == []
