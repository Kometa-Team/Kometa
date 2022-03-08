# MyAnimeList Builders

You can find anime using the features of [MyAnimeList.net](https://myanimelist.net/) (MyAnimeList).

[Configuring MyAnimeList](../../config/myanimelist) in the config is required for any of these builders.

| Attribute                                           | Description                                                                                                                                                       | Works with Movies | Works with Shows | Works with Playlists and Custom Sort |
|:----------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------:|:----------------:|:------------------------------------:|
| [`mal_all`](#myanimelist-top-all-anime)             | Finds every anime in MyAnimeList's [Top All Anime](https://myanimelist.net/topanime.php) list                                                                     |      &#9989;      |     &#9989;      |               &#9989;                | 
| [`mal_airing`](#myanimelist-top-airing-anime)       | Finds every anime in MyAnimeList's [Top Airing Anime](https://myanimelist.net/topanime.php?type=airing) list                                                      |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_upcoming`](#myanimelist-top-upcoming-anime)   | Finds every anime in MyAnimeList's [Top Upcoming Anime](https://myanimelist.net/topanime.php?type=upcoming) list                                                  |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_tv`](#myanimelist-top-anime-tv-series)        | Finds every anime in MyAnimeList's [Top Anime TV Series](https://myanimelist.net/topanime.php?type=tv) list                                                       |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_movie`](#myanimelist-top-anime-movies)        | Finds every anime in MyAnimeList's [Top Anime Movies](https://myanimelist.net/topanime.php?type=movie) list                                                       |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_ova`](#myanimelist-top-anime-ova-series)      | Finds every anime in MyAnimeList's [Top Anime OVA Series](https://myanimelist.net/topanime.php?type=ova) list                                                     |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_special`](#myanimelist-top-anime-specials)    | Finds every anime in MyAnimeList's [Top Anime Specials](https://myanimelist.net/topanime.php?type=special) list                                                   |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_popular`](#myanimelist-most-popular-anime)    | Finds every anime in MyAnimeList's [Most Popular Anime](https://myanimelist.net/topanime.php?type=bypopularity) list                                              |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_favorite`](#myanimelist-most-favorited-anime) | Finds every anime in MyAnimeList's [Most Favorited Anime](https://myanimelist.net/topanime.php?type=favorite) list                                                |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_suggested`](#myanimelist-suggested-anime)     | Finds the suggested anime in by MyAnimeList for the authorized user                                                                                               |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_id`](#myanimelist-id)                         | Finds the anime specified by the MyAnimeList ID                                                                                                                   |      &#9989;      |     &#9989;      |               &#10060;               |
| [`mal_userlist`](#myanimelist-user-anime-list)      | Finds anime in MyAnimeList User's Anime list the options are detailed below                                                                                       |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_season`](#myanimelist-seasonal-anime)         | Finds anime in MyAnimeList's [Seasonal Anime](https://myanimelist.net/anime/season) list the options are detailed below                                           |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_genre`](#myanimelist-genre)                   | Finds every anime tagged with the specified genre id. Genre options can be found on [MyAnimeList's Search](https://myanimelist.net/anime.php)                     |      &#9989;      |     &#9989;      |               &#9989;                |
| [`mal_studio`](#myanimelist-studio)                 | Finds every anime tagged with the specified studio/producer/licensor id. Studio options can be found on [MyAnimeList's Search](https://myanimelist.net/anime.php) |      &#9989;      |     &#9989;      |               &#9989;                |

## Expected Input

The builders below are expected to have a single integer value of how many movies/shows to query. 
* [MyAnimeList Top All Anime](#myanimelist-top-all-anime)
* [MyAnimeList Top Airing Anime](#myanimelist-top-airing-anime)
* [MyAnimeList Top Upcoming Anime](#myanimelist-top-upcoming-anime)
* [MyAnimeList Top Anime TV Series](#myanimelist-top-anime-tv-series)
* [MyAnimeList Top Anime Movies](#myanimelist-top-anime-movies)
* [MyAnimeList Top Anime OVA Series](#myanimelist-top-anime-ova-series)
* [MyAnimeList Top Anime Specials](#myanimelist-top-anime-specials)
* [MyAnimeList Most Popular Anime](#myanimelist-most-popular-anime)
* [MyAnimeList Most Favorited Anime](#myanimelist-most-favorited-anime)
* [MyAnimeList Suggested Anime](#myanimelist-suggested-anime)

The attributes of [MyAnimeList ID](#myanimelist-id), [MyAnimeList Seasonal Anime](#myanimelist-seasonal-anime), [MyAnimeList User Anime List](#myanimelist-user-anime-list), [MyAnimeList Genre](#myanimelist-genre), and [MyAnimeList Studio](#myanimelist-studio) are detailed in their sections below.


## MyAnimeList Top All Anime

Gets every anime in MyAnimeList's [Top Airing Anime](https://myanimelist.net/topanime.php?type=airing) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Top All Anime:
    mal_all: 30
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Top Airing Anime

Gets every anime in MyAnimeList's [Top Airing Anime](https://myanimelist.net/topanime.php?type=airing) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Top Airing Anime:
    mal_airing: 10
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Top Upcoming Anime

Gets every anime in MyAnimeList's [Top Upcoming Anime](https://myanimelist.net/topanime.php?type=upcoming) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Top Upcoming Anime:
    mal_upcoming: 10
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Top Anime TV Series

Gets every anime in MyAnimeList's [Top Anime TV Series](https://myanimelist.net/topanime.php?type=tv) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Top Anime TV Series:
    mal_tv: 20
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Top Anime Movies

Gets every anime in MyAnimeList's [Top Anime Movies](https://myanimelist.net/topanime.php?type=movie) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Top Anime Movies:
    mal_movie: 20
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Top Anime OVA Series

Gets every anime in MyAnimeList's [Top Anime OVA Series](https://myanimelist.net/topanime.php?type=ova) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Top Anime OVA Series:
    mal_ova: 20
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Top Anime Specials

Gets every anime in MyAnimeList's [Top Anime Specials](https://myanimelist.net/topanime.php?type=special) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Top Anime Specials:
    mal_special: 20
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Most Popular Anime

Gets every anime in MyAnimeList's [Most Popular Anime](https://myanimelist.net/topanime.php?type=bypopularity) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Most Popular Anime:
    mal_popular: 20
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Most Favorited Anime

Gets every anime in MyAnimeList's [Most Favorited Anime](https://myanimelist.net/topanime.php?type=favorite) list. (Maximum: 500)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Most Favorited Anime:
    mal_favorite: 20
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Suggested Anime

Gets the suggested anime in by MyAnimeList for the authorized user. (Maximum: 100)

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Suggested Anime:
    mal_suggested: 20
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList ID

Gets the anime specified by the MyAnimeList ID.

The expected input is a MyAnimeList ID. Multiple values are supported as either a list or a comma-separated string.

```yaml
collections:
  Cowboy Bebop:
    mal_id: 23, 219
```

## MyAnimeList User Anime List

Gets anime in MyAnimeList User's Anime list. The different sub-attributes are detailed below. The only required attribute is `username`

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

| Attribute  | Description                                                                                                                                                                                                                                                                                                                                                                                                                       |
|:-----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `username` | **Description:** A user's MyAnimeList Username or `@me` for the authorized user                                                                                                                                                                                                                                                                                                                                                   |
| `status`   | **Description:** Status to search for<br>**Default:** `all`<br>**Values:**<table class="clearTable"><tr><td>`all`</td><td>All Anime List</td></tr><tr><td>`watching`</td><td>Currently Watching List</td></tr><tr><td>`completed`</td><td>Completed List</td></tr><tr><td>`on_hold`</td><td>On Hold List</td></tr><tr><td>`dropped`</td><td>Dropped List</td></tr><tr><td>`plan_to_watch`</td><td>Plan to Watch</td></tr></table> |
| `sort_by`  | **Description:** Sort Order to return<br>**Default:** `score`<br>**Values:**<table class="clearTable"><tr><td>`score`</td><td>Sort by Score</td></tr><tr><td>`last_updated`</td><td>Sort by Last Updated</td></tr><tr><td>`title`</td><td>Sort by Anime Title</td></tr><tr><td>`start_date`</td><td>Sort by Start Date</td></tr></table>                                                                                          |
| `limit`    | **Description:** Don't return more then this number<br>**Default:** `100`<br>**Values:** Number of Anime to query from MyAnimeList (max: 1000)                                                                                                                                                                                                                                                                                    |

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

## MyAnimeList Seasonal Anime

Gets anime in MyAnimeList's [Seasonal Anime](https://myanimelist.net/anime/season) list the options are detailed below. 

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

| Attribute | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|:----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `season`  | **Description:** Season to search<br>**Default:** `current`<br>**Values:**<table class="clearTable"><tr><td>`winter`</td><td>For winter season January, February, March</td></tr><tr><td>`spring`</td><td>For spring season April, May, June</td></tr><tr><td>`summer`</td><td>For summer season July, August, September</td></tr><tr><td>`fall`</td><td>For fall season October, November, December</td></tr><tr><td>`current`</td><td>For the current Season</td></tr></table> |
| `year`    | **Description:** Year to search<br>**Default:** Current Year<br>**Values:** Number between `1917` and the current year.                                                                                                                                                                                                                                                                                                                                                          |
| `sort_by` | **Description:** Sort Order<br>**Default:** `members`<br>**Values:**<table class="clearTable"><tr><td>`members`</td><td>Sort by Most Members</td></tr><tr><td>`score`</td><td>Sort by Score</td></tr></table>                                                                                                                                                                                                                                                                    |
| `limit`   | **Description:** Don't return more then this number<br>**Default:** `100`<br>**Values:** Number of Anime to query from MyAnimeList (max: 500)                                                                                                                                                                                                                                                                                                                                    |

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

## MyAnimeList Genre

Gets every anime tagged with the specified genre ID sorted by members the options are detailed below. `genre_id` is the only required attribute.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

* Genre options can be found on [MyAnimeList's Search](https://myanimelist.net/anime.php) Page.
* To find the ID click on a Genre in the link above and there should be a number in the URL that's the `genre_id`.
* For example if the url is `https://myanimelist.net/anime/genre/1/Action` the `genre_id` would be `1`.

| Attribute  | Description                                                         |
|:-----------|:--------------------------------------------------------------------|
| `genre_id` | The ID of Genre from MyAnimeList                                    |
| `limit`    | Number of Anime to query from MyAnimeList<br>**Default:** `0` (All) |

```yaml
collections:
  Sports Anime:
    mal_genre:
      genre_id: 30
    collection_order: custom
    sync_mode: sync
```

## MyAnimeList Studio 

Gets every anime tagged with the specified studio/producer/licensor ID sorted by members the options are detailed below. `studio_id` is the only required attribute.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

* Studio options can be found on [MyAnimeList's Search](https://myanimelist.net/anime.php) Page.
* To find the ID click on a Studio in the link above and there should be a number in the URL that's the `studio_id`.
* For example if the url is `https://myanimelist.net/anime/producer/4/Bones` the `studio_id` would be `4`.

| Attribute   | Description                                                         |
|:------------|:--------------------------------------------------------------------|
| `studio_id` | The ID of Studio/Producer/Licensor from MyAnimeList                 |
| `limit`     | Number of Anime to query from MyAnimeList<br>**Default:** `0` (All) |

```yaml
collections:
  Bones Studio Anime:
    mal_studio:
      studio_id: 4
    collection_order: custom
    sync_mode: sync
```
