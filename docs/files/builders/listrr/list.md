---
hide:
  - toc
---
# Listrr List

Finds every item in one or more Listrr lists.

???+ warning "Listrr Configuration"

    [Configuring Listrr](../../../config/listrr.md) in the config is required for these builders.

## listrr_list

The expected input is one list, or a YAML list of them. Each value is a 24-character list id, or one of these site URLs:

- `https://listrr.pro/Lists/ShowMovieList/{id}` for a movie list
- `https://listrr.pro/Lists/ShowShowList/{id}` for a show list

`?page=` on a site URL is the website pager. Kometa ignores it and always starts at API page 1.

Multiple values are supported as a YAML list only. A comma-separated string is one value and will not be split, because a URL has to stay intact.

Several lists stay one builder. Kometa reads them in the order given, applies each list's own `sort_by` and `limit`, and skips an id that an earlier list already emitted. Playlists and `collection_order: custom` accept that single builder.

On an object, `url` and `list_id` are aliases for that same id or URL.

Movies use the TMDb id when Listrr sends one, then the IMDb id. Shows use the TVDb id, then the TMDb id, then the IMDb id.

The `sync_mode: sync` and `collection_order: custom` settings are recommended. Listrr has no curator rank. `collection_order: custom` follows the sort below, and the default `name.asc` matches the alphabetical order of the public list pages.

A very large list is one metadata request plus one request per page. Set `limit` to stop early, or set `cache_builders` to a number of days so later runs reuse the id list. `cache_builders` defaults to `0`, so membership is fetched again on every run until you opt in.

???+ tip "Details Builder"

    You can replace `listrr_list` with `listrr_list_details` to store the first list's description as the collection summary. An empty description stores nothing. If the description request fails, Kometa logs the error and still keeps the items.

## Sort Options

For these sorts to be reflected in your collection you **must** use `collection_order: custom`.

| `sort_by` | API sort | Direction | Description |
|:----------|:---------|:----------|:------------|
| `name.asc` | `Name` | `Ascending` | Alphabetical by name. This is the default, and it matches the public list pages. |
| `name.desc` | `Name` | `Descending` | Reverse alphabetical by name. |
| `release.asc` | `ReleaseDate` | `Ascending` | Oldest release first. Shows use the first air date. |
| `release.desc` | `ReleaseDate` | `Descending` | Newest release first. |

`limit` defaults to `0`, which reads every page. A positive integer stops once that many usable ids have been collected.

### Example Listrr List Builder(s)

```yaml
collections:
  Listrr Movies:
    listrr_list: 671527158e1c7df162d0fe69
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  Listrr Movies Limited:
    listrr_list:
      url: https://listrr.pro/Lists/ShowMovieList/671527158e1c7df162d0fe69
      sort_by: release.desc
      limit: 100
    collection_order: custom
    sync_mode: sync
    cache_builders: 1
```

```yaml
collections:
  Listrr Shows:
    listrr_list_details: https://listrr.pro/Lists/ShowShowList/67fb123c6f5a448f92e7ee03
    collection_order: custom
    sync_mode: sync
```
