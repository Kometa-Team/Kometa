---
hide:
  - toc
---
# TMDb Builders

You can find items using the features of [TheMovieDb.org](https://www.themoviedb.org/) (TMDb).

## TMDb Standard Builders

| Builder                                                              | Description                                              |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:---------------------------------------------------------------------|:---------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| `tmdb_discover`([movie](discover/movie.md)/[show](discover/show.md)) | Uses [TMDb's Discover Search](https://developer.themoviedb.org/docs/search-and-query-for-details) to find every movie/show based on the [movie search parameters](https://developers.themoviedb.org/3/discover/movie-discover) or [show search parameters](https://developers.themoviedb.org/3/discover/tv-discover) provided | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_collection`](collection.md)                                   | Finds every item in the TMDb collection                  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_list`](list.md)                                               | Finds every item in the TMDb List                        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_movie`](movie.md)                                             | Finds the movie specified                                | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_show`](show.md)                                               | Finds the show specified                                 |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_company`](company.md)                                         | Finds every item from the TMDb company's movie/show list | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_network`](network.md)                                         | Finds every item from the TMDb network's show list       |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_keyword`](keyword.md)                                         | Finds every item from the TMDb keyword's movie/show list | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |

## TMDb Chart Builders

| Builder                                                      | Description                                                                                                                                                     |              Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort     |
|:-------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------:|:------------------------------------------:|:-------------------------------------------:|
| [`tmdb_popular`](popular.md)                           | Finds the movies/shows in TMDb's [Popular Movies](https://www.themoviedb.org/movie)/[Popular Shows](https://www.themoviedb.org/tv) list                         | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_now_playing`](now-playing.md)                   | Finds the movies in TMDb's [Now Playing](https://www.themoviedb.org/movie/now-playing) list                                                                     | :fontawesome-solid-circle-check:{ .green }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_top_rated`](top-rated.md)                       | Finds the movies/shows in TMDb's [Top Rated Movies](https://www.themoviedb.org/movie/top-rated)/[Top Rated Shows](https://www.themoviedb.org/tv/top-rated) list |  :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_upcoming`](upcoming.md)                         | Finds the movies in TMDb's [Upcoming Movies](https://www.themoviedb.org/movie/upcoming) list                                                                    | :fontawesome-solid-circle-check:{ .green }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_airing_today`](airing-today.md)                 | Finds the shows in TMDb's [Airing Today Shows](https://www.themoviedb.org/tv/airing-today) list                                                                 |  :fontawesome-solid-circle-xmark:{ .red }   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_on_the_air`](on-the-air.md)                     | Finds the shows in TMDb's [On TV Shows](https://www.themoviedb.org/tv/on-the-air) list                                                                          |  :fontawesome-solid-circle-xmark:{ .red }   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_trending_daily`](trending-daily.md)                   | Finds the movies/shows in TMDb's Trending Daily list                                                                                                            | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_trending_weekly`](trending-weekly.md)                | Finds the movies/shows in TMDb's Trending Weekly list                                                                                                           | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |


## TMDb People Builders

    ???+ tip "People Collections"
    
        As Plex does not allow People to be part of Collections, Kometa will instead add any media that the person is associated with based om the Builder criteria.
    
        You can not have a Collection of "Top 10 Actors" for example, as Plex does not allow this.

| Builder                         | Description                                                                                                                                                     |              Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort     |
|:--------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------:|:------------------------------------------:|:-------------------------------------------:|
| [`tmdb_actor`](actor.md) | Finds every item in the TMDb Person's Actor Credits      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_crew`](crew.md)         | Finds every item in the TMDb Person's Crew Credits       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_director`](director.md) | Finds every item in the TMDb Person's Director Credits   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_producer`](producer.md) | Finds every item in the TMDb Person's Producer Credits   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_writer`](writer.md)     | Finds every item in the TMDb Person's Writer Credits     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
