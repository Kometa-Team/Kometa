# BoxOfficeMojo Builders

Collect movies from [BoxOfficeMojo](https://www.boxofficemojo.com/) box office
charts and records. All builders below support **movies, playlists, and custom
sorting**; they do not support shows.

## Choose a builder

| Builder | Finds |
|:--------|:------|
| [`mojo_domestic`](#boxofficemojo-domestic) | Domestic box office for a time period |
| [`mojo_international`](#boxofficemojo-international) | International or country-specific box office for a time period |
| [`mojo_world`](#boxofficemojo-worldwide) | Worldwide box office for a year |
| [`mojo_all_time`](#boxofficemojo-all-time) | All-time domestic or worldwide grosses |
| [`mojo_never`](#boxofficemojo-never-hit) | Grosses for movies that never reached a chart position |
| [`mojo_record`](#boxofficemojo-other-records) | Opening, daily, weekend, and other records |

## Shared options and value types

Each builder takes a **dictionary**: place its options beneath the builder name,
as shown in the examples. There are no boolean or AND/OR filters on this page.

| Option | Applies to | Value and behaviour |
|:-------|:-----------|:--------------------|
| `limit` | All builders | Positive integer, such as `10`; omit to return all results. |
| `year` | Domestic, International, Worldwide | A year from `1977` through the current year, `current`, or `current-#` for a relative year. Domestic ignores it for `range: daily`. |

For Domestic and International, `year` defaults to `current`. In a `year` value,
`current-1` means last year. In a supported `range_data` value, `current-1` means
**one day ago**, not one month or one year ago.

Named values, such as `worldwide`, `monthly`, and `current-1`, are strings.
Years, week numbers, limits, and the `never` threshold use integers where shown.

## Domestic and international periods

Domestic and International share these options:

| Option | Purpose |
|:-------|:--------|
| `range` | Select a period from the table below. |
| `range_data` | Select the date, week, month, quarter, season, or holiday. Required except for `yearly`. |
| `year` | Select the year; see [shared options](#shared-options-and-value-types). |
| `limit` | Cap results; see [shared options](#shared-options-and-value-types). |

### Period values {#allowed-values-for-range_data}

<span id="boxofficemojo-international-allowed-values-for-range_data"></span>

| `range` | `range_data` | Available for |
|:--------|:-------------|:--------------|
| `daily` | Date as `MM-DD-YYYY`, `current`, or `current-#` | Domestic |
| `weekend`, `weekly` | Week number `1`-`53`, `current`, or `current-#` | Both for `weekend`; Domestic for `weekly` |
| `monthly` | Lowercase month name (`january` through `december`), `current`, or `current-#` | Both |
| `quarterly` | `q1`, `q2`, `q3`, `q4`, `current`, or `current-#` | Both |
| `yearly` | Omit `range_data` | Both |
| `season` | `winter`, `spring`, `summer`, `fall`, `holiday`, or `current` | Domestic |
| `holiday` | A holiday value from the list below | Domestic |

For supported relative `range_data` values, `#` is the number of days before today.
Use a named month and explicit year when you want a specific historical month.

??? info "Holiday values"

    `new_years_day`, `new_year_weekend`, `mlk_day`, `mlk_day_weekend`, `presidents_day`, `presidents_day_weekend`, `easter`, `easter_weekend`, `memorial_day`, `memorial_day_weekend`, `independence_day`, `independence_day_weekend`, `labor_day`, `labor_day_weekend`, `indigenous_day`, `indigenous_day_weekend`, `halloween`, `thanksgiving`, `thanksgiving_3`, `thanksgiving_4`, `thanksgiving_5`, `post_thanksgiving_weekend`, `christmas_day`, `christmas_weekend`, `new_years_eve`

### Domestic {#boxofficemojo-domestic}

<span id="boxofficemojo-domestic-builder-attributes"></span>
<span id="example-mojo-domestic-builders"></span>

=== "Relative year"

    Selects up to 20 movies from last year's domestic box office.
    `current-1` is a relative-year string; `20` is an integer limit.

    ```yaml
    collections:
      Last Year's Top 20 Domestic Movies:
        mojo_domestic:
          range: yearly
          year: current-1
          limit: 20
    ```

=== "Specific day"

    Selects up to 10 movies from the domestic chart for July 4, 2020.
    Daily dates use `MM-DD-YYYY`; a separate `year` would be ignored.

    ```yaml
    collections:
      Domestic Box Office on July 4 2020:
        mojo_domestic:
          range: daily
          range_data: 07-04-2020
          limit: 10
    ```

### International {#boxofficemojo-international}

<span id="boxofficemojo-international-builder-attributes"></span>

International also accepts `chart`, defaulting to `international`. Choose a
country chart from the dropdown on [BoxOfficeMojo's international page](https://www.boxofficemojo.com/intl/).

<span id="example-mojo-international-builders"></span>

Selects the top 10 movies from Germany's box office for March 2020.
`germany` and `march` are named strings; `2020` selects the year explicitly.
Omit `chart` to use the international chart instead.

```yaml
collections:
  Top 10 German Movies in March 2020:
    mojo_international:
      range: monthly
      range_data: march
      chart: germany
      year: 2020
      limit: 10
```

## Worldwide {#boxofficemojo-worldwide}

Use `mojo_world` with `year` to select the [worldwide box office](https://www.boxofficemojo.com/year/world/).
It accepts the shared `year` and `limit` options, without `range` or `range_data`.

<span id="boxofficemojo-worldwide-builder-attributes"></span>
<span id="example-mojo-worldwide-builders"></span>

Selects the top 10 movies from the 2020 worldwide chart. Replace `2020` with
`current` to follow the current year's chart, or `current-1` for last year.

```yaml
collections:
  Top 10 Worldwide Movies in 2020:
    mojo_world:
      year: 2020
      limit: 10
```

## All-time grosses {#boxofficemojo-all-time}

Use `mojo_all_time` for [all-time charts](https://www.boxofficemojo.com/charts/overall/).

<span id="builder-attributes"></span>

| Option | Allowed values | Purpose |
|:-------|:---------------|:--------|
| `chart` | `domestic`, `worldwide` | Select the chart. |
| `content_rating_filter` | `g`, `g/pg`, `pg`, `pg-13`, `r`, `nc-17` | Filter by content rating. |

The shared `limit` option also applies.

<span id="example-mojo-all-time-builders"></span>

=== "Worldwide"

    Selects the top 100 movies by all-time worldwide gross, without a content-rating filter.

    ```yaml
    collections:
      Top 100 Worldwide All-Time Grosses:
        mojo_all_time:
          chart: worldwide
          limit: 100
    ```

=== "Content rating"

    Selects the top 10 G-rated movies by all-time domestic gross.
    `g` is a rating string; `10` is an integer limit.

    ```yaml
    collections:
      Top 10 G-Rated Domestic All-Time Grosses:
        mojo_all_time:
          chart: domestic
          content_rating_filter: g
          limit: 10
    ```

## Never-hit charts {#boxofficemojo-never-hit}

Use `mojo_never` for the Never Hit lists in the lower section of
[BoxOfficeMojo's overall charts](https://www.boxofficemojo.com/charts/overall/).

<span id="boxofficemojo-never-hit-builder-attributes"></span>

| Option | Allowed values | Purpose |
|:-------|:---------------|:--------|
| `chart` | A chart from the overall page's dropdown | Select the market, such as `domestic` or `germany`. |
| `never` | `1`, `5`, `10` | Select the never-hit threshold; default `1`. |

The shared `limit` option also applies.

<span id="example-mojo-never-hit-builders"></span>

Selects up to 100 movies from the domestic "Never in the Top 10" chart.
`never: 10` is an integer threshold. Use `1`, or omit `never`, for the
"Never #1" chart instead.

```yaml
collections:
  Top 100 Domestic Movies Never in the Top 10:
    mojo_never:
      chart: domestic
      never: 10
      limit: 100
```

## Other records {#boxofficemojo-other-records}

Use `mojo_record` for [weekend](https://www.boxofficemojo.com/charts/weekend/),
[daily](https://www.boxofficemojo.com/charts/daily/), and
[miscellaneous records](https://www.boxofficemojo.com/charts/misc/).
Set `chart` to a record value below; the shared `limit` option also applies.

<span id="boxofficemojo-other-records-builder-attributes"></span>

??? info "Record values by category"

    | Category | `chart` values |
    |:---------|:---------------|
    | Opening and other records | `second_weekend_drop`, `post_thanksgiving_weekend_drop`, `top_opening_weekend`, `worst_opening_weekend_theater_avg`, `top_opening_weekend_theater_avg_all`, `top_opening_weekend_theater_avg_wide`, `opening_day`, `single_day_grosses`, `christmas_day_gross`, `new_years_day_gross`, `biggest_theater_drop`, `opening_week` |
    | Holiday records | `mlk_opening`, `easter_opening`, `memorial_opening`, `labor_opening`, `president_opening`, `thanksgiving_3_opening`, `thanksgiving_5_opening`, `mlk`, `easter`, `4th`, `memorial`, `labor`, `president`, `thanksgiving_3`, `thanksgiving_5` |
    | Months | `january`, `february`, `march`, `april`, `may`, `june`, `july`, `august`, `september`, `october`, `november`, `december` |
    | Seasons | `spring`, `summer`, `fall`, `holiday_season`, `winter` |
    | Content ratings | `g`, `g/pg`, `pg`, `pg-13`, `r`, `nc-17` |
    | Days of the week | `friday`, `saturday`, `sunday`, `monday`, `tuesday`, `wednesday`, `thursday`, `friday_non_opening`, `saturday_non_opening`, `sunday_non_opening`, `monday_non_opening`, `tuesday_non_opening`, `wednesday_non_opening`, `thursday_non_opening` |

<span id="example-mojo-other-records-builders"></span>

Selects the 10 biggest opening weekends. Replace `top_opening_weekend` with
`opening_day` for opening-day records, or `opening_week` for opening-week records.

```yaml
collections:
  Top 10 Biggest Opening Weekends:
    mojo_record:
      chart: top_opening_weekend
      limit: 10
```
