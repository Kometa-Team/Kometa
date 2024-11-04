# Files

{%    
  include-markdown "../config/file_types.md"
%}

* **See [File Blocks](../config/files.md) for more information on how to define files in the config.**

## Structure of a collection/overlay/playlist file

A collection/overlay/playlist file is a YAML file that defines a collection, overlay, or playlist.  It is made up of a series of attributes that define how the collection/overlay/playlist is built and what metadata is associated with it.

The structure of a collection/overlay/playlist file is as follows:

=== "collection"
    ```yaml
    collections:
      COLLECTION_ONE:
        # BUILDERS
        # FILTERS
        # METADATA DETAILS
      COLLECTION_TWO:
        # BUILDERS
        # FILTERS
        # METADATA DETAILS
    ```

    `COLLECTION_ONE` and `COLLECTION_TWO` are the names of the collections as shown in Plex.  These are arbitrary, but should be unique.

=== "overlay"
    ```yaml
    overlays:
      OVERLAY_ONE:
        # BUILDERS
        # FILTERS
        # OVERLAY DETAILS
      OVERLAY_TWO:
        # BUILDERS
        # FILTERS
        # OVERLAY DETAILS
    ```

    `OVERLAY_ONE` and `OVERLAY_TWO` are the names of the overlays.  With overlays specifically, those names refer to the images that will be used, unless you specify differently in the `OVERLAY DETAILS`.

=== "playlist"
    ```yaml
    playlists:
      PLAYLIST_ONE:
        # BUILDERS
        # FILTERS
        # METADATA DETAILS
      PLAYLIST_TWO:
        # BUILDERS
        # FILTERS
        # METADATA DETAILS
    ```

    `PLAYLIST_ONE` and `PLAYLIST_TWO` are the names of the playlists as shown in Plex.  These are arbitrary, but should be unique.

### Step one: Builders

A "Builder" is an attribute that tells Kometa what items belong in a collection/overlay/playlist.  Builders are placed at the top level of the definition.  Multiple builders can be used in one definition.

This might be something like a search in Plex for a specific genre, or a list of items from a specific source.

All available builders are listed [here](builders/overview.md).

Builders are common to all types of definitions.

Every collection/overlay/playlist needs at least one builder, since without a starting point, there's nothing to build.

Here are some examples:

=== "Collection: Plex search"
    [plex_search](./builders/plex.md#plex-search) is a builder that searches your Plex library for items that match the criteria you provide.

    ```yaml
    collections:
      Documentaries:
        plex_search:             # This is the builder
          all:
            genre: Documentary
    ```
    That will create a collection of all documentaries in your Plex library.

=== "Collection: MDB List"
    [mdblist_list](./builders/mdblist.md#mdblist-list) is a builder that finds every item in a [MDBList List](https://mdblist.com/toplists/).

    ```yaml
    collections:
      Top Movies of The Week:
                    # mdblist_list is the builder
        mdblist_list: https://mdblist.com/lists/linaspurinis/top-watched-movies-of-the-week
    ```

    That will create a collection of the movies on that particular MDB list

=== "Collection: Plex All"
    [plex_all](./builders/plex.md#plex-all) is a builder that finds every item in your Plex library.

    It is typically used with filters.

    ```yaml
    collections:
      Everything in Plex: 
        plex_all: true             # This is the builder
    ```
    That will create a collection of everything in your Plex library.

=== "Overlay: 4K Banner"
    [plex_search](./builders/plex.md#plex-search) is a builder that searches your Plex library for items that match the criteria you provide.

    ```yaml
    overlays:
      4K:               # Since this is a minimal overlay, Kometa will look for '4K.png' in the overlays folder.
        plex_search:    # This is the builder
          all:
            resolution: 4K
    ```
    
    That would apply the `4K.png` overlay to all items in your Plex library that have a resolution of 4K.

=== "Overlay: IMDB Top 250"
    [imdb_chart](./builders/imdb.md#imdb-chart) is a builder that finds items based on IMDB charts.

    ```yaml
    overlays:
      IMDB-Top-250:            # Since this is a minimal overlay, Kometa will look for 'IMDB-Top-250.png' in the overlays folder.
        imdb_chart: top_movies # This is the builder
    ```
    
    That would apply the `IMDB-Top-250.png` overlay to whatever of the top 250 movies on IMDB you have in your library.

=== "Playlist: Plex Search"
    [plex_search](./builders/plex.md#plex-search) is a builder that searches your Plex library for items that match the criteria you provide.

    ```yaml
    playlists:
      1990s Movies:
        plex_search:      # This is the builder
          any:
            decade: 1990
    ```
    That will create a playlist of all movies from the 1990s in your Plex library.


All of the available builders work similarly, but have different attributes that you can use to define what items are included in the collection.

Some might require a URL, some might require a list of genres, some might require a list of keywords, etc.

Some might allow you to specify a minimum number of items to include, or a maximum number of items to include, etc.

With the builder, you have the initial list of items that you want to include in the collection.

### Step two: Filters

A filter is an attribute that tells Kometa to filter out items from the builder that don't meet the criteria you provide.  Filters are placed under the `filters` attribute.

All available filters are listed [here](./filters.md).

Filters are again common to all types of definitions.

Filters *require* builders; without a builder, there is nothing for the filter to do.

There are some specific filters that can filter missing items sent to Radarr/Sonarr and if needed you can use the 
[`only_filter_missing` setting](settings.md) to have the filter only effect the missing items.

Filters are optional, and generally speaking you should try to avoid using them if you can.  They are slower than builders, and can slow down the process of building a collection.

For example:

It's faster to ask Plex for a list of movies released in 1981 than it is to ask Plex for a list of all movies and then look at all 8000 filter out the ones released in 1981.

=== "Movies from 1981 created by `plex_search`"
    This:
    ```yaml
    collections:
      1981 by search:
        plex_search:
          all:
            year: 1981
    ```

    When run against a Plex library of 8842 items, produced a collection containing 46 items, and took 3 seconds:

    ```
    |==========================================================================================|
    |                            Finished 1981 by search Collection                            |
    |                               Collection Run Time: 0:00:03                               |
    |==========================================================================================|
    ```

=== "Movies from 1981 created by `plex_all` and `filters`"
    While this:
    ```yaml
    collections:
      1981 by filter:
        plex_all: true
        filters:
          year: 1981
    ```

    When run against the same Plex library of 8842 items, produced the same collection containing the same 46 items, and took over 5 minutes:

    ```
    |==========================================================================================|
    |                            Finished 1981 by filter Collection                            |
    |                               Collection Run Time: 0:05:30                               |
    |==========================================================================================|
    ```

In some cases, however, filters are unavoidable.  For example, if you want to filter out items that don't have a specific keyword, you have to use a filter.

Examples:
=== "Filtering on TMDB votes"
    ```yaml
    collections:
      Romance Movies that TMDB members liked:
        plex_search:
          all:
            genre: Romance
        filters:
          tmdb_vote_count.gte: 1000
          tmdb_vote_average.gte: 7.5
    ```

    That will create a collection of all romance movies in your Plex library that have a vote count of at least 1000 and a vote average of at least 7.5 on TMDb.

    You can search Plex for the romance genre, but Plex cannot access TMDB vote count or average, so those things need to use a filter in Kometa. 

=== "Filtering on TVDB status"
    ```yaml
    collections:
      All cancelled shows:
        plex_all: true
        filters:
          tvdb_status: ended
    ```

    That will create a collection of all cancelled shows in your Plex TV library.

    Plex cannot access TVDB status, so that needs to use a filter in Kometa. 

=== "Filtering on file attributes"
    ```yaml
    collections:
      Best Movies of 2020 with Commentary:
        trakt_list: https://trakt.tv/users/chazlarson/lists/looper-best-movies-of-2020
        filters:
          audio_track_title: Commentary
    ```

    That will create a collection of movies from that Looper list for which your copies have commentary tracks.

    The builder is the list of movies from the Looper list, and the filter looks for the commentary track.

### Step three: Metadata Details

`METADATA DETAILS` is where you'd set things like a poster or a sort order or the like.

You can also set metadata for items within the collection.

Some of these are usable with all types of definitions; some are not.  Refer to the specific page for details.

Settings to control how the collection is built are listed [here](./settings.md).

Settings to override Radarr/Sonarr settings are listed [here](./arr.md).

Settings to update the metadata of the collection/playlist are listed [here](./updates.md).

Settings to update the metadata of the items in the collection/playlist are listed [here](./item_updates.md).

Examples:
=== "Add a poster to a collection"
    ```yaml
    collections:
      Romance Movies:
        plex_search:
          all:
            genre: Romance
        url_poster: https://theposterdb.com/api/assets/213090
    ```

    Adds a poster to the collection, using one of the attributes [here](./updates.md).

=== "Change collection sort order"
    ```yaml
    collections:
      Romance Movies:
        plex_search:
          all:
            genre: Romance
        collection_order: release.desc
    ```

    Sorts the items in the collection by descending release date, using one of the attributes [here](./updates.md).

=== "Override global Radarr tag"
    ```yaml
    collections:
      Romance Movies:
        plex_search:
          all:
            genre: Romance
        radarr_tag: romance_tag
    ```

    Sets a tag in Radarr on items in the collection instead of any tag specified in the settings, using one of the attributes [here](./arr.md).

=== "Label items ONLY; no collection built"
    ```yaml
    collections:
      Tag IMDB Top 250 Tagger:
        imdb_chart: top_movies
        item_label: imdb_top_250
        build_collection: false
    ```

    Sets a label on all items in Plex that are part of the IMDB Top 250, but doesn't build the collection.

    Uses attributes from [here](./item_updates.md) and [here](./settings.md).

=== "Set a minumum collection size"
    ```yaml
    collections:
      At least ten action movies:
        minimum_items: 10
        plex_search:
          any:
            genre: Action
    ```
    This will create a collection of action movies from your plex library, **but** only if there are at **minimum 10 items** found by the search.

`OVERLAY DETAILS` is where you'd set up the attributes of an overlay.

There are a number of examples of overlays [here](./overlays.md).
