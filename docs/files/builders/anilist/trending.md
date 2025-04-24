---
hide:
  - toc
---
# AniList Trending

Finds every anime in AniList's [Trending Anime](https://anilist.co/search/anime/trending) list.

The expected input is a single integer value of how many movies/shows to query. 

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

### Example AniList Trending Builder(s)

```yaml
collections:
  Trending Anime:
    anilist_trending: 10
    collection_order: custom
    sync_mode: sync
```