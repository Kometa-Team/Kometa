# Collection Files

Collection Files holds information on how Plex Meta Manager should create collections. There are a large number of 
builders available to build collections, 

## Overview

This is a basic Collections File which contains the structure to build a collection called "Top 50 Grossing Films of All
Time (Worldwide)"

The collection order is set to be the same as is received from the source list, and items added/removed from the source 
list will be added/removed from the collection in the Plex library.

???+ example "Example "MyCollections.yml""

    Click the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml
    collections: #(1)!
      Top 50 Grossing Films of All Time (Worldwide):
        tmdb_list: 10 #(2)!
        collection_order: custom #(3)!
        sync_mode: sync #(4)!
    ```

    1.  This must appear once and **only once** in any Metadata file
    2.  This creates a collection based on tmdb list ID 10, https://www.themoviedb.org/list/10 would also be accepted
    3.  This will sort the items in the Plex collection to be the same as the order in the list
    4.  Syncs the collection to the list, so that if an item is added/removed from the list, the same is done to the 
    collection. Set this to `append` if you only want it to add things and not remove them.

For the purpose of this example, we are going to save the File as `MyCollections.yml` within the location mapped as 
`config` in our setup.

I then call "MyCollections.yml" in my [Configuration File](../config/overview.md) within the `collection_files` section

???+ example "config.yml Example Collection File Addition"

    Click the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml
    libraries:
      Movies: #(1)!
        collection_files:
          - file: config/MyCollections.yml #(2)!
    ```

    1.  This must match the name of a library in your Plex server
    2.  `config` refers to the location that you mapped to `config` when following the PMM Installation Guides.

Whenever I execute Plex Meta Manager and the Movies library is run, MyCollections.yml will run and my "Top 50 Grossing 
Films of All Time (Worldwide)" will be created/updated.

## File Attributes

Collection Files can utilize the following top-level attributes

| Attribute                                               | Description                                                                                                               |
|:--------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------|
| [`templates`](templates.md)                             | contains definitions of templates that can be leveraged by multiple collections                                           |
| [`external_templates`](templates.md#external-templates) | contains [file blocks](../config/files.md) that point to external templates that can be leveraged by multiple collections |
| [`collections`](#collection-operations--attributes)     | contains definitions of collections you wish to add to one or more libraries                                              |
| [`dynamic_collections`](#dynamic-collections)           | contains definitions of [dynamic collections](dynamic.md) you wish to create                                              |

* One of `metadata`, `collections` or `dynamic_collections` must be present for the File to run, else you will receive 
an error when trying to run the file against your library.

* Example Files can be found in the 
[Plex Meta Manager Configs Repository](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM)

## Collection Operations & Attributes

Whilst [Library Operations](../config/operations.md) are used to control library-wide operations, Collection Files can 
be used as a method to perform more limited operations, such as:

* Syncing collections with the source list if one is used (such as Trakt Lists, TMDb Lists, etc.)

* Sending missing media to Sonarr/Radarr

* Adding labels to items in collections

* Showing and Hiding collections at set intervals (i.e. show Christmas collections in December only)

These operations can be performed without the need to physically build a collection (using the `build_collection: false` 
attribute)

Examples of these can be seen here

???+ example "Examples of Collection Operations"
    
    Click the :fontawesome-solid-circle-plus: icon to learn more

    === "Example 1 - Sync Collection to List"

        ```yaml
        collections:
          Christmas Extravaganza:
            trakt_list: https://trakt.tv/users/plexmetamanager/lists/christmas-extravaganza-non-tv-movie #(1)!
            sync_mode: append #(2!)
            collection_order: custom #(3)!
        ```

        1.  This is a Trakt List builder, telling PMM to build a collection based on the items in this list
        2.  If items are removed from the source list, having sync mode set to `append` means they will not be removed 
        from the collection in Plex. Set this to `sync` if you want the items removed in the collection too
        3.  Sort the collection in the order that it is received from the Trakt list

    === "Example 2 - Send to Arr"
    
        ```yaml
        collections:
          IMDb Top 250:
            imdb_chart: top_movies 
            collection_order: custom #(1)!
            radarr_add_missing: true #(2)!
        ```

        1.  Sorts the collection in the same order as is received by the source list
        2.  Sends items that are in the source list but are not in your Plex library to Radarr. Replace with 
        `sonarr_add_missing` for any show-based builder.

    === "Example 3 - Add labels"

        ```yaml
        collections:
          Radarr Tags:
            build_collection: false #(1)!
            radarr_taglist: mytag #(2)!
            item_label: myplextag #(3)!
        ```

        1.  Tells PMM to not physically build a collection, but it will still perform the actions of the collection
        2.  Find all items in Radarr that have the tag `mytag`
        3.  For each of the items with `mytag` in Radarr, apply the `myplextag` to the items in the Plex library

    === "Example 4 - Schedule Collection"

        ```yaml
        collections:
          Christmas Extravaganza:
            trakt_list: https://trakt.tv/users/plexmetamanager/lists/christmas-extravaganza-non-tv-movie #(1)!
            schedule: range(12/01-12/31) #(2)!
            delete_not_scheduled: true #(3)!
        ```

        1.  Tells PMM to not physically build a collection, but it will still perform the actions of the collection
        2.  Only run this collection from December 1st through December 31st
        3.  If today is not part of the above scheduled range, delete the Christmas Extravaganza collection if it exists
        in the Plex library

There are multiple types of attributes that can be utilized within a collection:

* [Builders](builders/overview.md)
* [Filters](filters.md)
* [Settings](settings.md)
* [Radarr/Sonarr Settings](settings.md)
* [Collection/Playlist Metadata Updates](updates.md)
* [Item Metadata Updates](item_updates.md)

## Example File

Below is a common Collection File which will create two collections in a Plex library.

It will sync the collections to the source lists, order them randomly, and apply a summary to the collection.

```yaml
collections:
  Trending:
    trakt_trending: 10
    tmdb_trending_daily: 10
    tmdb_trending_weekly: 10
    sort_title: +1_Trending
    sync_mode: sync
    smart_label: random
    summary: Movies Trending across the internet
  Popular:
    tmdb_popular: 40
    imdb_search:
      type: movie, tv_movie
      limit: 40
    sort_title: +2_Popular
    sync_mode: sync
    smart_label: random
    summary: Popular Movies across the internet
```

## Dynamic Collections

In addition to manually defining each Collection that you want in your library, Plex Meta Manager can also dynamically 
create collections based on a variety of different criteria, such as

* Collections for the top `X` popular people on TMDb (Bruce Willis, Tom Hanks etc.)

* Collections for each decade represented in the library (Best of 1990s, Best of 2000s etc.)

* Collections for each of the moods/styles within a Music library (A Cappella, Pop Rock etc.)

* Collections for each of a Trakt Users Lists.

A full list of the available options is available on the [Dynamic Collections](dynamic.md) page