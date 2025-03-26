---
hide:
  - toc
---

# Plex Builders

Plex has two categories of builders - Smart and Dumb (non-smart).

Smart Builders use rules (filters) to automatically include items that match the criteria of the Builder. When new media is added to your library, or if metadata of any item in your library changes to match the Builder's rules, the media is automatically included in the collection without the need to run Kometa again. 

Dumb (non-Smart) Builders are static in nature and will not dynamically update as new media is added/metadata criteria changes across your library - you will have to run Kometa any time you want the Builder to re-run.

Smart Builders are usually the recommended approach as they are lightweight and faster to process than Dumb Builders.

???+ important

    The `Smart Builders` and `Dumb Builders` tabs below will give examples of how to use the Builders, whilst the `Search Options`, `Sort Options` and `Builder Attributes` will give the full list of attributes and customizations available for use with the Builders.

=== "Smart Builders"
 
    Smart Builders allow Kometa to create Smart Collections in two different ways.
    
    The results of these builders are dynamic and do not require Kometa to re-run in order to update, instead they will 
    update automatically as the data within your Plex Library updates (i.e. if new media is added)

    Smart Filter and Smart Label are the two methods available for Smart Builders.

    Smart Filter Bulders use Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/) to create a smart collection based on the filter parameters provided. Any Advanced Filter made using the Plex UI should be able to be recreated using `smart_filter`. This is the normal approach used when your Builder criteria is held solely within Plex, and no third-party service involvement is required.

    Smart Label Builders attaches a label to every item that meets the criteria, and then creates a Smart Filter to search for that label. This is the normal approach used when you want to use a third-party list (such as Trakt or TMDb) with a Smart Builder.

    ???+ important
        
        Smart Builders do not work with Playlists

    === "Smart Filter Builder"
    
        Like Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/), you have to start each filter with either `any` or `all` as a base. You can only 
        have one base attribute and all filter attributes must be under the base.
        
        Inside the base attribute you can use any filter below or nest more `any` or `all`. You can have as many nested `any` 
        or `all` next to each other as you want. If using multiple `any` or `all` you will have to do so in the form of a list.
        
        **Note: To search by `season`, `episode`, `album`, or `track` you must use the `builder_level` [Setting](../settings.md) 
        to change the type of items the collection holds.**

        ## Smart Filter Examples
        
        A few examples are listed below:
        
        ```yaml
        collections:
          Documentaries:
            smart_filter:
              all:
                genre: Documentary
        ```
        ```yaml
        collections:
          Dave Chappelle Comedy:
            smart_filter:
              all:
                actor: Dave Chappelle
                genre: Comedy
        ```
        ```yaml
        collections:
          Top Action Movies:
            smart_filter:
              all:
                genre: Action
              sort_by: audience_rating.desc
              limit: 20
        ```
        ```yaml
        collections:
          90s Movies:
            smart_filter:
              any:
                year:
                  - 1990
                  - 1991
                  - 1992
                  - 1993
                  - 1994
                  - 1995
                  - 1996
                  - 1997
                  - 1998
                  - 1999
        ```
        ```yaml
        collections:
          90s Movies:
            smart_filter:
              any:
                decade: 1990
        ```

        If you specify TMDb Person ID's using the Setting `tmdb_person` and then tell either `actor`, `director`, `producer`, or 
        `writer` to add `tmdb`, the script will translate the TMDb Person IDs into their names and run the filter on those names.
        
        ```yaml
        collections:
          Robin Williams:
            smart_filter:
              all:
                actor: tmdb
            tmdb_person: 2157
        ```
        ```yaml
        collections:
          Steven Spielberg:
            smart_filter:
              all:
                director: tmdb
            tmdb_person: https://www.themoviedb.org/person/488-steven-spielberg
        ```
        ```yaml
        collections:
          Quentin Tarantino:
            smart_filter:
              any:
                actor: tmdb
                director: tmdb
                producer: tmdb
                writer: tmdb
            tmdb_person: 138
        ```

    === "Smart Label Builder"

        A Smart Label Collection is a smart collection that grabs every item with a specific label generated by the program. 
        That label is added to all the items the Collection Builders find instead of being added to a normal collection. 
        
        To make a collection a Smart Label Collection, the `smart_label` attribute must be added to the collection definition. 
        It functions in two different ways:

        1. Define the sort using the Movies/Shows column of the [Sorts Table](#sort-options) below along with any other Builder 
        to make that collection a Smart Label Collection.
            ```yaml
            collections:
              Marvel Cinematic Universe:
                trakt_list: https://trakt.tv/users/jawann2002/lists/marvel-cinematic-universe-movies?sort=rank,asc
                smart_label: release.desc
            ```
        
        2. Provide a whole `smart_filter` to determine exactly how the smart collection should be built, ensuring to include `label: <<smart_label>>`, which will link it to the collection labels.
            ```yaml
            collections:
              Unplayed Marvel Cinematic Universe:
                trakt_list: https://trakt.tv/users/jawann2002/lists/marvel-cinematic-universe-movies?sort=rank,asc
                smart_label:
                  sort_by: release.desc
                  all:
                    label: <<smart_label>>
                    unplayed: true
            ```
        
        This is extremely useful because smart collections don't follow normal show/hide rules and can eliminate the need to 
        have [Plex Collectionless](#plex-collectionless) when used correctly. To fix the issue described in 
        [Plex Collectionless](#plex-collectionless) you would make `Marvel Cinematic Universe` a Smart Label Collection 
        and all other Marvel collection just normal collections, and they will show/hide all the movie properly.
        
        To have the Smart Label Collections to eliminate Plex Collectionless you have to go all in on using them. A good rule of 
        thumb to make sure this works correctly is that every item in your library should have a max of one non-smart collection.
        
        Reach out on the [Kometa Discord](https://kometa.wiki/en/latest/discord/) or in the [GitHub Discussions](https://github.com/Kometa-Team/Kometa/discussions) for help if you're having any issues getting 
        this to work properly.

    {%
        include-markdown "../../templates/snippets/plex_search_options.md"
    %}

    {%
        include-markdown "../../templates/snippets/plex_sort_options.md"
    %}

    {%
        include-markdown "../../templates/snippets/plex_builder_attributes.md"
    %}


=== "Dumb Builders"

    This Builder finds items by using data held solely within Plex.
     
    The results of these builders are static and require Kometa to re-run in order to update.
    
    | Builder                                       | Description                                                                 |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
    |:----------------------------------------------|:----------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
    | [`plex_all`](#plex-all)                       | Gets every movie/show in your library. Useful with [Filters](../filters.md) | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
    | [`plex_search`](#plex-search)                 | Gets every movie/show based on the search parameters provided               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
    | [`plex_watchlist`](#plex-watlist)             | Gets every movie/show in your Watchlist.                                    | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
    | [`plex_pilots`](#plex-pilots)                 | Gets the first episode of every show in your library                        |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
    | [`plex_collectionless`](#plex-collectionless) | Gets every movie/show that is not in a collection                           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
    
    === "Plex All"
    
        Finds every item in your library. Useful with [Filters](../filters.md).
        
        The expected input is either true or false.
        
        ```yaml
        collections:
          9.0 Movies:
            plex_all: true
            filters:
              user_rating.gte: 9
        ```
    
    === "Plex Search"
        
        Uses Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/) to find all items based on the search parameters provided.
        
        Any Advanced Filter made using the Plex UI should be able to be recreated using `plex_search`. If you're having trouble 
        getting `plex_search` to work correctly, build the collection you want inside of Plex's Advanced Filters and take a 
        screenshot of the parameters in the Plex UI and post it in either the 
        [Discussions](https://github.com/Kometa-Team/Kometa/discussions) or on [Discord](https://kometa.wiki/en/latest/discord/), 
        and I'll do my best to help you. 
        
        like Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/) you have to start each search with either `any` or `all` as a base. You can only 
        have one base attribute and all search attributes must be under the base.
        
        Inside the base attribute you can use any search below or nest more `any` or `all`. You can have as many nested `any` 
        or `all` next to each other as you want. If using multiple `any` or `all` you will have to do so in the form of a list.
        
        **Note: To search by `season`, `episode`, `album`, or `track` you must use the `builder_level` [Setting](../settings.md) to change 
        the type of items the collection holds.**
        
        There are a couple other attributes you can have at the top level only along with the base attribute are:
    
        ## Plex Search Examples
        
        A few examples are listed below:
        
        ```yaml
        collections:
          Documentaries:
            plex_search:
              all:
                genre: Documentary
        ```
        ```yaml
        collections:
          Dave Chappelle Comedy:
            plex_search:
              all:
                actor: Dave Chappelle
                genre: Comedy
        ```
        ```yaml
        collections:
          Top Action Movies:
            collection_order: custom
            plex_search:
              all:
                genre: Action
              sort_by: audience_rating.desc
              limit: 20
        ```
        ```yaml
        collections:
          90s Movies:
            plex_search:
              any:
                year:
                  - 1990
                  - 1991
                  - 1992
                  - 1993
                  - 1994
                  - 1995
                  - 1996
                  - 1997
                  - 1998
                  - 1999
        ```
        ```yaml
        collections:
          90s Movies:
            plex_search:
              any:
                decade: 1990
        ```
        ```yaml
        collections:
          Best 2010+ Movies:
            collection_order: custom
            plex_search:
              all:
                year.gte: 2010
              sort_by:
                - year.desc
                - audience_rating.desc
              limit: 20
        ```
        
        Here's an example of an episode collection using `plex_search`.
        
        ```yaml
         collections:
           Top 100 Simpsons Episodes:
             collection_order: custom
             builder_level: episode
             plex_search:
               type: episode
               sort_by: audience_rating.desc
               limit: 100
               all:
                 title.ends: "Simpsons"
             summary: A collection of the highest rated simpsons episodes.
        ```
        
        If you specify TMDb Person ID's using the Setting `tmdb_person` and then tell either `actor`, `director`, `producer`, or 
        `writer` to add `tmdb`, the script will translate the TMDb Person IDs into their names and run the search on those names.
        
        ```yaml
        collections:
          Robin Williams:
            plex_search:
              all:
                actor: tmdb
            tmdb_person: 2157
        ```
        ```yaml
        collections:
          Steven Spielberg:
            plex_search:
              all:
                director: tmdb
            tmdb_person: https://www.themoviedb.org/person/488-steven-spielberg
        ```
        ```yaml
        collections:
          Quentin Tarantino:
            plex_search:
              any:
                actor: tmdb
                director: tmdb
                producer: tmdb
                writer: tmdb
            tmdb_person: 138
        ```

    === "Plex Watchlist"
        
        Finds every item in your Watchlist.
        
        The expected input is the sort you want returned. It defaults to `added.asc`.
        
        ### Watchlist Sort Options
        
        | Sort Option                                 | Description                                 |
        |:--------------------------------------------|:--------------------------------------------|
        | `title.asc`<br>`title.desc`                 | Sort by Title                               |
        | `release.asc`<br>`release.desc`             | Sort by Release Date (Originally Available) |
        | `critic_rating.asc`<br>`critic_rating.desc` | Sort by Critic Rating                       |
        | `added.asc`<br>`added.desc`                 | Sort by Date Added to your Watchlist        |
        
        The `sync_mode: sync` and `collection_order: custom` Setting are recommended.
        
        ```yaml
        collections:
          My Watchlist:
            plex_watchlist: critic_rating.desc
            collection_order: custom
            sync_mode: sync
        ```
        
    === "Plex Pilots"
    
        Gets the first episode of every show in your library. This only works with `builder_level: episode`
        
        ```yaml
        collections:
          Pilots:
            builder_level: episode
            plex_pilots: true
        ```
        
    === "Plex Collectionless"
    
        **This is not needed if you're using [Smart Label Collections](#smart-label).**
        
        Finds every item that is not in a collection unless the collection is in the exclusion list. This is a special 
        collection type to help keep your library looking correct. When items in your library are in multiple collections it 
        can mess up how they're displayed in your library.
        
        For Example, if you have a `Marvel Cinematic Universe` Collection set to `Show this collection and its items` and an 
        `Iron Man` Collection set to `Hide items in this collection` what happens is the show overrides the hide, and you end 
        up with both the collections and the 3 Iron Man movies all displaying.
        
        Alternatively, if you set the `Marvel Cinematic Universe` Collection to `Hide items in this collection` then movies 
        without a collection like `The Incredible Hulk` will be hidden from the library view.
        
        To combat the problem above you set all collections to `Hide items in this collection` then create a collection set to 
        `Hide collection` and put every movie that you still want to display in that collection. 
        
        With the variability of collections generated by the Kometa maintaining a collection like this becomes very difficult, 
        so in order to automate it, you can use `plex_collectionless`. You just have to tell it what collections to exclude or 
        what collection prefixes to exclude.
        
        There are two attributes for `plex_collectionless`:
        
        * `exclude`: Exclude these Collections from being considered for collectionless. 
        * `exclude_prefix` Exclude Collections whose title or sort title starts with a prefix from being considered for 
        collectionless. 
         
        **At least one exclusion is required.**
        
        ```yaml
        collections:
          Collectionless:
            plex_collectionless:
              exclude_prefix:
                - "!"
                - "+"
                - "~"
              exclude: 
                - Marvel Cinematic Universe
            sort_title: ~_Collectionless
            collection_order: alpha
            collection_mode: hide
        ```
        
        * Both `exclude` and `exclude_prefix` can take multiple values as a List.
        * This is a known issue with Plex Collection and there is a [Feature Suggestion](https://forums.plex.tv/t/collection-display-issue/305406) detailing the issue more on their 
        forms.


    {%
        include-markdown "../../templates/snippets/plex_search_options.md"
    %}

    {%
        include-markdown "../../templates/snippets/plex_sort_options.md"
    %}

    {%
        include-markdown "../../templates/snippets/plex_builder_attributes.md"
    %}
