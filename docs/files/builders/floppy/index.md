# Floppy Builders

Collect movies, shows, and listed episodes from your
[Floppy](https://github.com/dannyvfilms/Floppy) instance. All builders below support
movies, shows, playlists, and custom sorting.

!!! warning "Configure Floppy first"

    Every builder requires the [Floppy connector](../../../config/floppy.md).
    Public lists work without a token. Private lists and tracking queries require
    an API token in the connector.

## Choose a builder

| Builder | Finds | Also copies |
|:--------|:------|:------------|
| [`floppy_list`](#floppy-list) | Supported items in specific lists | List tags as item labels, when enabled |
| [`floppy_list_details`](#floppy-list) | The same list items | List description as the collection summary; optional tags |
| [`floppy_tracked`](#floppy-tracked) | Tracked items matching statuses and media types | - |

For lists, use `collection_order: custom` to preserve source order and
`sync_mode: sync` to keep collection membership synchronized as the lists change.

## Lists {#floppy-list}

Use a list URL from your configured Floppy instance. Both list builders accept
list URLs; the dictionary form below adds the optional `sync_tags` setting.
Multiple URLs are supported, as illustrated by the YAML list of dictionaries.

| Option | Value | Purpose |
|:-------|:------|:--------|
| `url` | String | Full list URL from your configured instance. |
| `sync_tags` | Boolean | When `true`, adds the list's tags as Plex labels to items in the resulting collection. |

Replace the example URLs with URLs from your own instance.

=== "Summary and tags"

    Selects items from list 1, copies its description to the collection summary,
    and adds the list's tags as item labels. `url` is a string and `true` is an
    unquoted boolean.

    ```yaml
    collections:
      Floppy Picks:
        floppy_list_details:
          url: https://floppy.example.com/list/1
          sync_tags: true
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiple lists"

    Combines items from two lists using a YAML list of dictionaries. Tags are
    added from list 2, but not from list 1. These sources are combined, rather
    than used as AND/OR search filters.

    ```yaml
    collections:
      Combined Floppy Picks:
        floppy_list:
          - url: https://floppy.example.com/list/1
            sync_tags: false
          - url: https://floppy.example.com/list/2
            sync_tags: true
        collection_order: custom
        sync_mode: sync
    ```

=== "Exact episodes"

    Creates an episode collection from the exact episodes listed in the source,
    rather than selecting whole shows. Episode entries are read from the list's
    RSS feed; `builder_level: episode` is required.

    ```yaml
    collections:
      Floppy Episode Picks:
        builder_level: episode
        floppy_list: https://floppy.example.com/list/1
        collection_order: custom
        sync_mode: sync
    ```

## Tracked items {#floppy-tracked}

Use `floppy_tracked` to select items by tracking status and media type.
A private Floppy API token is required.

| Option | Allowed values | Purpose |
|:-------|:---------------|:--------|
| `status` | `no_status`, `completed`, `in_progress`, `planning`, `paused`, `dropped`, `all` | Select tracking statuses; `all` includes every tracked item regardless of status. |
| `type` | `movie`, `show`, `season`, `anime` | Select media types; defaults to `movie` in movie libraries and `show,season` in show libraries. |

=== "One status"

    Selects items marked in progress. `in_progress` is a status string; omitting
    `type` uses the media types appropriate to the current library.

    ```yaml
    collections:
      Tracked In Progress:
        floppy_tracked:
          status: in_progress
    ```

=== "Multiple statuses and anime"

    Selects tracked anime marked completed or in progress. `status` is a YAML
    list here, so either status matches; `type: anime` restricts the media type.
    There is no need for a pipe separator or `.any` suffix.

    ```yaml
    collections:
      Tracked Anime:
        floppy_tracked:
          status:
            - completed
            - in_progress
          type: anime
    ```

Anime entries are read by MyAnimeList ID and converted through Kometa's anime
mappings. Only anime resolving to an item in the current library is included.
