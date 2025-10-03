---
hide:
  - toc
---
# TMDb Trending Weekly

Finds the movies/shows in TMDb's Trending Weekly list.

This Builder is expected to have an integer (number) value of how many items to query

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

### Example TMDb Trending Weekly Builder(s)

```yaml
collections:
  TMDb Weekly Trending:
    tmdb_trending_weekly: 30
    collection_order: custom
    sync_mode: sync
```