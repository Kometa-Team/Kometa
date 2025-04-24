---
hide:
  - toc
---
# AniList Top Rated

Finds every anime in AniList's [Top Rated Anime](https://anilist.co/search/anime?sort=SCORE_DESC) list.

The expected input is a single integer value of how many movies/shows to query. 

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

### Example AniList Top Rated Builder(s)

```yaml
collections:
  Top Rated Anime:
    anilist_top_rated: 30
    collection_order: custom
    sync_mode: sync
```
