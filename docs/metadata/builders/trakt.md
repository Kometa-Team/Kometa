# Trakt Builders

You can find items using the features of [Trakt.tv](https://trakt.tv/) (Trakt). 

[Configuring Trakt](../../config/trakt) in the config is required for any of these builders.

| Attribute                                         | Description                                                                                                                                                                                                                                                                 | Works with Movies | Works with Shows | Works with Playlists and Custom Sort |
|:--------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------:|:----------------:|:------------------------------------:|
| [`trakt_list`](#trakt-list)                       | Finds every movie/show in the Trakt List                                                                                                                                                                                                                                    |      &#9989;      |     &#9989;      |               &#9989;                |
| [`trakt_list_details`](#trakt-list)               | Finds every movie/show in the Trakt List and updates the collection summary with the list description                                                                                                                                                                       |      &#9989;      |     &#9989;      |               &#9989;                |
| [`trakt_chart`](#trakt-chart)                     | Finds the movies/shows in the Trakt Chart                                                                                                                                                                                                                                   |      &#9989;      |     &#9989;      |               &#9989;                |
| [`trakt_userlist`](#trakt-userlist)               | Finds every movie/show in the Trakt Userlist                                                                                                                                                                                                                                |      &#9989;      |     &#9989;      |               &#9989;                |
| [`trakt_recommendations`](#trakt-recommendations) | Finds the movies/shows in Trakt's Personal Recommendations for your User [Movies](https://trakt.docs.apiary.io/#reference/recommendations/movies/get-movie-recommendations)/[Shows](https://trakt.docs.apiary.io/#reference/recommendations/shows/get-show-recommendations) |      &#9989;      |     &#9989;      |               &#9989;                | 
| [`trakt_boxoffice`](#trakt-box-office)            | Finds the 10 movies in Trakt's Top Box Office [Movies](https://trakt.tv/movies/boxoffice) list                                                                                                                                                                              |      &#9989;      |     &#10060;     |               &#9989;                |

## Trakt List

Finds every item in the Trakt List.

The expected input is a Trakt List URL. Multiple values are supported only as a list.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

**Trakt Lists cannot be sorted through the API, but the list is always returned to the default list order if you own the list.**

```yaml
collections:
  Christmas:
    trakt_list:
      - https://trakt.tv/users/movistapp/lists/christmas-movies
      - https://trakt.tv/users/2borno2b/lists/christmas-movies-extravanganza
    sync_mode: sync
```
```yaml
collections:
  Reddit Top 250:
    trakt_list: https://trakt.tv/users/jay-greene/lists/reddit-top-250-2019-edition
    collection_order: custom
    sync_mode: sync
```

* You can update the collection details with the Trakt List's description by using `trakt_list_details`.
* You can specify multiple collections in `trakt_list_details` but it will only use the first one to update the collection summary.

```yaml
collections:
  Reddit Top 250:
    trakt_list_details: https://trakt.tv/users/jay-greene/lists/reddit-top-250-2019-edition
    collection_order: custom
    sync_mode: sync
```

## Trakt Chart

Finds the movies/shows in the Trakt Chart. The options are detailed below.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order.

| Attribute     | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|:--------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `chart`       | **Description:** Which Trakt chart to query<br>**Values:**<table class="clearTable"><tr><td>`trending`</td><td>Trakt's Trending [Movies](https://trakt.tv/movies/trending)/[Shows](https://trakt.tv/shows/trending) list</td></tr><tr><td>`popular`</td><td>Trakt's Popular [Movies](https://trakt.tv/movies/popular)/[Shows](https://trakt.tv/shows/popular) list</td></tr><tr><td>`recommended`</td><td>Trakt's Recommended [Movies](https://trakt.tv/movies/recommended)/[Shows](https://trakt.tv/shows/recommended) list</td></tr><tr><td>`watched`</td><td>Trakt's Watched [Movies](https://trakt.tv/movies/watched)/[Shows](https://trakt.tv/shows/watched) list</td></tr><tr><td>`collected`</td><td>Trakt's Collected [Movies](https://trakt.tv/movies/collected)/[Shows](https://trakt.tv/shows/collected) list</td></tr></table> |
| `time_period` | **Description:** Time Period for the chart. Does not work with `trending` or `popular` chart types.<br>**Default:** `weekly`<br>**Values:** `daily`, `weekly`, `monthly`, `yearly`, or `all`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `limit`       | **Description:** Don't return more then this number<br>**Default:** `10`<br>**Values:** Number of Items to query.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

These are the links to the trakt charts that is looked at by time period.

| Period   |                                               Collected                                               |                                                Recommended                                                |                                              Watched                                              |
|:---------|:-----------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------:|
| Daily    |   [Movies](https://trakt.tv/movies/collected/daily)/[Shows](https://trakt.tv/shows/collected/daily)   |   [Movies](https://trakt.tv/movies/recommended/daily)/[Shows](https://trakt.tv/shows/recommended/daily)   |   [Movies](https://trakt.tv/movies/watched/daily)/[Shows](https://trakt.tv/shows/watched/daily)   |
| Weekly   |  [Movies](https://trakt.tv/movies/collected/weekly)/[Shows](https://trakt.tv/shows/collected/weekly)  |  [Movies](https://trakt.tv/movies/recommended/weekly)/[Shows](https://trakt.tv/shows/recommended/weekly)  |  [Movies](https://trakt.tv/movies/watched/weekly)/[Shows](https://trakt.tv/shows/watched/weekly)  |
| Monthly  | [Movies](https://trakt.tv/movies/collected/monthly)/[Shows](https://trakt.tv/shows/collected/monthly) | [Movies](https://trakt.tv/movies/recommended/monthly)/[Shows](https://trakt.tv/shows/recommended/monthly) | [Movies](https://trakt.tv/movies/watched/monthly)/[Shows](https://trakt.tv/shows/watched/monthly) |
| Yearly   |  [Movies](https://trakt.tv/movies/collected/yearly)/[Shows](https://trakt.tv/shows/collected/yearly)  |  [Movies](https://trakt.tv/movies/recommended/yearly)/[Shows](https://trakt.tv/shows/recommended/yearly)  |  [Movies](https://trakt.tv/movies/watched/yearly)/[Shows](https://trakt.tv/shows/watched/yearly)  |
| All-Time |     [Movies](https://trakt.tv/movies/collected/all)/[Shows](https://trakt.tv/shows/collected/all)     |     [Movies](https://trakt.tv/movies/recommended/all)/[Shows](https://trakt.tv/shows/recommended/all)     |     [Movies](https://trakt.tv/movies/watched/all)/[Shows](https://trakt.tv/shows/watched/all)     |

```yaml
collections:
  Trakt Trending:
    trakt_chart:
      chart: trending
      limit: 30
    collection_order: custom
    sync_mode: sync
```

You can use multiple charts in one builder using a list.

```yaml
collections:
  Trakt Trending & Popular:
    trakt_chart:
      - chart: trending
        limit: 30
      - chart: popular
        limit: 30
    collection_order: custom
    sync_mode: sync
```

## Trakt Userlist

Finds every movie/show in the Trakt Userlist.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order.

| Attribute  | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|:-----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `userlist` | **Description:** Which Trakt userlist to query<br>**Values:**<table class="clearTable"><tr><td>`trending`</td><td>Trakt's Trending [Movies](https://trakt.tv/movies/trending)/[Shows](https://trakt.tv/shows/trending) list</td></tr><tr><td>`popular`</td><td>Trakt's Popular [Movies](https://trakt.tv/movies/popular)/[Shows](https://trakt.tv/shows/popular) list</td></tr><tr><td>`recommended`</td><td>Trakt's Recommended [Movies](https://trakt.tv/movies/recommended)/[Shows](https://trakt.tv/shows/recommended) list</td></tr><tr><td>`watched`</td><td>Trakt's Watched [Movies](https://trakt.tv/movies/watched)/[Shows](https://trakt.tv/shows/watched) list</td></tr><tr><td>`collected`</td><td>Trakt's Collected [Movies](https://trakt.tv/movies/collected)/[Shows](https://trakt.tv/shows/collected) list</td></tr></table> |
| `user`     | **Description:** The User who's user lists you want to query.<br>**Default:** `me`<br>**Values:** Username of User or `me` for the authenticated user.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `sort_by`  | **Description:** How to sort the results<br>**Default:** `rank`<br>**Values:** `rank`, `added`, `released`, `title`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

```yaml
collections:
  Trakt Watchlist:
    trakt_userlist: 
      userlist: watchlist
      user: me
      sort_by: released
    collection_order: custom
    sync_mode: sync
```

You can use multiple charts in one builder using a list.

```yaml
collections:
  Trakt Watchlist:
    trakt_userlist:
      - userlist: watched
        user: me
      - userlist: collected
        user: me
    collection_order: custom
    sync_mode: sync
```

## Trakt Recommendations

Finds the movies/shows in Trakt's Recommendations for [Movies](https://trakt.docs.apiary.io/#reference/recommendations/movies/get-movie-recommendations)/[Shows](https://trakt.docs.apiary.io/#reference/recommendations/shows/get-show-recommendations)

The expected input is a single integer value of how many movies/shows to query. 

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Trakt Recommendations:
    trakt_recommendations: 30
    collection_order: custom
    sync_mode: sync
```

## Trakt Box Office

Finds the 10 movies in Trakt's Top Box Office [Movies](https://trakt.tv/movies/boxoffice) list.

The expected input is true. 

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Trakt Collected:
    trakt_boxoffice: true
    collection_order: custom
    sync_mode: sync
```
