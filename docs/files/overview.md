---
hide:
  - toc
---
# Files

{%    
  include-markdown "../config/file_types.md"
%}

* **See [File Blocks](../config/files.md) for more information on how to define files in the config.**

## Definition Component Overview

There are a few different types of attributes that can be used in any given Collection/Overlay/Playlist File.

### Builders

[Builders](builders/overview.md) are attributes placed at the top level of the definition that tell Kometa what items 
belong in a collection/overlay/playlist. Multiple builders can be used in one definition. These could come from a 
variety of sources including but not limited to:

* Your own Plex Sever using the Advance Filters.
* A Tautulli instance with your most played items.
* A List of media online on a site like IMDb, TMDb, or TVDb.

???+ example "Builder Example"
    
    ```yaml
    collections:
      My Test Collection 1:
        plex_search:
          any:
            genre: Action
      My Test Collection 2:
        imdb_chart: top_movies
      My Test Collection 3:
        imdb_search:
          type: movie
          limit: 100
          genre: action
          votes.gte: 1000
        plex_search:
          any:
            genre: Action
    ```

### Filters

[Filters](filters.md) are all put under a single attribute `filters`. These attributes will filter out items only after 
builders find them. **Filters alone do nothing, they need builders.** 

There are some specific filters that can filter missing items sent to Radarr/Sonarr and if needed you can use the 
[`only_filter_missing` setting](settings.md) to have the filter only effect the missing items.

Running filters are often slower than builders so whenever possible use only builders to build the definition.

???+ example "Filter Example"

    This uses the `plex_all` Buidler to get every item currently in the plex library and then checks TMDb if they have 
    either `aftercreditsstinger` or `duringcreditsstinger` as a keyword.
    
    ```yaml
    collections:
      My Test Collection 1:
        plex_all: true
        filters:
          tmdb_keyword: aftercreditsstinger, duringcreditsstinger
    ```

### Settings

[Settings](settings.md) are attributes placed at the top level of the definition that tells Kometa how to run the 
definition. Each setting will affect how the definition is run or shown in the log.

???+ example "Setting Example"

    This sets the colleciton to only build if the builders find at **minimum 10 items** and will sync items to the 
    collection (removing items that no longer are found by the builders).
    
    ```yaml
    collections:
      My Test Collection 1:
        sync_mode: sync
        minimum_items: 10
        plex_search:
          any:
            genre: Action
    ```

### Radarr/Sonarr Settings

[Radarr/Sonarr Settings](arr.md) are attributes placed at the top level of the definition that tells Kometa how 
Radarr/Sonarr is handled in this specific definition.

???+ example "Setting Example"

    This sets the colleciton to add missing movies from the builders to Radarr.
    
    ```yaml
    collections:
      My Test Collection 1:
        radarr_add_missing: true
        imdb_search:
          type: movie
          limit: 100
          genre: action
          votes.gte: 1000
    ```

### Collection/Playlist Metadata Updates

[Updates](updates.md) are attributes placed at the top level of the definition that tells Kometa Metadata Changes for the 
Collection/Playlist. 

???+ example "Collection/Playlist Metadata Update Example"

    ```yaml
    collections:
      My Test Collection 1:
        summary: This is my test collection's summary
        plex_search:
          any:
            genre: Action
    ```

### Item Metadata Updates

[Item Updates](item_updates.md) are attributes placed at the top level of the definition that tells Kometa Metadata Changes 
for every item found in the Collection/Playlist. 

???+ example "Item Metadata Update Example"

    This will add the genre `Credits` to every item found after builders and filters are run.

    ```yaml
    collections:
      My Test Collection 1:
        item_genre: Credits
        plex_all: true
        filters:
          tmdb_keyword: aftercreditsstinger, duringcreditsstinger
    ```
