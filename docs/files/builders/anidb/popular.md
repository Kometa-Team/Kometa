---
hide:
  - toc
---
# AniDB Popular

Finds every anime in AniDB's [Popular Anime](https://anidb.net/latest/anime/popular/?h=1) list.

The expected input is a single integer value of how much anime to query with a max of 30.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

### Example AniDB Popular Builder(s)

```yaml
collections:
  AniDB Popular:
    anidb_popular: 30
    collection_order: custom
    sync_mode: sync
```
