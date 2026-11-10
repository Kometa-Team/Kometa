#!/usr/bin/env bash
# Prints the files changed on nightly since the commit the published nightly image was built from; if that commit cannot be determined it prints a base image input so everything rebuilds (FALLBACK_MODE=rebuild, the default) or diffs since the last version bump (FALLBACK_MODE=last-bump); run in a full nightly checkout with NIGHTLY_IMAGE set.
set -euo pipefail

image="${NIGHTLY_IMAGE:?NIGHTLY_IMAGE is required}"
fallback_mode="${FALLBACK_MODE:-rebuild}"
retry_delays="${INSPECT_RETRY_DELAYS:-0 5 15}"
merge_sha="${MERGE_SHA:-}"

for tool in docker jq git; do
  command -v "$tool" >/dev/null || { echo "::error::${tool} is required to read the published image revision" >&2; exit 1; }
done

revision=""
# The image records the commit it was built from, so the diff also covers runs that were cancelled, failed after their bump or lost a push race; retried because registry reads can fail transiently.
for delay in $retry_delays; do
  sleep "$delay"
  revision=$(docker buildx imagetools inspect "$image" --format '{{json .Image}}' 2>/dev/null \
    | jq -r '(if has("config") then . else (.["linux/amd64"] // (to_entries | map(.value) | first)) end) | .config.Labels["org.opencontainers.image.revision"] // empty' 2>/dev/null || true)
  [[ "$revision" =~ ^[0-9a-f]{40}$ ]] && break
done

if [[ "$revision" =~ ^[0-9a-f]{40}$ ]] && git cat-file -e "${revision}^{commit}" 2>/dev/null && git merge-base --is-ancestor "$revision" HEAD; then
  echo "Diffing ${revision} to HEAD" >&2
  git diff --name-only "$revision" HEAD
  exit 0
fi

case "$fallback_mode" in
  rebuild)
    echo "::warning::No usable source revision on ${image}; rebuilding the base and nightly images to be safe" >&2
    echo "docker/Dockerfile.base"
    ;;
  last-bump)
    echo "::warning::No usable source revision on ${image}; diffing since the last version bump instead" >&2
    base=$(git log -1 --format=%H --author='^GitHub Action <action@github.com>$' -- VERSION)
    # Use this merge's first parent when the bump landed after this merge.
    if [[ -n "$base" && -n "$merge_sha" ]] && ! git merge-base --is-ancestor "$base" "${merge_sha}^1"; then
      base="${merge_sha}^1"
    fi
    if [[ -z "$base" ]]; then
      echo "docker/Dockerfile.base"
    else
      git diff --name-only "$base" HEAD
    fi
    ;;
  *)
    echo "::error::Unknown FALLBACK_MODE '${fallback_mode}' (expected rebuild or last-bump)" >&2
    exit 1
    ;;
esac
