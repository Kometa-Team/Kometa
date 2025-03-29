---
hide:
  - toc
---
# TMDb Builders

You can find items using the features of [TheMovieDb.org](https://www.themoviedb.org/) (TMDb).

## TMDb Standard Builders

| Builder                          | Description                                              |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:---------------------------------|:---------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`tmdb_discover`](#discover)     | Uses [TMDb's Discover Search](https://developer.themoviedb.org/docs/search-and-query-for-details) to find every movie/show based on the [movie search parameters](https://developers.themoviedb.org/3/discover/movie-discover) or [show search parameters](https://developers.themoviedb.org/3/discover/tv-discover) provided | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_collection`](#collection) | Finds every item in the TMDb collection                  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_list`](#list)             | Finds every item in the TMDb List                        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tmdb_movie`](#movie)           | Finds the movie specified                                | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_show`](#show)             | Finds the show specified                                 |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_company`](#company)       | Finds every item from the TMDb company's movie/show list | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_network`](#network)       | Finds every item from the TMDb network's show list       |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_keyword`](#keyword)       | Finds every item from the TMDb keyword's movie/show list | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |

## TMDb Chart Builders

| Builder                                    | Description                                                                                                                                                     |              Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort     |
|:-------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------:|:------------------------------------------:|:-------------------------------------------:|
| [`tmdb_popular`](#popular)                 | Finds the movies/shows in TMDb's [Popular Movies](https://www.themoviedb.org/movie)/[Popular Shows](https://www.themoviedb.org/tv) list                         | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_now_playing`](#now-playing)         | Finds the movies in TMDb's [Now Playing](https://www.themoviedb.org/movie/now-playing) list                                                                     | :fontawesome-solid-circle-check:{ .green }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_top_rated`](#top-rated)             | Finds the movies/shows in TMDb's [Top Rated Movies](https://www.themoviedb.org/movie/top-rated)/[Top Rated Shows](https://www.themoviedb.org/tv/top-rated) list |  :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_upcoming`](#upcoming)               | Finds the movies in TMDb's [Upcoming Movies](https://www.themoviedb.org/movie/upcoming) list                                                                    | :fontawesome-solid-circle-check:{ .green }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_airing_today`](#airing-today)       | Finds the shows in TMDb's [Airing Today Shows](https://www.themoviedb.org/tv/airing-today) list                                                                 |  :fontawesome-solid-circle-xmark:{ .red }   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_on_the_air`](#on-the-air)           | Finds the shows in TMDb's [On TV Shows](https://www.themoviedb.org/tv/on-the-air) list                                                                          |  :fontawesome-solid-circle-xmark:{ .red }   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_trending_daily`](#trending-daily)   | Finds the movies/shows in TMDb's Trending Daily list                                                                                                            | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |
| [`tmdb_trending_weekly`](#trending-weekly) | Finds the movies/shows in TMDb's Trending Weekly list                                                                                                           | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green }  |


## TMDb People Builders

| Builder                      | Description                                                                                                                                                     |              Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort     |
|:-----------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------:|:------------------------------------------:|:-------------------------------------------:|
| [`tmdb_actor`](#actor)       | Finds every item in the TMDb Person's Actor Credits      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_crew`](#crew)         | Finds every item in the TMDb Person's Crew Credits       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_director`](#director) | Finds every item in the TMDb Person's Director Credits   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_producer`](#producer) | Finds every item in the TMDb Person's Producer Credits   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`tmdb_writer`](#writer)     | Finds every item in the TMDb Person's Writer Credits     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |

=== "TMDb Standard Builders"

    These are the most commonly used TMDb Builders.
    
    === "Discover"
    
        Uses [TMDb's Discover Search](https://developer.themoviedb.org/docs/search-and-query-for-details) to find every 
        movie/show based on the [movie search attributes](https://developers.themoviedb.org/3/discover/movie-discover) or
        [show search attributes](https://developers.themoviedb.org/3/discover/tv-discover) provided.
        
        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.
        
        | Type               | Description                                       |
        |:-------------------|:--------------------------------------------------|
        | String             | Any number of alphanumeric characters             |
        | Integer            | Any whole number greater than zero i.e. 2, 10, 50 |
        | Number             | Any number greater than zero i.e. 2.5, 7.4, 9     |
        | Boolean            | Must be `true` or `false`                         |
        | Date: `MM/DD/YYYY` | Date that fits the specified format               |
        | Year: `YYYY`       | Year must be a 4 digit integer i.e. 1990          |
    
        === "Discover Movies Attributes"
            
            !!!important
            
                Note that a number of filters support being comma (,) or pipe (|) separated. Comma's are treated like an AND query 
                while pipe's are treated like an OR. This allows for quite complex filtering depending on your desired results.
            
            !!!bug
            
                We have noticed inconsistent responses from TMDb when using `popularity.asc` and `popularity.desc` as the sort order. This can result in movies/shows disappearing from and reapparing in collections/overlays sporadically. **We suggest users do not use the popularity sort options with `tmdb_discover`**.
            
                This bug is on TMDb's side and we are awaiting a fix from them.
            
            | Attribute                | Description                                                                                                                                                                                                                                                                                                                               |
            |:--------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
            | `limit`                         | Specify how many movies you want returned by the query.<br>**Type:** Integer<br>**Default:** 100                                                                                                                                                                                                                                          |
            | `region`                        | Specify a [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) to filter release dates. Must be uppercase. Will use the `region` specified in the [TMDb Config](../../config/tmdb.md) by default.<br>**Type:** `^[A-Z]{2}$`                                                                                    |
            | `sort_by`                       | Choose from one of the many available sort options.<br>**Type:** Any sort option below<br>**Default:** `popularity.desc`                                                                                                                                                                                                |
            | `certification_country`         | Used in conjunction with the certification parameter, use this to specify a country with a valid certification.<br>**Type:** String                                                                                                                                                                                                       |
            | `certification`                 | Filter results with a valid certification from the `certification_country` parameter.<br>**Type:** String                                                                                                                                                                                                                                 |
            | `certification.lte`             | Filter and only include movies that have a certification that is less than or equal to the specified value.<br>**Type:** String                                                                                                                                                                                                           |
            | `certification.gte`             | Filter and only include movies that have a certification that is greater than or equal to the specified value.<br>**Type:** String                                                                                                                                                                                                        |
            | `include_adult`                 | A filter and include or exclude adult movies.<br>**Type:** Boolean                                                                                                                                                                                                                                                                        |
            | `include_video`                 | A filter and include or exclude videos.<br>**Type:** Boolean                                                                                                                                                                                                                                                                              |
            | `primary_release_year`          | A filter to limit the results to a specific primary release year.<br>**Type:** Year: YYYY                                                                                                                                                                                                                                                 |
            | `primary_release_date.gte`      | Filter and only include movies that have a primary release date that is greater or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                          |
            | `primary_release_date.lte`      | Filter and only include movies that have a primary release date that is less than or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                        |
            | `release_date.gte`              | Filter and only include movies that have a release date (looking at all release dates) that is greater or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                   |
            | `release_date.lte`              | Filter and only include movies that have a release date (looking at all release dates) that is less than or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                 |
            | `with_release_type`             | Specify a comma (AND) or pipe (OR) separated value to filter release types by.<br>**Type:** String<br>**Values:** `1`: Premiere, `2`: Theatrical (limited), `3`: Theatrical, `4`: Digital, `5`: Physical, `6`: TV                                                                                                                         |
            | `year`                          | A filter to limit the results to a specific year (looking at all release dates).<br>**Type:** Year: `YYYY`                                                                                                                                                                                                                                |
            | `vote_count.gte`                | Filter and only include movies that have a vote count that is greater or equal to the specified value.<br>**Type:** Integer                                                                                                                                                                                                               |
            | `vote_count.lte`                | Filter and only include movies that have a vote count that is less than or equal to the specified value.<br>**Type:** Integer                                                                                                                                                                                                             |
            | `vote_average.gte`              | Filter and only include movies that have a rating that is greater or equal to the specified value.<br>**Type:** Number                                                                                                                                                                                                                    |
            | `vote_average.lte`              | Filter and only include movies that have a rating that is less than or equal to the specified value.<br>**Type:** Number                                                                                                                                                                                                                  |
            | `with_cast`                     | A comma-separated list of person ID's. Only include movies that have one of the ID's added as an actor.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                 |
            | `with_crew`                     | A comma-separated list of person ID's. Only include movies that have one of the ID's added as a crew member.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                            |
            | `with_people`                   | A comma-separated list of person ID's. Only include movies that have one of the ID's added as either an actor or a crew member.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                         |
            | `with_companies`                | A comma-separated list of production company ID's. Only include movies that have one of the ID's added as a production company.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                         |
            | `without_companies`             | Filter the results to exclude the specific production companies you specify here. AND / OR filters are supported.<br>**Type:** String                                                                                                                                                                                                     |
            | `with_genres`                   | Comma-separated value of genre ids that you want to include in the results.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                             |
            | `without_genres`                | Comma-separated value of genre ids that you want to exclude from the results.<br>**Type:** String                                                                                                                                                                                                                                         |
            | `with_keywords`                 | A comma-separated list of keyword ID's. Only includes movies that have one of the ID's added as a keyword.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                              |
            | `without_keywords`              | Exclude items with certain keywords. You can comma and pipe separate these values to create an 'AND' or 'OR' logic.<br>**Type:** String                                                                                                                                                                                                   |
            | `with_runtime.gte`              | Filter and only include movies that have a runtime that is greater or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                              |
            | `with_runtime.lte`              | Filter and only include movies that have a runtime that is less than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                            |
            | `with_origin_country`           | Specify an origin country string to filter results by their original country value.<br>**Type:** String                                                                                                                                                                                                                                   |
            | `with_original_language`        | Specify an ISO 639-1 string to filter results by their original language value.<br>**Type:** String                                                                                                                                                                                                                                       |
            | `with_watch_providers`          | A comma or pipe separated list of watch provider ID's.<br>use in conjunction with watch_region, can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                            |
            | `without_watch_providers`       | Filter the results to exclude certain watch providers.<br>**Type:** String                                                                                                                                                                                                                                                                |
            | `watch_region`                  | An [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes). Combine this filter with `with_watch_providers` in order to filter your results by a specific watch provider in a specific region.<br>**Type:** String<br>**Values:** [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) |
            | `with_watch_monetization_types` | In combination with `watch_region`, you can filter by monetization type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `flatrate`, `free`, `ads`, `rent`, `buy`                                                                                                        |
            
        === "Discover Shows Attributes"
            
            ???+ warning "Important"
            
                Note that a number of filters support being comma (,) or pipe (|) separated. Comma's are treated like an AND query 
                while pipe's are treated like an OR. This allows for quite complex filtering depending on your desired results.
            
            
            | Attributes                 | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
            |:--------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
            | `limit`                         | Specify how many movies you want to be returned by the query.<br>**Type:** Integer<br>**Default:** 100                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
            | `sort_by`                       | Choose from one of the many available sort options.<br>**Type:** Any sort option below<br>**Default:** `popularity.desc`                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
            | `air_date.gte`                  | Filter and only include TV shows that have an air date (by looking at all episodes) that is greater or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
            | `air_date.lte`                  | Filter and only include TV shows that have an air date (by looking at all episodes) that is less than or equal to the specified value.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                                                                                                                     |
            | `first_air_date.gte`            | Filter and only include TV shows that have a original air date that is greater or equal to the specified value. Can be used in conjunction with the `include_null_first_air_dates` filter if you want to include items with no air date.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                   |
            | `first_air_date.lte`            | Filter and only include TV shows that have a original air date that is less than or equal to the specified value. Can be used in conjunction with the `include_null_first_air_dates` filter if you want to include items with no air date.<br>**Type:** Date: `MM/DD/YYYY`                                                                                                                                                                                                                                                                                                                                 |
            | `first_air_date_year`           | Filter and only include TV shows that have an original air date year that equal to the specified value. Can be used in conjunction with the `include_null_first_air_dates` filter if you want to include items with no air date.<br>**Type:** Year: `YYYY`                                                                                                                                                                                                                                                                                                                                                 |
            | `include_adult`                 | A filter and include or exclude adult movies.<br>**Type:** Boolean                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
            | `include_null_first_air_dates`  | Use this filter to include TV shows that don't have an air date while using any of the `first_air_date` filters.<br>**Type:** Boolean                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
            | `timezone`                      | Used in conjunction with the `air_date.gte/lte` filter to calculate the proper UTC offset.<br>**Type:** String<br>**Default:** `America/New_York`                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
            | `vote_count.gte`                | Filter and only include TV that have a vote count that is greater or equal to the specified value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
            | `vote_count.lte`                | Filter and only include TV that have a vote count that is less than or equal to the specified value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
            | `vote_average.gte`              | Filter and only include TV that have a rating that is greater or equal to the specified value.<br>**Type:** Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
            | `vote_average.lte`              | Filter and only include TV that have a rating that is less than or equal to the specified value.<br>**Type:** Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
            | `with_networks`                 | Comma-separated value of network ids that you want to include in the results.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
            | `with_companies`                | A comma-separated list of production company ID's. Only include movies that have one of the ID's added as a production company.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                          |
            | `without_companies`             | Filter the results to exclude the specific production companies you specify here. AND / OR filters are supported.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
            | `with_genres`                   | Comma-separated value of genre ids that you want to include in the results.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                              |
            | `without_genres`                | Comma-separated value of genre ids that you want to exclude from the results.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
            | `with_keywords`                 | A comma-separated list of keyword ID's. Only includes TV shows that have one of the ID's added as a keyword.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                             |
            | `without_keywords`              | Exclude items with certain keywords. You can comma and pipe separate these values to create an 'AND' or 'OR' logic.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
            | `with_runtime.gte`              | Filter and only include TV shows with an episode runtime that is greater than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
            | `with_runtime.lte`              | Filter and only include TV shows with an episode runtime that is less than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
            | `with_original_language`        | Specify an ISO 639-1 string to filter results by their original language value.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
            | `with_name_translation`         | Specify a language/country string to filter the results by if the item has a type of name translation.<br>**Type:** String<br>**Values:** `ar-AE`, `ar-SA`, `bg-BG`, `bn-BD`, `ca-ES`, `ch-GU`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-US`, `eo-EO`, `es-ES`, `es-MX`, `eu-ES`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ka-GE`, `kn-IN`, `ko-KR`, `lt-LT`, `ml-IN`, `nb-NO`, `nl-NL`, `no-NO`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sl-SI`, `sr-RS`, `sv-SE`, `ta-IN`, `te-IN`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-TW` |
            | `screened_theatrically`         | Filter results to include items that have been screened theatrically.<br>**Type:** Boolean                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
            | `with_watch_providers`          | A comma or pipe separated list of watch provider ID's.<br>use in conjunction with watch_region, can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                             |
            | `without_watch_providers`       | Filter the results to exclude certain watch providers.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
            | `watch_region`                  | An [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes). Combine this filter with `with_watch_providers` in order to filter your results by a specific watch provider in a specific region.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                 |
            | `with_watch_monetization_types` | In combination with `watch_region`, you can filter by monetization type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `flatrate`, `free`, `ads`, `rent`, `buy`                                                                                                                                                                                                                                                                                                                                                                         |
            | `with_status`                   | Filter TV shows by their status.<br>**Type:** String<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Values:** `0`: Returning Series, `1`: Planned, `2`: In Production, `3`: Ended, `4`: Cancelled, `5`: Pilot                                                                                                                                                                                                                                                                                                                                                          | 
            | `with_type`                     | Filter TV shows by their type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `0`: Documentary, `1`: News, `2`: Miniseries, `3`: Reality, `4`: Scripted, `5`: Show, `6`: Video                                                                                                                                                                                                                                                                                                                                                           |
            
        === "Sort Options"
        
            | Sort Option                 |                 Movie Sort                 |                 Show Sort                  |
            |:----------------------------|:------------------------------------------:|:------------------------------------------:|
            | `popularity.asc`            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
            | `popularity.desc`           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
            | `title.asc`                 | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `title.desc`                | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `original_title.asc`        | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `original_title.desc`       | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `name.asc`                  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
            | `name.desc`                 |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
            | `original_name.asc`         |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
            | `original_name.desc`        |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
            | `revenue.asc`               | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `revenue.desc`              | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `release_date.asc`          | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `release_date.desc`         | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `primary_release_date.asc`  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `primary_release_date.desc` | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
            | `first_air_date.asc`        |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
            | `first_air_date.desc`       |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
            | `vote_average.asc`          | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
            | `vote_average.desc`         | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
            | `vote_count.asc`            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
            | `vote_count.desc`           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

        ### Example TMDb Discover Builder(s)

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
    
    
    === "Collection"
    
        Finds every item in the TMDb collection.

        This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list or a comma-separated string.

        ### Example TMDb Collection Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          The Lord of the Rings:
            tmdb_collection: 
                - 121938 #(3)!
          The Hobbit:
            tmdb_collection:  https://www.themoviedb.org/collection/119 
          Middle Earth:
            tmdb_collection_details: #(1)!
              - 119 #(2)!
              - https://www.themoviedb.org/collection/121938
        ```
    
        1. You can replace `tmdb_collection` with `tmdb_collection_details` if you would like to fetch and use the TMDb collection's summary, poster, and background from the list. 
        2. You can specify multiple collections in `tmdb_collection_details` but it will only use the first one to update the collection details.
        3. https://www.themoviedb.org/collection/121938-the-hobbit-collection also accepted

        * Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.
    
    === "List"
        
        Finds every item in the TMDb List.
        
        This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list or a comma-separated string.

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order. 

        ### Example TMDb List Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          Top 50 Grossing Films of All Time (Worldwide):
            tmdb_list: 10 #(1)!
            collection_order: custom
            sync_mode: sync
          Marvel & DC Universes:
            tmdb_list_details: #(2)!
              - 1 #(3)!
              - 3
            collection_order: custom
            sync_mode: sync
        ```

        1. https://www.themoviedb.org/list/10 also accepted
        2. You can replace `tmdb_list` with `tmdb_list_details` if you would like to fetch and use the TMDb collection's summary, poster, and background from the list
        3. You can specify multiple lists in `tmdb_list_details` but it will only use the first one to update the collection details

    === "Movie"
        
        Finds the movie specified.
        
        This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list or a comma-separated string.

        ### Example TMDb Movie Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          Anaconda:
            tmdb_movie: #(1)!
              - 336560
          Wizard of Oz & Wicked:
            tmdb_movie_details: #(2)!
              - 630 #(3)!
              - 402431
        ```

        1. You can replace `tmdb_movie` with `tmdb_movie_details` if you would like to fetch and use the TMDb show's summary, poster, and background from the list
        2. You can specify multiple shows in `tmdb_movie_details` but it will only use the first one to update the collection details
        3. https://www.themoviedb.org/movie/630-the-wizard-of-oz also accepted

        * Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.
    

    === "Show"
        
        Finds the show specified.
        
        This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list or a comma-separated string.

        ### Example TMDb Show Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          Star Wars (Animated Shows):
            tmdb_show:
              - 4194 #(1)!
              - 60554
            Pokémon Evolutions & Chronicles:
              tmdb_show_details: #(2)!
                - 132636 #(3)!
                - 13230
        ```

        1. https://www.themoviedb.org/tv/4194-star-wars-the-clone-wars also accepted
        2. You can replace `tmdb_show` with `tmdb_show_details` if you would like to fetch and use the TMDb show's summary, poster, and background from the list
        3. You can specify multiple shows in `tmdb_show_details` but it will only use the first one to update the collection details

        * Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.

    === "Company"
        
        Finds every movie from the TMDb company's movie list.
        
        This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list or a comma-separated string.

        ### Example TMDb Company Builder(s)

        ```yaml
        collections:
          Studio Ghibli:
            tmdb_company: 10342 #(1)!
        ```

        1. https://www.themoviedb.org/company/10342 also accepted

    === "Network"

        Finds every item from the TMDb network's movie/show list.
        
        This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list or a comma-separated string.

        ### Example TMDb Network Builder(s)

        ```yaml
        collections:
          CBS:
            tmdb_network: 16 #(1)!
        ```

        1.  https://www.themoviedb.org/network/16 also accepted



    === "Keyword"

        Finds every item from the TMDb keyword's movie/show list.

        ### Example TMDb Keyword Builder(s)

        ```yaml
        collections:
          Marvel Cinematic Universe:
            tmdb_keyword: 180547 #(1)!
        ```

        1.   https://www.themoviedb.org/keyword/180547 also accepted

=== "TMDb Chart Builders"

    These Builders use TMDb's Chart data

    === "Popular"
        
        Finds the movies/shows in TMDb's [Popular Movies](https://www.themoviedb.org/movie)/[Popular Shows](https://www.themoviedb.org/tv) list.
        
        Use `tmdb_region` with this Builder to set the region.
        
        This Builder is expected to have an integer (number) value of how many items to query

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.
        
        ### Example TMDb Popular Builder(s)

        ```yaml
        collections:
          TMDb Popular:
            tmdb_popular: 30
            collection_order: custom
            sync_mode: sync
        ```

    === "Now Playing"
        
        Finds the movies in TMDb's [Now Playing](https://www.themoviedb.org/movie/now-playing) list.
        
        Use `tmdb_region` with this Builder to set the region.
        
        This Builder is expected to have an integer (number) value of how many items to query

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.

        ### Example TMDb Now Playing Builder(s)

        ```yaml
        collections:
          TMDb Now Playing:
            tmdb_now_playing: 30
            collection_order: custom
            sync_mode: sync
        ```

    === "Top Rated"
        
        Finds the movies/shows in TMDb's [Top Rated Movies](https://www.themoviedb.org/movie/top-rated)/[Top Rated Shows](https://www.themoviedb.org/tv/top-rated) list.
        
        Use `tmdb_region` with this Builder to set the region.
        
        This Builder is expected to have an integer (number) value of how many items to query

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.

        ### Example TMDb Top Rated Builder(s)

        ```yaml
        collections:
          TMDb Top Rated:
            tmdb_top_rated: 30
            collection_order: custom
            sync_mode: sync
        ```

    === "Upcoming"
        
        Finds the movies in TMDb's [Upcoming Movies](https://www.themoviedb.org/movie/upcoming) list.
        
        Use `tmdb_region` with this Builder to set the region.
        
        This Builder is expected to have an integer (number) value of how many items to query

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.

        ### Example TMDb Upcoming Builder(s)

        ```yaml
        collections:
          TMDb Upcoming:
            tmdb_upcoming: 30
            collection_order: custom
            sync_mode: sync
        ```

    === "Airing Today"
        
        Finds the shows in TMDb's [Airing Today Shows](https://www.themoviedb.org/tv/airing-today) list.
        
        This Builder is expected to have an integer (number) value of how many items to query

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.

        ### Example TMDb Airing Today Builder(s)

        ```yaml
        collections:
          TMDb Airing Today:
            tmdb_airing_today: 30
            collection_order: custom
            sync_mode: sync
        ```

    === "On the Air"
        
        Finds the shows in TMDb's [On TV Shows](https://www.themoviedb.org/tv/on-the-air) list.
        
        This Builder is expected to have an integer (number) value of how many items to query

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.

        ### Example TMDb On the Air Builder(s)

        ```yaml
        collections:
          TMDb On the Air:
            tmdb_on_the_air: 30
            collection_order: custom
            sync_mode: sync
        ```

    === "Trending Daily"
        
        Finds the movies/shows in TMDb's Trending Daily list.
        
        This Builder is expected to have an integer (number) value of how many items to query

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.

        ### Example TMDb Trending Daily Builder(s)

        ```yaml
        collections:
          TMDb Daily Trending:
            tmdb_trending_daily: 30
            collection_order: custom
            sync_mode: sync
        ```

    === "Trending Weekly"
        
        Finds the movies/shows in TMDb's Trending Weekly list.
        
        This Builder is expected to have an integer (number) value of how many items to query

        The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
        and in a specific order.

        ### Example TMDb Trending Weekly Builder(s)

        ```yaml
        collections:
          TMDb Weekly Trending:
            tmdb_trending_weekly: 30
            collection_order: custom
            sync_mode: sync
        ```

=== "TMDb People Builders"
    
    These Builders use data on people's credited work.
    
    ???+ tip "People Collections"
    
        As Plex does not allow People to be part of Collections, Kometa will instead add any media that the person is associated with based om the Builder criteria.
    
        You can not have a Collection of "Top 10 Actors" for example, as Plex does not allow this.

    === "Actor"
        
        Finds every item in the TMDb Person's Actor Credits.

        ### Example TMDb Actor Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          Robin Williams:
            tmdb_actor: 2157 #(1)!
          Hemsworth Brothers:
            tmdb_actor_details: #(2)!
              - 74568 #(3)!
              - 96066
              - 216986
        ```
        
        1.  https://www.themoviedb.org/person/2157-robin-williams also accepted
        2.  You can replace `tmdb_actor` with `tmdb_actor_details` if you would like to fetch and use the TMDb Person's biography and profile from the list
        3.  You can specify multiple people in `tmdb_actor_details` but it will only use the first one to update the collection details

    === "Crew"

        Finds every item in the TMDb Person's Crew Credits.

        ### Example TMDb Crew Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          Quentin Tarantino:
            tmdb_crew: 138 #(1)!
          The Skarsgards Family
            tmdb_crew_details: #(2)!
              - 28846 #(3)!
              - 137905
              - 63764
              - 1640
              - 1281937
              - 2367741
        ```

        1.  https://www.themoviedb.org/person/138-quentin-tarantino also accepted
        2.  You can replace `tmdb_crew` with `tmdb_crew_details` if you would like to fetch and use the TMDb Person's biography and profile from the list
        3.  You can specify multiple people in `tmdb_crew_details` but it will only use the first one to update the collection details

    === "Director"
        
        Finds every item in the TMDb Person's Director Credits.

        ### Example TMDb Director Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          Steven Spielberg:
            tmdb_director: 488 #(1)!
          The Russo Brothers:
            tmdb_director_details: #(2)!
              - 19271 #(3)!
              - 19272
        ```

        1.  #https://www.themoviedb.org/person/488-steven-spielberg also accepted
        1.  You can replace `tmdb_director` with `tmdb_director_details` if you would like to fetch and use the TMDb Person's biography and profile from the list
        3.  You can specify multiple people in `tmdb_director_details` but it will only use the first one to update the collection details


    === "Producer"
        
        Finds every item in the TMDb Person's Producer Credits.

        ### Example TMDb Producer Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          Adam Sandler:
            tmdb_producer: 19292 #(3)! 
          The Wachowskis:
            tmdb_producer_details: #(1)!
              - 9339 #(2)!
              - 9340
        ```
    
        1.  You can replace `tmdb_producer` with `tmdb_producer_details` if you would like to fetch and use the TMDb collection's summary, poster, and background from the list
        2.  You can specify multiple producers in `tmdb_producer_details` but it will only use the first one to update the collection details
        3.  https://www.themoviedb.org/person/19292-adam-sandler also accepted

    === "Writer"

        Finds every item in the TMDb Person's Writer Credits.

        ### Example TMDb Writer Builder(s)

        ```yaml title="Press the + icon to learn more"
        collections:
          Woody Allen:
            tmdb_writer: 
                - 1243 #(3)!
          The Daniels::
            tmdb_writer_details: #(1)!
              - 1383612 #(2)!
              - https://www.themoviedb.org/person/1317730
        ```
    
        1.  You can replace `tmdb_writer` with `tmdb_writer_details` if you would like to fetch and use the TMDb collection's summary, poster, and background from the list
        2.  You can specify multiple people in `tmdb_writer_details` but it will only use the first one to update the collection details
        3.  https://www.themoviedb.org/person/1243-woody-allen also accepted

