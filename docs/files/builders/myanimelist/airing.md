---
hide:
  - toc
---
# MyAnimeList Top Airing

Gets every anime in MyAnimeList's [Top Airing Anime](https://myanimelist.net/topanime.php?type=airing) list. (Maximum: 500)

The expected input value is a single integer value of how many movies/shows to query.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

???+ warning "MyAnimeList Configuration"

    [Configuring MyAnimeList](../../../config/myanimelist.md) in the config is required for any of these builders to function.

### Example MyAnimeList Top Airing Builder(s)

```yaml
collections:
  Top Airing Anime:
    mal_airing: 10
    collection_order: custom
    sync_mode: sync
```
