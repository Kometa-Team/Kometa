---
hide:
  - toc
---
# MyAnimeList Suggested
    
Gets the suggested anime in by MyAnimeList for the authorized user. (Maximum: 100)

The expected input value is a single integer value of how many movies/shows to query.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

???+ warning "MyAnimeList Configuration"

    [Configuring MyAnimeList](../../../config/myanimelist.md) in the config is required for any of these builders to function.

### Example MyAnimeList Suggested Builder(s)

```yaml
collections:
  Suggested Anime:
    mal_suggested: 20
    collection_order: custom
    sync_mode: sync
```