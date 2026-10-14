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

# Warn until the metadata workflow reaches master; retain validated identity
# independently of runtime environment overrides.
RUN /.venv/bin/python3 - <<'PY'
import os
import re
import sys
from pathlib import Path

commit = os.environ.get("KOMETA_GIT_SHA", "")
version = os.environ.get("KOMETA_VERSION", "")
hint = Path(".kometa_sha")
hint.unlink(missing_ok=True)
valid_commit = bool(re.fullmatch(r"[0-9a-f]{40}", commit))
valid_version = bool(version) and version == Path("VERSION").read_text().strip()
if not valid_commit:
    print("WARNING: KOMETA_GIT_SHA must be the full source commit SHA; source identity hint omitted", file=sys.stderr)
if not valid_version:
    print("WARNING: KOMETA_VERSION must match the source VERSION file; source identity hint omitted", file=sys.stderr)
if valid_commit and valid_version:
    hint.write_text(commit + "\n")
PY

VOLUME /config
ENTRYPOINT ["/tini", "-s", "/.venv/bin/python3", "kometa.py", "--"]
