# Design: `tmdb_discover` if/then/else Schema Validation

**Date:** 2026-06-09
**Branch:** schema-improvements
**Scope:** `json-schema/collection-schema.json` only — no runtime code changes

---

## Problem

The `tmdb_discover` builder in `collection-schema.json` is currently defined as:

```json
"tmdb_discover": {
    "type": "object",
    "additionalProperties": true
}
```

This allows any key with any value. The runtime (`builder.py:3118–3227`) enforces ~50 valid parameter keys, value types, movie-only vs TV-only restrictions, and cross-dependencies — but none of these are caught at schema validation time.

---

## Goal

Replace `additionalProperties: true` with a fully-typed, conditionally-validated object schema that:

1. Rejects unknown keys (`additionalProperties: false`)
2. Type-checks every valid parameter
3. Enforces cross-dependency co-requirements (certification, watch_region)
4. Infers library type from the keys present and enforces mutual exclusion between movie-only and TV-only parameters
5. Restricts `sort_by` enum to the correct set when library type can be inferred

No changes to `builder.py`, `modules/tmdb.py`, or any other runtime code.

---

## Approach: Inferred Mutual Exclusion

Collection YAML files are library-agnostic — there is no `type: movie|show` key inside a `tmdb_discover` block at authoring time. Library type is resolved at runtime against the actual Plex library.

Instead of a discriminator key, the schema infers library type from the presence of known movie-only or TV-only parameters, then enforces mutual exclusion via `allOf` if/then blocks. Both conditions evaluate simultaneously with no ordering dependency.

---

## Parameter Definitions

All parameters defined under `properties` on the `tmdb_discover` object schema.

### Control

| Key | Type | Constraints |
|-----|------|-------------|
| `limit` | integer | minimum: 0 |
| `sort_by` | string | unconstrained at base level; enum-constrained by inferred library type (Section: Mutual Exclusion) |

### Shared — strings

`with_companies`, `without_companies`, `with_genres`, `without_genres`, `with_keywords`,
`without_keywords`, `with_watch_providers`, `without_watch_providers`,
`with_original_language`, `with_overview_translation`

### Shared — watch region

| Key | Type |
|-----|------|
| `watch_region` | string |
| `with_watch_monetization_types` | string |

### Shared — numeric

| Key | Type | Constraints |
|-----|------|-------------|
| `vote_count.gte` | integer | — |
| `vote_count.lte` | integer | — |
| `with_runtime.gte` | integer | — |
| `with_runtime.lte` | integer | — |
| `vote_average.gte` | number | — |
| `vote_average.lte` | number | — |

### Shared — boolean

| Key | Type |
|-----|------|
| `include_adult` | boolean |

### Movie-only — strings

`with_cast`, `with_crew`, `with_people`, `with_release_type`, `with_title_translation`, `with_origin_country`

### Movie-only — certification (cross-dep group)

`region` (string), `certification_country` (string), `certification` (string),
`certification.lte` (string), `certification.gte` (string)

### Movie-only — years and dates

| Key | Type | Constraints |
|-----|------|-------------|
| `year` | integer | minimum: 1800 |
| `primary_release_year` | integer | minimum: 1800 |
| `primary_release_date.gte` | string | — |
| `primary_release_date.lte` | string | — |
| `release_date.gte` | string | — |
| `release_date.lte` | string | — |

### Movie-only — boolean

| Key | Type |
|-----|------|
| `include_video` | boolean |

### TV-only — strings

`with_networks`, `with_name_translation`, `timezone`

### TV-only — year and dates

| Key | Type | Constraints |
|-----|------|-------------|
| `first_air_date_year` | integer | minimum: 1800 |
| `air_date.gte` | string | — |
| `air_date.lte` | string | — |
| `first_air_date.gte` | string | — |
| `first_air_date.lte` | string | — |

### TV-only — integers

| Key | Type | Constraints |
|-----|------|-------------|
| `with_status` | integer | minimum: 0, maximum: 5 |
| `with_type` | integer | minimum: 0, maximum: 6 |

### TV-only — booleans

`screened_theatrically`, `include_null_first_air_dates`

---

## Cross-Dependency Rules

Four `allOf` if/then entries, mapping directly to `builder.py:3156–3174`:

| If | Then (required) |
|----|-----------------|
| `certification_country` present | at least one of `certification`, `certification.lte`, `certification.gte` |
| any of `certification` / `certification.lte` / `certification.gte` present | `certification_country` |
| `watch_region` present | at least one of `with_watch_providers`, `without_watch_providers`, `with_watch_monetization_types` |
| `with_watch_monetization_types` present | `watch_region` |

---

## Inferred Mutual Exclusion

Two `allOf` if/then entries. Both evaluate simultaneously — ordering is irrelevant.

### Movie signal

**If** any of the following keys is present:
`with_cast`, `with_crew`, `with_people`, `year`, `primary_release_year`,
`primary_release_date.gte`, `primary_release_date.lte`, `release_date.gte`, `release_date.lte`,
`with_release_type`, `with_title_translation`, `with_origin_country`,
`certification_country`, `certification`, `certification.lte`, `certification.gte`,
`region`, `include_video`

**Then:**
- Disallow all TV-only keys (via `not: { anyOf: [{ required: [key] }, ...] }` for each TV-only key)
- Restrict `sort_by` to movie sort enum:
  `original_title.asc`, `original_title.desc`, `popularity.asc`, `popularity.desc`,
  `primary_release_date.asc`, `primary_release_date.desc`, `release_date.asc`, `release_date.desc`,
  `revenue.asc`, `revenue.desc`, `title.asc`, `title.desc`,
  `vote_average.asc`, `vote_average.desc`, `vote_count.asc`, `vote_count.desc`

### TV signal

**If** any of the following keys is present:
`with_networks`, `with_type`, `with_status`, `with_name_translation`,
`first_air_date_year`, `first_air_date.gte`, `first_air_date.lte`,
`air_date.gte`, `air_date.lte`, `timezone`, `screened_theatrically`,
`include_null_first_air_dates`

**Then:**
- Disallow all movie-only keys (same `not: { anyOf: [...] }` pattern)
- Restrict `sort_by` to TV sort enum:
  `first_air_date.asc`, `first_air_date.desc`, `name.asc`, `name.desc`,
  `original_name.asc`, `original_name.desc`, `popularity.asc`, `popularity.desc`,
  `vote_average.asc`, `vote_average.desc`, `vote_count.asc`, `vote_count.desc`

### Ambiguous case (shared keys only)

When neither signal fires, `sort_by` accepts any string and all keys in `properties` are valid. This is correct: library type is genuinely unknown.

### Mixed case (both signals fire)

Both `allOf` entries evaluate and both fail. The user receives errors from both directions, which is the correct outcome — mixing movie-only and TV-only keys is never valid regardless of which side has more keys. This matches `builder.py:3140–3143` exactly.

---

## Schema Structure (outline)

```json
"tmdb_discover": {
    "description": "...",
    "oneOf": [
        { "$ref": "#/definitions/tmdb-discover-block" },
        { "type": "array", "items": { "$ref": "#/definitions/tmdb-discover-block" } }
    ]
}
```

```json
"tmdb-discover-block": {
    "type": "object",
    "additionalProperties": false,
    "properties": { ...all ~50 keys... },
    "allOf": [
        { ...cross-dep: certification_country... },
        { ...cross-dep: certification → certification_country... },
        { ...cross-dep: watch_region... },
        { ...cross-dep: with_watch_monetization_types... },
        { ...movie signal mutual exclusion + sort_by... },
        { ...TV signal mutual exclusion + sort_by... }
    ]
}
```

Note: `builder.py:3119` parses `tmdb_discover` with `datatype="listdict"`, which accepts both a single dict and a list of dicts. The `oneOf` array wrapper therefore matches actual runtime behaviour and should be included.

---

## Files Changed

- `json-schema/collection-schema.json` — the only file modified

## Files Not Changed

- `modules/builder.py`
- `modules/tmdb.py`
- Any other Python module

---

## Testing

Run the existing validator tests after implementation:

```bash
pytest tests/test_validator.py
```

Manually validate:
- `json-schema/kitchen_sink_config.yml` still passes
- A crafted invalid file (TV + movie keys mixed) fails with expected errors
- A crafted invalid file (certification without certification_country) fails
