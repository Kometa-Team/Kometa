---
hide:
  - toc
---
# Simkl Trending

Finds movies, TV shows and anime from Simkl's trending lists.

- [Movies](https://simkl.com/movies/best-movies/most-watched/)
- [Shows](https://simkl.com/tv/best-shows/most-watched/)
- [Anime](https://simkl.com/anime/best-anime/most-watched/)

The list is filtered automatically to match your library type (movies, shows, or both for playlists).

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

## Attribute

| Attribute | Description                                                         | Required | Default  |
|:----------|:--------------------------------------------------------------------|:--------:|:--------:|
| `period`  | Time period for the trending list. Options: `today`, `week`, `month` |    No    | `today`  |
| `limit`   | Maximum number of items to return. Must be between `1` and `500`.  |    No    |   `20`   |

!!! note
    The Simkl service provides lists of the top 100 items (`small`) or top 500 items (`large`). Kometa automatically
    selects the appropriate list size based on your `limit` value: `small` is used when `limit` is 100 or fewer,
    `large` when `limit` is greater than 100.

### Example Simkl Trending Builder(s)

Simple usage with just a limit:

```yaml
collections:
  Simkl Trending Today:
    simkl_trending: 20
    collection_order: custom
    sync_mode: sync
```

Using a specific period:

```yaml
collections:
  Simkl Trending This Week:
    simkl_trending:
      period: week
      limit: 50
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  Simkl Trending This Month:
    simkl_trending:
      period: month
      limit: 100
    collection_order: custom
    sync_mode: sync
```
