# syntax=docker/dockerfile:1.7
ARG BASE_TAG=base
FROM kometateam/kometa:${BASE_TAG}
WORKDIR /
# Bump: verify master's increment-build.yml fix (PR #3309) unblocks nightly Docker builds

ARG BRANCH_NAME=master
ENV BRANCH_NAME=${BRANCH_NAME}
ENV KOMETA_DOCKER=True
# Exact source identity only; the integrity baseline is obtained at runtime.
ARG KOMETA_GIT_SHA
ENV KOMETA_GIT_SHA=${KOMETA_GIT_SHA}
ARG KOMETA_VERSION
LABEL org.opencontainers.image.version=${KOMETA_VERSION}
LABEL org.opencontainers.image.revision=${KOMETA_GIT_SHA}
LABEL org.opencontainers.image.source="https://github.com/Kometa-Team/Kometa"

COPY . /

# Reject images without the exact source identity and version, and retain the
# identity independently of runtime environment overrides.
RUN /.venv/bin/python3 - <<'PY'
import os
import re
from pathlib import Path

commit = os.environ.get("KOMETA_GIT_SHA", "")
version = os.environ.get("KOMETA_VERSION", "")
if not re.fullmatch(r"[0-9a-f]{40}", commit):
    raise SystemExit("KOMETA_GIT_SHA must be the full source commit SHA")
if not version or version != Path("VERSION").read_text().strip():
    raise SystemExit("KOMETA_VERSION must match the source VERSION file")
Path(".kometa_sha").write_text(commit + "\n")
PY

VOLUME /config
ENTRYPOINT ["/tini", "-s", "/.venv/bin/python3", "kometa.py", "--"]
