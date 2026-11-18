# AniDB Builders

Collect anime from [AniDB](https://anidb.net/) IDs, relation graphs, and tags.
All builders support movie and show libraries; playlist and custom-sort support
varies as shown below.

## Choose a builder

| Builder | Finds | Playlists / custom sort |
|:--------|:------|:-----------------------|
| [`anidb_id`](#anidb-id) | Specific anime | No |
| [`anidb_relation`](#anidb-relation) | Anime in a relation graph | No |
| [`anidb_tag`](#anidb-tag) | Anime matching a tag ID | Yes |
| [`anidb_tag_name`](#anidb-tag-name) | Anime matching all named tags | Yes |

## IDs and relations

Both ID-based builders accept an AniDB ID or anime URL. Supply multiple sources
as a YAML list or comma-separated string. These combine sources; named tags use
different matching rules, described below.

### Specific anime {#anidb-id}

<span id="example-anidb-id-builders"></span>

Selects the three specified Sword Art Online entries using a YAML list of IDs.
A quoted string such as `"8692,8691,13494"` or anime URLs such as
`https://anidb.net/anime/8692` can also be used.

```yaml
collections:
  Sword Art Online:
    anidb_id:
      - 8692
      - 8691
      - 13494
```

### Relation graphs {#anidb-relation}

<span id="example-anidb-relation-builders"></span>

Selects all anime in the relation graph for entry 8692, rather than just that
entry. The graph URL is also accepted; use this format to inspect relations
in your browser, replacing the ID as needed.

```yaml
collections:
  All Sword Art Online:
    anidb_relation: https://anidb.net/anime/8692/relation/graph
```

## Tags

Both tag builders support custom ordering. Use `collection_order: custom` to
preserve returned order and `sync_mode: sync` to keep membership synchronized.
The `mature` setting in your AniDB configuration controls whether mature/adult
anime are included.

### Tag IDs {#anidb-tag}

Use an integer tag ID directly, or a dictionary with these options. Browse the
[Kometa AniDB tag reference](https://utilities.kometa.wiki/anidb-service/tags) to find IDs.

<span id="attributes"></span>

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `tag_id` | Tag ID, required | Tag to match |
| `limit` | Integer; default `1000` | Maximum anime to return |

<span id="example-anidb-tag-builders"></span>

Selects up to 10 anime with the Military tag. `36` is a tag ID; `10` is a result
limit. Use `anidb_tag: 36` for the simpler form with the default limit.

```yaml
collections:
  Top 10 Military Anime:
    anidb_tag:
      tag_id: 36
      limit: 10
    collection_order: custom
    sync_mode: sync
```

### Tag ID examples {#tag-id-examples}

| Tag | ID |
|:----|:---|
| Military | `36` |
| Future | `2626` |
| Comedy | `2853` |
| Action | `2604` |
| Fantasy | `2849` |
| Sci-Fi | `2846` |

### Named tags {#anidb-tag-name}

Accepts a tag-name string, a YAML list of names, or a dictionary. Names are
case-insensitive. **Multiple names must all match (AND)**; a YAML list here does
not mean OR.

<span id="anidb-tag-name-attributes"></span>

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `tags` | String or YAML list, required | All tags to match |
| `min_weight` | Integer, 0-1000; default `0` | Minimum tag weight |

<span id="example-anidb-tag-name-builders"></span>

=== "One tag"

    Selects anime with the Action tag. The builder value is a string.

    ```yaml
    collections:
      Action Anime:
        anidb_tag_name: action
        collection_order: custom
        sync_mode: sync
    ```

=== "AND and tag weight"

    Requires both Action and Comedy, with the matched tags meeting a minimum
    weight of 400. The YAML list supplies tag names; `400` is a numeric threshold.
    Omit `min_weight` to use the default of zero.

    ```yaml
    collections:
      Action Comedy With Strong Tags:
        anidb_tag_name:
          tags:
            - action
            - comedy
          min_weight: 400
        collection_order: custom
        sync_mode: sync
    ```

### Tag weight {#tag-weight}

| Weight | Meaning |
|:-------|:--------|
| `600` and above | Core theme or element |
| `400`-`599` | Significant element |
| `200`-`399` | Notable element |
| `0`-`199` | Minor element |

### Common tag names {#common-tag-names}

`action`, `adventure`, `comedy`, `drama`, `fantasy`, `horror`, `mecha`, `military`,
`mystery`, `romance`, `sci-fi`, `slice of life`, `sports`, `supernatural`, `thriller`.
