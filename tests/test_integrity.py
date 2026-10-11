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
    return config / integrity.CACHE_DIR / f"Kometa-Team-Kometa-{commit}-source-v{integrity.SCHEMA}.json"


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


def test_output_bounded_and_escaped():
    report = {"state": "Modified", "modified": ["bad\nInjected"] + [str(index) for index in range(30)], "missing": [], "added": []}
    lines = integrity.format_integrity(report)
    assert all("\n" not in line for line in lines)
    assert lines[-1] == "  11 more"
    assert lines[2] == "  bad\\nInjected"


def test_authoritative_download_is_pinned_and_tls_verified(monkeypatch):
    from types import SimpleNamespace

    zipped, commit, raw, entries = archive_and_proof()
    client = integrity.Upstream()
    calls = []
    git_calls = []
    monkeypatch.setenv("GIT_SSL_NO_VERIFY", "true")

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

    def run_git(args, **kwargs):
        git_calls.append((args, kwargs))
        return SimpleNamespace(stdout=raw if "cat-file" in args else b"")

    monkeypatch.setattr(integrity.subprocess, "run", run_git)
    original = integrity.manifest_from_zip
    archive_files = []

    def from_disk(source, *args):
        assert not isinstance(source, bytes)
        assert source.fileno() >= 0
        archive_files.append(source)
        return original(source, *args)

    monkeypatch.setattr(integrity, "manifest_from_zip", from_disk)
    manifest = client.baseline(commit, "source")
    client.close()
    assert archive_files and archive_files[0].closed
    assert manifest["commit"] == commit
    assert calls[-1][0] == f"https://codeload.github.com/{integrity.REPOSITORY}/zip/{commit}"
    assert all(kwargs["verify"] is True for _, kwargs in calls)
    assert git_calls and all("GIT_SSL_NO_VERIFY" not in kwargs["env"] for _, kwargs in git_calls)
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


@pytest.mark.parametrize("path", ["modules/builder.py", "scripts/baseline.json", "defaults/data.yml", "VERSION"])
def test_text_line_endings_are_not_modifications(installation, path):
    root = installation[0]
    if path in SHIPPED:
        (root / path).write_bytes(SHIPPED[path].replace(b"\n", b"\r\n"))
        assert check(installation)["state"] == "Verified"
    else:
        files = {**SHIPPED, path: b'{"value": true}\n'}
        zipped, commit, raw, entries = archive_and_proof(files)
        manifest = integrity.manifest_from_zip(zipped, commit, "source", raw, entries)
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(files[path].replace(b"\n", b"\r\n"))
        assert integrity._compare(root, manifest, "source", installation[1])["state"] == "Verified"
        target.write_bytes(b'{"value": false}\r\n')
        assert integrity._compare(root, manifest, "source", installation[1])["state"] == "Modified"


def test_binary_line_endings_remain_significant(installation):
    files = {**SHIPPED, "fonts/font.ttf": b"font\r\n"}
    zipped, commit, raw, entries = archive_and_proof(files)
    manifest = integrity.manifest_from_zip(zipped, commit, "source", raw, entries)
    (installation[0] / "fonts/font.ttf").write_bytes(b"font\n")
    assert integrity._compare(installation[0], manifest, "source", installation[1])["modified"] == ["fonts/font.ttf"]


@pytest.mark.parametrize("name", [".DS_Store", "Thumbs.db", "desktop.ini", "modules/.DS_Store", "defaults/Thumbs.db", "defaults/overlays/desktop.ini"])
def test_desktop_metadata_is_excluded_everywhere(installation, name):
    path = installation[0] / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"desktop")
    assert check(installation)["state"] == "Verified"


def test_cache_prunes_only_this_repository_and_profile(installation):
    check(installation)
    current = cache_path(installation)
    old = current.with_name(f"Kometa-Team-Kometa-{'a' * 40}-source-v1.json")
    old.write_text("old", encoding="utf-8")
    docker = current.with_name(f"Kometa-Team-Kometa-{'a' * 40}-docker-v2.json")
    unrelated = current.with_name("unrelated.json")
    linked = current.with_name(f"Kometa-Team-Kometa-{'b' * 40}-source-v2.json")
    docker.write_text("docker", encoding="utf-8")
    unrelated.write_text("keep", encoding="utf-8")
    try:
        linked.symlink_to(unrelated)
    except OSError:
        linked = None
    integrity._write_manifest(current, json.loads(current.read_text()))
    assert old.exists()
    assert current.exists() and docker.exists() and unrelated.read_text() == "keep"
    if linked:
        assert linked.is_symlink()


def test_integrity_opt_out_does_not_inspect_or_download(installation, monkeypatch):
    monkeypatch.setattr(integrity, "check_integrity", lambda *a, **k: pytest.fail("disabled"))
    monkeypatch.setattr(integrity, "_start_background_check", lambda *a, **k: pytest.fail("disabled"))
    logger = MagicMock()
    run = integrity.log_integrity(installation[0], installation[1], logger, enabled=False)
    logger.info.assert_called_once_with("Source Integrity: Not Verified (disabled by source-integrity option)")
    integrity.log_integrity_summary(run, logger)
    logger.info.assert_called_with("Source Integrity: Not Verified (disabled by source-integrity option)")


@pytest.mark.parametrize("cached", [False, True])
def test_startup_does_not_wait_for_hashing_or_download(installation, monkeypatch, cached):
    import threading

    if cached:
        check(installation)
        installation[3].baseline.side_effect = requests.ConnectionError("offline")
    entered, release, finished = threading.Event(), threading.Event(), threading.Event()
    original = integrity.check_integrity

    def slow_check(*args, **kwargs):
        entered.set()
        assert release.wait(3)
        try:
            return original(*args, upstream=installation[3], **kwargs)
        finally:
            finished.set()

    monkeypatch.setattr(integrity, "check_integrity", slow_check)
    logger = MagicMock()
    integrity.log_integrity(installation[0], installation[1], logger)
    assert entered.wait(1)
    assert not finished.is_set()
    logger.info.assert_called_with("Source Integrity: Not Verified (comparison in progress)")
    release.set()
    assert finished.wait(3)


@pytest.mark.parametrize("state", ["Verified", "Modified", "Not Verified", "exception"])
def test_background_failure_does_not_prevent_startup(installation, monkeypatch, state):
    import threading

    logged = threading.Event()
    logger = MagicMock()
    logger.info.side_effect = lambda line: logged.set() if "comparison in progress" not in line else None
    if state == "exception":

        def fail(*args, **kwargs):
            logged.set()
            raise RuntimeError("unexpected")

        monkeypatch.setattr(integrity, "check_integrity", fail)
    else:
        monkeypatch.setattr(integrity, "check_integrity", lambda *a, **k: {"state": state, "reason": "authoritative manifest unavailable", "modified": ["modules/builder.py"] if state == "Modified" else [], "missing": [], "added": []})
    integrity.log_integrity(installation[0], installation[1], logger)
    assert logged.wait(3)


@pytest.mark.parametrize("status", [403, 429, 500])
def test_upstream_http_failure_is_not_rejected_commit(monkeypatch, status):
    client = integrity.Upstream()
    response = requests.Response()
    response.status_code = status
    failure = requests.HTTPError(response=response)
    monkeypatch.setattr(client, "_json", MagicMock(side_effect=failure))
    with pytest.raises(integrity.Unavailable, match="upstream validation request failed"):
        client.baseline("a" * 40, "source")
    assert client._json.call_count == 1
    client.close()


def test_export_exclusions_come_from_bound_upstream_attributes(installation):
    content = b".gitattributes export-ignore\nfuture/ export-ignore\n*.private export-ignore\n"
    files = {**SHIPPED, ".gitattributes": content, "future/resource.txt": b"export only", "new.private": b"private"}
    zipped, commit, raw, entries = archive_and_proof(files)
    attributes = {".gitattributes": base64.b64encode(content).decode()}
    manifest = integrity.manifest_from_zip(zipped, commit, "source", raw, entries, attributes)
    assert set(manifest["files"]) == set(SHIPPED) - {"config/config.yml.template"}
    target = installation[0] / "future/local.txt"
    target.parent.mkdir()
    target.write_bytes(b"ignored")
    assert integrity._compare(installation[0], manifest, "source", installation[1])["state"] == "Verified"
    manifest["attributes"][".gitattributes"] = base64.b64encode(b"modules/ export-ignore\n").decode()
    with pytest.raises(ValueError, match="attributes do not match tree"):
        integrity._validate_manifest(manifest, commit, "source")


def test_windows_archive_line_endings_match_canonical_git_blob():
    files = {**SHIPPED, "script.ps1": b"Write-Output 'hello'\n"}
    _, commit, raw, entries = archive_and_proof(files)
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        for name, content in files.items():
            zipped.writestr(f"Kometa-{commit}/{name}", content.replace(b"\n", b"\r\n") if name.endswith(".ps1") else content)
    manifest = integrity.manifest_from_zip(archive.getvalue(), commit, "source", raw, entries)
    assert manifest["files"]["script.ps1"] == integrity.hashlib.sha256(files["script.ps1"]).hexdigest()


@pytest.mark.parametrize("original", [b"binary\x00\r\n", b"binary\xff\r\n"])
def test_binary_content_in_text_path_is_not_normalized(installation, original):
    files = {**SHIPPED, "data.json": original}
    zipped, commit, raw, entries = archive_and_proof(files)
    manifest = integrity.manifest_from_zip(zipped, commit, "source", raw, entries)
    (installation[0] / "data.json").write_bytes(original.replace(b"\r\n", b"\n"))
    report = integrity._compare(installation[0], manifest, "source", installation[1])
    assert report["state"] == "Modified"
    assert report["modified"] == ["data.json"]


def test_normalization_handles_chunk_boundary_and_preserves_lone_cr():
    canonical = b"x" * (128 * 1024 - 1) + b"\nend\r"
    content = canonical.replace(b"\n", b"\r\n")
    assert integrity._normalized_digest(io.BytesIO(content)) == integrity._digest_stream(io.BytesIO(canonical), len(canonical))


def test_unsupported_export_pattern_is_not_trusted():
    content = b"secret/** export-ignore\n"
    entries = [{"path": ".gitattributes", "sha": integrity._git_hash("blob", content)}]
    with pytest.raises(ValueError, match="Unsupported export pattern"):
        integrity._export_rules(entries, {".gitattributes": base64.b64encode(content).decode()})


@pytest.mark.parametrize("state", ["Verified", "Modified", "Not Verified"])
def test_summary_repeats_completed_report(state):
    report = {"state": state, "reason": "upstream validation request failed" if state == "Not Verified" else "", "modified": ["modules/builder.py"] if state == "Modified" else [], "missing": [], "added": []}
    run = integrity.IntegrityRun()
    run.finish(report)
    logger = MagicMock()
    integrity.log_integrity_summary(run, logger)
    assert [call.args[0] for call in logger.info.call_args_list] == integrity.format_integrity(report)
    logger.separator.assert_called_once_with("Source Integrity Summary", space=False, border=False)


def test_pending_summary_does_not_wait_or_claim_a_failure():
    run = integrity.IntegrityRun()
    logger = MagicMock()
    integrity.log_integrity_summary(run, logger)
    logger.info.assert_called_once_with("Source Integrity: Not Verified (comparison still in progress at end of run)")
    assert run.snapshot()["reason"] == "comparison in progress"


def test_summary_snapshot_is_independent_of_other_runs():
    first, second = integrity.IntegrityRun(), integrity.IntegrityRun()
    first.finish({"state": "Modified", "reason": "", "modified": ["modules/builder.py"], "missing": [], "added": []})
    snapshot = first.snapshot()
    snapshot["modified"].clear()
    assert first.snapshot()["modified"] == ["modules/builder.py"]
    assert second.snapshot()["reason"] == "comparison in progress"


def test_background_report_is_retained_for_summary(installation, monkeypatch):
    import threading

    complete = threading.Event()
    original = integrity.check_integrity
    monkeypatch.setattr(integrity, "check_integrity", lambda *args, **kwargs: original(*args, upstream=installation[3], **kwargs))
    logger = MagicMock()
    logger.info.side_effect = lambda line: complete.set() if line == "Source Integrity: Verified" else None
    run = integrity.log_integrity(installation[0], installation[1], logger)
    assert complete.wait(3)
    integrity.log_integrity_summary(run, logger)
    assert logger.info.call_args.args == ("Source Integrity: Verified",)


def test_thread_creation_failure_is_in_summary(installation, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("unavailable")

    monkeypatch.setattr(integrity.threading.Thread, "start", fail)
    logger = MagicMock()
    run = integrity.log_integrity(installation[0], installation[1], logger)
    integrity.log_integrity_summary(run, logger)
    logger.info.assert_called_with("Source Integrity: Not Verified (background check could not be started)")


def test_cache_retention_is_bounded(installation):
    import os

    check(installation)
    current = cache_path(installation)
    old = []
    for index in range(5):
        path = current.with_name(f"Kometa-Team-Kometa-{index:040x}-source-v2.json")
        path.write_text("old", encoding="utf-8")
        os.utime(path, ns=(index + 1, index + 1))
        old.append(path)
    integrity._write_manifest(current, json.loads(current.read_text()))
    assert len(list(current.parent.glob("*-source-v*.json"))) == integrity.CACHE_KEEP
    assert current.exists() and old[-1].exists() and old[-2].exists()
    assert not any(path.exists() for path in old[:-2])


def test_shared_config_preserves_two_installation_caches(installation, tmp_path, monkeypatch):
    first, config, first_commit, first_client = installation
    assert check(installation)["state"] == "Verified"
    files = {**SHIPPED, "VERSION": b"2.5.2-build4\n"}
    zipped, second_commit, raw, entries = archive_and_proof(files)
    second = tmp_path / "second-kometa"
    for name, content in files.items():
        path = second / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    second_client = MagicMock()
    second_client.baseline.side_effect = lambda requested, profile: integrity.manifest_from_zip(zipped, requested, profile, raw, entries)
    monkeypatch.setattr(integrity.timings, "git_sha", lambda root, **kwargs: first_commit if Path(root) == first else second_commit)
    assert integrity.check_integrity(second, config, upstream=second_client)["state"] == "Verified"
    first_client.baseline.side_effect = requests.ConnectionError("offline")
    second_client.baseline.side_effect = requests.ConnectionError("offline")
    assert check(installation)["state"] == "Verified"
    assert integrity.check_integrity(second, config, upstream=second_client)["state"] == "Verified"
    assert first_client.baseline.call_count == second_client.baseline.call_count == 1


@pytest.mark.parametrize(
    "flags, environment, expected",
    [
        ([], {}, True),
        (["--source-integrity"], {}, True),
        (["--no-source-integrity"], {}, False),
        (["-si"], {}, True),
        ([], {"KOMETA_SOURCE_INTEGRITY": "false"}, False),
        ([], {"KOMETA_SOURCE_INTEGRITY": "true"}, True),
        (["--source-integrity"], {"KOMETA_SOURCE_INTEGRITY": "false"}, False),
        (["--no-source-integrity"], {"KOMETA_SOURCE_INTEGRITY": "true"}, True),
        ([], {"PMM_SOURCE_INTEGRITY": "false"}, False),
    ],
)
def test_source_integrity_uses_standard_argument_resolution(monkeypatch, flags, environment, expected):
    import argparse
    import ast
    import os
    import sys

    # Execute the real argument table/parser/resolver without starting Kometa or APIs.
    source = ast.parse((Path(__file__).resolve().parents[1] / "kometa.py").read_text(encoding="utf-8"))
    start = next(index for index, node in enumerate(source.body) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "arguments" for target in node.targets))
    end = next(index for index, node in enumerate(source.body) if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "env_branch" for target in node.targets))
    for name in tuple(os.environ):
        if name.startswith(("KOMETA_", "PMM_")):
            monkeypatch.delenv(name)
    for name, value in environment.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sys, "argv", ["kometa.py", *flags])
    namespace = {"argparse": argparse, "os": os}
    exec(compile(ast.Module(body=source.body[start:end], type_ignores=[]), "kometa-arguments", "exec"), namespace)
    assert namespace["run_args"]["source-integrity"] is expected
    assert namespace["run_args"]["timings"] is False
    assert "KOMETA_SOURCE_INTEGRITY" in namespace["static_envs"]
    assert "--no-source-integrity" in namespace["parser"].format_help()
    assert not namespace["unknown"]
