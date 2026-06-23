# Stats Dict Expansion Plan

## Current State

**Location**: `kometa.py:476` (main stats) and `modules/library.py:130` (per-library stats)

**Current shape**:
```python
{
    "created": 0,          # Collections/playlists created
    "modified": 0,         # Collections/playlists modified
    "deleted": 0,          # Collections/playlists deleted
    "added": 0,            # Items added to collections
    "unchanged": 0,        # Items unchanged in collections
    "removed": 0,          # Items removed from collections
    "radarr": 0,           # Items added to Radarr
    "sonarr": 0,           # Items added to Sonarr
    "names": []            # List of collection/playlist names (with library context)
}
```

**Webhook payload** (modules/webhooks.py:172):
```json
{
    "event": "run_end",
    "start_time": "...",
    "end_time": "...",
    "run_time": "...",
    "collections_created": stats["created"],
    "collections_modified": stats["modified"],
    "collections_deleted": stats["deleted"],
    "items_added": stats["added"],
    "items_removed": stats["removed"],
    "added_to_radarr": stats["radarr"],
    "added_to_sonarr": stats["sonarr"],
    "names": stats["names"]
}
```

---

## Expansion Opportunities

### Tier 1: Low-Hanging Fruit (Easy, High Value)

These are data points already being tracked or easily derivable from current code:

#### 1. **Overlays Applied**
- **What**: Count of items that received overlay updates
- **Already tracked?** Implicitly (overlays.py runs, but no stat counter)
- **Effort**: Low — add counter in `modules/overlays.py`
- **Webhook impact**: `overlays_applied: 0`
- **Rationale**: Users want to know if overlays actually ran successfully
- **Location**: `modules/overlays.py` around line 450-500 where overlays are applied

#### 2. **Items Unchanged**
- **What**: Total items processed but not modified
- **Already tracked?** YES — `library.stats["unchanged"]`
- **Effort**: Trivial — just add to webhook
- **Webhook impact**: `items_unchanged: 0`
- **Rationale**: Completes the picture of item mutation
- **Note**: This is already aggregated in stats dict, just not sent to webhook

#### 3. **Metadata Updates Applied**
- **What**: Count of items that received metadata (title, summary, artwork, tags, etc.)
- **Already tracked?** Partially — logged per collection, but no global counter
- **Effort**: Low — add global counter to stats dict
- **Webhook impact**: `metadata_updated: 0`
- **Rationale**: Distinct from collection creation; users want to know if metadata sync happened
- **Location**: `kometa.py` lines 980-1010 (items_added tracking for collections)

#### 4. **Run Duration Breakdown**
- **What**: Time spent in each major phase (config load, libraries, playlists, webhooks)
- **Already tracked?** Partially — `library_status[name]` contains phase timings
- **Effort**: Low — already have timing data in `library_status`, restructure for stats
- **Webhook impact**:
  ```json
  "duration": {
      "total": "4m 37s",
      "config_load": "0m 2s",
      "libraries": "4m 20s",
      "playlists": "0m 10s",
      "operations": "0m 5s"
  }
  ```
- **Rationale**: Performance monitoring, bottleneck identification
- **Note**: Already computed as `library_status[name]` values (All Collections Deleted, Library Loading, etc.)

#### 5. **Error Count**
- **What**: Total errors encountered during run
- **Already tracked?** YES — `data["errors"]` arrays in status dict
- **Effort**: Trivial — count errors during aggregation
- **Webhook impact**: `errors_encountered: 0`
- **Rationale**: Quick health check; distinguishes "partial success" from "complete success"

---

### Tier 2: Medium Effort, High Value

These require minor refactoring or new counters, but are commonly requested:

#### 6. **Library-Level Breakdown**
- **What**: Per-library stats instead of global totals
- **Already tracked?** YES — `library.stats` exists
- **Effort**: Medium — restructure webhook payload
- **Webhook impact**:
  ```json
  "libraries": {
      "Movies": {
          "collections_created": 3,
          "collections_modified": 5,
          "items_added": 120,
          "items_removed": 8,
          "items_unchanged": 450
      },
      "TV Shows": { ... }
  }
  ```
- **Rationale**: Multi-library users want granular diagnostics
- **Breaking change?** Only if strict JSON schema validation required; otherwise backward compatible (add new field)

#### 7. **Playlist Breakdown**
- **What**: Separate stats for playlists vs. collections
- **Already tracked?** YES — `playlist_stats` exists
- **Effort**: Medium — aggregate separately
- **Webhook impact**:
  ```json
  "collections": { "created": 5, ... },
  "playlists": { "created": 2, ... }
  ```
- **Rationale**: Users often manage collections and playlists separately; helps identify issues

#### 8. **Poster/Artwork Updates**
- **What**: Count of poster updates applied
- **Already tracked?** No — Plex poster changes are silent
- **Effort**: Medium — add flag tracking in `modules/plex.py` when poster is set
- **Webhook impact**: `posters_updated: 0`
- **Rationale**: Critical for poster-update-focused workflows
- **Note**: Related to the "poster update not needed" issue you're investigating

#### 9. **API Call Counts**
- **What**: How many external API calls were made (TMDb, Trakt, IMDB, etc.)
- **Already tracked?** Partially — logged individually, not aggregated
- **Effort**: Medium — add counter in API modules
- **Webhook impact**:
  ```json
  "api_calls": {
      "tmdb": 45,
      "trakt": 12,
      "anidb": 3,
      "radarr": 8,
      ...
  }
  ```
- **Rationale**: Performance optimization, rate-limit awareness, API quota planning

#### 10. **Cache Hit/Miss Ratio**
- **What**: How many API calls were served from cache
- **Already tracked?** YES — `modules/cache.py` has cache logic
- **Effort**: Medium — instrument cache.py with counters
- **Webhook impact**:
  ```json
  "cache": {
      "hits": 123,
      "misses": 45,
      "hit_ratio": "0.73"
  }
  ```
- **Rationale**: Benchmarking, cache effectiveness analysis

---

### Tier 3: Complex, Domain-Specific

These are valuable but require significant refactoring or new logic:

#### 11. **Item-Level Mutation Details**
- **What**: Breakdown of what changed per item (title changed, poster changed, tags added, etc.)
- **Already tracked?** No — mutations are applied but not categorized
- **Effort**: High — refactor builder/metadata logic to track mutation type
- **Webhook impact**:
  ```json
  "item_mutations": {
      "titles_changed": 5,
      "summaries_updated": 3,
      "ratings_set": 12,
      "posters_updated": 45,
      "tags_added": 67,
      "tags_removed": 8
  }
  ```
- **Rationale**: Fine-grained diagnostics, audit trail
- **Note**: This is related to your poster-update investigation

#### 12. **Collection Source Breakdown**
- **What**: How many collections came from each source (TMDb, Trakt, custom YAML, etc.)
- **Already tracked?** Partially — builder names are logged, not aggregated by source
- **Effort**: High — categorize builder names by source prefix
- **Webhook impact**:
  ```json
  "collection_sources": {
      "tmdb": 3,
      "trakt": 2,
      "custom": 5,
      "anidb": 1
  }
  ```
- **Rationale**: Understand reliance on each API source

#### 13. **Filtered Items Count**
- **What**: How many items were filtered out during collection build (filters: released_year, rating, etc.)
- **Already tracked?** No — filters are applied silently
- **Effort**: High — instrument builder.py filter logic
- **Webhook impact**:
  ```json
  "filters_applied": {
      "released_year": 45,
      "tmdb_rating": 23,
      "user_rating": 12,
      "resolution": 34
  }
  ```
- **Rationale**: Understand filter effectiveness, collection size drivers

#### 14. **Overlay Coverage**
- **What**: How many items received overlays vs. total items processed
- **Already tracked?** No — overlay logic is complex
- **Effort**: High — track overlay success/failure per item
- **Webhook impact**:
  ```json
  "overlays": {
      "items_processed": 1200,
      "items_applied": 987,
      "coverage_percent": "82.25",
      "skipped": { "no_image": 150, "invalid_template": 45, ... }
  }
  ```
- **Rationale**: Overlay effectiveness, issue diagnosis

#### 15. **Configuration Warnings/Deprecations**
- **What**: Count of warnings or deprecated config options used
- **Already tracked?** Partially — logged as warnings
- **Effort**: High — categorize and aggregate warnings
- **Webhook impact**:
  ```json
  "warnings": {
      "deprecated_options": 2,
      "unused_keys": 5,
      "api_failures": 1
  }
  ```
- **Rationale**: Help users proactively fix config issues

---

## Recommended Implementation Path

### Phase 1 (Immediate, ~2-3 hours)
**Goal**: 90% value with 10% effort

1. **Add to webhook payload** (backward compatible):
   - `items_unchanged` (already tracked)
   - `errors_encountered` (count from status dicts)
   - `overlays_applied` (add counter in overlays.py)
   - `metadata_updated` (aggregate from collection builder)

2. **Files to modify**:
   - `modules/webhooks.py` — expand payload (lines 172-184)
   - `modules/overlays.py` — add overlay counter
   - `kometa.py` — add metadata counter aggregation

### Phase 2 (Short-term, ~4-6 hours)
**Goal**: Diagnostic depth for power users

1. **Restructure for granularity**:
   - Library-level breakdown
   - Playlist vs. collection separation
   - Duration breakdown by phase
   - API call counts

2. **Files to modify**:
   - `kometa.py` — refactor stats aggregation
   - `modules/webhooks.py` — new payload structure
   - API modules (radarr.py, sonarr.py, etc.) — add call counters

### Phase 3 (Future, ~8-12 hours)
**Goal**: Full observability

1. **Mutation tracking**:
   - Poster updates (critical for your investigation!)
   - Metadata field changes
   - Filter application details

2. **Files to modify**:
   - `modules/builder.py` — track mutation types
   - `modules/overlays.py` — detailed application tracking
   - `modules/cache.py` — hit/miss ratio

---

## Design Considerations

### Backward Compatibility
- **Webhook receivers** may expect specific fields
- **Strategy**: Add new fields; keep existing ones
- **Alternative**: Version the webhook payload (`"version": 2`)

### Performance Impact
- **Avoid**: Per-item tracking in hot paths
- **Prefer**: Aggregate counters updated at phase boundaries

### JSON Schema Impact
- `json-schema/config-schema.json` doesn't validate webhook payloads (it validates config)
- No schema update needed for Phase 1

### Memory/Storage
- Stats dict is small (< 1 KB per run)
- Webhook payload stays reasonable (< 5 KB)

---

## Questions for Chaz

1. **Priority**: Which Tier 1 items matter most to you?
2. **Webhook version**: Keep current structure or restructure for library breakdown?
3. **Poster updates**: Is this related to your `investigate/poster-update-not-needed` branch?
4. **Frequency**: Do users want stats saved to a history file, or just webhook?

---

## Related Code Locations

| Item | File | Lines |
|------|------|-------|
| Stats init (main) | kometa.py | 476 |
| Stats init (library) | modules/library.py | 130 |
| Stats aggregation | kometa.py | 712–730 |
| Webhook payload | modules/webhooks.py | 172–184 |
| Library status | kometa.py | 741–913 |
| Overlay logic | modules/overlays.py | 450–500+ |
| Builder item tracking | kometa.py | 959–1040 |
| Playlist builder | kometa.py | 1113–1240 |
| Cache module | modules/cache.py | (main) |
| API modules | modules/{radarr,sonarr,tmdb,...}.py | (various) |

