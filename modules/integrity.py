"""Nonblocking source integrity diagnostics.

Expected SHA-256 values always come from pristine upstream archives. Git's
content-addressed commit/tree objects bind cached paths to the requested commit;
Git blob identities additionally prevent edited expected hashes blessing changes.
This is a support diagnostic, not protection against replacement of the checker.
"""

from __future__ import annotations

import base64
import codecs
import copy
import fnmatch
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import stat

# Fixed Git commands for upstream provenance; never invoke a shell.
import subprocess  # nosec B404
import tempfile
import threading
import time
import unicodedata
import zipfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any

import requests

from modules import timings

REPOSITORY = "Kometa-Team/Kometa"
SCHEMA = 2
CACHE_DIR = ".source-integrity"
SHA = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
IGNORED_ROOTS = {
    "config",
    "logs",
    ".git",
    ".venv",
    "venv",
    "env",
    "pmm-venv",
    "kometa-venv",
    ".source-integrity",
    ".cache",
    ".hypothesis",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".worktrees",
    ".agents",
    ".claude",
    ".vscode",
    ".idea",
}
DOCKER_ROOTS = {"modules", "defaults", "fonts", "docker", "scripts"}
DOCKER_OMITTED = {"docs", "json-schema", "CHANGELOG.md", "Dockerfile", "LICENSE", "README.md", ".readthedocs.yml", "test.py"}
DESKTOP_METADATA = {".DS_Store", "Thumbs.db", "desktop.ini"}
TEXT_SUFFIXES = {".py", ".pyi", ".pyx", ".sh", ".bash", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini", ".txt", ".template", ".md", ".rst", ".html", ".css", ".js", ".svg", ".bat", ".cmd", ".ps1", ".lock"}
TEXT_NAMES = {"VERSION", "PART", "Dockerfile", "LICENSE"}
METADATA = {".kometa_sha", ".kometa_branch", ".kometa_integrity.json", ".env", ".DS_Store", "dictionary.dic", "UUID", ".coverage"}
REQUIRED = {"kometa.py", "VERSION", "requirements.txt"}
MAX_ARCHIVE = 512 * 1024 * 1024
MAX_EXPANDED = 1024 * 1024 * 1024
CACHE_KEEP = 3
_pending: dict[tuple[str, str, str], IntegrityRun] = {}
_pending_lock = threading.Lock()


class Unavailable(Exception):
    """The diagnostic cannot safely complete an authoritative comparison."""


class IntegrityRun:
    """Thread-safe result retained for this run's nonblocking footer."""

    def __init__(self):
        self._lock = threading.Lock()
        self._report = {"state": "Not Verified", "reason": "comparison in progress", "modified": [], "missing": [], "added": []}

    def finish(self, report):
        with self._lock:
            self._report = copy.deepcopy(report)

    def snapshot(self):
        with self._lock:
            return copy.deepcopy(self._report)


def _safe_relative_path(value: str) -> PurePosixPath:
    # Validate archive and manifest paths, including Windows paths.
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\x00" in value:
        raise ValueError("Invalid integrity file path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError("Invalid integrity file path")
    return path


def _ignored(path: PurePosixPath, profile: str) -> bool:
    return (
        path.parts[0] in IGNORED_ROOTS
        or path.name in DESKTOP_METADATA
        or "__pycache__" in path.parts
        or path.suffix.lower() in {".pyc", ".pyo"}
        or (len(path.parts) == 1 and (path.name in METADATA or path.name.startswith((".kometa_integrity-", ".coverage."))))
        or (profile == "docker" and (path.parts[0] in DOCKER_OMITTED or path.name == "MODULE.md" or path.suffix.lower() == ".psd" or any(part in {"dist", "build", "log"} for part in path.parts)))
    )


def _git_hash(kind: str, data: bytes) -> str:
    # SHA-1 here is Git's object identity, not the file integrity comparison.
    return hashlib.sha1(f"{kind} {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def _digest_stream(stream, size: int) -> tuple[str, str]:
    """Chunked SHA-256, with Git identity in the same read pass."""
    digest = hashlib.sha256()
    blob = hashlib.sha1(f"blob {size}\0".encode(), usedforsecurity=False)
    for chunk in iter(lambda: stream.read(128 * 1024), b""):
        digest.update(chunk)
        blob.update(chunk)
    return digest.hexdigest(), blob.hexdigest()


def _text_path(path: str) -> bool:
    relative = PurePosixPath(path)
    return relative.suffix.lower() in TEXT_SUFFIXES or relative.name in TEXT_NAMES


def _normalized_digest(stream) -> tuple[str, str] | None:
    """Normalize CRLF only for known text paths; never reinterpret binary files."""
    with tempfile.SpooledTemporaryFile(max_size=1024 * 1024) as canonical:
        pending = b""
        decoder = codecs.getincrementaldecoder("utf-8")()
        for chunk in iter(lambda: stream.read(128 * 1024), b""):
            if b"\x00" in chunk:
                return None
            try:
                decoder.decode(chunk)
            except UnicodeDecodeError:
                return None
            chunk = pending + chunk
            pending = b"\r" if chunk.endswith(b"\r") else b""
            canonical.write((chunk[:-1] if pending else chunk).replace(b"\r\n", b"\n"))
        try:
            decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            return None
        canonical.write(pending)
        size = canonical.tell()
        canonical.seek(0)
        return _digest_stream(canonical, size)


def _tree_hashes(entries: list[dict[str, str]]) -> dict[str, str]:
    """Reconstruct Git trees so cache edits cannot change the commit's file list."""
    directories: dict[str, list[tuple[str, str, str]]] = {"": []}
    seen = set()
    for entry in entries:
        path = _safe_relative_path(entry["path"])
        if path.as_posix() in seen or not SHA.fullmatch(entry["sha"]) or entry["mode"] not in {"100644", "100755", "120000", "160000"}:
            raise ValueError("Invalid Git tree entry")
        seen.add(path.as_posix())
        parent = path.parent.as_posix() if len(path.parts) > 1 else ""
        directories.setdefault(parent, []).append((path.name, entry["mode"], entry["sha"]))
        for index in range(1, len(path.parts)):
            directories.setdefault("/".join(path.parts[:index]), [])
    hashes = {}
    for directory in sorted(directories, key=lambda value: value.count("/") + bool(value), reverse=True):
        children = directories[directory]
        data = b"".join(mode.encode() + b" " + name.encode("utf-8") + b"\0" + bytes.fromhex(sha) for name, mode, sha in sorted(children, key=lambda item: (item[0] + ("/" if item[1] == "40000" else "")).encode("utf-8")))
        hashes[directory] = _git_hash("tree", data)
        if directory:
            path = PurePosixPath(directory)
            parent = path.parent.as_posix() if len(path.parts) > 1 else ""
            directories[parent].append((path.name, "40000", hashes[directory]))
    return hashes


def _export_rules(entries, attributes):
    """Bind export exclusions to pristine attributes rather than a manual list."""
    objects = {entry["path"]: entry["sha"] for entry in entries if PurePosixPath(entry["path"]).name == ".gitattributes"}
    if set(attributes) != set(objects):
        raise ValueError("Incomplete upstream attributes")
    rules = []
    for path in sorted(attributes, key=lambda key: (key.count("/"), key)):
        content = base64.b64decode(attributes[path], validate=True)
        if _git_hash("blob", content) != objects[path]:
            raise ValueError("Upstream attributes do not match tree")
        parent = PurePosixPath(path).parent.as_posix()
        for line in content.decode("utf-8").splitlines():
            fields = shlex.split(line, comments=True)
            if not fields:
                continue
            if fields[0].startswith("[attr]"):
                raise ValueError("Unsupported Git attribute macro")
            for attribute in fields[1:]:
                if attribute in {"export-ignore", "-export-ignore", "!export-ignore"}:
                    pattern = fields[0]
                    # Fail safely on unsupported patterns rather than exclude too much.
                    if pattern.startswith("!") or "[" in pattern or "**" in pattern or ("/" in pattern.strip("/") and any(char in pattern for char in "*?")):
                        raise ValueError("Unsupported export pattern")
                    rules.append((parent, pattern, attribute == "export-ignore"))
    return rules


def _export_ignored(path: PurePosixPath, rules) -> bool:
    ignored = False
    for parent, pattern, value in rules:
        scope = PurePosixPath(parent)
        try:
            relative = path.relative_to(scope).as_posix()
        except ValueError:
            continue
        pattern = pattern.removeprefix("/")
        if pattern.endswith("/"):
            matches = relative == pattern[:-1] or relative.startswith(pattern)
        elif "/" in pattern:
            matches = fnmatch.fnmatchcase(relative, pattern)
        else:
            matches = fnmatch.fnmatchcase(path.name, pattern)
        if matches:
            ignored = value
    return ignored


def _validate_manifest(manifest: dict[str, Any], commit: str, profile: str) -> dict[str, str]:
    if any(manifest.get(key) != value for key, value in {"repository": REPOSITORY, "commit": commit, "profile": profile, "schema_version": SCHEMA, "upstream_validated": True}.items()):
        raise ValueError("Integrity cache identity mismatch")
    raw_commit = base64.b64decode(manifest["commit_object"], validate=True)
    if _git_hash("commit", raw_commit) != commit:
        raise ValueError("Integrity cache commit mismatch")
    tree = _tree_hashes(manifest["entries"])
    if raw_commit.splitlines()[0] != f"tree {tree['']}".encode():
        raise ValueError("Integrity cache tree mismatch")
    rules = _export_rules(manifest["entries"], manifest.get("attributes", {}))
    expected = {entry["path"]: entry["sha"] for entry in manifest["entries"] if not _ignored(_safe_relative_path(entry["path"]), profile) and not _export_ignored(_safe_relative_path(entry["path"]), rules)}
    files = manifest["files"]
    if not isinstance(files, dict) or set(files) != set(expected) or not REQUIRED.issubset(files):
        raise ValueError("Incomplete integrity manifest")
    if any(not isinstance(value, str) or not DIGEST.fullmatch(value) for value in files.values()):
        raise ValueError("Invalid SHA-256 digest")
    return expected


def manifest_from_zip(zip_source, commit: str, profile: str, commit_object: bytes, entries: list[dict[str, str]], attributes=None) -> dict[str, Any]:
    """Hash pristine upstream ZIP files with exact-commit cache binding."""
    attributes = attributes or {}
    rules = _export_rules(entries, attributes)
    files: dict[str, str] = {}
    roots = set()
    seen = set()
    expanded = 0
    objects = {entry["path"]: entry["sha"] for entry in entries}
    with zipfile.ZipFile(io.BytesIO(zip_source) if isinstance(zip_source, bytes) else zip_source) as archive:
        for entry in archive.infolist():
            member = _safe_relative_path(entry.orig_filename.rstrip("/"))
            roots.add(member.parts[0])
            expanded += entry.file_size
            if roots != {f"Kometa-{commit}"} or stat.S_ISLNK(entry.external_attr >> 16) or expanded > MAX_EXPANDED:
                raise ValueError("Unsupported Kometa archive layout")
            if entry.is_dir():
                continue
            if len(member.parts) < 2:
                raise ValueError("Unsupported Kometa archive layout")
            relative = PurePosixPath(*member.parts[1:])
            key = relative.as_posix()
            if key.casefold() in seen:
                raise ValueError("Duplicate Kometa archive file")
            seen.add(key.casefold())
            if not _ignored(relative, profile) and not _export_ignored(relative, rules):
                with archive.open(entry) as stream:
                    digest, blob = _digest_stream(stream, entry.file_size)
                if blob != objects.get(key) and _text_path(key):
                    with archive.open(entry) as stream:
                        normalized = _normalized_digest(stream)
                        if normalized is not None:
                            digest, blob = normalized
                if blob != objects.get(key):
                    raise ValueError("Archive does not match upstream tree")
                files[key] = digest
    manifest = {
        "schema_version": SCHEMA,
        "repository": REPOSITORY,
        "commit": commit,
        "profile": profile,
        "upstream_validated": True,
        "commit_object": base64.b64encode(commit_object).decode(),
        "entries": entries,
        "attributes": attributes,
        "files": dict(sorted(files.items())),
    }
    _validate_manifest(manifest, commit, profile)
    return manifest


def _read_identity(root: Path) -> str:
    # Git HEAD belongs to this installation, not the caller's working directory.
    git_commit = timings.git_sha(root, use_env=False)
    env_commit = os.environ.get("KOMETA_GIT_SHA") or None
    if git_commit and env_commit and git_commit != env_commit:
        raise Unavailable("conflicting build identities")
    commit = git_commit or env_commit
    if not commit:
        hint = root / ".kometa_sha"
        if _is_link(hint):
            raise Unavailable("authoritative build identity unavailable")
        if hint.is_file():
            commit = hint.read_text(encoding="utf-8").strip()
    if not isinstance(commit, str) or not SHA.fullmatch(commit):
        raise Unavailable("authoritative build identity unavailable")
    return commit


class Upstream:
    """Bounded, TLS-verified requests; no long application retry loop at startup."""

    def __init__(self):
        self.deadline = time.monotonic() + 180
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Kometa source integrity"

    def _remaining(self) -> float:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise Unavailable("authoritative manifest unavailable")
        return remaining

    def _json(self, path: str) -> dict[str, Any]:
        response = self.session.get(f"https://api.github.com/repos/{REPOSITORY}/{path}", timeout=(min(3, self._remaining()), min(8, self._remaining())), verify=True)
        response.raise_for_status()
        return response.json()

    def baseline(self, commit: str, profile: str) -> dict[str, Any]:
        if not isinstance(commit, str) or not SHA.fullmatch(commit):
            raise Unavailable("upstream commit could not be validated")
        # GitHub can resolve fork objects through upstream's API. Existence alone
        # is insufficient: the commit must be an ancestor of a published branch.
        validated = False
        for branch in ("nightly", "master", "develop"):
            try:
                comparison = self._json(f"compare/{commit}...{branch}")
                if comparison.get("merge_base_commit", {}).get("sha") == commit:
                    validated = True
                    break
            except requests.HTTPError as error:
                if error.response is not None and error.response.status_code == 404:
                    continue
                raise Unavailable("upstream validation request failed") from error
            except requests.RequestException as error:
                raise Unavailable("upstream commit could not be validated") from error
        if not validated:
            raise Unavailable("upstream commit could not be validated")
        # Obtain the original commit object, including signatures/timezones.
        # GitHub's JSON commit representation cannot reconstruct it faithfully.
        git_executable = shutil.which("git")
        if not git_executable:
            raise Unavailable("authoritative manifest unavailable")
        with tempfile.TemporaryDirectory(prefix="kometa-integrity-") as directory:

            def git(*args: str) -> bytes:
                # All commands are fixed; the only identity argument is a validated full SHA.
                result = subprocess.run(  # nosec B603
                    [git_executable, "-C", directory, *args],
                    check=True,
                    capture_output=True,
                    timeout=min(20, self._remaining()),
                    env={**{key: value for key, value in os.environ.items() if key != "GIT_SSL_NO_VERIFY"}, "GIT_TERMINAL_PROMPT": "0"},
                )
                return result.stdout

            git("init", "--bare", "--quiet")
            git("-c", "http.sslVerify=true", "-c", "credential.helper=", "fetch", "--quiet", "--depth=1", "--filter=blob:none", f"https://github.com/{REPOSITORY}.git", commit)
            raw_commit = git("cat-file", "commit", commit)
        if _git_hash("commit", raw_commit) != commit:
            raise ValueError("Invalid upstream commit object")
        tree_sha = raw_commit.splitlines()[0].decode().split()[1]
        tree = self._json(f"git/trees/{tree_sha}?recursive=1")
        if tree.get("truncated") or tree.get("sha") != tree_sha:
            raise ValueError("Incomplete upstream tree")
        entries = [{"path": entry["path"], "mode": entry["mode"], "sha": entry["sha"]} for entry in tree["tree"] if entry["type"] != "tree"]
        attributes = {}
        for entry in entries:
            if PurePosixPath(entry["path"]).name == ".gitattributes":
                blob = self._json(f"git/blobs/{entry['sha']}")
                if blob.get("encoding") != "base64":
                    raise ValueError("Unsupported upstream attributes")
                attributes[entry["path"]] = blob["content"].replace("\n", "")
        with tempfile.TemporaryFile() as content:
            with self.session.get(f"https://codeload.github.com/{REPOSITORY}/zip/{commit}", stream=True, timeout=(min(3, self._remaining()), min(10, self._remaining())), verify=True) as response:
                response.raise_for_status()
                for chunk in response.iter_content(128 * 1024):
                    self._remaining()
                    content.write(chunk)
                    if content.tell() > MAX_ARCHIVE:
                        raise ValueError("Upstream archive too large")
            content.seek(0)
            return manifest_from_zip(content, commit, profile, raw_commit, entries, attributes)

    def close(self):
        self.session.close()


def _write_manifest(path: Path, manifest: dict[str, Any]):
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=".kometa_integrity-", suffix=".tmp", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(manifest, stream, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
        prefix = REPOSITORY.replace("/", "-")
        pattern = re.compile(rf"{re.escape(prefix)}-[0-9a-f]{{40}}-{re.escape(manifest['profile'])}-v[0-9]+\.json")
        candidates = []
        for old in path.parent.iterdir():
            if old != path and pattern.fullmatch(old.name) and not _is_link(old):
                try:
                    candidates.append((old.stat().st_mtime_ns, old))
                except OSError:
                    continue
        # Keep this write plus the two newest other identities for shared configs.
        for _, old in sorted(candidates, key=lambda item: (item[0], item[1].name), reverse=True)[CACHE_KEEP - 1 :]:
            try:
                old.unlink()
            except OSError:
                continue

    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def _is_link(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except (FileNotFoundError, NotADirectoryError):
        return False
    return stat.S_ISLNK(mode) or bool(getattr(path, "is_junction", lambda: False)())


def _symlink_in_path(root: Path, relative: PurePosixPath) -> bool:
    return any(_is_link(root.joinpath(*relative.parts[:index])) for index in range(1, len(relative.parts) + 1))


@contextmanager
def _open_local(root: Path, relative: PurePosixPath):
    """On POSIX, open each component without following links, including races."""
    if os.open in os.supports_dir_fd and hasattr(os, "O_NOFOLLOW"):
        descriptors = []
        try:
            directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            descriptors.append(directory)
            for part in relative.parts[:-1]:
                directory = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                descriptors.append(directory)
            descriptor = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
            with os.fdopen(descriptor, "rb") as stream:
                yield stream
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)
    else:
        # Windows lacks POSIX dir_fd/no-follow support. Reject any link or
        # junction before opening; no traversal is performed by the walker.
        if _symlink_in_path(root, relative):
            raise OSError("Symbolic-link source file")
        with root.joinpath(*relative.parts).open("rb") as stream:
            yield stream


def _compare(root: Path, manifest: dict[str, Any], profile: str, runtime: Path) -> dict[str, Any]:
    objects = _validate_manifest(manifest, manifest["commit"], profile)
    rules = _export_rules(manifest["entries"], manifest.get("attributes", {}))

    def ignored(path):
        return _ignored(path, profile) or _export_ignored(path, rules)

    report: dict[str, Any] = {"state": "Verified", "reason": "", "modified": [], "missing": [], "added": []}
    expected = manifest["files"]
    for key, digest in expected.items():
        relative = _safe_relative_path(key)
        path = root.joinpath(*relative.parts)
        if _symlink_in_path(root, relative):
            report["modified"].append(key)
        else:
            try:
                file_stat = path.lstat()
            except FileNotFoundError:
                report["missing"].append(key)
                continue
            if not stat.S_ISREG(file_stat.st_mode):
                report["modified"].append(key)
                continue
            with _open_local(root, relative) as stream:
                digest_actual, blob = _digest_stream(stream, os.fstat(stream.fileno()).st_size)
                if blob != objects[key] and digest_actual != digest and _text_path(key):
                    stream.seek(0)
                    normalized = _normalized_digest(stream)
                    if normalized is not None:
                        digest_actual, blob = normalized
            upstream_matches = blob == objects[key]
            digest_matches = digest_actual == digest
            if upstream_matches != digest_matches:
                raise Unavailable("authoritative manifest unavailable")
            if not digest_matches:
                report["modified"].append(key)

    def walk_error(error):
        raise error

    # Docker's application lives at /. Walk only its explicitly owned roots.
    locations = [root] if profile == "source" else []
    actual = set()
    if profile == "docker":
        for directory in sorted(DOCKER_ROOTS):
            location = root / directory
            try:
                mode = location.lstat().st_mode
            except FileNotFoundError:
                continue
            if stat.S_ISDIR(mode):
                locations.append(location)
            else:
                actual.add(directory)
    for location in locations:
        if _is_link(location):
            continue
        for directory, dirs, names in os.walk(location, followlinks=False, onerror=walk_error):
            base = Path(directory)
            for name in dirs[:]:
                path = base / name
                relative = PurePosixPath(path.relative_to(root).as_posix())
                if ignored(relative) or path == runtime or _is_link(path) or (path / "pyvenv.cfg").is_file():
                    dirs.remove(name)
                    if _is_link(path) and not ignored(relative) and path != runtime:
                        actual.add(relative.as_posix())
            for name in names:
                relative = PurePosixPath((base / name).relative_to(root).as_posix())
                if not ignored(relative):
                    actual.add(unicodedata.normalize("NFC", relative.as_posix()))
    if profile == "docker":
        root_names = {key for key in expected if "/" not in key}
        for path in root.iterdir():
            if path.name in root_names or path.suffix in {".py", ".yml", ".yaml", ".json", ".toml", ".txt", ".lock", ".sh"}:
                if not ignored(PurePosixPath(path.name)) and (path.is_file() or _is_link(path)):
                    actual.add(path.name)
    report["added"] = sorted(actual - set(expected))
    for category in ("modified", "missing"):
        report[category] = sorted(set(report[category]))
    if any(report[category] for category in ("modified", "missing", "added")):
        report["state"] = "Modified"
    return report


def check_integrity(root: Path, config_dir: Path, profile: str = "source", upstream=None, allow_network: bool = True) -> dict[str, Any]:
    """Never treat an incomplete inspection or unavailable baseline as modified."""
    reason = "authoritative build identity unavailable"
    try:
        root = Path(root).resolve()
        runtime = Path(config_dir).resolve()
        if profile not in {"source", "docker"}:
            raise Unavailable("installation profile unavailable")
        commit = _read_identity(root)
        reason = "authoritative manifest unavailable"
        cache = runtime / CACHE_DIR / f"{REPOSITORY.replace('/', '-')}-{commit}-{profile}-v{SCHEMA}.json"
        manifest = None
        # Refuse symbolic-link metadata paths.
        if _symlink_in_path(Path(cache.anchor), PurePosixPath(*cache.parts[1:])):
            raise Unavailable("authoritative manifest unavailable")
        try:
            if cache.stat().st_size > 8 * 1024 * 1024:
                raise ValueError("Integrity cache too large")
            candidate = json.loads(cache.read_text(encoding="utf-8"))
            _validate_manifest(candidate, commit, profile)
            manifest = candidate
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            pass
        if manifest is None:
            if not allow_network:
                raise Unavailable("authoritative manifest unavailable")
            client = upstream or Upstream()
            try:
                manifest = client.baseline(commit, profile)
                _validate_manifest(manifest, commit, profile)
            finally:
                if upstream is None:
                    client.close()
            try:
                _write_manifest(cache, manifest)
            except OSError:
                # A read-only config directory must not invalidate a comparison.
                pass
        reason = "installation could not be inspected"
        return _compare(root, manifest, profile, runtime)
    except Unavailable as error:
        reason = str(error)
    except Exception as error:
        # Diagnostic boundary: filesystem/network/metadata errors cannot block runs.
        return {"state": "Not Verified", "reason": reason, "diagnostic": type(error).__name__, "modified": [], "missing": [], "added": []}
    return {"state": "Not Verified", "reason": reason, "modified": [], "missing": [], "added": []}


def format_integrity(report: dict[str, Any], limit: int = 20) -> list[str]:
    if report["state"] == "Verified":
        return ["Source Integrity: Verified"]
    if report["state"] == "Not Verified":
        return [f"Source Integrity: Not Verified ({report['reason']})"]
    lines = ["Source Integrity: MODIFIED"]
    for category in ("modified", "missing", "added"):
        if report[category]:
            lines.append(f"{category.title()}:")
            lines.extend(f"  {json.dumps(path, ensure_ascii=True)[1:-1]}" for path in report[category][:limit])
            if len(report[category]) > limit:
                lines.append(f"  {len(report[category]) - limit} more")
    return lines


def _start_background_check(root: Path, config_dir: Path, logger, profile: str, run: IntegrityRun):
    key = (str(root), str(config_dir), profile)
    with _pending_lock:
        if key in _pending:
            return _pending[key]
        _pending[key] = run

    def refresh():
        try:
            report = check_integrity(root, config_dir, profile)
            run.finish(report)
            for line in format_integrity(report):
                logger.info(f"    {line}")
            if report.get("diagnostic"):
                logger.debug(f"Source integrity diagnostic: {report['diagnostic']}")
        except Exception:
            run.finish({"state": "Not Verified", "reason": "installation could not be inspected", "modified": [], "missing": [], "added": []})
        finally:
            with _pending_lock:
                _pending.pop(key, None)

    try:
        threading.Thread(target=refresh, name="Kometa source integrity", daemon=True).start()
    except Exception:
        run.finish({"state": "Not Verified", "reason": "background check could not be started", "modified": [], "missing": [], "added": []})
        with _pending_lock:
            _pending.pop(key, None)
    return run


def log_integrity(root: Path | str, config_dir: Path | str, logger, profile: str = "source", enabled: bool = True) -> IntegrityRun:
    """Run both cached hashing and cold retrieval off the startup thread."""
    run = IntegrityRun()
    try:
        if not enabled:
            run.finish({"state": "Not Verified", "reason": "disabled by source-integrity option", "modified": [], "missing": [], "added": []})
            for line in format_integrity(run.snapshot()):
                logger.info(f"    {line}")
            return run
        logger.info("    Source Integrity: Not Verified (comparison in progress)")
        return _start_background_check(Path(root), Path(config_dir), logger, profile, run)
    except Exception:
        run.finish({"state": "Not Verified", "reason": "installation could not be inspected", "modified": [], "missing": [], "added": []})
        logger.info("    Source Integrity: Not Verified (installation could not be inspected)")
        return run


def log_integrity_summary(run: IntegrityRun, logger):
    """Repeat the completed result, or pending reason, without joining the thread."""
    try:
        report = run.snapshot()
        if report["reason"] == "comparison in progress":
            report["reason"] = "comparison still in progress at end of run"
        logger.separator("Source Integrity Summary", space=False, border=False)
        for line in format_integrity(report):
            logger.info(line)
    except Exception:
        logger.info("Source Integrity: Not Verified (summary unavailable)")
