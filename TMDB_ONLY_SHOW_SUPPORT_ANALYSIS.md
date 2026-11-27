# TMDb-only Plex show support

## Question

Can Kometa match and operate on Plex TV shows that have a TMDb ID but no TVDb ID?

Example: *The Great British Bake-Off*.

## Current behavior

Kometa recognizes `tmdb://...` GUIDs on Plex items, but for shows it currently tries to convert the TMDb ID to a TVDb ID. If the TMDb record has no TVDb external ID, conversion fails with a `MappingConvertError`.

Relevant code:

- `modules/convert.py`: `get_id()` converts TMDb show IDs to TVDb IDs and raises if none is available.
- `modules/convert.py`: `tmdb_to_tvdb()` and `tvdb_to_tmdb()` perform the provider conversion and cache successful mappings.
- `modules/library.py`: Plex show indexes are currently built as `show_map` and `show_rating_key_map`, whose values are assumed to be TVDb IDs.
- `modules/builder.py`: `tmdb_show` inputs are converted to TVDb IDs before searching Plex's `show_map`.

This is why a TMDb-only Plex show cannot currently be found through the normal TMDb show matching path.

## Proposed design

Add a parallel TMDb show index instead of putting TMDb IDs into the existing TVDb maps.

Likely additions:

- `tmdb_show_map`: TMDb show ID -> Plex rating keys.
- `tmdb_show_rating_key_map`: Plex rating key -> TMDb show ID.
- A helper such as `get_show_tmdb_id()` that first checks the TMDb map and otherwise converts the known TVDb ID.

Keep the existing TVDb maps unchanged. This preserves behavior for Sonarr, TVDb episode/season IDs, TVDb artwork, and other integrations that genuinely require TVDb.

Update TMDb show matching to search the TMDb map first and use TMDb->TVDb conversion only as a fallback. Update cache/index construction so a show with only a TMDb GUID is retained rather than rejected.

## Season and episode operations

The change can support season- and episode-level TMDb operations, but the downstream paths must also use the new TMDb show lookup. A show-level index alone is not enough.

TMDb season and episode operations are feasible because Plex supplies the parent show, season number, and episode number. Kometa already has TMDb lookups for:

```python
TMDb.get_season(show_tmdb_id, season_number)
TMDb.get_episode(show_tmdb_id, season_number, episode_number)
```

`modules/plex.py:get_tmdb_episode()` already supports an episode TMDb GUID and falls back to positional lookup.

Expected support after the full change:

- TMDb-based season artwork: yes.
- TMDb-based episode artwork: yes.
- TMDb-based episode ratings/metadata: yes, using the TMDb show ID plus season/episode numbers.
- Episode-level collections based on TMDb-derived items: yes, provided collection selection uses Plex hierarchy and season/episode coordinates.
- Sonarr, TVDb-specific artwork, and workflows requiring TVDb season/episode IDs: still require a TVDb ID.

Relevant current consumers that assume TVDb-backed show mappings include:

- `modules/plex.py:find_poster_url()`
- season title/artwork logic in `modules/builder.py` and `modules/operations.py`
- Trakt/MDBList synchronization paths in `modules/builder.py`
- Sonarr path/tag operations

These should use the new TMDb helper only where the operation is TMDb-compatible; TVDb-only integrations should continue to skip or warn when no TVDb ID exists.

## Important logging behavior

A missing cross-reference is usually an online metadata gap, not a Kometa crash. The conversion function labels the condition as a `Convert Warning`, but callers may log it as an error if the requested operation cannot continue. After TMDb-only support, warnings should remain for TVDb-only operations while TMDb-compatible operations proceed.

## Suggested tests

Add mocked tests covering:

1. A Plex show with only a `tmdb://` GUID is indexed in the TMDb show map.
2. A `tmdb_show` builder finds that show without calling TMDb->TVDb conversion.
3. A show with both IDs continues to use the existing TVDb path.
4. Season artwork resolves through `get_season()` using the TMDb show ID.
5. Episode artwork/ratings resolve through positional TMDb episode lookup.
6. Sonarr/TVDb-only operations still warn or skip rather than using a TMDb ID as a TVDb ID.

