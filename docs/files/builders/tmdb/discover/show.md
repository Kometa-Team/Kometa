# TMDb Discover Shows

Find shows using filters in `tmdb_discover`. For direct IDs, charts, or people, see [TMDb builders](../builders.md).

## Quick start

```yaml
collections:
  Popular Shows:
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

All attributes below belong under `tmdb_discover:`. Only show attributes are listed here;
see [Discover movies](movie.md) for the other media type.

### Results and ordering

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `limit` | Integer | Maximum results; default `100`. |
| `sort_by` | Sort option | Result order; default `popularity.desc`. See [sort options](#sort-options). |

### Air dates

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `air_date.gte` | Date | Earliest episode air date. |
| `air_date.lte` | Date | Latest episode air date. |
| `first_air_date.gte` | Date | Earliest original air date. |
| `first_air_date.lte` | Date | Latest original air date. |
| `first_air_date_year` | Year | Original air year. |
| `include_null_first_air_dates` | Boolean | Include shows without an air date when using first-air-date filters. |
| `timezone` | String | Timezone for `air_date` filters; default `America/New_York`. |

### Ratings and runtime

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `vote_count.gte` | Integer | Minimum vote count. |
| `vote_count.lte` | Integer | Maximum vote count. |
| `vote_average.gte` | Number | Minimum average rating. |
| `vote_average.lte` | Number | Maximum average rating. |
| `with_runtime.gte` | Integer | Minimum episode runtime in minutes. |
| `with_runtime.lte` | Integer | Maximum episode runtime in minutes. |

### Networks and companies

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `with_networks` | IDs, comma | Include networks. |
| `with_companies` | IDs, AND/OR | Include production companies. |
| `without_companies` | IDs, AND/OR | Exclude production companies. |

### Genres, keywords, and language

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `with_genres` | IDs, AND/OR | Include genres. |
| `without_genres` | IDs, comma | Exclude genres. |
| `with_keywords` | IDs, AND/OR | Include keywords. |
| `without_keywords` | IDs, AND/OR | Exclude keywords. |
| `with_original_language` | String | Original language as an ISO 639-1 code, such as `en`. |
| `with_name_translation` | String | Require a name translation; see [translation codes](#translation-codes). |

### Status, type, and content

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `with_status` | String, AND/OR | `0`: Returning Series; `1`: Planned; `2`: In Production; `3`: Ended; `4`: Cancelled; `5`: Pilot. |
| `with_type` | String, AND/OR | `0`: Documentary; `1`: News; `2`: Miniseries; `3`: Reality; `4`: Scripted; `5`: Show; `6`: Video. |
| `include_adult` | Boolean | Include or exclude adult titles. |
| `screened_theatrically` | Boolean | Include titles screened theatrically. |

### Streaming availability

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `with_watch_providers` | IDs, AND/OR | Include streaming providers; use with `watch_region`. |
| `without_watch_providers` | IDs | Exclude streaming providers. |
| `watch_region` | String | Two-letter ISO 3166-1 country code, such as `GB`, for provider availability. |
| `with_watch_monetization_types` | String, AND/OR | Availability type: `flatrate`, `free`, `ads`, `rent`, or `buy`; use with `watch_region`. |

??? info "Translation codes"

    <span id="translation-codes"></span>

    `ar-AE`, `ar-SA`, `bg-BG`, `bn-BD`, `ca-ES`, `ch-GU`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-US`, `eo-EO`, `es-ES`, `es-MX`, `eu-ES`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ka-GE`, `kn-IN`, `ko-KR`, `lt-LT`, `ml-IN`, `nb-NO`, `nl-NL`, `no-NO`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sl-SI`, `sr-RS`, `sv-SE`, `ta-IN`, `te-IN`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-TW`

## Sort options

Append `.asc` for ascending or `.desc` for descending order, such as
`vote_average.desc`. The default is `popularity.desc`.

| Sort field | Orders by |
|:-----------|:----------|
| `popularity` | Popularity |
| `name` | Name |
| `original_name` | Original name |
| `first_air_date` | First air date |
| `vote_average` | Average rating |
| `vote_count` | Vote count |

## Examples {#example-tmdb-discover-builders}

Each tab demonstrates a different value type or filter combination. All examples are complete collection definitions.

=== "Dates"

    Finds shows whose first air date falls within October 2020, including both boundary dates. This filters the show premiere, rather than individual episode air dates.

    ```yaml
    collections:
      Shows First Aired in October 2020:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          first_air_date.gte: 10/01/2020
          first_air_date.lte: 10/31/2020
    ```

=== "Strings and booleans"

    Finds English-language shows, excluding adult titles, ordered by popularity. `"en"` is a string; `false` is an unquoted boolean.

    ```yaml
    collections:
      Popular English-Language Shows:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_original_language: "en"
          include_adult: false
          sort_by: popularity.desc
    ```

=== "Years and numbers"

    Finds dramas first aired in 2020 with an average rating of at least 7.5 and at least 100 votes, highest rated first. `2020` is a year, `7.5` is a decimal number, and `100` is an integer.

    ```yaml
    collections:
      Top Rated Dramas From 2020:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_genres: 18
          first_air_date_year: 2020
          vote_average.gte: 7.5
          vote_count.gte: 100
          sort_by: vote_average.desc
    ```

=== "AND / OR"

    Both collections use genre IDs for drama (`18`) and comedy (`35`). The comma requires **both** genres; the pipe accepts **either** genre. Results are ordered by popularity. Keep these multi-value strings quoted.

    ```yaml
    collections:
      Drama Comedies:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_genres: "18,35"
          sort_by: popularity.desc

      Dramas or Comedies:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_genres: "18|35"
          sort_by: popularity.desc
    ```

=== "Streaming region"

    Finds shows available through Disney+ (provider ID `337`) in the United Kingdom. `watch_region: "GB"` selects the provider availability region; it does not filter the show's country of origin.

    ```yaml
    collections:
      Streaming on Disney+ in the UK:
        collection_order: custom
        sync_mode: sync
        tmdb_discover:
          with_watch_providers: 337
          watch_region: "GB"
    ```

For the upstream API reference, see [TMDb Discover shows](https://developer.themoviedb.org/reference/discover-tv).
