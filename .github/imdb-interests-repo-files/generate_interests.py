#!/usr/bin/env python3
"""Regenerate INTERESTS.json for the Kometa-Team/IMDb-Interests repo.

NOTE: This file is staged inside the Kometa repo for convenience but is intended to live in the
Kometa-Team/IMDb-Interests repository. A scheduled GitHub Action in that repo runs it and commits
INTERESTS.json when it changes; Kometa fetches that file at runtime (modules/imdb.py: interests_url)
and falls back to its bundled snapshot if the fetch fails.

It queries IMDb's public GraphQL `interestCategories` catalog and emits a flat
{normalized_name: in-id} map matching the key format Kometa's imdb_search `interests:` filter expects
(text lowercased, spaces and hyphens -> underscores, '&' preserved).

Usage:
    python generate_interests.py            # writes ./INTERESTS.json
    python generate_interests.py out.json   # writes to a custom path
"""

import json
import sys
import time

import requests

GRAPHQL_URL = "https://api.graphql.imdb.com/"
HEADERS = {"content-type": "application/json"}
# One request pulls every category with all of its interests; these caps are generous ceilings.
QUERY = (
    "{ interestCategories(first: 200) { edges { node { "
    "interests(first: 2000) { edges { node { id primaryText { text } } } } "
    "} } } }"
)


def normalize(text):
    """Match modules/imdb.py's historical key format: lowercase, spaces/hyphens -> underscores."""
    return text.lower().replace(" ", "_").replace("-", "_")


def fetch_interests(retries=3):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": QUERY}, timeout=60)
            response.raise_for_status()
            payload = response.json()
            if "errors" in payload:
                raise RuntimeError(f"GraphQL errors: {payload['errors']}")
            return payload["data"]["interestCategories"]["edges"]
        except Exception as e:  # noqa: BLE001 - script-level: any failure should retry then fail loudly
            last_error = e
            print(f"Attempt {attempt}/{retries} failed: {e}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise SystemExit(f"Failed to fetch IMDb interests after {retries} attempts: {last_error}")


def build_map(category_edges):
    interests = {}
    for category in category_edges:
        node = category.get("node") or {}
        for edge in (node.get("interests") or {}).get("edges") or []:
            interest = edge.get("node") or {}
            interest_id = interest.get("id")
            text = ((interest.get("primaryText") or {}).get("text")) or ""
            if not interest_id or not text:
                continue
            key = normalize(text)
            # First occurrence wins; interests can appear under multiple categories.
            interests.setdefault(key, interest_id)
    # Sort by numeric id for a stable, readable diff.
    return dict(sorted(interests.items(), key=lambda kv: int(kv[1][2:])))


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "INTERESTS.json"
    interests = build_map(fetch_interests())
    if len(interests) < 200:
        raise SystemExit(f"Refusing to write: only {len(interests)} interests found (expected 300+); IMDb response looks incomplete.")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(interests, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {len(interests)} interests to {out_path}")


if __name__ == "__main__":
    main()
