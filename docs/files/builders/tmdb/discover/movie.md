---
hide:
  - toc
---
# TMDb Discover (Movies)

Uses [TMDb's Discover Search](https://developer.themoviedb.org/docs/search-and-query-for-details) to find every movie based on the [movie search attributes](https://developers.themoviedb.org/3/discover/movie-discover) provided.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.
 
???+ important 

    Note that a number of filters support being comma (,) or pipe (|) separated. Commas are treated like an AND query 
    while pipes are treated like an OR. This allows for quite complex filtering depending on your desired results.

## Value Types

These are the types of values you can use in your TMDb Discover queries. The type and formatting of attributes such as date and year is important to know when building your queries.

| Type               | Description                                       |
|:-------------------|:--------------------------------------------------|
| String             | Any number of alphanumeric characters             |
| Integer            | Any whole number greater than zero i.e. 2, 10, 50 |
| Number             | Any number greater than zero i.e. 2.5, 7.4, 9     |
| Boolean            | Must be `true` or `false`                         |
| Date: `MM/DD/YYYY` | Date that fits the specified format               |
| Year: `YYYY`       | Year must be a 4 digit integer i.e. 1990          |

## Discover Attributes

| Attribute                       | Description                                                                                                                                                                                                                                                                                                                               |
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
| `with_cast`                     | A comma-separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of person ID's. Only include movies that have one of the ID's added as an actor.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                 |
| `with_crew`                     | A comma-separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of person ID's. Only include movies that have one of the ID's added as a crew member.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                            |
| `with_people`                   | A comma-separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of person ID's. Only include movies that have one of the ID's added as either an actor or a crew member.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                         |
| `with_companies`                | A comma-separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of production company ID's. Only include movies that have one of the ID's added as a production company.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                         |
| `without_companies`             | Filter the results to exclude the specific production companies you specify here. AND / OR filters are supported.<br>**Type:** String                                                                                                                                                                                                     |
| `with_genres`                   | Comma-separated value of genre ids that you want to include in the results.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                             |
| `without_genres`                | Comma-separated value of genre ids that you want to exclude from the results.<br>**Type:** String                                                                                                                                                                                                                                         |
| `with_keywords`                 | A comma-separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of keyword ID's. Only includes movies that have one of the ID's added as a keyword.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                              |
| `without_keywords`              | Exclude items with certain keywords. You can comma and pipe separate these values to create an 'AND' or 'OR' logic.<br>**Type:** String                                                                                                                                                                                                   |
| `with_runtime.gte`              | Filter and only include movies that have a runtime that is greater or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                              |
| `with_runtime.lte`              | Filter and only include movies that have a runtime that is less than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                            |
| `with_origin_country`           | Specify an origin country string to filter results by their original country value.<br>**Type:** String                                                                                                                                                                                                                                   |
| `with_original_language`        | Specify an ISO 639-1 string to filter results by their original language value.<br>**Type:** String                                                                                                                                                                                                                                       |
| `with_watch_providers`          | A comma or pipe separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of watch provider ID's.<br>use in conjunction with watch_region, can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                            |
| `without_watch_providers`       | Filter the results to exclude certain watch providers.<br>**Type:** String                                                                                                                                                                                                                                                                |
| `watch_region`                  | An [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes). Combine this filter with `with_watch_providers` in order to filter your results by a specific watch provider in a specific region.<br>**Type:** String<br>**Values:** [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) |
| `with_watch_monetization_types` | In combination with `watch_region`, you can filter by monetization type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `flatrate`, `free`, `ads`, `rent`, `buy`                                                                                                        |


## Sort Options

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

