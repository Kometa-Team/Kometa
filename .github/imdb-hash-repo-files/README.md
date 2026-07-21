# IMDb-Hash repo files (staging)

These files are **not part of Kometa's runtime**. They are staged here for convenience and are meant to
be copied into the **`Kometa-Team/IMDb-Hash`** repository (which hosts `HASH`, `LIST_HASH`,
`WATCHLIST_HASH` that Kometa already fetches at runtime).

## What they do

Kometa's `imdb_search` `interests:` filter needs a `name -> in-id` map to translate friendly interest
names into the `in########` IDs IMDb's GraphQL `advancedTitleSearch` expects. That catalog changes over
time (IMDb currently exposes 313 interests; Kometa's historical hardcoded map had 211). Rather than
hand-maintain it, Kometa fetches a live copy at runtime from:

    https://raw.githubusercontent.com/Kometa-Team/IMDb-Hash/master/INTERESTS.json

(see `interests_url` in `modules/imdb.py`), falling back to the bundled `interest_options_fallback`
snapshot if the fetch fails.

## Files

- **`generate_interests.py`** — queries IMDb's public GraphQL `interestCategories` catalog and writes
  `INTERESTS.json` (`{normalized_name: in-id}`, keys lowercased with spaces/hyphens -> underscores).
- **`update-interests.yml`** — a scheduled GitHub Action (weekly + manual) that runs the generator and
  commits `INTERESTS.json` when it changes.

## To wire it up

1. Copy `generate_interests.py` to the root of `Kometa-Team/IMDb-Hash`.
2. Copy `update-interests.yml` to `.github/workflows/update-interests.yml` in that repo.
3. Run it once (manually via `workflow_dispatch`, or `python generate_interests.py`) to create the
   initial `INTERESTS.json`.

The same generator can be used to periodically refresh Kometa's bundled `interest_options_fallback`
in `modules/imdb.py`.
