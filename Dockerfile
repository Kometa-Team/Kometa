# syntax=docker/dockerfile:1.7
ARG BASE_TAG=base
FROM kometateam/kometa:${BASE_TAG}
# Bump: verify master's increment-build.yml fix (PR #3309) unblocks nightly Docker builds

ARG BRANCH_NAME=master
ENV BRANCH_NAME=${BRANCH_NAME}
ENV KOMETA_DOCKER=True

COPY . /

VOLUME /config
ENTRYPOINT ["/tini", "-s", "python3", "kometa.py", "--"]
