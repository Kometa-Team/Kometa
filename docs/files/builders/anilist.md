---
hide:
  - toc
---
# AniList Builders

You can find anime using the features of [AniList.co](https://anilist.co/) (AniList).

| Builder                                   | Description                                                                                                              |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`anilist_search`](#anilist-search)       | Finds the anime specified by the AniList search parameters provided                                                      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`anilist_top_rated`](#anilist-top-rated) | Finds every anime in AniList's [Top Rated Anime](https://anilist.co/search/anime?sort=SCORE_DESC) list                   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`anilist_popular`](#anilist-popular)     | Finds every anime in AniList's [Popular Anime](https://anilist.co/search/anime/popular) list                             | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`anilist_trending`](#anilist-trending)   | Finds every anime in AniList's [Trending Anime](https://anilist.co/search/anime/trending) list                           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`anilist_relations`](#anilist-relations) | Finds the anime specified by the AniList ID and every relation in its relation tree except Character and Other relations | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`anilist_studio`](#anilist-studio)       | Finds all anime specified by the AniList Studio ID                                                                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`anilist_id`](#anilist-id)               | Finds the anime specified by the AniList ID                                                                              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`anilist_userlist`](#anilist-userlist)   | Finds the anime in AniList User's Anime list the options are detailed below                                              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |


=== "AniList Search"
    
    Finds the anime specified by the AniList Search the options are detailed below. 
    
    There are three fields per search option when using AniList's Search just like Plex's Advanced Filters in the Web UI. The first is the **Attribute** (what attribute you wish to search), the second is the **Modifier** (which modifier to use), and the third is the **Term** (actual term to search).
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    === "Special Attributes"
        
        Special attributes do not support any modifiers.
        
        | Special Attribute | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
        |:------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `sort_by`         | **Description:** How to sort the Anime<br>**Default:** `score`<br>**Values:**<table class="clearTable"><tr><td>`score`</td><td>Sort by Average Score</td></tr><tr><td>`popular`</td><td>Sort by Popularity</td></tr><tr><td>`trending`</td><td>Sort by Trending</td></tr></table>                                                                                                                                                                                                 |
        | `limit`           | **Description:** Number of Anime to query<br>**Values:** Number greater or equal to `0` (use 0 or don't use it at all for all anime)<br>**Default:** `0`                                                                                                                                                                                                                                                                                                                          |
        | `search`          | **Description:** Text to search<br>**Values:** Any Text                                                                                                                                                                                                                                                                                                                                                                                                                           | 
        | `season`          | **Description:** Season to search for<br>**Default:** `current`<br>**Values:** <table class="clearTable"><tr><td>`winter`</td><td>For winter season December, January, February</td></tr><tr><td>`spring`</td><td>For spring season March, April, May</td></tr><tr><td>`summer`</td><td>For summer season June, July, August</td></tr><tr><td>`fall`</td><td>For fall season September, October, November</td></tr><tr><td>`current`</td><td>For current Season</td></tr></table> |
        | `year`            | **Description:** Season year to search for<br>**Default:** Current Year<br>**Values:** Number between `1917` and next year or leave blank for the current year                                                                                                                                                                                                                                                                                                                    |
        | `min_tag_percent` | **Description:** Minimum tag percentage for the Anime<br>**Values:** Number between `0`-`100`                                                                                                                                                                                                                                                                                                                                                                                     |
        | `adult`           | **Description:** Search for or not for Adult Anime<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                               |
        | `country`         | **Description:** Search for anime from a specific country<br>**Values:** [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)                                                                                                                                                                                                                                                                                                                      |
        | `source`          | **Description:** Uses the anime's source to match<br>**Values:** `original`, `manga`, `light_novel`, `visual_novel`, `video_game`, `other`, `novel`, `doujinshi`, or `anime`                                                                                                                                                                                                                                                                                                      |

    === "Date Attributes"
    
        Date attributes can be used with either `.before`, or `.after`.
        
        No date attribute can take multiple values.
        
        ### "Date Attributes"
        
        | Date Attributes | Description                                  |
        |:----------------|:---------------------------------------------|
        | `start`         | Uses the anime start date attribute to match |
        | `end`           | Uses the anime end date attribute to match   |

        ???+ tip "Date Attribute Modifiers"    

            | Date Modifier | Description                                                                                                      |
            |:--------------|:-----------------------------------------------------------------------------------------------------------------|
            | `.before`     | Matches every item where the date attribute is before the given date<br>**Format:** MM/DD/YYYY e.g. `01/01/2000` |
            | `.after`      | Matches every item where the date attribute is after the given date<br>**Format:** MM/DD/YYYY e.g. `01/01/2000`  |

    === "Number Searches"
    
        Number attributes must use `.gt`, `.gte`, `.lt`, or `.lte` as a modifier.
        
        No number attribute can take multiple values.
        
        ### "Number Attributes"
        
        | Number Attribute | Description                                                                                           |
        |:-----------------|:------------------------------------------------------------------------------------------------------|
        | `duration`       | **Description:** Uses the duration attribute to match using minutes<br>**Restrictions:** minimum: `1` |
        | `episodes`       | **Description:** Uses the number of episodes attribute to match<br>**Restrictions:** minimum: `1`     |
        | `score`          | **Description:** Uses the score attribute to match<br>**Restrictions:** minimum: `1`                  |
        | `popularity`     | **Description:** Uses the popularity attribute to match<br>**Restrictions:** minimum: `1`             |

        ???+ tip "Number Attribute Modifiers"    
        
        | Number Modifier | Description                                                                                                                                             |
        |:----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `.gt`           | Matches every item where the number attribute is greater than the given number<br>**Format:** number<br>**Example:** `30`, `1995`, or `7.5`             |
        | `.gte`          | Matches every item where the number attribute is greater than or equal to the given number<br>**Format:** number<br>**Example:** `30`, `1995`, or `7.5` |
        | `.lt`           | Matches every item where the number attribute is less than the given number<br>**Format:** number<br>**Example:** `30`, `1995`, or `7.5`                |
        | `.lte`          | Matches every item where the number attribute is less than or equal to the given number<br>**Format:** number<br>**Example:** `30`, `1995`, or `7.5`    |
        

    === "Tag Attributes"
        
        Tag attributes can be used with either no modifier or with `.not`.
        
        String attributes can take multiple values as a **list or a comma-separated string**.
        
        ### "Tag Attributes"
        
        | Tag Attribute  | Description & Values                                                                                                                                                                            |
        |:---------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `format`       | **Description:** Uses the anime's format to match<br>**Values:** `tv`, `short`, `movie`, `special`, `ova`, `ona`, `music`                                                                       |
        | `status`       | **Description:** Uses the anime's status to match<br>**Values:** `finished`, `airing`, `not_yet_aired`, `cancelled`, `hiatus`                                                                   |
        | `genre`        | **Description:** Uses the anime's genre to match<br>**Values:** Any Genre in the Genre Dropdown box on the [AniList Search Page](https://anilist.co/search/anime)                               |
        | `tag`          | **Description:** Uses the anime's tag to match<br>**Values:** Any Tag in the Genre Dropdown box on the [AniList Search Page](https://anilist.co/search/anime)                                   |
        | `tag_category` | **Description:** Uses the anime's tag category to match<br>**Values:** Any Tag Category in the Advanced Genres & Tag Filters Menu on the [AniList Search Page](https://anilist.co/search/anime) |

        ???+ tip "Tag Attribute Modifiers"
        
            | Tag Modifier | Description                                                            |
            |:-------------|:-----------------------------------------------------------------------|
            | No Modifier  | Matches every item where the attribute matches the given string        |
            | `.not`       | Matches every item where the attribute does not match the given string |
            
            

    ### Example AniList Search Builder(s)
    
    ```yaml
    collections:
      Current Anime Season:
        anilist_search:
          season:
          year:
          sort_by: popular
        collection_order: custom
        sync_mode: sync
    ```
    ```yaml
    collections:
      Fall 2020 Anime:
        anilist_search:
          season: fall
          year: 2020
        collection_order: custom
        sync_mode: sync
    ```
    ```yaml
    collections:
      Pirates Anime:
        anilist_search:
          tag: Pirates
          sort_by: popular
        collection_order: custom
        sync_mode: sync
    ```
    ```yaml
    collections:
      Top Sports Anime:
        anilist_genre:
          genre: Sports
          limit: 20
          sort_by: popular
        collection_order: custom
        sync_mode: sync
    ```

=== "AniList Top Rated"
    
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

=== "AniList Popular"

    Finds every anime in AniList's [Popular Anime](https://anilist.co/search/anime/popular) list.
    
    The expected input is a single integer value of how many movies/shows to query. 
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example AniList Popular Builder(s)
    
    ```yaml
    collections:
      Popular Anime:
        anilist_popular: 10
        collection_order: custom
        sync_mode: sync
    ```

=== "AniList Trending"

    Finds every anime in AniList's [Trending Anime](https://anilist.co/search/anime/trending) list.
    
    The expected input is a single integer value of how many movies/shows to query. 
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example AniList Trending Builder(s)

    ```yaml
    collections:
      Trending Anime:
        anilist_trending: 10
        collection_order: custom
        sync_mode: sync
    ```

=== "AniList Relations"

    Finds the anime specified by the AniList ID and every relation in its relation tree except Character and Other relations.
    
    The expected input is an AniList ID. Multiple values are supported as either a list or a comma-separated string.

    ### Example AniList Relations Builder(s)

    ```yaml
    collections:
      One Piece:
        anilist_relations: 21
    ```

=== "AniList Studio"
    
    Finds all anime specified by the AniList Studio ID.
    
    The expected input is an AniList ID. Multiple values are supported as either a list or a comma-separated string.

    ### Example AniList Studio Builder(s)
    
    ```yaml
    collections:
      Studio Ghibli:
        anilist_studio: 21
    ```

=== "AniList ID"

    Finds the anime specified by the AniList ID.
    
    The expected input is an AniList ID. Multiple values are supported as either a list or a comma-separated string.

    ### Example AniList ID Builder(s)
    
    ```yaml
    collections:
      Cowboy Bebop:
        anilist_id: 23, 219
    ```

=== "AniList UserList"
    
    Gets anime in AniList User's Anime list. The different sub-attributes are detailed below. 
    
    Both `username` and `list_name` are required.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.
    
    | Attribute               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    |:------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `username`              | **Description:** A user's AniList Username                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | `list_name`             | **Description:** A user's AniList List Name                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | `score.gt`<sup>**1**</sup>  | **Description:** Only return items that have a score greater than the given number.<br>**Values:** `0.0`-`10.0`                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | `score.gte`<sup>**1**</sup> | **Description:** Only return items that have a score greater than or equal to the given number.<br>**Values:** `0.0`-`10.0`                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
    | `score.lt`<sup>**1**</sup>  | **Description:** Only return items that have a score less than the given number.<br>**Values:** `0.0`-`10.0`                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
    | `score.lte`<sup>**1**</sup> | **Description:** Only return items that have a score less than or equal to the given number.<br>**Values:** `0.0`-`10.0`                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
    | `sort_by`               | **Description:** Sort Order to return<br>**Default:** `score`<br>**Values:**<table class="clearTable"><tr><td>`score`</td><td>Sort by User Score</td></tr><tr><td>`popularity`</td><td>Sort by Popularity</td></tr><tr><td>`status`</td><td>Sort by Status</td></tr><tr><td>`progress`</td><td>Sort by Progress</td></tr><tr><td>`last_updated`</td><td>Sort by Last Updated</td></tr><tr><td>`last_added`</td><td>Sort by Last Added</td></tr><tr><td>`start_date`</td><td>Sort by Start Date</td></tr><tr><td>`completed_date`</td><td>Sort by Completed Date</td></tr></table> |
    
    <sup>**1**</sup> You can use multiple score filters but the number will have to match every filter. All unrated items are considered to have a 0 rating. 

    ### Example AniList UserList Builder(s)

    ```yaml
    collections:
      Currently Watching Anime:
        anilist_userlist:
          username: Username
          list_name: Watching
          sort_by: score
        collection_order: custom
        sync_mode: sync
    ```
