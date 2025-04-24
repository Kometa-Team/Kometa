---
hide:
  - toc
---
# Trakt Recommendations

Finds the movies/shows in Trakt's Recommendations for [Movies](https://trakt.docs.apiary.io/#reference/recommendations/movies/get-movie-recommendations)/[Shows](https://trakt.docs.apiary.io/#reference/recommendations/shows/get-show-recommendations)

The expected input is a single integer value of how many movies/shows to query. 

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

???+ warning "Trakt Configuration"

    [Configuring Trakt](../../../config/trakt.md) in the config is required for any of these builders.

### Example Trakt Recommendations Builder(s)

```yaml
collections:
  Trakt Recommendations:
    trakt_recommendations: 30
    collection_order: custom
    sync_mode: sync
```