---
hide:
  - toc
---
# TMDb Now Playing

Finds the movies in TMDb's [Now Playing](https://www.themoviedb.org/movie/now-playing) list.

Use `tmdb_region` with this Builder to set the region.

This Builder is expected to have an integer (number) value of how many items to query

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

### Example TMDb Now Playing Builder(s)

```yaml
collections:
  TMDb Now Playing:
    tmdb_now_playing: 30
    collection_order: custom
    sync_mode: sync
```
