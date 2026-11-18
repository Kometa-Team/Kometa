# TMDb Discover Movies

Find movies using filters in `tmdb_discover`. For direct IDs, charts, or people, see [TMDb builders](../builders.md).

## Quick start

```yaml
collections:
  Popular Movies:
    collection_order: custom
    sync_mode: sync
    tmdb_discover:
      sort_by: popularity.desc
      limit: 100
```

Use `collection_order: custom` to preserve the query's order and `sync_mode: sync`
to keep collection membership synchronized as results change.

## Value types

- **String:** text, codes, or IDs. Quote values containing separators, such as `"18,35"`.
- **Integer / Number:** a positive whole number / a positive whole or decimal number.
- **Boolean:** `true` or `false`.
- **Date / Year:** `MM/DD/YYYY` / a four-digit year, such as `2020`.

### Ranges and multiple values

`.gte` means **greater than or equal to** (minimum); `.lte` means **less than or equal to**
(maximum). Use either bound on its own or both for an inclusive range.

For filters marked **AND/OR**, join values with a comma for **all** or a pipe for **any**:

`with_genres: "18,35"` requires both genres; `with_genres: "18|35"` accepts either.
Filters marked **comma** accept comma-separated IDs. These are string values, not YAML lists.

## Discover attributes

All attributes below belong under `tmdb_discover:`. Only movie attributes are listed here;
see [Discover shows](show.md) for the other media type.

### Results and ordering

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `limit` | Integer | Maximum results; default `100`. |
| `sort_by` | Sort option | Result order; default `popularity.desc`. See [sort options](#sort-options). |
| `region` | Country code | Uppercase two-letter ISO 3166-1 code for release dates; defaults to the region in [TMDb configuration](../../../../config/tmdb.md). |

### Release dates

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `primary_release_year` | Year | Primary release year. |
| `primary_release_date.gte` | Date | Earliest primary release date. |
| `primary_release_date.lte` | Date | Latest primary release date. |
| `year` | Year | Release year, considering all release dates. |
| `release_date.gte` | Date | Earliest release (all release dates) date. |
| `release_date.lte` | Date | Latest release (all release dates) date. |
| `with_release_type` | String, AND/OR | `1`: Premiere; `2`: Theatrical (limited); `3`: Theatrical; `4`: Digital; `5`: Physical; `6`: TV. |

### Ratings and runtime

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `vote_count.gte` | Integer | Minimum vote count. |
| `vote_count.lte` | Integer | Maximum vote count. |
| `vote_average.gte` | Number | Minimum average rating. |
| `vote_average.lte` | Number | Maximum average rating. |
| `with_runtime.gte` | Integer | Minimum movie runtime in minutes. |
| `with_runtime.lte` | Integer | Maximum movie runtime in minutes. |

### Certification and content

Use `certification_country` with exact or ranged certification filters.

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `certification_country` | String | Country used to interpret certification filters. |
| `certification` | String | Exact certification; use with `certification_country`. |
| `certification.gte` | String | Minimum certification. |
| `certification.lte` | String | Maximum certification. |
| `include_adult` | Boolean | Include or exclude adult titles. |
| `include_video` | Boolean | Include or exclude videos. |

### People and companies

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `with_cast` | IDs, AND/OR | People credited as actors. |
| `with_crew` | IDs, AND/OR | People credited as crew. |
| `with_people` | IDs, AND/OR | People credited as actors or crew. |
| `with_companies` | IDs, AND/OR | Include production companies. |
| `without_companies` | IDs, AND/OR | Exclude production companies. |

### Genres, keywords, and language

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `with_genres` | IDs, AND/OR | Include genres. |
| `without_genres` | IDs, comma | Exclude genres. |
| `with_keywords` | IDs, AND/OR | Include keywords. |
| `without_keywords` | IDs, AND/OR | Exclude keywords. |
| `with_origin_country` | String | Original country. |
| `with_original_language` | String | Original language as an ISO 639-1 code, such as `en`. |

### Streaming availability

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `with_watch_providers` | IDs, AND/OR | Include streaming providers; use with `watch_region`. |
| `without_watch_providers` | IDs | Exclude streaming providers. |
| `watch_region` | String | Two-letter ISO 3166-1 country code, such as `GB`, for provider availability. |
| `with_watch_monetization_types` | String, AND/OR | Availability type: `flatrate`, `free`, `ads`, `rent`, or `buy`; use with `watch_region`. |

## Sort options

Append `.asc` for ascending or `.desc` for descending order, such as
`vote_average.desc`. The default is `popularity.desc`.

| Sort field | Orders by |
|:-----------|:----------|
| `popularity` | Popularity |
| `title` | Title |
| `original_title` | Original title |
| `revenue` | Revenue |
| `release_date` | Release date |
| `primary_release_date` | Primary release date |
| `vote_average` | Average rating |
| `vote_count` | Vote count |

## Examples {#example-tmdb-discover-builders}

Each tab demonstrates a different value type or filter combination. All examples are complete collection definitions.

=== "Dates"

    Finds movies whose primary release date falls within October 2020, including both boundary dates. The two date values form an inclusive range.

    ```yaml
    collections:
      Movies Released in October 2020:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          primary_release_date.gte: 10/01/2020
          primary_release_date.lte: 10/31/2020
    ```

=== "Strings and booleans"

    Finds English-language movies, excluding adult titles, ordered by popularity. `"en"` is a string; `false` is a boolean, so it is not quoted.

    ```yaml
    collections:
      Popular English-Language Movies:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_original_language: "en"
          include_adult: false
          sort_by: popularity.desc
    ```

=== "Years and numbers"

    Finds dramas with a primary release year of 2014, an average rating of at least 7.5, and at least 100 votes, highest rated first. `2014` is a year, `7.5` is a decimal number, and `100` is an integer.

    ```yaml
    collections:
      Top Rated Dramas From 2014:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_genres: 18
          primary_release_year: 2014
          vote_average.gte: 7.5
          vote_count.gte: 100
          sort_by: vote_average.desc
    ```

=== "AND / OR"

    Both collections use person IDs for Brad Pitt (`287`) and Edward Norton (`819`), ordered by rating. The comma requires **both** people; the pipe accepts **either** person. `with_people` matches acting or crew credits. Keep these multi-value strings quoted.

    ```yaml
    collections:
      Movies with Brad Pitt and Edward Norton:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_people: "287,819"
          sort_by: vote_average.desc

      Movies with Brad Pitt or Edward Norton:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_people: "287|819"
          sort_by: vote_average.desc
    ```

For the upstream API reference, see [TMDb Discover movies](https://developer.themoviedb.org/reference/discover-movie).
