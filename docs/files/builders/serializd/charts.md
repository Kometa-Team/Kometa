---
search:
  boost: 2
---

# Serializd Charts

The Serializd chart builders retrieve the homepage's ordered show charts through its JSON API. Each builder value is the maximum number of shows to return.

| Builder | Homepage chart |
| ------- | -------------- |
| `serializd_trending` | Trending TV Shows |
| `serializd_popular` | Popular TV Shows |
| `serializd_featured` | Featured Shows |

```yaml
collections:
  Trending TV Shows:
    serializd_trending: 10
    collection_order: custom
    sync_mode: sync

  Popular TV Shows:
    serializd_popular: 10
    collection_order: custom
    sync_mode: sync

  Featured Shows:
    serializd_featured: 10
    collection_order: custom
    sync_mode: sync
```

The value must be an integer greater than `0`.
