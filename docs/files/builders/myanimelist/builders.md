# MyAnimeList Builders

Collect anime from [MyAnimeList](https://myanimelist.net/) charts, searches,
seasons, user lists, and recommendations. All builders support movie and show
libraries. All except `mal_id` support playlists and custom sorting.

!!! warning "Configure MyAnimeList first"

    Every builder requires [MyAnimeList configuration](../../../config/myanimelist.md).
    Suggested anime and `"@me"` user lists use the authorized account.

## Choose a builder

| Builder | Finds |
|:--------|:------|
| [`mal_id`](#myanimelist-id) | Specific anime |
| [Chart builders](#charts-and-rankings) | Ranked, popular, favorited, airing, or upcoming anime |
| [`mal_search`](#myanimelist-search) | Anime matching detailed filters |
| [`mal_season`](#myanimelist-seasonal) | Anime from a selected season |
| [`mal_suggested`](#myanimelist-suggested) | Recommendations for the authorized user |
| [`mal_userlist`](#myanimelist-userlist) | A user's list, optionally filtered by status |

For all except `mal_id`, use `collection_order: custom` to preserve returned
order and `sync_mode: sync` to keep membership synchronized.

## Specific IDs {#myanimelist-id}

Accepts MyAnimeList anime IDs as a YAML list or comma-separated string.

<span id="example-myanimelist-id-builders"></span>

Selects the two Cowboy Bebop entries. These are numeric IDs, rather than result
limits. A quoted string such as `"23,219"` is also accepted.

```yaml
collections:
  Cowboy Bebop:
    mal_id:
      - 23
      - 219
```

## Charts and rankings

Each builder takes an integer result count, up to **500**.

| Builder | Chart |
|:--------|:------|
| <span id="myanimelist-top-airing"></span>`mal_airing` | [Top airing](https://myanimelist.net/topanime.php?type=airing) |
| <span id="myanimelist-top-all"></span>`mal_all` | [Top all anime](https://myanimelist.net/topanime.php) |
| <span id="myanimelist-most-favorited"></span>`mal_favorite` | [Most favorited](https://myanimelist.net/topanime.php?type=favorite) |
| <span id="myanimelist-top-movies"></span>`mal_movie` | [Top movies](https://myanimelist.net/topanime.php?type=movie) |
| <span id="myanimelist-top-ova-series"></span>`mal_ova` | [Top OVA series](https://myanimelist.net/topanime.php?type=ova) |
| <span id="myanimelist-most-popular"></span>`mal_popular` | [Most popular](https://myanimelist.net/topanime.php?type=bypopularity) |
| <span id="myanimelist-top-specials"></span>`mal_special` | [Top specials](https://myanimelist.net/topanime.php?type=special) |
| <span id="myanimelist-top-tv-series"></span>`mal_tv` | [Top TV series](https://myanimelist.net/topanime.php?type=tv) |
| <span id="myanimelist-top-upcoming"></span>`mal_upcoming` | [Top upcoming](https://myanimelist.net/topanime.php?type=upcoming) |

<span id="example-myanimelist-top-airing-builders"></span>
<span id="example-myanimelist-top-all-builders"></span>
<span id="example-myanimelist-most-favorited-builders"></span>
<span id="example-myanimelist-top-movies-builders"></span>
<span id="example-myanimelist-top-ova-series-builders"></span>
<span id="example-myanimelist-most-popular-builders"></span>
<span id="example-myanimelist-top-specials-builders"></span>
<span id="example-myanimelist-top-tv-series-builders"></span>
<span id="example-myanimelist-top-upcoming-builders"></span>

Selects up to 30 entries from the overall top-anime chart in returned order.
Replace `mal_all` with another chart builder to use that chart instead.

```yaml
collections:
  Top 30 Anime:
    mal_all: 30
    collection_order: custom
    sync_mode: sync
```

## Search {#myanimelist-search}

`mal_search` requires at least one attribute. Options belong beneath the builder.

### Results and title filters

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `limit` | Integer | Maximum anime to query |
| `sort_by` | Sort option below | Result order |
| `query` | String | Text query |
| `prefix` | String | Required beginning of the result title |
| `type` | `tv`, `movie`, `ova`, `special`, `ona`, `music` | Anime format |
| `status` | `airing`, `complete`, `upcoming` | Airing status |
| `content_rating` | `g`, `pg`, `pg13`, `r17`, `r`, `rx` | Content rating |
| `sfw` | `true` | Require safe-for-work results |

### Genres, studios, and scores

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `genre` | Genre name or ID string | Include genres |
| `genre.not` | Genre name or ID string | Exclude genres |
| `studio` | Studio name or ID string | Include studios |
| `score.gt`, `score.gte` | Number, 0.00-10.00 | Minimum score, exclusive / inclusive |
| `score.lt`, `score.lte` | Number, 0.00-10.00 | Maximum score, exclusive / inclusive |

For genre and studio strings, commas mean **AND** and pipes mean **OR**. Quote
multi-value strings: `genre: "Action,Comedy"` requires both; `genre: "Action|Comedy"`
accepts either. This also applies to `genre.not` exclusions.

Find names and IDs on [MyAnimeList search](https://myanimelist.net/anime.php).
The number in a producer or genre URL is its ID: `/anime/producer/4/Bones` uses
studio ID `4`; `/anime/genre/1/Action` uses genre ID `1`.

### Search sorting

Append `.asc` or `.desc` to a field below, such as `score.desc` for highest score first.

`mal_id`, `title`, `type`, `rating`, `start_date`, `end_date`, `episodes`, `score`,
`scored_by`, `rank`, `popularity`, `members`, `favorites`.

<span id="example-myanimelist-search-builders"></span>

=== "Numbers and boolean"

    Selects up to 100 action anime scoring at least 7.5, highest scores first,
    requiring safe-for-work results. `7.5` is a decimal score, `100` is an integer
    limit, and `true` is a boolean.

    ```yaml
    collections:
      Highly Rated Action Anime:
        mal_search:
          genre: Action
          score.gte: 7.5
          sfw: true
          sort_by: score.desc
          limit: 100
        collection_order: custom
        sync_mode: sync
    ```

=== "AND / OR"

    The first collection requires both Action and Comedy; the second accepts
    either. Both strings are quoted. Only the separator changes the matching.

    ```yaml
    collections:
      Action Comedies:
        mal_search:
          genre: "Action,Comedy"
          sort_by: score.desc
          limit: 50
        collection_order: custom
        sync_mode: sync

      Action or Comedy:
        mal_search:
          genre: "Action|Comedy"
          sort_by: score.desc
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```

## Seasonal anime {#myanimelist-seasonal}

Selects anime from [MyAnimeList's seasonal lists](https://myanimelist.net/anime/season).

| Attribute | Value | Default |
|:----------|:------|:--------|
| `season` | `winter`, `spring`, `summer`, `fall`, `current` | `current` |
| `year` | Integer, 1917 through the current year | Current year |
| `sort_by` | `members`, `score` | `members` |
| `limit` | Integer, maximum 500 | `100` |
| `starting_only` | Boolean; only anime beginning in that season | `false` |

Season months are January-March for winter, April-June for spring,
July-September for summer, and October-December for fall.
Seasonal score sorting has a [reported issue](https://myanimelist.net/forum/?topicid=2030371).

<span id="example-myanimelist-seasonal-builders"></span>

Selects up to 50 anime that **began** airing in fall 2020, ordered by members.
`starting_only: true` excludes titles merely continuing through the season.
Omit season and year to use the current season and year.

```yaml
collections:
  New Fall 2020 Anime:
    mal_season:
      season: fall
      year: 2020
      starting_only: true
      sort_by: members
      limit: 50
    collection_order: custom
    sync_mode: sync
```

## Suggested anime {#myanimelist-suggested}

<span id="example-myanimelist-suggested-builders"></span>

Selects up to 20 recommendations for the authorized user. `mal_suggested` takes
an integer result count, with a maximum of **100**.

```yaml
collections:
  Suggested Anime:
    mal_suggested: 20
    collection_order: custom
    sync_mode: sync
```

## User lists {#myanimelist-userlist}

Only `username` is required. Quote `"@me"` to select the authorized account.

| Attribute | Value | Default |
|:----------|:------|:--------|
| `username` | Username string or `"@me"`, required | - |
| `status` | `all`, `watching`, `completed`, `on_hold`, `dropped`, `plan_to_watch` | `all` |
| `sort_by` | `score`, `last_updated`, `title`, `start_date` | `score` |
| `limit` | Integer, maximum 1000 | `100` |

<span id="example-myanimelist-userlist-builders"></span>

Selects up to 500 entries from the authorized account's Currently Watching list,
ordered by score. Use another username string to select that user's list instead.

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
