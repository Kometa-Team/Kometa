#!/usr/bin/env bash
# Reads changed file paths (one per line) on stdin and prints build/base/deps=true lines for $GITHUB_OUTPUT; shared by ci.yml and increment-build.yml.
set -euo pipefail

build=false
base=false
deps=false

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  case "$file" in
    # base image inputs: only the runtime export changes what ships, uv.lock and pyproject.toml also cover the docs and dev groups
    Dockerfile.base | uv-bootstrap.txt | requirements.txt)
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

# the nightly image is built FROM the base image, so a base change always rebuilds both
if [[ "$base" == true ]]; then
  build=true
fi

echo "build=$build"
echo "base=$base"
echo "deps=$deps"
