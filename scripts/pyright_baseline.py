#!/usr/bin/env python3
"""Ratcheting baseline gate for pyright.

We don't require zero pyright errors on this codebase. We require that the
error count does not GO UP on a PR. New errors fail CI; fixing old errors
silently rolls the baseline forward without anyone having to do anything.

Usage:
    # Regenerate baseline (run after intentionally fixing errors)
    python scripts/pyright_baseline.py --regenerate

    # Check current state vs baseline (used by CI)
    python scripts/pyright_baseline.py --check

    # Show what's in the baseline
    python scripts/pyright_baseline.py --show

The baseline lives at .pyright-baseline.json and tracks per-file error
counts. This means:

  * Adding a new error to ANY file fails CI.
  * Fixing an error anywhere reduces the count (CI still passes).
  * Refactoring within a file is fine as long as the count doesn't grow.
  * Moving a file/error elsewhere may show as "decreased here, increased
    there" -- net delta is what matters.

Why per-file (not global total)? A global counter lets you swap one
error in builder.py for one in plex.py and CI never notices. Per-file
catches that.

Why not per-line fingerprints? Too brittle -- every formatting change
breaks the baseline. Per-file count is the right balance of strictness
and ergonomics.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

BASELINE_PATH = Path(__file__).resolve().parent.parent / ".pyright-baseline.json"


def run_pyright() -> dict:
    """Run pyright in JSON mode and return the parsed report."""
    result = subprocess.run(
        ["pyright", "--outputjson"],
        capture_output=True,
        text=True,
        check=False,
    )
    if not result.stdout.strip():
        print("pyright produced no output. stderr:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"failed to parse pyright JSON output: {exc}", file=sys.stderr)
        print("first 500 chars:", result.stdout[:500], file=sys.stderr)
        sys.exit(2)


def errors_by_file(report: dict) -> dict[str, int]:
    """Return {relative_file_path: error_count}."""
    repo_root = Path(__file__).resolve().parent.parent
    counts: Counter[str] = Counter()
    for diag in report.get("generalDiagnostics", []):
        if diag.get("severity") != "error":
            continue
        path = Path(diag["file"])
        try:
            rel = str(path.relative_to(repo_root))
        except ValueError:
            rel = str(path)
        counts[rel] += 1
    return dict(counts)


def load_baseline() -> dict[str, int]:
    if not BASELINE_PATH.exists():
        return {}
    with BASELINE_PATH.open() as f:
        data = json.load(f)
    return data.get("per_file_errors", {})


def save_baseline(per_file: dict[str, int]) -> None:
    total = sum(per_file.values())
    payload = {
        "_comment": (
            "Ratcheting pyright baseline. DO NOT hand-edit unless you know "
            "what you're doing. Regenerate with: "
            "python scripts/pyright_baseline.py --regenerate"
        ),
        "total_errors": total,
        "per_file_errors": dict(sorted(per_file.items())),
    }
    with BASELINE_PATH.open("w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(f"Baseline written to {BASELINE_PATH.name}: {total} errors across {len(per_file)} files")


def cmd_regenerate() -> int:
    print("Running pyright to regenerate baseline...")
    report = run_pyright()
    per_file = errors_by_file(report)
    save_baseline(per_file)
    return 0


def cmd_show() -> int:
    baseline = load_baseline()
    if not baseline:
        print(f"No baseline at {BASELINE_PATH}. Run with --regenerate to create one.")
        return 1
    total = sum(baseline.values())
    print(f"Baseline: {total} errors across {len(baseline)} files\n")
    for path, count in sorted(baseline.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {count:>4}  {path}")
    return 0


def cmd_check() -> int:
    baseline = load_baseline()
    if not baseline:
        print(
            f"ERROR: no baseline file at {BASELINE_PATH}.\n"
            "Run `python scripts/pyright_baseline.py --regenerate` to create one.",
            file=sys.stderr,
        )
        return 2

    print("Running pyright...")
    report = run_pyright()
    current = errors_by_file(report)

    baseline_total = sum(baseline.values())
    current_total = sum(current.values())

    print(f"\nBaseline total: {baseline_total} errors")
    print(f"Current total:  {current_total} errors")
    print(f"Delta:          {current_total - baseline_total:+d}\n")

    # Per-file comparison
    all_files = sorted(set(baseline) | set(current))
    regressions: list[tuple[str, int, int]] = []
    improvements: list[tuple[str, int, int]] = []

    for path in all_files:
        before = baseline.get(path, 0)
        after = current.get(path, 0)
        if after > before:
            regressions.append((path, before, after))
        elif after < before:
            improvements.append((path, before, after))

    if improvements:
        print(f"Improvements ({len(improvements)} files):")
        for path, before, after in improvements:
            print(f"  {path}: {before} -> {after}  ({after - before:+d})")
        print()

    if regressions:
        print(f"REGRESSIONS ({len(regressions)} files):")
        for path, before, after in regressions:
            print(f"  {path}: {before} -> {after}  ({after - before:+d})")
        print()
        print(
            "Pyright errors increased. Either fix the new errors, or if "
            "the changes are intentional and reviewed, regenerate the "
            "baseline with:",
            file=sys.stderr,
        )
        print("  python scripts/pyright_baseline.py --regenerate", file=sys.stderr)
        return 1

    if current_total < baseline_total:
        print(
            "Net improvement! Consider regenerating the baseline so future "
            "PRs are held to the new lower bar:"
        )
        print("  python scripts/pyright_baseline.py --regenerate")

    print("OK: no per-file regressions.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--regenerate", action="store_true", help="Rewrite the baseline file")
    group.add_argument("--check", action="store_true", help="Verify current state vs baseline (CI mode)")
    group.add_argument("--show", action="store_true", help="Print the current baseline")
    args = parser.parse_args()

    if args.regenerate:
        return cmd_regenerate()
    if args.check:
        return cmd_check()
    if args.show:
        return cmd_show()
    return 2


if __name__ == "__main__":
    sys.exit(main())
