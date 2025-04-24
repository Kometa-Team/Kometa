---
hide:
  - toc
---
# TMDb On the Air

Finds the shows in TMDb's [On TV Shows](https://www.themoviedb.org/tv/on-the-air) list.

This Builder is expected to have an integer (number) value of how many items to query

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

### Example TMDb On the Air Builder(s)

```yaml
collections:
  TMDb On the Air:
    tmdb_on_the_air: 30
    collection_order: custom
    sync_mode: sync
```
