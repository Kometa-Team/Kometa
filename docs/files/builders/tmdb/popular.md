---
hide:
  - toc
---
# TMDb Popular

Finds the movies/shows in TMDb's [Popular Movies](https://www.themoviedb.org/movie)/[Popular Shows](https://www.themoviedb.org/tv) list.

Use `tmdb_region` with this Builder to set the region.

This Builder is expected to have an integer (number) value of how many items to query

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

### Example TMDb Popular Builder(s)

```yaml
collections:
  TMDb Popular:
    tmdb_popular: 30
    collection_order: custom
    sync_mode: sync
```