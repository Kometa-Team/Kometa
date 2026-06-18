# tmdb_discover Schema Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `tmdb_discover`'s `additionalProperties: true` in `collection-schema.json` with a fully-typed object that rejects unknown keys, enforces cross-dependencies, and infers movie vs TV context to enforce mutual exclusion.

**Architecture:** A new `tmdb-discover-block` definition is extracted into `collection-schema.json`'s `definitions` section. The existing `tmdb_discover` property is rewired to reference it via `oneOf` (single block or array of blocks, matching runtime `listdict` parsing). All 51 valid parameters are typed; six `allOf` if/then entries enforce cross-deps and mutual exclusion.

**Tech Stack:** JSON Schema Draft-06, `jsonschema` Python library (already in dev deps), `pytest`

---

## File Map

| File | Action |
|------|--------|
| `tests/test_collection_schema.py` | Create — all schema tests live here |
| `json-schema/collection-schema.json` | Modify — add `tmdb-discover-block` definition; rewire `tmdb_discover` property |

---

### Task 1: Test infrastructure + failing property tests

**Files:**
- Create: `tests/test_collection_schema.py`

- [ ] **Step 1: Create the test file with fixture and helpers**

```python
# tests/test_collection_schema.py
import json
import os

import pytest
from jsonschema import ValidationError, validate

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "json-schema", "collection-schema.json")


@pytest.fixture(scope="module")
def collection_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _collection_with_discover(discover_block):
    """Wrap a tmdb_discover block in a minimal valid collection document."""
    return {"collections": {"Test": {"tmdb_discover": discover_block}}}
```

- [ ] **Step 2: Write failing tests — unknown key and wrong type**

Append to `tests/test_collection_schema.py`:

```python
# ── Property validation ────────────────────────────────────────────────────────


def test_valid_shared_keys_pass(collection_schema):
    doc = _collection_with_discover({
        "limit": 50,
        "sort_by": "popularity.asc",
        "with_genres": "28",
        "vote_average.gte": 7.0,
        "include_adult": False,
    })
    validate(doc, collection_schema)  # must not raise


def test_unknown_key_rejected(collection_schema):
    doc = _collection_with_discover({"limit": 50, "nonexistent_key": "value"})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_limit_must_be_integer(collection_schema):
    doc = _collection_with_discover({"limit": "fifty"})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_vote_average_must_be_number(collection_schema):
    doc = _collection_with_discover({"vote_average.gte": "high"})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_include_adult_must_be_boolean(collection_schema):
    doc = _collection_with_discover({"include_adult": "yes"})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_with_status_out_of_range(collection_schema):
    doc = _collection_with_discover({"with_status": 6})  # max is 5
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_with_type_out_of_range(collection_schema):
    doc = _collection_with_discover({"with_type": 7})  # max is 6
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_year_below_minimum(collection_schema):
    doc = _collection_with_discover({"year": 1799})
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_array_of_blocks_valid(collection_schema):
    doc = _collection_with_discover([
        {"limit": 20, "with_genres": "28"},
        {"limit": 30, "with_genres": "35"},
    ])
    validate(doc, collection_schema)  # must not raise
```

- [ ] **Step 3: Run tests — expect failures on all except `test_valid_shared_keys_pass`**

```bash
pytest tests/test_collection_schema.py -v
```

Expected: `test_valid_shared_keys_pass` PASS (schema allows everything now), all others FAIL with `Failed: DID NOT RAISE` or similar.

---

### Task 2: Implement base property definitions

**Files:**
- Modify: `json-schema/collection-schema.json`

- [ ] **Step 1: Add the `tmdb-discover-block` definition**

In `json-schema/collection-schema.json`, inside the `"definitions"` object (add before the closing `}` of definitions), add the new definition. The block has `"type": "object"`, `"additionalProperties": false`, and all 51 properties. The `"allOf"` array is left empty (`[]`) for now — it will be filled in Tasks 4 and 6.

```json
"tmdb-discover-block": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
        "limit":                      { "type": "integer", "minimum": 0 },
        "sort_by":                    { "type": "string" },
        "with_companies":             { "type": "string" },
        "without_companies":          { "type": "string" },
        "with_genres":                { "type": "string" },
        "without_genres":             { "type": "string" },
        "with_keywords":              { "type": "string" },
        "without_keywords":           { "type": "string" },
        "with_watch_providers":       { "type": "string" },
        "without_watch_providers":    { "type": "string" },
        "with_original_language":     { "type": "string" },
        "with_overview_translation":  { "type": "string" },
        "watch_region":               { "type": "string" },
        "with_watch_monetization_types": { "type": "string" },
        "vote_count.gte":             { "type": "integer" },
        "vote_count.lte":             { "type": "integer" },
        "with_runtime.gte":           { "type": "integer" },
        "with_runtime.lte":           { "type": "integer" },
        "vote_average.gte":           { "type": "number" },
        "vote_average.lte":           { "type": "number" },
        "include_adult":              { "type": "boolean" },
        "with_cast":                  { "type": "string" },
        "with_crew":                  { "type": "string" },
        "with_people":                { "type": "string" },
        "with_release_type":          { "type": "string" },
        "with_title_translation":     { "type": "string" },
        "with_origin_country":        { "type": "string" },
        "region":                     { "type": "string" },
        "certification_country":      { "type": "string" },
        "certification":              { "type": "string" },
        "certification.lte":          { "type": "string" },
        "certification.gte":          { "type": "string" },
        "year":                       { "type": "integer", "minimum": 1800 },
        "primary_release_year":       { "type": "integer", "minimum": 1800 },
        "primary_release_date.gte":   { "type": "string" },
        "primary_release_date.lte":   { "type": "string" },
        "release_date.gte":           { "type": "string" },
        "release_date.lte":           { "type": "string" },
        "include_video":              { "type": "boolean" },
        "with_networks":              { "type": "string" },
        "with_name_translation":      { "type": "string" },
        "timezone":                   { "type": "string" },
        "first_air_date_year":        { "type": "integer", "minimum": 1800 },
        "air_date.gte":               { "type": "string" },
        "air_date.lte":               { "type": "string" },
        "first_air_date.gte":         { "type": "string" },
        "first_air_date.lte":         { "type": "string" },
        "with_status":                { "type": "integer", "minimum": 0, "maximum": 5 },
        "with_type":                  { "type": "integer", "minimum": 0, "maximum": 6 },
        "screened_theatrically":      { "type": "boolean" },
        "include_null_first_air_dates": { "type": "boolean" }
    },
    "allOf": []
}
```

- [ ] **Step 2: Rewire `tmdb_discover` in `collection-definition`**

Find this in `collection-definition.properties`:

```json
"tmdb_discover": {
    "description": "TMDb Discover search. Uses TMDb's Discover API with movie or show search attributes.",
    "type": "object",
    "additionalProperties": true
},
```

Replace with:

```json
"tmdb_discover": {
    "description": "TMDb Discover search. Uses TMDb's Discover API with movie or show search attributes.",
    "oneOf": [
        { "$ref": "#/definitions/tmdb-discover-block" },
        { "type": "array", "items": { "$ref": "#/definitions/tmdb-discover-block" } }
    ]
},
```

- [ ] **Step 3: Run the Task 1 tests — expect property tests to pass now**

```bash
pytest tests/test_collection_schema.py -v
```

Expected: `test_valid_shared_keys_pass`, `test_unknown_key_rejected`, `test_limit_must_be_integer`, `test_vote_average_must_be_number`, `test_include_adult_must_be_boolean`, `test_with_status_out_of_range`, `test_with_type_out_of_range`, `test_year_below_minimum`, `test_array_of_blocks_valid` all PASS. Cross-dep and mutual exclusion tests not yet added.

- [ ] **Step 4: Run existing validator tests — must still pass**

```bash
pytest tests/test_validator.py -v
```

Expected: all existing tests PASS.

- [ ] **Step 5: Commit**

```bash
git add json-schema/collection-schema.json tests/test_collection_schema.py
git commit -m "feat: add tmdb-discover-block definition with typed properties"
```

---

### Task 3: Failing tests for cross-dependency rules

**Files:**
- Modify: `tests/test_collection_schema.py`

- [ ] **Step 1: Append cross-dependency tests**

```python
# ── Cross-dependency rules ─────────────────────────────────────────────────────


def test_certification_country_without_certification_rejected(collection_schema):
    doc = _collection_with_discover({
        "certification_country": "US",
        # missing: certification / certification.lte / certification.gte
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_certification_without_certification_country_rejected(collection_schema):
    doc = _collection_with_discover({
        "certification": "PG-13",
        # missing: certification_country
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_certification_lte_without_certification_country_rejected(collection_schema):
    doc = _collection_with_discover({
        "certification.lte": "PG-13",
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_certification_pair_valid(collection_schema):
    doc = _collection_with_discover({
        "certification_country": "US",
        "certification": "PG-13",
    })
    validate(doc, collection_schema)  # must not raise


def test_certification_country_with_lte_valid(collection_schema):
    doc = _collection_with_discover({
        "certification_country": "US",
        "certification.lte": "R",
    })
    validate(doc, collection_schema)  # must not raise


def test_watch_region_without_providers_rejected(collection_schema):
    doc = _collection_with_discover({
        "watch_region": "US",
        # missing: with_watch_providers / without_watch_providers / with_watch_monetization_types
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_monetization_types_without_watch_region_rejected(collection_schema):
    doc = _collection_with_discover({
        "with_watch_monetization_types": "flatrate",
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_watch_region_with_providers_valid(collection_schema):
    doc = _collection_with_discover({
        "watch_region": "US",
        "with_watch_providers": "8",
    })
    validate(doc, collection_schema)  # must not raise


def test_watch_region_with_monetization_valid(collection_schema):
    doc = _collection_with_discover({
        "watch_region": "GB",
        "with_watch_monetization_types": "flatrate",
    })
    validate(doc, collection_schema)  # must not raise
```

- [ ] **Step 2: Run — expect all cross-dep tests to fail**

```bash
pytest tests/test_collection_schema.py -v -k "certification or watch"
```

Expected: all nine tests FAIL (cross-dep allOf not yet in schema).

---

### Task 4: Implement cross-dependency allOf entries

**Files:**
- Modify: `json-schema/collection-schema.json`

- [ ] **Step 1: Replace the empty `allOf` with the four cross-dependency entries**

In `tmdb-discover-block`, replace `"allOf": []` with:

```json
"allOf": [
    {
        "if": { "required": ["certification_country"] },
        "then": {
            "anyOf": [
                { "required": ["certification"] },
                { "required": ["certification.lte"] },
                { "required": ["certification.gte"] }
            ]
        }
    },
    {
        "if": {
            "anyOf": [
                { "required": ["certification"] },
                { "required": ["certification.lte"] },
                { "required": ["certification.gte"] }
            ]
        },
        "then": { "required": ["certification_country"] }
    },
    {
        "if": { "required": ["watch_region"] },
        "then": {
            "anyOf": [
                { "required": ["with_watch_providers"] },
                { "required": ["without_watch_providers"] },
                { "required": ["with_watch_monetization_types"] }
            ]
        }
    },
    {
        "if": { "required": ["with_watch_monetization_types"] },
        "then": { "required": ["watch_region"] }
    }
]
```

- [ ] **Step 2: Run cross-dep tests — expect all to pass now**

```bash
pytest tests/test_collection_schema.py -v -k "certification or watch"
```

Expected: all nine tests PASS.

- [ ] **Step 3: Run full test suite**

```bash
pytest tests/test_collection_schema.py tests/test_validator.py -v
```

Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add json-schema/collection-schema.json tests/test_collection_schema.py
git commit -m "feat: add tmdb_discover cross-dependency allOf validation"
```

---

### Task 5: Failing tests for mutual exclusion and sort_by branching

**Files:**
- Modify: `tests/test_collection_schema.py`

- [ ] **Step 1: Append mutual exclusion tests**

```python
# ── Mutual exclusion ──────────────────────────────────────────────────────────


def test_movie_only_keys_pass(collection_schema):
    doc = _collection_with_discover({
        "limit": 100,
        "with_cast": "500",
        "primary_release_year": 2023,
        "sort_by": "popularity.desc",
    })
    validate(doc, collection_schema)  # must not raise


def test_tv_only_keys_pass(collection_schema):
    doc = _collection_with_discover({
        "limit": 100,
        "with_networks": "213",
        "first_air_date_year": 2023,
        "sort_by": "popularity.desc",
    })
    validate(doc, collection_schema)  # must not raise


def test_mixed_movie_and_tv_keys_rejected(collection_schema):
    doc = _collection_with_discover({
        "primary_release_year": 2023,  # movie-only
        "with_networks": "213",         # TV-only
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_tv_signal_disallows_movie_key(collection_schema):
    doc = _collection_with_discover({
        "first_air_date_year": 2022,    # TV signal
        "with_cast": "500",              # movie-only — must be rejected
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_movie_signal_disallows_tv_key(collection_schema):
    doc = _collection_with_discover({
        "with_cast": "500",              # movie signal
        "include_null_first_air_dates": True,  # TV-only — must be rejected
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_shared_only_allows_all_sort_options(collection_schema):
    """No movie/TV signal — sort_by is unconstrained."""
    doc = _collection_with_discover({"sort_by": "name.asc"})  # TV-only sort option
    validate(doc, collection_schema)  # must not raise (no signal present)


def test_movie_signal_restricts_sort_by(collection_schema):
    doc = _collection_with_discover({
        "with_cast": "500",       # movie signal
        "sort_by": "name.asc",    # TV-only sort option — must be rejected
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_movie_signal_allows_movie_sort(collection_schema):
    doc = _collection_with_discover({
        "with_cast": "500",
        "sort_by": "revenue.desc",   # movie sort option
    })
    validate(doc, collection_schema)  # must not raise


def test_tv_signal_restricts_sort_by(collection_schema):
    doc = _collection_with_discover({
        "with_networks": "213",       # TV signal
        "sort_by": "revenue.desc",    # movie-only sort option — must be rejected
    })
    with pytest.raises(ValidationError):
        validate(doc, collection_schema)


def test_tv_signal_allows_tv_sort(collection_schema):
    doc = _collection_with_discover({
        "with_networks": "213",
        "sort_by": "name.asc",   # TV sort option
    })
    validate(doc, collection_schema)  # must not raise
```

- [ ] **Step 2: Run — expect all mutual exclusion tests to fail**

```bash
pytest tests/test_collection_schema.py -v -k "movie or tv or sort or mixed"
```

Expected: `test_movie_only_keys_pass`, `test_tv_only_keys_pass`, `test_shared_only_allows_all_sort_options`, `test_movie_signal_allows_movie_sort`, `test_tv_signal_allows_tv_sort` PASS; `test_mixed_movie_and_tv_keys_rejected`, `test_tv_signal_disallows_movie_key`, `test_movie_signal_disallows_tv_key`, `test_movie_signal_restricts_sort_by`, `test_tv_signal_restricts_sort_by` FAIL.

---

### Task 6: Implement mutual exclusion allOf entries

**Files:**
- Modify: `json-schema/collection-schema.json`

- [ ] **Step 1: Append movie-signal entry to `allOf` in `tmdb-discover-block`**

Add after the four cross-dep entries:

```json
{
    "if": {
        "anyOf": [
            { "required": ["with_cast"] },
            { "required": ["with_crew"] },
            { "required": ["with_people"] },
            { "required": ["year"] },
            { "required": ["primary_release_year"] },
            { "required": ["primary_release_date.gte"] },
            { "required": ["primary_release_date.lte"] },
            { "required": ["release_date.gte"] },
            { "required": ["release_date.lte"] },
            { "required": ["with_release_type"] },
            { "required": ["with_title_translation"] },
            { "required": ["with_origin_country"] },
            { "required": ["certification_country"] },
            { "required": ["certification"] },
            { "required": ["certification.lte"] },
            { "required": ["certification.gte"] },
            { "required": ["region"] },
            { "required": ["include_video"] }
        ]
    },
    "then": {
        "allOf": [
            {
                "not": {
                    "anyOf": [
                        { "required": ["with_networks"] },
                        { "required": ["with_type"] },
                        { "required": ["with_status"] },
                        { "required": ["with_name_translation"] },
                        { "required": ["first_air_date_year"] },
                        { "required": ["first_air_date.gte"] },
                        { "required": ["first_air_date.lte"] },
                        { "required": ["air_date.gte"] },
                        { "required": ["air_date.lte"] },
                        { "required": ["timezone"] },
                        { "required": ["screened_theatrically"] },
                        { "required": ["include_null_first_air_dates"] }
                    ]
                }
            },
            {
                "properties": {
                    "sort_by": {
                        "enum": [
                            "original_title.asc", "original_title.desc",
                            "popularity.asc", "popularity.desc",
                            "primary_release_date.asc", "primary_release_date.desc",
                            "release_date.asc", "release_date.desc",
                            "revenue.asc", "revenue.desc",
                            "title.asc", "title.desc",
                            "vote_average.asc", "vote_average.desc",
                            "vote_count.asc", "vote_count.desc"
                        ]
                    }
                }
            }
        ]
    }
}
```

- [ ] **Step 2: Append TV-signal entry to `allOf`**

```json
{
    "if": {
        "anyOf": [
            { "required": ["with_networks"] },
            { "required": ["with_type"] },
            { "required": ["with_status"] },
            { "required": ["with_name_translation"] },
            { "required": ["first_air_date_year"] },
            { "required": ["first_air_date.gte"] },
            { "required": ["first_air_date.lte"] },
            { "required": ["air_date.gte"] },
            { "required": ["air_date.lte"] },
            { "required": ["timezone"] },
            { "required": ["screened_theatrically"] },
            { "required": ["include_null_first_air_dates"] }
        ]
    },
    "then": {
        "allOf": [
            {
                "not": {
                    "anyOf": [
                        { "required": ["with_cast"] },
                        { "required": ["with_crew"] },
                        { "required": ["with_people"] },
                        { "required": ["year"] },
                        { "required": ["primary_release_year"] },
                        { "required": ["primary_release_date.gte"] },
                        { "required": ["primary_release_date.lte"] },
                        { "required": ["release_date.gte"] },
                        { "required": ["release_date.lte"] },
                        { "required": ["with_release_type"] },
                        { "required": ["with_title_translation"] },
                        { "required": ["with_origin_country"] },
                        { "required": ["certification_country"] },
                        { "required": ["certification"] },
                        { "required": ["certification.lte"] },
                        { "required": ["certification.gte"] },
                        { "required": ["region"] },
                        { "required": ["include_video"] }
                    ]
                }
            },
            {
                "properties": {
                    "sort_by": {
                        "enum": [
                            "first_air_date.asc", "first_air_date.desc",
                            "name.asc", "name.desc",
                            "original_name.asc", "original_name.desc",
                            "popularity.asc", "popularity.desc",
                            "vote_average.asc", "vote_average.desc",
                            "vote_count.asc", "vote_count.desc"
                        ]
                    }
                }
            }
        ]
    }
}
```

- [ ] **Step 3: Run the full test suite**

```bash
pytest tests/test_collection_schema.py tests/test_validator.py -v
```

Expected: all tests PASS.

- [ ] **Step 4: Commit**

```bash
git add json-schema/collection-schema.json tests/test_collection_schema.py
git commit -m "feat: add tmdb_discover mutual exclusion and sort_by branching"
```

---

### Task 7: Final verification

**Files:** none changed

- [ ] **Step 1: Validate the kitchen_sink config still passes**

`json-schema/kitchen_sink_config.yml` is a config-level file, not a collection file, so it isn't validated against `collection-schema.json` directly. Confirm this:

```bash
python3 -c "
import json, sys
from jsonschema import validate, ValidationError
schema = json.load(open('json-schema/collection-schema.json'))
try:
    validate({'collections': {}}, schema)
    print('empty collections: OK')
except ValidationError as e:
    print('FAIL:', e.message)
"
```

Expected output: `empty collections: OK`

- [ ] **Step 2: Spot-check a real defaults file with tmdb_discover**

```bash
python3 -c "
import json, yaml
from jsonschema import validate, ValidationError

schema = json.load(open('json-schema/collection-schema.json'))

# Minimal synthetic collection with shared-only tmdb_discover
doc = {
    'collections': {
        'Popular Movies': {
            'tmdb_discover': {'limit': 100, 'sort_by': 'popularity.desc', 'vote_average.gte': 6.5}
        }
    }
}
validate(doc, schema)
print('Shared-only discover: OK')

# Movie-only discover
doc2 = {
    'collections': {
        'Recent Movies': {
            'tmdb_discover': {'limit': 50, 'primary_release_year': 2024, 'sort_by': 'release_date.desc'}
        }
    }
}
validate(doc2, schema)
print('Movie-only discover: OK')

# TV-only discover
doc3 = {
    'collections': {
        'New Shows': {
            'tmdb_discover': {'limit': 50, 'first_air_date_year': 2024, 'sort_by': 'name.asc'}
        }
    }
}
validate(doc3, schema)
print('TV-only discover: OK')
"
```

Expected output:
```
Shared-only discover: OK
Movie-only discover: OK
TV-only discover: OK
```

- [ ] **Step 3: Run the complete test suite one final time**

```bash
pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 4: Final commit if any loose changes remain**

```bash
git status
# If clean, nothing to do. If any files modified, commit them.
```
