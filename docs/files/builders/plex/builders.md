# Plex Builders

Build collections from items already in your Plex library. Use a
[smart filter](smart-filter.md) for rules Plex maintains automatically, or a manual
builder when Kometa should select the members on each run.

## Understanding smart vs manual collections

| Behaviour | Smart collection | Manual collection |
|:----------|:-----------------|:------------------|
| Membership updates | Plex reevaluates rules as library data changes | Kometa updates membership when it runs; items can also be edited manually |
| Selection | Plex's available filters | Library items selected by builders and filters |
| Typical use | Live rules, such as highly rated thrillers | Specific IDs, curated lists, or external sources |
| Editing | Change the filter rules | Change items or the configuration selecting them |
| Plex icon | Gear icon | Standard collection |

Smart collections are usually lighter and faster when all criteria live in Plex.
[Smart label collections](../../settings.md#smart-label-definitions) are an
exception to this simple distinction.

## Choose a builder {#plex-builder-types}

| Builder | Selects | Supports | Playlists / custom sort |
|:--------|:--------|:---------|:-----------------------|
| [`smart_filter`](smart-filter.md) | A live Plex filter | Movies, shows, music | Custom sort; music smart playlists only |
| [`plex_search`](search.md) | Search results when Kometa runs | See search attributes for library support | Yes |
| [`plex_all`](#plex-all) | Every library item | Movies, shows | No |
| [`plex_id`](#plex-id) | Plex metadata IDs or GUIDs | Movies, shows | No |
| [`plex_rating_key`](#plex-rating-key) | Server-local rating keys | Movies, shows | No |
| [`plex_watchlist`](#plex-watchlist) | Watchlist items | Movies, shows | Yes |
| [`plex_pilots`](#plex-pilots) | First episode of each show | Shows, episode level | Yes |
| [`plex_collectionless`](#plex-collectionless) | Items outside the considered collections | Movies, shows | No |

## Builder attributes

These query options apply to search and smart filters. Individual builders below
have their own input forms.

{%
    include-markdown "./search.md"
    start="<!--query-options-start-->"
    end="<!--query-options-end-->"
%}

{%
    include-markdown "./search-options.md"
    start="<!--shared-content-start-->"
%}

{%
    include-markdown "./sort-options.md"
    start="<!--shared-content-start-->"
%}

## All library items {#plex-all}

`plex_all` accepts a boolean. Use `true` to select the library, optionally narrowing
it with Kometa [filters](../../filters.md).

<span id="example-plex-all-builders"></span>

Selects items whose user rating is at least 9. `true` is an unquoted boolean and
`9` is an inclusive numeric threshold. These are Kometa filters, rather than a
live Plex smart filter.

```yaml
collections:
  My 9.0 Movies:
    plex_all: true
    filters:
      user_rating.gte: 9
```

## Specific identifiers

Neither ID builder guarantees a collection ordered like the input list.

### Metadata IDs {#plex-id}

`plex_id` accepts one value or a YAML list. Values are bare 24-character metadata
IDs or complete `plex://` GUIDs. Missing library items are skipped with a warning.
Episode GUIDs, such as `plex://episode/63e3eedd166819851638a317`, are also supported
for show-part collections.

Selects two movies using different identifier forms. Replace the example values
with Plex metadata identifiers for the items you want.

```yaml
collections:
  Selected Plex Movies:
    plex_id:
      - 5d7768243c3c2a001fbca85b
      - plex://movie/5d776824880197001ec901ab
```

### Rating keys {#plex-rating-key}

`plex_rating_key` accepts one numeric key or a YAML list. Keys are local to your
Plex server and may change if a library is rebuilt. Prefer `plex_id` when a stable
metadata identifier is available.

Selects items with local keys 123 and 456. Replace these integers with keys from
your server; they are not IMDb, TMDb, or Plex metadata IDs.

```yaml
collections:
  Selected Local Items:
    plex_rating_key:
      - 123
      - 456
```

## Pilot episodes {#plex-pilots}

!!! important "Episode level required"

    `plex_pilots` requires `builder_level: episode` and a show library.

<span id="example-plex-pilots-builders"></span>

Selects the first episode of every show. `true` enables the builder; the
collection contains episodes rather than complete shows.

```yaml
collections:
  Pilots:
    builder_level: episode
    plex_pilots: true
```

## Watchlist {#plex-watchlist}

`plex_watchlist` takes a sort string, defaulting to `added.asc`.

### Watchlist sort options {#watchlist-sort-options}

Append `.asc` or `.desc` to `title`, `release`, `critic_rating`, or `added`.
These sort by title, original release date, critic rating, or watchlist-added date.

<span id="example-plex-watchlist-builders"></span>

Selects watchlist items highest critic rating first. Custom ordering preserves
that order; synchronization aligns membership on Kometa runs.

```yaml
collections:
  My Watchlist:
    plex_watchlist: critic_rating.desc
    collection_order: custom
    sync_mode: sync
```

## Collectionless items {#plex-collectionless}

Selects items not in a collection, ignoring collections named by your exclusions.
**At least one exclusion is required.** This is not needed with
[smart label collections](../../settings.md#smart-label-definitions).

| Attribute | Value | Ignores when checking membership |
|:----------|:------|:--------------------------------|
| `exclude` | Collection title or YAML list | Named collections |
| `exclude_prefix` | Prefix or YAML list | Titles or sort titles starting with a prefix |

This can help when overlapping collection display modes expose or hide items
unexpectedly. A broad Marvel Cinematic Universe collection can conflict with a
hidden-items Iron Man collection. Set normal collections to hide their items,
then use a hidden collection to hold items that should remain visible. See the
[Plex display issue discussion](https://forums.plex.tv/t/collection-display-issue/305406).

<span id="example-plex-collectionless-builders"></span>

Builds a hidden collection of items that are collectionless after ignoring Marvel
Cinematic Universe and collections starting with `!`, `+`, or `~`. These exclusions
apply to the membership check, rather than excluding movies from the result.

```yaml
collections:
  Collectionless:
    plex_collectionless:
      exclude_prefix:
        - "!"
        - "+"
        - "~"
      exclude:
        - Marvel Cinematic Universe
    sort_title: ~_Collectionless
    collection_order: alpha
    collection_mode: hide
```
