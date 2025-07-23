---
hide:
  - toc
---
# TMDb Discover (Shows)

Uses [TMDb's Discover Search](https://developer.themoviedb.org/docs/search-and-query-for-details) to find every show based on the [show search attributes](https://developers.themoviedb.org/3/discover/show-discover) provided.

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
| `with_companies`                | A comma-separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of production company ID's. Only include movies that have one of the ID's added as a production company.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                          |
| `without_companies`             | Filter the results to exclude the specific production companies you specify here. AND / OR filters are supported.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `with_genres`                   | Comma-separated value of genre ids that you want to include in the results.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `without_genres`                | Comma-separated value of genre ids that you want to exclude from the results.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `with_keywords`                 | A comma-separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of keyword ID's. Only includes TV shows that have one of the ID's added as a keyword.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                             |
| `without_keywords`              | Exclude items with certain keywords. You can comma and pipe separate these values to create an 'AND' or 'OR' logic.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `with_runtime.gte`              | Filter and only include TV shows with an episode runtime that is greater than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `with_runtime.lte`              | Filter and only include TV shows with an episode runtime that is less than or equal to a value.<br>**Type:** Integer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `with_original_language`        | Specify an ISO 639-1 string to filter results by their original language value.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `with_name_translation`         | Specify a language/country string to filter the results by if the item has a type of name translation.<br>**Type:** String<br>**Values:** `ar-AE`, `ar-SA`, `bg-BG`, `bn-BD`, `ca-ES`, `ch-GU`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-US`, `eo-EO`, `es-ES`, `es-MX`, `eu-ES`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ka-GE`, `kn-IN`, `ko-KR`, `lt-LT`, `ml-IN`, `nb-NO`, `nl-NL`, `no-NO`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sl-SI`, `sr-RS`, `sv-SE`, `ta-IN`, `te-IN`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-TW` |
| `screened_theatrically`         | Filter results to include items that have been screened theatrically.<br>**Type:** Boolean                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `with_watch_providers`          | A comma or pipe separated list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of watch provider ID's.<br>use in conjunction with watch_region, can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                             |
| `without_watch_providers`       | Filter the results to exclude certain watch providers.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `watch_region`                  | An [ISO 3166-1 code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes). Combine this filter with `with_watch_providers` in order to filter your results by a specific watch provider in a specific region.<br>**Type:** String                                                                                                                                                                                                                                                                                                                                                                 |
| `with_watch_monetization_types` | In combination with `watch_region`, you can filter by monetization type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `flatrate`, `free`, `ads`, `rent`, `buy`                                                                                                                                                                                                                                                                                                                                                                         |
| `with_status`                   | Filter TV shows by their status.<br>**Type:** String<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Values:** `0`: Returning Series, `1`: Planned, `2`: In Production, `3`: Ended, `4`: Cancelled, `5`: Pilot                                                                                                                                                                                                                                                                                                                                                          | 
| `with_type`                     | Filter TV shows by their type.<br>Can be a comma (`,`) for an AND, or a pipe (`|`) for an OR separated query<br>**Type:** String<br>**Values:** `0`: Documentary, `1`: News, `2`: Miniseries, `3`: Reality, `4`: Scripted, `5`: Show, `6`: Video                                                                                                                                                                                                                                                                                                                                                           |


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
  Shows Released in October 2020:
    tmdb_discover:
      first_air_date.gte: 10/01/2020
      first_air_date.lte: 10/31/2020
```
```yaml
collections:
  100 Most Popular Shows:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      sort_by: popularity.desc
      limit: 100
```
```yaml
collections:
  Highest Rated TV-MA Shows:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      certification_country: US
      certification: TV-MA
      sort_by: vote_average.desc
```
```yaml
collections:
  Most Popular Kids Shows:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      certification_country: US
      certification.lte: TV-G
      sort_by: popularity.desc
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
  Streaming on Disney+ in UK:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      with_watch_providers: 337
      region: GB
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

