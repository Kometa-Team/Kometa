# YamTrack Builders

Collect movies, shows, and tracked anime from your
[YamTrack](https://github.com/FuzzyGrim/YamTrack) instance. Both builders support
movies, shows, playlists, and custom sorting, using TMDb and TVDb IDs to identify items.

!!! warning "Configure YamTrack first"

    All builders require [YamTrack configuration](../../../config/yamtrack.md).
    List URLs must belong to the configured instance; tracking uses the configured user.

## Choose a builder

| Builder | Finds |
|:--------|:------|
| [`yamtrack_list`](#yamtrack-list) | Items in specific lists |
| [`yamtrack_tracked`](#yamtrack-tracked) | Tracked items with selected statuses and media types |

## Lists {#yamtrack-list}

`yamtrack_list` accepts a full list URL. Multiple sources can be supplied as a
YAML list or comma-separated string. Use `collection_order: custom` to preserve
list order and `sync_mode: sync` to keep membership synchronized.

Use `yamtrack_list_details` to also copy the list description into the collection
summary. With multiple lists, **only the first supplies the description**.
Replace the example URLs with URLs from your configured instance.

<span id="example-yamtrack-list-builders"></span>

=== "URL string"

    Follows list 1 in source order. The builder value is a full URL string.

    ```yaml
    collections:
      YamTrack Picks:
        yamtrack_list: https://yamtrack.domain.com/list/1
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiple lists and summary"

    Combines items from lists 1 and 2 using a YAML list of URL strings. The
    collection summary comes from list 1. This combines sources, rather than
    applying AND/OR search logic.

    ```yaml
    collections:
      Combined YamTrack Picks:
        yamtrack_list_details:
          - https://yamtrack.domain.com/list/1
          - https://yamtrack.domain.com/list/2
        collection_order: custom
        sync_mode: sync
    ```

## Tracked items {#yamtrack-tracked}

`yamtrack_tracked` selects tracked items using nested media and status dictionaries.

### Media blocks {#attributes}

| Attribute | Selects | Required |
|:----------|:--------|:---------|
| `movies` | Tracked movies | No |
| `tv_shows` | Tracked TV shows | No |
| `anime` | Tracked anime | No |

Anime may contain both movies and shows. Kometa includes only items matching the
current library's media type.

Each present block supports `dropped`, `planning`, `in_progress`, `paused`, and
`completed`. These are **unquoted booleans**: `true` includes a status and `false`
excludes it. **An omitted status in a present block defaults to `true`.**
To select only certain statuses, explicitly disable the others.

<span id="example-yamtrack-tracked-builder"></span>

=== "Select planning and in progress"

    Selects only movies marked Planning or In Progress. Both desired statuses
    are enabled; the remaining statuses are explicitly disabled. The nested
    dictionary is under `movies`, rather than directly under the builder.

    ```yaml
    collections:
      YamTrack Movies to Continue:
        yamtrack_tracked:
          movies:
            dropped: false
            planning: true
            in_progress: true
            paused: false
            completed: false
    ```

=== "Shows and anime"

    Selects Planning and In Progress items from both TV shows and anime.
    Each media block has its own status flags; the filters are not shared
    automatically between blocks. Anime is filtered to the current library type.

    ```yaml
    collections:
      YamTrack Shows and Anime to Continue:
        yamtrack_tracked:
          tv_shows:
            dropped: false
            planning: true
            in_progress: true
            paused: false
            completed: false
          anime:
            dropped: false
            planning: true
            in_progress: true
            paused: false
            completed: false
    ```
