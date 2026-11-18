---
search:
  boost: 2
---

# Serializd Builders

Collect shows from Serializd lists, watchlists, and homepage charts.

!!! warning "Configure Serializd first"

    These builders are **show-library only** and require
    [Serializd authentication](../../../config/serializd.md).

## Choose a builder

| Builder | Finds | Value |
|:--------|:------|:------|
| [`serializd_list`](#serializd-list) | Shows in public lists | List URL or YAML list of URLs |
| [`serializd_watchlist`](#serializd-watchlist) | Shows in a watchlist | `me`, username, or full watchlist URL |
| [`serializd_trending`](#serializd-charts) | Trending TV Shows | Positive integer limit |
| [`serializd_popular`](#serializd-charts) | Popular TV Shows | Positive integer limit |
| [`serializd_featured`](#serializd-charts) | Featured Shows | Positive integer limit |

Use `collection_order: custom` to preserve the returned order and `sync_mode: sync`
to keep membership synchronized as the source changes. These builders use
Serializd's JSON API; private or otherwise API-inaccessible content produces a
builder error rather than falling back to web-page scraping.

## Charts {#serializd-charts}

Each chart builder takes an integer greater than zero. This example selects up
to 10 trending shows in chart order. Replace `serializd_trending` with
`serializd_popular` or `serializd_featured` to follow another homepage chart.

```yaml
collections:
  Trending TV Shows:
    serializd_trending: 10
    collection_order: custom
    sync_mode: sync
```

## Lists {#serializd-list}

This example follows the public Live Action Ranked list. The builder value is a
URL string. To combine lists, supply one URL per entry in a YAML list; returned
Serializd order is retained.

```yaml
collections:
  Live Action Ranked:
    serializd_list: https://www.serializd.com/list/live-action-ranked-662885
    collection_order: custom
    sync_mode: sync
```

## Watchlists {#serializd-watchlist}

=== "Authenticated account"

    Selects the watchlist of the account authenticated in your Kometa configuration.
    `me` is a string identifying that account, not a boolean switch.

    ```yaml
    collections:
      My Serializd Watchlist:
        serializd_watchlist: me
        collection_order: custom
        sync_mode: sync
    ```

=== "Public user"

    Selects another user's public watchlist. Replace the placeholder with their
    username. A full URL such as
    `https://www.serializd.com/user/somebodys_username/watchlist` is also accepted.

    ```yaml
    collections:
      Community Watchlist:
        serializd_watchlist: somebodys_username
        collection_order: custom
        sync_mode: sync
    ```
