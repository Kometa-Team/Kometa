---
hide:
  - toc
---
# MyAnimeList Top Movies

Gets every anime in MyAnimeList's [Top Anime Movies](https://myanimelist.net/topanime.php?type=movie) list. (Maximum: 500)

The expected input value is a single integer value of how many movies/shows to query.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

???+ warning "MyAnimeList Configuration"

    [Configuring MyAnimeList](../../../config/myanimelist.md) in the config is required for any of these builders to function.

### Example MyAnimeList Top Movies Builder(s)

```yaml
collections:
  Top Anime Movies:
    mal_movie: 20
    collection_order: custom
    sync_mode: sync
```
