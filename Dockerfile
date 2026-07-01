# syntax=docker/dockerfile:1.7
ARG BASE_TAG=base
FROM kometateam/kometa:${BASE_TAG}
# Bump v4: actions:write fix is in, trigger nightly rebuild

ARG BRANCH_NAME=master
ENV BRANCH_NAME=${BRANCH_NAME}
ENV KOMETA_DOCKER=True

COPY . /

VOLUME /config
ENTRYPOINT ["/tini", "-s", "python3", "kometa.py", "--"]
