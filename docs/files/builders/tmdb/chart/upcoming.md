---
hide:
  - toc
---
# TMDb Upcoming

Finds the movies in TMDb's [Upcoming Movies](https://www.themoviedb.org/movie/upcoming) list.

Use `tmdb_region` with this Builder to set the region.

This Builder is expected to have an integer (number) value of how many items to query

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

### Example TMDb Upcoming Builder(s)

```yaml
collections:
  TMDb Upcoming:
    tmdb_upcoming: 30
    collection_order: custom
    sync_mode: sync
```
