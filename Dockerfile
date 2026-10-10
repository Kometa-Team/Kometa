# syntax=docker/dockerfile:1.7
ARG BASE_TAG=base
FROM kometateam/kometa:${BASE_TAG}
# Bump: verify master's increment-build.yml fix (PR #3309) unblocks nightly Docker builds

ARG BRANCH_NAME=master
ENV BRANCH_NAME=${BRANCH_NAME}
ENV KOMETA_DOCKER=True
# Exact source identity only; the integrity baseline is obtained at runtime.
ARG KOMETA_GIT_SHA
ENV KOMETA_GIT_SHA=${KOMETA_GIT_SHA}
ARG KOMETA_VERSION
LABEL org.opencontainers.image.version=${KOMETA_VERSION}

COPY . /

VOLUME /config
ENTRYPOINT ["/tini", "-s", "/.venv/bin/python3", "kometa.py", "--"]
