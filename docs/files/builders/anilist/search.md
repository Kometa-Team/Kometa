# AniList Advanced Search

Find anime with `anilist_search`. For IDs, relations, studios, charts, and named
user lists, see [AniList builders](builders.md). Searches support movie and show
libraries, playlists, and custom sorting.

## Quick start

Selects up to 20 sports anime, requesting popularity order. `Sports` is a genre
string and `20` is an integer limit.

```yaml
collections:
  Top Sports Anime:
    anilist_search:
      genre: Sports
      limit: 20
      sort_by: popular
    collection_order: custom
    sync_mode: sync
```

Use `collection_order: custom` to preserve returned order and `sync_mode: sync`
to keep membership synchronized as results change.

## Filter syntax

Each filter combines an attribute, an optional or required modifier, and a value:
for example, `episodes.gte: 12` sets an inclusive minimum episode count.

| Attribute group | Modifiers | Value format |
|:----------------|:----------|:-------------|
| [Special options](#special-options) | None | As listed below |
| [Dates](#date-attributes) | `.before`, `.after` | One date as `MM/DD/YYYY` |
| [Numbers](#number-attributes) | `.gt`, `.gte`, `.lt`, `.lte`, required | One number |
| [Tags](#tag-attributes) | None or `.not` | String, YAML list, or comma-separated string |

`.gt` / `.lt` mean strictly greater / less than; `.gte` / `.lte` include the
boundary. Date and number filters do not accept multiple values. Use `.not` to
exclude tag values. Keep booleans unquoted and quote comma-separated strings.

## Special options

These attributes do not support modifiers.

| Attribute | Value | Purpose / default |
|:----------|:------|:------------------|
| `sort_by` | `score`, `popular`, `trending` | Sort by average score, popularity, or trending; default `score` |
| `limit` | Integer, 0 or greater | Maximum anime; default `0` returns all, as does omitting it |
| `search` | String | Text search |
| `season` | `winter`, `spring`, `summer`, `fall`, `current` | Season; default `current` |
| `year` | Integer, 1917 through next year, or blank | Season year; defaults to the current year |
| `min_tag_percent` | Number, 0-100 | Minimum tag percentage |
| `adult` | Boolean | Search for or exclude adult anime |
| `country` | ISO 3166-1 alpha-2 code | Country to match |
| `source` | `original`, `manga`, `light_novel`, `visual_novel`, `video_game`, `other`, `novel`, `doujinshi`, `anime` | Original source material |

Season months are January-March for winter, April-June for spring,
July-September for summer, and October-December for fall.

## Date attributes

| Attribute | Matches |
|:----------|:--------|
| `start` | Anime start date |
| `end` | Anime end date |

Append `.before` or `.after`, such as `start.after: 01/01/2020`.

## Number attributes

| Attribute | Matches | Minimum |
|:----------|:--------|:--------|
| `duration` | Duration in minutes | `1` |
| `episodes` | Episode count | `1` |
| `score` | Score | `1` |
| `popularity` | Popularity | `1` |

Each requires `.gt`, `.gte`, `.lt`, or `.lte`. For example, `episodes.gte: 12`
and `episodes.lte: 26` together form an inclusive episode-count range.

## Tag attributes

| Attribute | Allowed values |
|:----------|:---------------|
| `format` | `tv`, `short`, `movie`, `special`, `ova`, `ona`, `music` |
| `status` | `finished`, `airing`, `not_yet_aired`, `cancelled`, `hiatus` |
| `genre` | Genre from the [AniList search dropdown](https://anilist.co/search/anime) |
| `tag` | Tag from the same dropdown |
| `tag_category` | Category from the Advanced Genres & Tag Filters menu |

Use the base attribute to match values or `.not` to exclude them, such as
`format.not: music`. Multiple values can be a YAML list or comma-separated string.

## Examples {#example-anilist-search-builders}

=== "Season and year"

    Finds anime for fall 2020, requesting popularity order. `fall` is a string
    and `2020` is a year integer. Use `season: current` and leave `year` blank
    to select the current season and year.

    ```yaml
    collections:
      Fall 2020 Anime:
        anilist_search:
          season: fall
          year: 2020
          sort_by: popular
        collection_order: custom
        sync_mode: sync
    ```

=== "Text and boolean"

    Searches for Naruto and excludes adult anime. `Naruto` is a text string;
    `false` is an unquoted boolean. The integer limit caps results at 20.

    ```yaml
    collections:
      Naruto Search:
        anilist_search:
          search: "Naruto"
          adult: false
          limit: 20
        collection_order: custom
        sync_mode: sync
    ```

=== "Dates and number range"

    Finds anime starting after January 1, 2020, with 12 through 26 episodes,
    excluding music-format entries. The start date uses `MM/DD/YYYY`; the episode
    limits are inclusive and `format.not` excludes a tag value.

    ```yaml
    collections:
      Recent Shorter Anime:
        anilist_search:
          start.after: 01/01/2020
          episodes.gte: 12
          episodes.lte: 26
          format.not: music
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```

=== "Tag and percentage"

    Searches the Pirates tag with a minimum tag percentage of 50, requesting
    popularity order. The tag is a string and the percentage is numeric.

    ```yaml
    collections:
      Pirates Anime:
        anilist_search:
          tag: Pirates
          min_tag_percent: 50
          sort_by: popular
          limit: 20
        collection_order: custom
        sync_mode: sync
    ```
