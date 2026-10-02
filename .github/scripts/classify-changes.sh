#!/usr/bin/env bash
# Reads changed file paths (one per line) on stdin and prints build/base/deps=true lines for $GITHUB_OUTPUT; shared by ci.yml and increment-build.yml.
set -euo pipefail

build=false
base=false
deps=false

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  case "$file" in
    # base image inputs: these change what ships in :base (uv.lock/pyproject.toml are handled below, via deps)
    docker/Dockerfile.base | docker/uv-bootstrap.txt | requirements.txt)
      echo "$file will trigger base image build" >&2
      base=true
      ;;
    defaults/* | fonts/* | modules/* | kometa.py | Dockerfile | .dockerignore)
      echo "$file will trigger docker build" >&2
      build=true
      ;;
    pyproject.toml | uv.lock)
      echo "$file will regenerate dependency exports" >&2
      deps=true
      ;;
    *)
      echo "$file will not trigger docker build" >&2
      ;;
  esac
done

# pyproject.toml/uv.lock also gate the runtime dependency group (not just docs/dev), so a deps
# change must rebuild the base image too, or requirements.txt can drift from what ships in :base
if [[ "$deps" == true ]]; then
  base=true
fi

# the nightly image is built FROM the base image, so a base change always rebuilds both
if [[ "$base" == true ]]; then
  build=true
fi

echo "build=$build"
echo "base=$base"
echo "deps=$deps"
