"""Check that the installed packages match requirements.txt, so a stale base image cannot ship newer source with older dependencies."""

import json
import sys
from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def locked_requirements(text):
    """Yield the requirements from uv's exported requirements.txt that apply to this interpreter."""
    for line in text.splitlines():
        if not line.strip() or line[0] in " #":
            continue
        requirement = Requirement(line)
        if requirement.marker is None or requirement.marker.evaluate():
            yield requirement


def installed_commit(name):
    """Return the commit a package was installed from, or None when it was not a VCS install."""
    direct_url = metadata.distribution(name).read_text("direct_url.json")
    return json.loads(direct_url).get("vcs_info", {}).get("commit_id") if direct_url else None


def find_problems(requirements):
    """Return one message per locked requirement that is missing or differs from what is installed."""
    problems = []
    for requirement in requirements:
        name = canonicalize_name(requirement.name)
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            problems.append(f"{name}: not installed")
            continue
        if requirement.url:
            locked = requirement.url.rsplit("@", 1)[-1]
            actual = installed_commit(name)
            if actual != locked:
                problems.append(f"{name}: installed commit {actual}, locked {locked}")
        elif not requirement.specifier.contains(installed, prereleases=True):
            problems.append(f"{name}: installed {installed}, locked {requirement.specifier}")
    return problems


def main(argv):
    if len(argv) != 2:
        print("usage: verify_runtime_dependencies.py <requirements.txt>", file=sys.stderr)
        return 2
    requirements = list(locked_requirements(Path(argv[1]).read_text()))
    problems = find_problems(requirements)
    if problems:
        print(f"ERROR: {len(problems)} installed package(s) do not match {argv[1]}; the base image is probably stale:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    print(f"Verified {len(requirements)} locked runtime dependencies")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
