#!/usr/bin/env bash
# Pushes the version bump commit to nightly; if nightly moved meanwhile, rebases onto it only when what landed cannot change the images.
set -euo pipefail

checkout_sha="${1:?checkout SHA is required}"

if git push origin nightly; then
  exit 0
fi

git fetch origin nightly
landed=$(git diff --name-only "$checkout_sha" origin/nightly | bash "$(dirname "$0")/classify-changes.sh" 2>/dev/null)
if [[ "$landed" == *=true* ]]; then
  echo "::error::nightly gained image-affecting changes during this run; the next run will build them" >&2
  exit 1
fi

git rebase origin/nightly
git push origin nightly
