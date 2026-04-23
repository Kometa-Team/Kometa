---
hide:
  - toc
---
# Simkl DVD

Finds movies and TV shows from [Simkl's DVD release lists](https://simkl.com/movies/dvd-releases/).

The list is filtered automatically to match your library type: movie libraries receive movies, show libraries receive TV shows, and playlists receive both.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

## Attribute

| Attribute | Description                                                        | Required | Default |
|:----------|:-------------------------------------------------------------------|:--------:|:-------:|
| `limit`   | Maximum number of items to return. Must be between `1` and `500`. |    No    |  `20`   |

!!! note
    The Simkl service provides lists of the top 100 items (`small`) or top 500 items (`large`). Kometa automatically
    selects the appropriate list size based on your `limit` value: `small` is used when `limit` is 100 or fewer,
    `large` when `limit` is greater than 100.

### Example Simkl DVD Builder(s)

Simple usage with just a limit:

```yaml
collections:
  New on DVD:
    simkl_dvd: 20
    collection_order: custom
    sync_mode: sync
```

Using a dict:

```yaml
collections:
  New on DVD:
    simkl_dvd:
      limit: 50
    collection_order: custom
    sync_mode: sync
```
