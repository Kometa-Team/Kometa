# Tautulli Builders

Select library items using [Tautulli](https://tautulli.com/) activity rankings.
Both builders support movies, shows, music, playlists, and custom sorting.

!!! warning "Configure Tautulli first"

    Every builder requires [Tautulli configuration](../../../config/tautulli.md).
    In Music libraries, set `builder_level` to choose artists, albums, or tracks.

## Choose a builder

| Builder | Ranks by | Default Music level |
|:--------|:---------|:--------------------|
| [`tautulli_popular`](#tautulli-popular) | Popularity; distinct listeners for Music | Artist |
| [`tautulli_top`](#tautulli-top) | Most plays | Album |

`tautulli_watched` remains a backward-compatible alias for `tautulli_top`.
Use `collection_order: custom` to retain returned rank order and `sync_mode: sync`
to keep membership synchronized on Kometa runs.

## Shared options

Both builders accept the same dictionary options; none is required.

| Attribute | Purpose | Default |
|:----------|:--------|:--------|
| `list_days` | Number of days to look back | `30` |
| `list_minimum` | Minimum users/listeners for popular results, or plays for top results | `0` |
| `list_size` | Maximum items to add | `10` |
| `list_buffer` | Extra items requested when filtering results on older Tautulli versions | `list_size * 3` |

## Popular items {#tautulli-popular}

<span id="example-tautulli-popular-builders"></span>

Selects up to 10 movies from the last 30 days' popular list. The values are
integer counts: `30` is a lookback window and `10` is a result size.

```yaml
collections:
  Most Popular Movies in 30 Days:
    tautulli_popular:
      list_days: 30
      list_size: 10
    collection_order: custom
    sync_mode: sync
```

## Most-played items {#tautulli-top}

<span id="example-tautulli-top-builders"></span>

=== "Top movies"

    Selects up to 10 movies from Tautulli's most-played list for the last 30 days.
    This ranks plays rather than selecting the popular list above.

    ```yaml
    collections:
      Most Watched Movies in 30 Days:
        tautulli_top:
          list_days: 30
          list_size: 10
        collection_order: custom
        sync_mode: sync
    ```

=== "Combine rankings"

    Combines up to 20 popular and 20 most-played items from the last 30 days.
    The resulting collection is displayed alphabetically, rather than trying
    to preserve two different rankings.

    ```yaml
    collections:
      Plex Popular and Most Played:
        tautulli_popular:
          list_days: 30
          list_size: 20
        tautulli_top:
          list_days: 30
          list_size: 20
        collection_order: alpha
        sync_mode: sync
    ```

=== "Playlist"

    Creates a playlist from up to 20 popular movies. Replace `Movies` with your
    configured library name. `libraries` belongs to the playlist definition,
    outside the Tautulli builder dictionary.

    ```yaml
    playlists:
      Plex Popular Movies:
        libraries: Movies
        tautulli_popular:
          list_days: 30
          list_size: 20
        collection_order: custom
        sync_mode: sync
    ```

## Music {#music}

Use `builder_level: artist`, `album`, or `track`. Popular defaults to artist level;
top defaults to album level. Artist and album results aggregate Tautulli music
statistics. Track results use history within `list_days`: popular counts distinct
listeners, while top counts plays. `list_minimum` uses the corresponding count.

=== "Popular tracks"

    Selects up to 20 tracks listened to by at least one distinct listener in the
    last 30 days. Track level overrides the popular builder's artist default.

    ```yaml
    collections:
      Popular Music Tracks:
        builder_level: track
        tautulli_popular:
          list_days: 30
          list_size: 20
          list_minimum: 1
        collection_order: custom
        sync_mode: sync
    ```

=== "Top albums"

    Selects up to 15 albums with at least two plays over the last 90 days.
    Album level is explicit here, but is already the default for `tautulli_top`.

    ```yaml
    collections:
      Top Music Albums:
        builder_level: album
        tautulli_top:
          list_days: 90
          list_size: 15
          list_minimum: 2
        collection_order: custom
        sync_mode: sync
    ```
