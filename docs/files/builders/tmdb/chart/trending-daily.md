---
hide:
  - toc
---
# TMDb Trending Daily

Finds the movies/shows in TMDb's Trending Daily list.

This Builder is expected to have an integer (number) value of how many items to query

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

### Example TMDb Trending Daily Builder(s)

```yaml
collections:
  TMDb Daily Trending:
    tmdb_trending_daily: 30
    collection_order: custom
    sync_mode: sync
```
