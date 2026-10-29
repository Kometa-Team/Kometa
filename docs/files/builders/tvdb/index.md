# TVDb Builders

Find movies and shows using [TheTVDb](https://www.thetvdb.com/). Select specific
titles by ID or URL, or collect the items in a TVDb list.

## Choose a builder

| Builder | Finds | Supports | Playlists / custom sort |
|:--------|:------|:---------|:-----------------------|
| [`tvdb_list`](#tvdb-list) | Items in a TVDb list or user list | Movies, shows | Yes |
| [`tvdb_movie`](#tvdb-movie) | Specific movies | Movies | No |
| [`tvdb_show`](#tvdb-show) | Specific shows | Shows | No |

## Using IDs and URLs

| Builder | Accepted value |
|:--------|:---------------|
| `tvdb_list` | Full [list](https://www.thetvdb.com/lists) or [user list](https://www.thetvdb.com/lists/custom) URL |
| `tvdb_movie` | Movie ID or full movie URL |
| `tvdb_show` | Series ID or full series URL |

These formats also apply to the corresponding [`_details` variants](#copy-metadata-from-tvdb).
An ID selects a specific title; a list URL selects the titles in that list.

All three builders accept multiple values. Use one value per YAML list entry or quote the complete
comma-separated string, such as `tvdb_movie: "107,157,74"`. Both formats combine
all the supplied sources; they do not provide AND/OR search logic.

## Lists {#tvdb-list}

Use `tvdb_list` with a full URL. Both named list URLs, such as
`https://www.thetvdb.com/lists/arrowverse`, and numbered list URLs, such as
`https://www.thetvdb.com/lists/6957`, are accepted.

<span id="example-tvdb-list-builders"></span>

This collection follows the Arrowverse list in its source order.
`collection_order: custom` preserves that order; `sync_mode: sync` keeps
collection membership synchronized as the list changes.

```yaml
collections:
  Arrowverse:
    tvdb_list: https://www.thetvdb.com/lists/arrowverse
    collection_order: custom
    sync_mode: sync
```

## Movies {#tvdb-movie}

Use `tvdb_movie` to select specific movies. These two examples select the same
three Lord of the Rings movies using different input formats.

<span id="example-tvdb-movie-builders"></span>

=== "Comma-separated IDs"

    Combines the three movie IDs into one collection. The quoted value is a
    single string containing comma-separated IDs.

    ```yaml
    collections:
      The Lord of the Rings:
        tvdb_movie: "107,157,74"
    ```

=== "YAML list of URLs"

    Selects the same movies by their full URLs. Each URL is a string in a YAML
    list, rather than part of a comma-separated string.

    ```yaml
    collections:
      The Lord of the Rings:
        tvdb_movie:
          - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-fellowship-of-the-ring
          - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-two-towers
          - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-return-of-the-king
    ```

## Shows {#tvdb-show}

Use `tvdb_show` to select specific series. This collection includes The Clone Wars
and Rebels, using a YAML list of numeric series IDs. Full series URLs, such as
`https://www.thetvdb.com/series/star-wars-the-clone-wars`, are also accepted.

<span id="example-tvdb-show-builders"></span>

```yaml
collections:
  Star Wars (Animated Shows):
    tvdb_show:
      - 83268
      - 283468
```

## Copy metadata from TVDb

Use a `_details` variant to select the same items and copy metadata to your
Kometa collection. With multiple values, **only the first entry supplies metadata**;
items from all entries are still included.

| Builder | Metadata variant | Copies |
|:--------|:-----------------|:-------|
| `tvdb_list` | `tvdb_list_details` | Description and poster |
| `tvdb_movie` | `tvdb_movie_details` | Summary, poster, and background |
| `tvdb_show` | `tvdb_show_details` | Summary, poster, and background |

=== "List metadata"

    Follows the Arrowverse list and copies its description and poster to the
    collection. The list's order and membership remain synchronized.

    ```yaml
    collections:
      Arrowverse:
        tvdb_list_details: https://www.thetvdb.com/lists/arrowverse
        collection_order: custom
        sync_mode: sync
    ```

=== "First-entry metadata"

    Includes both The Clone Wars and Rebels, but copies the summary, poster, and
    background from The Clone Wars (`83268`), the first entry. Put the series whose
    metadata you want first; the same rule applies to movies and lists.

    ```yaml
    collections:
      Star Wars (Animated Shows):
        tvdb_show_details:
          - 83268
          - 283468
    ```

!!! note "Artwork priority"

    For movie and show details, posters and backgrounds in your library's asset
    directory take priority over copied artwork, unless `tvdb_poster` or
    `tvdb_background` is also specified.
