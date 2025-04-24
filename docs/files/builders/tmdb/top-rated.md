---
hide:
  - toc
---
# TMDb Top Rated

Finds the movies/shows in TMDb's [Top Rated Movies](https://www.themoviedb.org/movie/top-rated)/[Top Rated Shows](https://www.themoviedb.org/tv/top-rated) list.

Use `tmdb_region` with this Builder to set the region.

This Builder is expected to have an integer (number) value of how many items to query

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

### Example TMDb Top Rated Builder(s)

```yaml
collections:
  TMDb Top Rated:
    tmdb_top_rated: 30
    collection_order: custom
    sync_mode: sync
```
