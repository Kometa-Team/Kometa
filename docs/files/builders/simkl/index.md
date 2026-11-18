# Simkl Builders

Collect trending movies, shows, anime, and DVD releases from [Simkl](https://simkl.com/)
through the [Kometa Simkl Service](https://utilities.kometa.wiki/simkl-service).
No API key or Simkl account is required. Both builders support movies, shows,
playlists, and custom sorting.

## Choose a builder

| Builder | Finds |
|:--------|:------|
| [`simkl_dvd`](#simkl-dvd) | Movies and shows in DVD release lists |
| [`simkl_trending`](#simkl-trending) | Trending movies, shows, and anime |

Results are filtered to the library type: movies for movie libraries, shows for
show libraries, and both for playlists. Use `collection_order: custom` to retain
returned order and `sync_mode: sync` to keep membership synchronized.

## Shared options

Both builders accept an integer limit directly or a dictionary containing `limit`.
Trending also accepts `period`.

<span id="attribute"></span>
<span id="simkl-trending-attribute"></span>

| Attribute | Applies to | Value | Default |
|:----------|:-----------|:------|:--------|
| `limit` | Both | Integer, 1-500 | `20` |
| `period` | Trending only | `today`, `week`, `month` | `today` |

Kometa automatically requests the service's top-100 (`small`) list for limits
up to 100, or top-500 (`large`) list for larger limits.

## DVD releases {#simkl-dvd}

Selects items from [Simkl's DVD release lists](https://simkl.com/movies/dvd-releases/).
In playlists, the endpoint's flat item order is preserved, including any
interleaving of movies and shows.

<span id="example-simkl-dvd-builders"></span>

=== "Integer limit"

    Selects up to 20 DVD releases matching the current library type. The builder
    value is an integer, not a boolean.

    ```yaml
    collections:
      New on DVD:
        simkl_dvd: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "Dictionary"

    Selects up to 150 DVD releases. The larger limit automatically uses the
    service's top-500 list; the dictionary form keeps the limit as a named option.

    ```yaml
    collections:
      More DVD Releases:
        simkl_dvd:
          limit: 150
        collection_order: custom
        sync_mode: sync
    ```

## Trending {#simkl-trending}

Uses Simkl's trending lists for [movies](https://simkl.com/movies/best-movies/most-watched/),
[shows](https://simkl.com/tv/best-shows/most-watched/), and
[anime](https://simkl.com/anime/best-anime/most-watched/).

!!! note "Trending playlist order"

    Trending data arrives in separate sections: movies first, then TV shows,
    then anime. Each section's order is retained, but media types are not
    interleaved. Use [text files](../textfile/index.md) when you need explicit
    per-item ordering across types.

<span id="example-simkl-trending-builders"></span>

=== "Default period"

    Selects up to 20 trending items using the default `today` period.

    ```yaml
    collections:
      Simkl Trending Today:
        simkl_trending: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "Named period"

    Selects up to 50 items trending this week. `week` is a string and `50` is an
    integer. Use `month` for the monthly list or `today` for the daily list.

    ```yaml
    collections:
      Simkl Trending This Week:
        simkl_trending:
          period: week
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```
