---
hide:
  - toc
---
# TMDb Airing Today

Finds the shows in TMDb's [Airing Today Shows](https://www.themoviedb.org/tv/airing-today) list.

This Builder is expected to have an integer (number) value of how many items to query

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

### Example TMDb Airing Today Builder(s)

```yaml
collections:
  TMDb Airing Today:
    tmdb_airing_today: 30
    collection_order: custom
    sync_mode: sync
```
