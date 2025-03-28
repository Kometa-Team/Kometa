---
hide:
  - toc
---
# MyAnimeList Builders

You can find anime using the features of [MyAnimeList.net](https://myanimelist.net/) (MyAnimeList).

???+ warning "MyAnimeList Configuration"

    [Configuring MyAnimeList](../../config/myanimelist.md) in the config is required for any of these builders to function.

| Builder                                      | Description                                                                                                             |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:---------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`mal_search`](#myanimelist-search)          | Finds every anime in a MyAnimeList Search list                                                                          | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | 
| [`mal_all`](#myanimelist-top-all)            | Finds every anime in MyAnimeList's [Top All Anime](https://myanimelist.net/topanime.php) list                           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | 
| [`mal_airing`](#myanimelist-top-airing)      | Finds every anime in MyAnimeList's [Top Airing Anime](https://myanimelist.net/topanime.php?type=airing) list            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_upcoming`](#myanimelist-top-upcoming)  | Finds every anime in MyAnimeList's [Top Upcoming Anime](https://myanimelist.net/topanime.php?type=upcoming) list        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_tv`](#myanimelist-top-tv)              | Finds every anime in MyAnimeList's [Top Anime TV Series](https://myanimelist.net/topanime.php?type=tv) list             | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_movie`](#myanimelist-top-movie)        | Finds every anime in MyAnimeList's [Top Anime Movies](https://myanimelist.net/topanime.php?type=movie) list             | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_ova`](#myanimelist-top-ova)            | Finds every anime in MyAnimeList's [Top Anime OVA Series](https://myanimelist.net/topanime.php?type=ova) list           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_special`](#myanimelist-top-special)    | Finds every anime in MyAnimeList's [Top Anime Specials](https://myanimelist.net/topanime.php?type=special) list         | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_popular`](#myanimelist-most-popular)   | Finds every anime in MyAnimeList's [Most Popular Anime](https://myanimelist.net/topanime.php?type=bypopularity) list    | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_favorite`](#myanimelist-most-favorite) | Finds every anime in MyAnimeList's [Most Favorited Anime](https://myanimelist.net/topanime.php?type=favorite) list      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_suggested`](#myanimelist-suggested)    | Finds the suggested anime in by MyAnimeList for the authorized user                                                     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_id`](#myanimelist-id)                  | Finds the anime specified by the MyAnimeList ID                                                                         | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`mal_userlist`](#myanimelist-userlist)      | Finds anime in MyAnimeList User's Anime list the options are detailed below                                             | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`mal_season`](#myanimelist-seasonal)        | Finds anime in MyAnimeList's [Seasonal Anime](https://myanimelist.net/anime/season) list the options are detailed below | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

=== "MyAnimeList Search"
    
    Gets every anime in a MyAnimeList search. The different sub-attributes are detailed below. At least one attribute is required.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 
    
    | Attribute              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    |:-----------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `sort_by`              | **Description:** Sort Order to return<br>**Values:** `mal_id.desc`, `mal_id.asc`, `title.desc`, `title.asc`, `type.desc`, `type.asc`, `rating.desc`, `rating.asc`, `start_date.desc`, `start_date.asc`, `end_date.desc`, `end_date.asc`, `episodes.desc`, `episodes.asc`, `score.desc`, `score.asc`, `scored_by.desc`, `scored_by.asc`, `rank.desc`, `rank.asc`, `popularity.desc`, `popularity.asc`, `members.desc`, `members.asc`, `favorites.desc`, `favorites.asc` |
    | `limit`                | **Description:** Don't return more than this number<br>**Values:** Number of Anime to query from MyAnimeList                                                                                                                                                                                                                                                                                                                                                           |
    | `query`                | **Description:** Text query to search for                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | `prefix`               | **Description:** Results must begin with this prefix                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | `type`                 | **Description:** Type of Anime to search for<br>**Values:** `tv`, `movie`, `ova`, `special`, `ona`, `music`                                                                                                                                                                                                                                                                                                                                                            |
    | `status`               | **Description:** Status to search for<br>**Values:** `airing`, `complete`, `upcoming`                                                                                                                                                                                                                                                                                                                                                                                  |
    | `genre`                | **Description:** Comma-separated String of Genres to include using `,` for `AND` and <code>&#124;</code> for `OR`<br>**Values:** Genre Name or ID                                                                                                                                                                                                                                                                                                                      |
    | `genre.not`            | **Description:** Comma-separated String of Genres to exclude using `,` for `AND` and <code>&#124;</code> for `OR`<br>**Values:** Genre Name or ID                                                                                                                                                                                                                                                                                                                      |
    | `studio`               | **Description:** Comma-separated String of Genres to include using `,` for `AND` and <code>&#124;</code> for `OR`<br>**Values:** Studio Name or ID                                                                                                                                                                                                                                                                                                                     |
    | `content_rating`       | **Description:** Content Rating to search for<br>**Values:** `g`, `pg`, `pg13`, `r17`, `r`, `rx`                                                                                                                                                                                                                                                                                                                                                                       |
    | `score.gt`/`score.gte` | **Description:** Score must be greater than the given number<br>**Values:** Float between `0.00`-`10.00`                                                                                                                                                                                                                                                                                                                                                               |
    | `score.lt`/`score.lte` | **Description:** Score must be less than the given number<br>**Values:** Float between `0.00`-`10.00`                                                                                                                                                                                                                                                                                                                                                                  |
    | `sfw`                  | **Description:** Results must be Safe for Work<br>**Value:** `true`                                                                                                                                                                                                                                                                                                                                                                                                    |

    * Studio options can be found on [MyAnimeList's Search](https://myanimelist.net/anime.php) Page.
    * Genre options can be found on [MyAnimeList's Search](https://myanimelist.net/anime.php) Page.
    * To find the ID click on a Studio or Genre in the link above and there should be a number in the URL that's the `id`.
    * For example if the url is `https://myanimelist.net/anime/producer/4/Bones` the `id` would be `4` or if the url is `https://myanimelist.net/anime/genre/1/Action` the `id` would be `1`.

    ### Example MyAnimeList Search Builder(s)

    ```yaml
    collections:
      Top Action Anime:
        mal_search:
          limit: 100
          sort_by: score.desc
          genre: Action
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Top All"
    
    Gets every anime in MyAnimeList's [Top Airing Anime](https://myanimelist.net/topanime.php?type=airing) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Top All Builder(s)

    ```yaml
    collections:
      Top All Anime:
        mal_all: 30
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Top Airing"

    Gets every anime in MyAnimeList's [Top Airing Anime](https://myanimelist.net/topanime.php?type=airing) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Top Airing Builder(s)

    ```yaml
    collections:
      Top Airing Anime:
        mal_airing: 10
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Top Upcoming"

    Gets every anime in MyAnimeList's [Top Upcoming Anime](https://myanimelist.net/topanime.php?type=upcoming) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Top Upcoming Builder(s)

    ```yaml
    collections:
      Top Upcoming Anime:
        mal_upcoming: 10
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Top TV Series"

    Gets every anime in MyAnimeList's [Top Anime TV Series](https://myanimelist.net/topanime.php?type=tv) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Top TV Series Builder(s)

    ```yaml
    collections:
      Top Anime TV Series:
        mal_tv: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Top Movies"

    Gets every anime in MyAnimeList's [Top Anime Movies](https://myanimelist.net/topanime.php?type=movie) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Top Movies Builder(s)

    ```yaml
    collections:
      Top Anime Movies:
        mal_movie: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Top OVA Series"

    Gets every anime in MyAnimeList's [Top Anime OVA Series](https://myanimelist.net/topanime.php?type=ova) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Top OVA Series Builder(s)

    ```yaml
    collections:
      Top Anime OVA Series:
        mal_ova: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Top Specials"

    Gets every anime in MyAnimeList's [Top Anime Specials](https://myanimelist.net/topanime.php?type=special) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Top Specials Builder(s)

    ```yaml
    collections:
      Top Anime Specials:
        mal_special: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Most Popular"

    Gets every anime in MyAnimeList's [Most Popular Anime](https://myanimelist.net/topanime.php?type=bypopularity) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Most Popular Builder(s)

    ```yaml
    collections:
      Most Popular Anime:
        mal_popular: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Most Favorited"

    Gets every anime in MyAnimeList's [Most Favorited Anime](https://myanimelist.net/topanime.php?type=favorite) list. (Maximum: 500)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Most Favorited Builder(s)

    ```yaml
    collections:
      Most Favorited Anime:
        mal_favorite: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Suggested"
    
    Gets the suggested anime in by MyAnimeList for the authorized user. (Maximum: 100)
    
    The expected input value is a single integer value of how many movies/shows to query.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

    ### Example MyAnimeList Suggested Builder(s)

    ```yaml
    collections:
      Suggested Anime:
        mal_suggested: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList ID"

    Gets the anime specified by the MyAnimeList ID.
    
    The expected input is a MyAnimeList ID. Multiple values are supported as either a list or a comma-separated string.

    ### Example MyAnimeList ID Builder(s)

    ```yaml
    collections:
      Cowboy Bebop:
        mal_id: 23, 219
    ```

=== "MyAnimeList UserList"

    Gets anime in MyAnimeList User's Anime list. The different sub-attributes are detailed below. The only required attribute is `username`
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 
    
    | Attribute  | Description                                                                                                                                                                                                                                                                                                                                                                                                                       |
    |:-----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `username` | **Description:** A user's MyAnimeList Username or `@me` for the authorized user                                                                                                                                                                                                                                                                                                                                                   |
    | `status`   | **Description:** Status to search for<br>**Default:** `all`<br>**Values:**<table class="clearTable"><tr><td>`all`</td><td>All Anime List</td></tr><tr><td>`watching`</td><td>Currently Watching List</td></tr><tr><td>`completed`</td><td>Completed List</td></tr><tr><td>`on_hold`</td><td>On Hold List</td></tr><tr><td>`dropped`</td><td>Dropped List</td></tr><tr><td>`plan_to_watch`</td><td>Plan to Watch</td></tr></table> |
    | `sort_by`  | **Description:** Sort Order to return<br>**Default:** `score`<br>**Values:**<table class="clearTable"><tr><td>`score`</td><td>Sort by Score</td></tr><tr><td>`last_updated`</td><td>Sort by Last Updated</td></tr><tr><td>`title`</td><td>Sort by Anime Title</td></tr><tr><td>`start_date`</td><td>Sort by Start Date</td></tr></table>                                                                                          |
    | `limit`    | **Description:** Don't return more than this number<br>**Default:** `100`<br>**Values:** Number of Anime to query from MyAnimeList (max: 1000)                                                                                                                                                                                                                                                                                    |

    ### Example MyAnimeList UserList Builder(s)

    ```yaml
    collections:
      Currently Watching Anime:
        mal_userlist:
          username: "@me"
          status: watching
          sort_by: score
          limit: 500
        collection_order: custom
        sync_mode: sync
    ```

=== "MyAnimeList Seasonal"

    Gets anime in MyAnimeList's [Seasonal Anime](https://myanimelist.net/anime/season) list the options are detailed below. 
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 
    
    | Attribute       | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
    |:----------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `season`        | **Description:** Season to search<br>**Default:** `current`<br>**Values:**<table class="clearTable"><tr><td>`winter`</td><td>For winter season January, February, March</td></tr><tr><td>`spring`</td><td>For spring season April, May, June</td></tr><tr><td>`summer`</td><td>For summer season July, August, September</td></tr><tr><td>`fall`</td><td>For fall season October, November, December</td></tr><tr><td>`current`</td><td>For the current Season</td></tr></table> |
    | `year`          | **Description:** Year to search<br>**Default:** Current Year<br>**Values:** Number between `1917` and the current year.                                                                                                                                                                                                                                                                                                                                                          |
    | `sort_by`       | **Description:** Sort Order<br>**Default:** `members`<br>**Values:**<table class="clearTable"><tr><td>`members`</td><td>Sort by Most Members</td></tr><tr><td>`score`</td><td>Sort by Score</td></tr></table>                                                                                                                                                                                                                                                                    |
    | `limit`         | **Description:** Don't return more than this number<br>**Default:** `100`<br>**Values:** Number of Anime to query from MyAnimeList (max: 500)                                                                                                                                                                                                                                                                                                                                    |
    | `starting_only` | **Description:** Return only anime that began airing in the selected season<br>**Default:** `False`<br>**Values:** `True` or `False`                                                                                                                                                                                                                                                                                                                                             |

    ### Example MyAnimeList Seasonal Builder(s)

    ```yaml
    collections:
      Current Anime Season:
        mal_season:
          sort_by: members
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```
    ```yaml
    collections:
      Fall 2020 Anime:
        mal_season:
          season: fall
          year: 2020
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```
