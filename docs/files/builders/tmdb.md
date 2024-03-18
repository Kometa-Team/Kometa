# TMDb Builders

You can find items using the features of [TheMovieDb.org](https://www.themoviedb.org/) (TMDb).
## Standard TMDb Builders

| Attribute                             | Description                                              |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:--------------------------------------|:---------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`tmdb_collection`](#tmdb-collection) | Finds every item in the TMDb collection                  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_list`](#tmdb-list)             | Finds every item in the TMDb List                        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_actor`](#tmdb-actor)           | Finds every item in the TMDb Person's Actor Credits      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_crew`](#tmdb-crew)             | Finds every item in the TMDb Person's Crew Credits       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_director`](#tmdb-director)     | Finds every item in the TMDb Person's Director Credits   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_producer`](#tmdb-producer)     | Finds every item in the TMDb Person's Producer Credits   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_writer`](#tmdb-writer)         | Finds every item in the TMDb Person's Writer Credits     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_movie`](#tmdb-movie)           | Finds the movie specified                                | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_show`](#tmdb-show)             | Finds the show specified                                 |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_company`](#tmdb-company)       | Finds every item from the TMDb company's movie/show list | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_network`](#tmdb-network)       | Finds every item from the TMDb network's show list       |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_keyword`](#tmdb-keyword)       | Finds every item from the TMDb keyword's movie/show list | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |

## Standard TMDb Details Builders

| Attribute                                     | Description                                                                                                                          |             Works with Movies              |              Works with Shows              |   Works with Playlists and Custom Sort   |
|:----------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:----------------------------------------:|
| [`tmdb_collection_details`](#tmdb-collection) | Finds every item in the TMDb collection and updates the collection with the summary, poster, and background from the TMDb collection | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |
| [`tmdb_list_details`](#tmdb-list)             | Finds every item in the TMDb List and updates the collection with the description and poster of the TMDb list                        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| [`tmdb_actor_details`](#tmdb-actor)           | Finds every item in the TMDb Person's Actor Credits with the biography and profile from the TMDb person                              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| [`tmdb_crew_details`](#tmdb-crew)             | Finds every item in the TMDb Person's Crew Credits with the biography and profile from the TMDb person                               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| [`tmdb_director_details`](#tmdb-director)     | Finds every item in the TMDb Person's Actor Credits with the biography and profile from the TMDb person                              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| [`tmdb_producer_details`](#tmdb-producer)     | Finds every item in the TMDb Person's Producer Credits with the biography and profile from the TMDb person                           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| [`tmdb_writer_details`](#tmdb-writer)         | Finds every item in the TMDb Person's Writer Credits with the biography and profile from the TMDb person                             | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| [`tmdb_movie_details`](#tmdb-movie)           | Finds the movie specified and updates the collection with the summary, poster, and background from the TMDb movie                    | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |
| [`tmdb_show_details`](#tmdb-show)             | Finds the show specified and updates the collection with the summary, poster, and background from the TMDb show                      |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |

## Other TMDb Builders

| Attribute                                       | Description                                                                                                                                                                                                                                                                                                                   |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`tmdb_popular`](#tmdb-popular)                 | Finds the movies/shows in TMDb's [Popular Movies](https://www.themoviedb.org/movie)/[Popular Shows](https://www.themoviedb.org/tv) list                                                                                                                                                                                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_now_playing`](#tmdb-now-playing)         | Finds the movies in TMDb's [Now Playing](https://www.themoviedb.org/movie/now-playing) list                                                                                                                                                                                                                                   | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_top_rated`](#tmdb-top-rated)             | Finds the movies/shows in TMDb's [Top Rated Movies](https://www.themoviedb.org/movie/top-rated)/[Top Rated Shows](https://www.themoviedb.org/tv/top-rated) list                                                                                                                                                               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_upcoming`](#tmdb-upcoming)               | Finds the movies in TMDb's [Upcoming Movies](https://www.themoviedb.org/movie/upcoming) list                                                                                                                                                                                                                                  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_airing_today`](#tmdb-airing-today)       | Finds the shows in TMDb's [Airing Today Shows](https://www.themoviedb.org/tv/airing-today) list                                                                                                                                                                                                                               |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_on_the_air`](#tmdb-on-the-air)           | Finds the shows in TMDb's [On TV Shows](https://www.themoviedb.org/tv/on-the-air) list                                                                                                                                                                                                                                        |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_trending_daily`](#tmdb-trending-daily)   | Finds the movies/shows in TMDb's Trending Daily list                                                                                                                                                                                                                                                                          | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_trending_weekly`](#tmdb-trending-weekly) | Finds the movies/shows in TMDb's Trending Weekly list                                                                                                                                                                                                                                                                         | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_discover`](#tmdb-discover)               | Uses [TMDb's Discover Search](https://developer.themoviedb.org/docs/search-and-query-for-details) to find every movie/show based on the [movie search parameters](https://developers.themoviedb.org/3/discover/movie-discover) or [show search parameters](https://developers.themoviedb.org/3/discover/tv-discover) provided | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

## Expected Input

The builders below are expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list or a comma-separated string.

* [TMDb Collection](#tmdb-collection) and [TMDb Collection Details](#tmdb-collection)
* [TMDb List](#tmdb-list) and [TMDb List Details](#tmdb-list)
* [TMDb Actor](#tmdb-actor) and [TMDb Actor Details](#tmdb-actor)
* [TMDb Crew](#tmdb-crew) and [TMDb Crew Details](#tmdb-crew)
* [TMDb Director](#tmdb-director) and [TMDb Director Details](#tmdb-director)
* [TMDb Producer](#tmdb-producer) and [TMDb Producer Details](#tmdb-producer)
* [TMDb Writer](#tmdb-writer) and [TMDb Writer Details](#tmdb-writer)
* [TMDb Movie](#tmdb-movie) and [TMDb Movie Details](#tmdb-movie)
* [TMDb Show](#tmdb-show) and [TMDb Show Details](#tmdb-show)
* [TMDb Company](#tmdb-company)
* [TMDb Network](#tmdb-network)

The builders below are expected to have a single integer value of how many movies/shows to query.

* [TMDb Popular](#tmdb-popular)
* [TMDb Now Playing](#tmdb-now-playing)
* [TMDb Top Rated](#tmdb-top-rated)
* [TMDb Trending Daily](#tmdb-trending-daily)
* [TMDb Trending Weekly](#tmdb-trending-weekly)

[TMDb Discover](#tmdb-discover)'s attributes are detailed [below](#tmdb-discover).

## TMDb Collection

Finds every item in the TMDb collection.

```yaml
collections:
  The Lord of the Rings:
    tmdb_collection: https://www.themoviedb.org/collection/119
  The Hobbit:
    tmdb_collection: 121938
  Middle Earth:
    tmdb_collection:
      - 119
      - https://www.themoviedb.org/collection/121938
```

* You can update the collection details with the TMDb collection's summary, poster, and background by using `tmdb_collection_details`.
* You can specify multiple collections in `tmdb_collection_details` but it will only use the first one to update the collection details.
* Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.

```yaml
collections:
  Harry Potter:
    tmdb_collection_details: 1241   #https://www.themoviedb.org/collection/1241 also accepted
  Fantastic Beasts:
    tmdb_collection_details: 435259 #https://www.themoviedb.org/collection/435259 also accepted
  Wizarding World:
    tmdb_collection_details:
      - 1241
      - https://www.themoviedb.org/collection/435259
```

## TMDb List

Finds every item in the TMDb List.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Top 50 Grossing Films of All Time (Worldwide):
    tmdb_list: 10     #https://www.themoviedb.org/list/10 also accepted
    collection_order: custom
    sync_mode: sync
```

* You can update the collection details with the TMDb list's description and poster by using `tmdb_list_details`.
* You can specify multiple lists in `tmdb_list_details` but it will only use the first one to update the collection details.

```yaml
collections:
  Rotten Tomatoes Top 100 Movies of All Time:
    tmdb_list_details: 3697   #themoviedb.org/list/3697 also accepted
```

## TMDb Actor

Finds every item in the TMDb Person's Actor Credits.

```yaml
collections:
  Robin Williams:
    tmdb_actor: 2157  #https://www.themoviedb.org/person/2157-robin-williams also accepted
```

* You can update the collection details with the TMDb Person's biography and profile by using `tmdb_actor_details`.
* You can specify multiple people in `tmdb_actor_details` but it will only use the first one to update the collection details.

```yaml
collections:
  Meryl Streep:
    tmdb_actor_details: 5064
```

## TMDb Crew

Finds every item in the TMDb Person's Crew Credits.

```yaml
collections:
  Quentin Tarantino:
    tmdb_crew: 138  #https://www.themoviedb.org/person/138-quentin-tarantino also accepted
```

* You can update the collection details with the TMDb Person's biography and profile by using `tmdb_crew_details`.
* You can specify multiple people in `tmdb_crew_details` but it will only use the first one to update the collection details.

```yaml
collections:
  James Cameron:
    tmdb_crew_details: 2710
```

## TMDb Director

Finds every item in the TMDb Person's Director Credits.

```yaml
collections:
  Steven Spielberg:
    tmdb_director: 488  #https://www.themoviedb.org/person/488-steven-spielberg also accepted
```

* You can update the collection details with the TMDb Person's biography and profile by using `tmdb_director_details`.
* You can specify multiple people in `tmdb_director_details` but it will only use the first one to update the collection details.

```yaml
collections:
  Sofia Coppola:
    tmdb_director_details: 1769
```

## TMDb Producer

Finds every item in the TMDb Person's Producer Credits.

```yaml
collections:
  Adam Sandler:
    tmdb_producer: 19292  #https://www.themoviedb.org/person/19292-adam-sandler also accepted
```

* You can update the collection details with the TMDb Person's biography and profile by using `tmdb_producer_details`.
* You can specify multiple people in `tmdb_producer_details` but it will only use the first one to update the collection details.

```yaml
collections:
  Kathleen Kennedy:
    tmdb_producer_details: 489
```

## TMDb Writer

Finds every item in the TMDb Person's Writer Credits.

```yaml
collections:
  Woody Allen:
    tmdb_writer: 1243 #https://www.themoviedb.org/person/1243-woody-allen also accepted
```

* You can update the collection details with the TMDb Person's biography and profile by using `tmdb_writer_details`.
* You can specify multiple people in `tmdb_writer_details` but it will only use the first one to update the collection details.

```yaml
collections:
  Tina Fey:
    tmdb_writer_details: 56323
```

## TMDb Movie

Finds the movie specified.

```yaml
collections:
  Anaconda:
    tmdb_collection: 105995 #https://www.themoviedb.org/collection/105995 also accepted
    tmdb_movie: 336560      #https://www.themoviedb.org/movie/336560 also accepted
```

* You can update the collection details with the TMDb movie's summary, poster, and background by using `tmdb_movie_details`.
* You can specify multiple movies in `tmdb_movie_details` but it will only use the first one to update the collection details.
* Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.

```yaml
collections:
  Deadpool Specials:
    tmdb_collection: 567604
    tmdb_movie_details: 558144
```

## TMDb Show

Finds the show specified.

```yaml
collections:
  Star Wars (Animated Shows):
    tmdb_show:
      - 4194  #https://www.themoviedb.org/tv/4194-star-wars-the-clone-wars also accepted
      - 60554 #https://www.themoviedb.org/tv/60554-star-wars-rebels also accepted
```

* You can update the collection details with the TMDb show's summary, poster, and background by using `tmdb_show_details`.
* You can specify multiple shows in `tmdb_show_details` but it will only use the first one to update the collection details.
* Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.

```yaml
collections:
  Pokémon Evolutions & Chronicles:
    tmdb_show_details:
      - 132636
      - 13230
```

## TMDb Company

Finds every movie from the TMDb company's movie list.

```yaml
collections:
  Studio Ghibli:
    tmdb_company: 10342 #https://www.themoviedb.org/company/10342 also accepted
```
## TMDb Network

Finds every item from the TMDb network's movie/show list.

```yaml
collections:
  CBS:
    tmdb_network: 16  #https://www.themoviedb.org/network/16 also accepted
```
## TMDb Keyword

Finds every item from the TMDb keyword's movie/show list.

```yaml
collections:
  Marvel Cinematic Universe:
    tmdb_keyword: 180547  #https://www.themoviedb.org/keyword/180547 also accepted
```

## TMDb Popular

Finds the movies/shows in TMDb's [Popular Movies](https://www.themoviedb.org/movie)/[Popular Shows](https://www.themoviedb.org/tv) list.

Use `tmdb_region` with this builder to set the region.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  TMDb Popular:
    tmdb_popular: 30
    collection_order: custom
    sync_mode: sync
```

## TMDb Now Playing

Finds the movies in TMDb's [Now Playing](https://www.themoviedb.org/movie/now-playing) list.

Use `tmdb_region` with this builder to set the region.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  TMDb Now Playing:
    tmdb_now_playing: 30
    collection_order: custom
    sync_mode: sync
```

## TMDb Top Rated

Finds the movies/shows in TMDb's [Top Rated Movies](https://www.themoviedb.org/movie/top-rated)/[Top Rated Shows](https://www.themoviedb.org/tv/top-rated) list.

Use `tmdb_region` with this builder to set the region.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  TMDb Top Rated:
    tmdb_top_rated: 30
    collection_order: custom
    sync_mode: sync
```

## TMDb Upcoming

Finds the movies in TMDb's [Upcoming Movies](https://www.themoviedb.org/movie/upcoming) list.

Use `tmdb_region` with this builder to set the region.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  TMDb Upcoming:
    tmdb_upcoming: 30
    collection_order: custom
    sync_mode: sync
```

## TMDb Airing Today

Finds the shows in TMDb's [Airing Today Shows](https://www.themoviedb.org/tv/airing-today) list.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  TMDb Airing Today:
    tmdb_airing_today: 30
    collection_order: custom
    sync_mode: sync
```

## TMDb On the Air

Finds the shows in TMDb's [On TV Shows](https://www.themoviedb.org/tv/on-the-air) list.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  TMDb On the Air:
    tmdb_on_the_air: 30
    collection_order: custom
    sync_mode: sync
```

## TMDb Trending Daily

Finds the movies/shows in TMDb's Trending Daily list.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  TMDb Daily Trending:
    tmdb_trending_daily: 30
    collection_order: custom
    sync_mode: sync
```

## TMDb Trending Weekly

Finds the movies/shows in TMDb's Trending Weekly list.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  TMDb Weekly Trending:
    tmdb_trending_weekly: 30
    collection_order: custom
    sync_mode: sync
```

## TMDb Discover

Uses [TMDb's Discover Search](https://developer.themoviedb.org/docs/search-and-query-for-details) to find every movie/show based on the [movie search parameters](https://developers.themoviedb.org/3/discover/movie-discover) or [show search parameters](https://developers.themoviedb.org/3/discover/tv-discover) provided.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

| Type               | Description                                       |
|:-------------------|:--------------------------------------------------|
| String             | Any number of alphanumeric characters             |
| Integer            | Any whole number greater than zero i.e. 2, 10, 50 |
| Number             | Any number greater than zero i.e. 2.5, 7.4, 9     |
| Boolean            | Must be `true` or `false`                         |
| Date: `MM/DD/YYYY` | Date that fits the specified format               |
| Year: `YYYY`       | Year must be a 4 digit integer i.e. 1990          |

### Discover Movies Parameters

!!!important

    Note that a number of filters support being comma (,) or pipe (|) separated. Comma's are treated like an AND query while pipe's are treated like an OR. This allows for quite complex filtering depending on your desired results.

| Movie Parameters                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|:--------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                         | Specify how many movies you want returned by the query.<br>**Type:** Integer<br>**Default:** 100                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `region`                        | Specify a [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) to filter release dates. Must be uppercase. Will use the `region` specified in the [TMDb Config](../../config/tmdb.md) by default.<br>**Type:** `^[A-Z]{2}$`                                                                                                                                                                                                                                                                                                                                                         |
| `sort_by`                       | Choose from one of the many available sort options.<br>**Type:** Any [sort options](#sort-options) below<br>**Default:** `popularity.desc`                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `certification_country`         | Used in conjunction with the certification parameter, use this to specify a country with a valid certification.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `certification`                 | Filter results with a valid certification from the `certification_country` parameter.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `certification.lte`             | Filter and only include movies that have a certification that is less than or equal to the specified value.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `certification.gte`             | Filter and only include movies that have a certification that is greater than or equal to the specified value.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `include_adult`                 | A filter and include or exclude adult movies.<br>**Type:** Boolean                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `include_video`                 | A filter and include or exclude videos.<br>**Type:** Boolean                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `primary_release_year`          | A filter to limit the results to a specific primary release year.<br>**Type:** Year: YYYY                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `primary_release_date.gte`      | Filter and only include movies that have a primary release date that is greater or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `primary_release_date.lte`      | Filter and only include movies that have a primary release date that is less than or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `release_date.gte`              | Filter and only include movies that have a release date (looking at all release dates) that is greater or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `release_date.lte`              | Filter and only include movies that have a release date (looking at all release dates) that is less than or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `with_release_type`             | Specify a comma (AND) or pipe (OR) separated value to filter release types by.<br>**Type:** String<br>**Values:** `1`: Premiere, `2`: Theatrical (limited), `3`: Theatrical, `4`: Digital, `5`: Physical, `6`: TV                                                                                                                                                                                                                                                                                                                                                                                              |
| `year`                          | A filter to limit the results to a specific year (looking at all release dates).<br>**Type:** Year: `YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `vote_count.gte`                | Filter and only include movies that have a vote count that is greater or equal to the specified value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `vote_count.lte`                | Filter and only include movies that have a vote count that is less than or equal to the specified value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `vote_average.gte`              | Filter and only include movies that have a rating that is greater or equal to the specified value.<br>**Type:** Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `vote_average.lte`              | Filter and only include movies that have a rating that is less than or equal to the specified value.<br>**Type:** Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `with_cast`                     | A comma-separated list of person ID's. Only include movies that have one of the ID's added as an actor.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `with_crew`                     | A comma-separated list of person ID's. Only include movies that have one of the ID's added as a crew member.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `with_people`                   | A comma-separated list of person ID's. Only include movies that have one of the ID's added as either an actor or a crew member.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                       |
| `with_companies`                | A comma-separated list of production company ID's. Only include movies that have one of the ID's added as a production company.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                       |
| `without_companies`             | Filter the results to exclude the specific production companies you specify here. AND / OR filters are supported.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `with_genres`                   | Comma-separated value of genre ids that you want to include in the results.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `without_genres`                | Comma-separated value of genre ids that you want to exclude from the results.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `with_keywords`                 | A comma-separated list of keyword ID's. Only includes movies that have one of the ID's added as a keyword.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `without_keywords`              | Exclude items with certain keywords. You can comma and pipe separate these values to create an 'AND' or 'OR' logic.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `with_runtime.gte`              | Filter and only include movies that have a runtime that is greater or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `with_runtime.lte`              | Filter and only include movies that have a runtime that is less than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `with_original_language`        | Specify an ISO 639-1 string to filter results by their original language value.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `with_watch_providers`          | A comma or pipe separated list of watch provider ID's.<br>use in conjunction with watch_region, can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `watch_region`                  | An [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes). Combine this filter with `with_watch_providers` in order to filter your results by a specific watch provider in a specific region.<br>**Type:** String<br>**Values:** [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                                                                                                                                                                                      |
| `with_watch_monetization_types` | In combination with `watch_region`, you can filter by monetization type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `flatrate`, `free`, `ads`, `rent`, `buy`                                                                                                                                                                                                                                                                                                                                                                                                      |


### Discover Shows Parameters

!!!important

    Note that a number of filters support being comma (,) or pipe (|) separated. Comma's are treated like an AND query while pipe's are treated like an OR. This allows for quite complex filtering depending on your desired results.

| Show Parameters                 | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|:--------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                         | Specify how many movies you want to be returned by the query.<br>**Type:** Integer<br>**Default:** 100                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `sort_by`                       | Choose from one of the many available sort options.<br>**Type:** Any [sort options](#sort-options) below<br>**Default:** `popularity.desc`                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `air_date.gte`                  | Filter and only include TV shows that have an air date (by looking at all episodes) that is greater or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `air_date.lte`                  | Filter and only include TV shows that have an air date (by looking at all episodes) that is less than or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `first_air_date.gte`            | Filter and only include TV shows that have a original air date that is greater or equal to the specified value. Can be used in conjunction with the `include_null_first_air_dates` filter if you want to include items with no air date.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                   |
| `first_air_date.lte`            | Filter and only include TV shows that have a original air date that is less than or equal to the specified value. Can be used in conjunction with the `include_null_first_air_dates` filter if you want to include items with no air date.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                 |
| `first_air_date_year`           | Filter and only include TV shows that have an original air date year that equal to the specified value. Can be used in conjunction with the `include_null_first_air_dates` filter if you want to include items with no air date.<br>**Type:** Year: `YYYY`                                                                                                                                                                                                                                                                                                                                                 |
| `include_null_first_air_dates`  | Use this filter to include TV shows that don't have an air date while using any of the `first_air_date` filters.<br>**Type:** Boolean                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `timezone`                      | Used in conjunction with the `air_date.gte/lte` filter to calculate the proper UTC offset.<br>**Type:** String<br>**Default:** `America/New_York`                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `vote_count.gte`                | Filter and only include TV that have a vote count that is greater or equal to the specified value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `vote_count.lte`                | Filter and only include TV that have a vote count that is less than or equal to the specified value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `vote_average.gte`              | Filter and only include TV that have a rating that is greater or equal to the specified value.<br>**Type:** Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `vote_average.lte`              | Filter and only include TV that have a rating that is less than or equal to the specified value.<br>**Type:** Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `with_networks`                 | Comma-separated value of network ids that you want to include in the results.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `with_companies`                | A comma-separated list of production company ID's. Only include movies that have one of the ID's added as a production company.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `without_companies`             | Filter the results to exclude the specific production companies you specify here. AND / OR filters are supported.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `with_genres`                   | Comma-separated value of genre ids that you want to include in the results.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `without_genres`                | Comma-separated value of genre ids that you want to exclude from the results.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `with_keywords`                 | A comma-separated list of keyword ID's. Only includes TV shows that have one of the ID's added as a keyword.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `without_keywords`              | Exclude items with certain keywords. You can comma and pipe separate these values to create an 'AND' or 'OR' logic.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `with_runtime.gte`              | Filter and only include TV shows with an episode runtime that is greater than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `with_runtime.lte`              | Filter and only include TV shows with an episode runtime that is less than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `with_original_language`        | Specify an ISO 639-1 string to filter results by their original language value.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `with_name_translation`         | Specify a language/country string to filter the results by if the item has a type of name translation.<br>**Type:** String<br>**Values:** `ar-AE`, `ar-SA`, `bg-BG`, `bn-BD`, `ca-ES`, `ch-GU`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-US`, `eo-EO`, `es-ES`, `es-MX`, `eu-ES`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ka-GE`, `kn-IN`, `ko-KR`, `lt-LT`, `ml-IN`, `nb-NO`, `nl-NL`, `no-NO`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sl-SI`, `sr-RS`, `sv-SE`, `ta-IN`, `te-IN`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-TW` |
| `screened_theatrically`         | Filter results to include items that have been screened theatrically.<br>**Type:** Boolean                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `with_watch_providers`          | A comma or pipe separated list of watch provider ID's.<br>use in conjunction with watch_region, can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `watch_region`                  | An [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes). Combine this filter with `with_watch_providers` in order to filter your results by a specific watch provider in a specific region.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                 |
| `with_watch_monetization_types` | In combination with `watch_region`, you can filter by monetization type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `flatrate`, `free`, `ads`, `rent`, `buy`                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `with_status`                   | Filter TV shows by their status.<br>**Type:** String<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Values:** `0`: Returning Series, `1`: Planned, `2`: In Production, `3`: Ended, `4`: Cancelled, `5`: Pilot                                                                                                                                                                                                                                                                                                                                                                                                                                        | 
| `with_type`                     | Filter TV shows by their type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `0`: Documentary, `1`: News, `2`: Miniseries, `3`: Reality, `4`: Scripted, `5`: Show, `6`: Video                                                                                                                                                                                                                                                                                                                                                                                                                                         |

### Sort Options

| Sort Option                 |                  Movie Sort                   |                  Show Sort                   |
|:----------------------------|:---------------------------------------------:|:--------------------------------------------:|
| `popularity.asc`            | :fontawesome-solid-circle-check:{ .green }    | :fontawesome-solid-circle-check:{ .green }   |
| `popularity.desc`           |  :fontawesome-solid-circle-check:{ .green }   |  :fontawesome-solid-circle-check:{ .green }  |
| `original_title.asc`        |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `original_title.desc`       |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `revenue.asc`               |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `revenue.desc`              |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `release_date.asc`          |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `release_date.desc`         |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `primary_release_date.asc`  |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `primary_release_date.desc` |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `first_air_date.asc`        |   :fontawesome-solid-circle-xmark:{ .red }    |  :fontawesome-solid-circle-check:{ .green }  |
| `first_air_date.desc`       |   :fontawesome-solid-circle-xmark:{ .red }    |  :fontawesome-solid-circle-check:{ .green }  |
| `vote_average.asc`          |  :fontawesome-solid-circle-check:{ .green }   |  :fontawesome-solid-circle-check:{ .green }  |
| `vote_average.desc`         |  :fontawesome-solid-circle-check:{ .green }   |  :fontawesome-solid-circle-check:{ .green }  |
| `vote_count.asc`            |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |
| `vote_count.desc`           |  :fontawesome-solid-circle-check:{ .green }   |   :fontawesome-solid-circle-xmark:{ .red }   |

```yaml
collections:
  Movies Released in October 2020:
    tmdb_discover:
      primary_release_date.gte: 10/01/2020
      primary_release_date.lte: 10/31/2020
```
```yaml
collections:
  Popular Movies:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      sort_by: popularity.desc
```
```yaml
collections:
  Highest Rated R Movies:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      certification_country: US
      certification: R
      sort_by: vote_average.desc
```
```yaml
collections:
  Most Popular Kids Movies:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      certification_country: US
      certification.lte: G
      sort_by: popularity.desc
```
```yaml
collections:
  Highest Rated Movies From 2010:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      primary_release_year: 2010
      sort_by: vote_average.desc
```
```yaml
collections:
  Best Dramas From 2014:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      with_genres: 18
      primary_release_year: 2014
      sort_by: vote_average.desc
```
```yaml
collections:
  Highest Rated Science Fiction Movies with Tom Cruise:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      with_genres: 878
      with_cast: 500
      sort_by: vote_average.desc
```
```yaml
collections:
  Highest Grossing Comedy Movies with Will Ferrell:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      with_genres: 35
      with_cast: 23659
      sort_by: revenue.desc
```
```yaml
collections:
  Top Rated Movies with Brad Pitt and Edward Norton:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      with_people: 287,819
      sort_by: vote_average.desc
```
```yaml
collections:
  Popular Movies with David Fincher and Rooney Mara:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      with_people: 108916,7467
      sort_by: popularity.desc
```
```yaml
collections:
  Top Rated Dramas:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      with_genres: 18
      sort_by: vote_average.desc
      vote_count.gte: 10
```
```yaml
collections:
  Highest Grossing R Movies with Liam Neeson:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      certification_country: US
      certification: R
      sort_by: revenue.desc
      with_cast: 3896
```
