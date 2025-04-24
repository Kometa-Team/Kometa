---
hide:
  - toc
---
# IMDb Watchlist

Finds every item in an IMDb User's Watchlist.

| List Parameter | Description                                                                                                                                                                                                                                                                                                                                   |
|:---------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `user_id`      | Specify the User ID for the IMDb Watchlist. **This attribute is required.**<br>**Options:** The ID that starts with `ur` found in the URL of the watchlist. (ex. `ur12345678`)                                                                                                                                                                |
| `limit`        | Specify how items you want returned by the query.<br>**Options:** Any Integer `0` or greater where `0` get all items.<br>**Default:** `0`                                                                                                                                                                                                     |
| `sort_by`      | Choose from one of the many available sort options.<br>**Options:** `custom.asc`, `custom.desc`, `title.asc`, `title.desc`, `rating.asc`, `rating.desc`, `popularity.asc`, `popularity.desc`, `votes.asc`, `votes.desc`, `release.asc`, `release.desc`, `runtime.asc`, `runtime.desc`, `added.asc`, `added.desc`<br>**Default:** `custom.asc` |

Multiple values are supported as a list only a comma-separated string will not work.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

### Example IMDb Watchlist Builder(s)

```yaml
collections:
  My Watch Watchlist:
    imdb_watchlist: 
      user_id: ur64054558
      sort_by: rating.asc
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  My Friends Watchlists:
    imdb_watchlist: 
      - user_id: ur64054558
        sort_by: rating.asc
        limit: 100
      - user_id: ur12345678
        sort_by: rating.asc
        limit: 100
    sync_mode: sync
```
