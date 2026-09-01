---
hide:
  - toc
---
# Trakt Box Office

Finds the 10 movies in Trakt's Top Box Office [Movies](https://trakt.tv/movies/boxoffice) list.

The expected input is true. 

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

???+ warning "Trakt Authentication"

    :lock: Trakt [authentication](../../../config/authentication.md) is required for this builder

### Example Trakt Box Office Builder(s)

```yaml
collections:
  Trakt Collected:
    trakt_boxoffice: true
    collection_order: custom
    sync_mode: sync
```