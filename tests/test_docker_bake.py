"""Keep docker-bake.hcl in step with the Dockerfile and the workflows that build from it."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pr_base_context_matches_the_dockerfile_from_line():
    dockerfile = (ROOT / "Dockerfile").read_text()
    default_tag = re.search(r"^ARG BASE_TAG=(\S+)$", dockerfile, re.MULTILINE).group(1)
    image = re.search(r"^FROM (\S+):\$\{BASE_TAG\}$", dockerfile, re.MULTILINE).group(1)
    bake = (ROOT / "docker-bake.hcl").read_text()
    assert f'"{image}:{default_tag}" = "target:base"' in bake


def test_workflows_select_targets_that_exist():
    bake = (ROOT / "docker-bake.hcl").read_text()
    assert {"base", "app", "app-pr-base"} <= set(re.findall(r'^target "([^"]+)"', bake, re.MULTILINE))
    for workflow in ("ci.yml", "docker-test.yml"):
        text = (ROOT / ".github" / "workflows" / workflow).read_text()
        assert "docker-bake.hcl" in text, workflow
        assert set(re.findall(r"'(app(?:-pr-base)?)'", text)) == {"app", "app-pr-base"}, workflow
