#!/usr/bin/env python3
"""Run offline contracts or prepare/run isolated live multi-server smoke cases."""

import argparse
import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FIXTURES = ROOT / "tests" / "fixtures" / "multi_server"
CASES = ["shared", "selected", "failure", "playlist", "playlist-cross-server", "overlays", "overlays-selected", "operations", "operations-selected", "shelves"]


def read_yaml(path):
    from ruamel.yaml import YAML

    with path.open() as stream:
        return YAML(typ="safe").load(stream)


def write_yaml(path, data):
    from ruamel.yaml import YAML

    # Request owner-only permissions on POSIX; Windows uses inherited access rules.
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as stream:
        YAML().dump(data, stream)


def prepare(args):
    source = read_yaml(args.source.resolve())
    data = read_yaml(FIXTURES / "shared.yml")
    available = source.get("media_servers", {})
    names = {"my-plex": args.plex, "my-silo": args.silo, "my-emby": args.emby}
    connections = {}
    targets = {}
    overrides = dict(pair.split("=", 1) for pair in args.library)
    for alias, name in names.items():
        connection = available.get(name)
        if connection is None and alias == "my-plex":
            connection = {"type": "plex", **source.get("plex", {})}
        if not connection or not connection.get("url") or not connection.get("token"):
            raise ValueError(f"Missing connection for {name}; supply a named server or top-level plex connection")
        expected_type = {"my-plex": "plex", "my-silo": "silo", "my-emby": "emby"}[alias]
        if connection.get("type") != expected_type:
            raise ValueError(f"{name} must have type {expected_type}")
        connections[alias] = copy.deepcopy(connection)
        # Credentials may be copied; unrelated operations, webhooks, and files are not.
        candidates = [value.get("library_name", key) for key, value in source.get("libraries", {}).items() if isinstance(value, dict) and value.get("server") == name]
        remote_name = overrides.get(alias) or (candidates[0] if len(candidates) == 1 else "Movies")
        targets[alias] = {"library_name": remote_name}
    data["media_servers"] = connections
    if not source.get("tmdb", {}).get("apikey"):
        raise ValueError("Source config must supply tmdb.apikey")
    data["tmdb"] = copy.deepcopy(source["tmdb"])
    data["libraries"]["Movies"]["servers"] = targets
    data["libraries"]["Movies"]["collection_files"] = [{"file": str(FIXTURES / "collections.yml")}]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    write_yaml(output / "config.yml", data)
    print(f"Prepared {output / 'config.yml'}; inspect library names before running live cases.")
    print("Default live cases create/update the named validation collection and playlist; explicit overlay cases change posters. Cleanup is manual.")
    return 0


def live(args):
    from ruamel.yaml.error import YAMLError

    directory = args.directory.resolve()
    base = read_yaml(directory / "config.yml")
    targets = list(base["libraries"]["Movies"]["servers"])
    if not targets:
        raise ValueError("No server targets configured")
    cases = args.case or ["shared", "selected", "failure", "playlist"]
    results = []
    for case in cases:
        config = copy.deepcopy(base)
        flags = ["--collections-only"]
        expected = targets
        failed = []
        if case == "shelves":
            config["libraries"]["Movies"]["silo_shelves"] = True
            config["libraries"]["Movies"]["collection_files"] = [{"file": str(FIXTURES / name)} for name in ("shelves.yml", "shelves-default.yml", "shelves-earlier.yml")]
        if case == "selected" or case.endswith("-selected"):
            expected = [args.target]
            if args.target not in targets:
                raise ValueError(f"Unknown target {args.target}")
            flags += ["--libraries", f"Movies@{args.target}"]
        if case == "failure":
            config["media_servers"]["unavailable"] = {"type": "plex", "url": "http://127.0.0.1:1", "token": "validation-unavailable", "timeout": 1}
            config["libraries"]["Movies"]["servers"] = {"unavailable": {}, **config["libraries"]["Movies"]["servers"]}
            failed = ["unavailable"]
        elif case.startswith("playlist"):
            flags = ["--playlists-only"]
            filename = "playlists-cross-server.yml" if case == "playlist-cross-server" else "playlists.yml"
            config["playlist_files"] = [{"file": str(FIXTURES / filename)}]
        case_dir = directory / case
        case_dir.mkdir(mode=0o700)
        if case.startswith(("overlays", "operations")):
            library = config["libraries"]["Movies"]
            # Keep these cases independent of collection definitions and source operations.
            library.pop("collection_files", None)
            library.pop("operations", None)
            library.pop("overlay_files", None)
            config.pop("playlist_files", None)
            for target, overrides in library["servers"].items():
                for key in ("collection_files", "operations", "overlay_files"):
                    overrides.pop(key, None)
                if case.startswith("operations"):
                    overrides["operations"] = {"metadata_backup": {"path": str(case_dir / f"Movies@{target}_Metadata_Backup.yml"), "add_blank_entries": True}}
                else:
                    overrides["overlay_files"] = [{"file": str(FIXTURES / "overlays.yml")}]
            flags = ["--operations-only" if case.startswith("operations") else "--overlays-only", *flags[1:]]
        path = case_dir / "config.yml"
        write_yaml(path, config)
        command = [sys.executable, str(ROOT / "kometa.py"), "--run", "--config", str(path), "--read-only-config", "--timings", *flags]
        output = case_dir / "console.log"
        print(f"Running {case}; artifacts: {case_dir}", flush=True)
        timed_out = False
        with os.fdopen(os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as stream:
            try:
                process = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=args.timeout, check=False)
                code = process.returncode
            except subprocess.TimeoutExpired:
                code = None
                timed_out = True
        text = output.read_text(errors="replace")
        log_text = "\n".join(path.read_text(errors="replace") for path in (case_dir / "logs").rglob("*.log"))
        error_pattern = r"\bError:|\bTraceback\b|\bCRITICAL\b|\[ERROR\]"
        connected = set(re.findall(r"\((Movies@[^)]+)\) Library Connection Successful", text))
        disconnected = set(re.findall(r"\((Movies@[^)]+)\) Library Connection Failed", text))
        checks = {
            "finished_process": code == 0 and not timed_out,
            "connected_targets": connected == {f"Movies@{name}" for name in expected},
            "failed_targets": disconnected == {f"Movies@{name}" for name in failed},
            "no_collection_errors": not any(status in text for status in ("Collection Error:", "Kometa Failure", "Builder Validation Error", "Unknown Error")),
        }
        if case == "playlist-cross-server":
            checks["rejected_cross_server_playlist"] = "Playlist Error: All defined libraries must be on the same server" in text
        elif case == "playlist":
            checks["ran_playlist"] = "Finished Kometa Multi-Server Validation Playlist Playlist" in text
            checks["no_errors"] = not re.search(error_pattern, text + "\n" + log_text)
        elif case.startswith(("overlays", "operations")):
            stage = "Overlays" if case.startswith("overlays") else "Operations"
            checks["completed_stage_per_target"] = len(re.findall(rf"Finished .+ Library {stage}", text)) == len(expected)
            if stage == "Overlays":
                checks["uploaded_validation_posters"] = len(re.findall(r"Overlays Applied: [^\n]*MULTI SERVER TEST", text)) >= len(expected)
            for target in expected:
                checks[f"summary_{target}"] = f"(Movies@{target}) Summary" in text
                if stage == "Operations":
                    backup = case_dir / f"Movies@{target}_Metadata_Backup.yml"
                    try:
                        document = read_yaml(backup)
                        checks[f"backup_{target}"] = isinstance(document, dict) and isinstance(document.get("metadata"), dict) and bool(document["metadata"])
                    except (OSError, ValueError, YAMLError):
                        checks[f"backup_{target}"] = False
                else:
                    backup_dir = case_dir / "overlays" / f"Movies@{target} Original Posters"
                    checks[f"poster_backups_{target}"] = backup_dir.is_dir() and any(path.is_file() and path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") for path in backup_dir.iterdir())
            checks["no_errors"] = not re.search(error_pattern, text + "\n" + log_text)
        else:
            if case == "shelves":
                for title in ("Custom One", "Custom Two", "Automatic", "Earlier"):
                    name = f"Kometa Multi-Server Shelf {title}"
                    shelf = "Kometa Multi-Server Earlier Shelf" if title == "Earlier" else "Kometa Multi-Server Validation Shelf"
                    checks[f"collection_{title.lower().replace(' ', '_')}"] = text.count(f"Finished {name} Collection") == len(expected)
                    checks[f"shelf_{title.lower().replace(' ', '_')}"] = bool(re.search(rf"Silo Shelf: Movies@my-silo \| {shelf} \| {re.escape(name)} \| (Assigned|Unchanged)", text))
                checks["shelf_section_order"] = "Silo Shelf Order: Movies@my-silo | 20,60" in text
                checks["no_shelves_on_other_servers"] = not re.search(r"Silo Shelf: Movies@(my-plex|my-emby)", text)
            else:
                checks["ran_collection_per_target"] = text.count("Finished Kometa Multi-Server Validation Collection") == len(expected)
            for target in expected:
                checks[f"summary_{target}"] = f"(Movies@{target}) Summary" in text
            if not failed:
                checks["no_errors"] = not re.search(error_pattern, text + "\n" + log_text)
        result = {"case": case, "passed": all(checks.values()), "checks": checks, "returncode": code, "console": str(output)}
        results.append(result)
        print(json.dumps(result, indent=2))
    report = directory / "results.json"
    report.write_text(json.dumps(results, indent=2) + "\n")
    print("Log checks do not verify remote membership or artwork. Follow the README's manual checks.")
    return 0 if all(result["passed"] for result in results) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("offline", help="Run parser, path, schema, and adapter regression tests without live APIs")
    prep = commands.add_parser("prepare", help="Copy only connections into a private, isolated live config")
    prep.add_argument("--source", type=Path, required=True)
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--plex", default="my-plex")
    prep.add_argument("--silo", default="my-silo")
    prep.add_argument("--emby", default="my-emby")
    prep.add_argument("--library", action="append", default=[], metavar="ALIAS=NAME", help="Remote library name, e.g. my-silo=Cinema")
    run = commands.add_parser("live", help="Run validation cases and check logs; overlay cases change posters")
    run.add_argument("--directory", type=Path, required=True)
    run.add_argument("--case", action="append", choices=CASES)
    run.add_argument("--target", default="my-silo")
    run.add_argument("--timeout", type=int, default=900, help="Maximum seconds per case")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            return prepare(args)
        if args.command == "live":
            return live(args)
        env = dict(os.environ)
        # Disable PlexAPI file logging: offline tests must not write to a user's config.
        env["PLEXAPI_LOG_PATH"] = ""
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-rx",
                "tests/test_multi_server_validation.py",
                "tests/test_multi_server_harness.py",
                "tests/test_library_config.py",
                "tests/test_server_selection.py",
                "tests/test_media_server.py",
                "tests/test_schema_validation.py",
                "tests/test_silo_shelves.py",
                "tests/test_silo_collection_conflicts.py",
            ],
            cwd=ROOT,
            env=env,
            check=False,
        ).returncode
    except (ValueError, OSError, KeyError) as error:
        print(f"Validation setup failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
