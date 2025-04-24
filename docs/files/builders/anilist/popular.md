---
hide:
  - toc
---
# AniList Popular

Finds every anime in AniList's [Popular Anime](https://anilist.co/search/anime/popular) list.

The expected input is a single integer value of how many movies/shows to query. 

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

### Example AniList Popular Builder(s)

```yaml
collections:
  Popular Anime:
    anilist_popular: 10
    collection_order: custom
    sync_mode: sync
```
