---
hide:
  - tags
tags:
  - actor
  - added
  - albums
  - aspect
  - audience_rating
  - audio_language
  - channels
  - collection
  - content_rating
  - country
  - critic_rating
  - director
  - dovi_level
  - dovi_profile
  - duration
  - episodes
  - first_episode_aired
  - genre
  - has_collection
  - has_dolby_vision
  - has_edition
  - has_overlay
  - has_stinger
  - height
  - history
  - imdb_keyword
  - label
  - last_episode_aired
  - last_episode_aired_or_never
  - last_played
  - network
  - origin_country
  - original_language
  - plays
  - producer
  - release
  - resolution
  - seasons
  - stinger_rating
  - subtitle_language
  - tmdb_genre
  - tmdb_keyword
  - tmdb_status
  - tmdb_type
  - tmdb_vote_average
  - tmdb_vote_count
  - tmdb_year
  - tracks
  - tvdb_genre
  - user_rating
  - versions
  - width
  - writer
  - year
---

# Filters

Use `filters` to narrow the items selected by builders for a collection, overlay,
or playlist. These are Kometa filters applied to builder results; they do not
create a live Plex smart collection.

!!! important "A builder is required"

    Filters do not select items on their own. Use at least one
    [builder](definition-components.md#builders), such as `plex_all: true` to
    start with your library, then apply filters to its results.

## Using filters

| Structure | Matching rule |
|:----------|:--------------|
| Several attributes in one dictionary | Every filter must pass (AND) |
| Multiple values for a filter that supports them | At least one value must match |
| YAML list of filter dictionaries | At least one complete set must pass (OR) |

Values must match Plex metadata, including special characters. String filters
accept multiple values **only as a YAML list**; tag filters also accept a
comma-separated string. Date and number filters accept one value per attribute.
Boolean filters take unquoted `true` or `false` with no modifier.

A filter combines an attribute, an optional modifier, and a value. For example,
`user_rating.gte: 7.5` requires a user rating greater than or equal to 7.5.
`.gt` / `.lt` exclude the boundary; `.gte` / `.lte` include it.

### Inspecting results

Set `show_filtered: true` on the definition to display rejected items, or
`show_unfiltered: true` to display items that pass. These are definition options,
not entries under `filters`.

!!! warning "Narrow candidates before filtering"

    Filters can be slow, especially on large libraries. Where possible, narrow
    the source with [Plex Search](builders/plex/search.md), a
    [smart label collection](settings.md#smart-label-definitions), or another
    [builder](definition-components.md#builders) before applying filters.

## Examples

=== "AND within a set"

    Includes only items with both Action and Germany in their Plex metadata.
    `plex_all` supplies candidates; the two string-valued tag filters must both pass.

    ```yaml
    collections:
      German Action Movies:
        plex_all: true
        filters:
          genre: Action
          country: Germany
    ```

=== "OR between sets"

    Includes either German action movies or French comedies. Each YAML list
    entry is a complete AND set; passing either set is enough.

    ```yaml
    collections:
      European Action and Comedy:
        plex_all: true
        filters:
          - genre: Action
            country: Germany
          - genre: Comedy
            country: France
    ```

=== "Multiple values"

    Includes movies matching Action or Comedy, and also requires a user rating
    of at least 7.5. The genre values form a YAML list; the rating is a decimal
    threshold. This differs from requiring both genres as separate conditions.

    ```yaml
    collections:
      My Highly Rated Action or Comedy:
        plex_all: true
        filters:
          genre:
            - Action
            - Comedy
          user_rating.gte: 7.5
    ```

=== "Boolean and dates"

    Includes movies with an edition, released after May 1 and before August 31,
    2020. `true` is a boolean, and explicit dates use `MM/DD/YYYY`. A relative
    filter such as `release: 180` instead selects releases in the last 180 days.

    ```yaml
    collections:
      Summer 2020 Movies With Editions:
        plex_all: true
        filters:
          has_edition: true
          release.after: 05/01/2020
          release.before: 08/31/2020
    ```

=== "String list and diagnostics"

    Includes movies whose audio-track titles contain Commentary or Director.
    String filters use contains matching by default, and multiple values must
    be a YAML list. `show_filtered` displays rejected items for inspection.

    ```yaml
    collections:
      Movies With Commentary:
        plex_all: true
        show_filtered: true
        filters:
          audio_track_title:
            - Commentary
            - Director
    ```

=== "Narrow before filtering"

    Starts with Romance movies featuring Adam Sandler, then keeps only those
    also tagged Comedy and user-rated at least 7. Using Plex Search reduces the
    candidate set before the Kometa filters run.

    ```yaml
    collections:
      My Highly Rated Adam Sandler Romantic Comedies:
        plex_search:
          all:
            genre: Romance
            actor: Adam Sandler
        filters:
          genre: Comedy
          user_rating.gte: 7
    ```

## Filter options

The reference below preserves the supported media for each attribute. "Child
items" notes identify filters evaluated through episodes or tracks for the
listed parent levels; see [child-item filters](#child-item-filters).

### Boolean filters {#boolean-filters}

Use unquoted `true` or `false`; no modifiers are supported.

<span id="boolean-filter-attributes"></span>

| Attribute | Matches / constraints | Supports |
|:----------|:----------------------|:---------|
| `has_collection` | Has / does not have collection | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `has_dolby_vision` | Has / does not have Dolby Vision<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `has_edition` | Has / does not have edition | Movies, Shows |
| `has_overlay` | Has / does not have overlay | Movies, Shows, Seasons, Episodes, Artists, Albums |
| `has_stinger` | Listed by [MediaStinger](http://www.mediastinger.com/) for a during/after-credits scene | Movies |

### Date filters {#date-filters}

Use one value; multiple dates are not supported.

| Modifier | Matches | Value |
|:---------|:--------|:------|
| No modifier | In the last X days | Number of days, such as `30` |
| `.not` | Not in the last X days | Number of days |
| `.before`, `.after` | Before / after a date | `MM/DD/YYYY` or `today` |
| `.regex` | Matches the date against a regular expression | Regex string |

<span id="date-filter-attributes"></span>

| Attribute | Matches / constraints | Supports |
|:----------|:----------------------|:---------|
| `added` | Date added | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `first_episode_aired` | First episode aired date<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `last_episode_aired_or_never` | Similar to `last_episode_aired` but also includes those that haven't aired yet<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `last_episode_aired` | Last episode aired date<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `last_played` | Date last played | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `release` | Original release date | Movies, Shows, Episodes, Albums |

### Number filters {#number-filters}

Use one number per attribute; multiple values are not supported. Rating values, counts, dimensions, and durations retain the constraints shown below.

| Modifier | Matches | Value |
|:---------|:--------|:------|
| No modifier, `.not` | Equal / not equal | One number |
| `.gt`, `.gte` | Greater than / greater than or equal | One number |
| `.lt`, `.lte` | Less than / less than or equal | One number |

<span id="number-filter-attributes"></span>

| Attribute | Matches / constraints | Supports |
|:----------|:----------------------|:---------|
| `aspect` | Aspect<br>minimum: 0.0<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `audience_rating` | Audience rating<br>0.0 - 10.0 | Movies, Shows, Episodes |
| `channels` | Audio channels<br>minimum: 0<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `critic_rating` | Critic rating<br>0.0 - 10.0 | Movies, Shows, Episodes, Albums |
| `duration` | Duration in minutes; minimum: `0` | Movies, Shows, Episodes, Tracks |
| `dovi_level` | Matches the Dolby Vision level reported by a video stream. Values: 1–13.<br>Use `plex_search` with `dovi: true` to narrow candidates first.<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `dovi_profile` | Matches the Dolby Vision profile reported by a video stream. Values: 5, 7, 8, 9, 10, 20.<br>Use `plex_search` with `dovi: true` to narrow candidates first.<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `height` | Height<br>minimum: 0<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `plays` | Plays<br>minimum: 1 | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `stinger_rating` | Signed integer MediaStinger rating; see [unrated behaviour](#mediastinger-ratings) | Movies |
| `tmdb_vote_average` | TMDb vote average rating<br>minimum: 0.0<br>[Missing items](#external-metadata-and-missing-items). | Movies, Shows |
| `tmdb_vote_count` | TMDb vote count<br>minimum: 1<br>[Missing items](#external-metadata-and-missing-items). | Movies, Shows |
| `tmdb_year` | Year on TMDb<br>minimum: 1<br>[Missing items](#external-metadata-and-missing-items); [Current year](#external-metadata-and-missing-items). | Movies, Shows |
| `user_rating` | User rating<br>0.0 - 10.0 | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `versions` | Number of versions found<br>minimum: 0<br>[Child items](#child-item-filters): Shows, Seasons, Artists, Albums. | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `width` | Width<br>minimum: 0<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `year` | Year<br>minimum: 1<br>[Current year](#external-metadata-and-missing-items). | Movies, Shows, Seasons, Episodes, Albums, Tracks |

### String filters {#string-filters}

Contains matching is the default. Multiple values require a YAML list; a comma-separated string is not a replacement.

| Modifier | Matches | Value |
|:---------|:--------|:------|
| No modifier, `.not` | Contains / does not contain | String or YAML list |
| `.is`, `.isnot` | Exact match / not an exact match | String or YAML list |
| `.begins`, `.ends` | Begins / ends with | String or YAML list |
| `.regex` | Matches a regular expression | Regex string |

<span id="string-filter-attributes"></span>

| Attribute | Matches / constraints | Supports |
|:----------|:----------------------|:---------|
| `audio_codec` | Audio codec<br>[Child items](#child-item-filters): Shows, Seasons, Artists, Albums. | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `audio_profile` | Audio profile<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `audio_track_title` | Audio track titles<br>[Child items](#child-item-filters): Shows, Seasons, Artists, Albums. | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `edition` | Edition | Movies, Shows |
| `filepath` | Item's filepath<br>[Child items](#child-item-filters): Shows, Seasons, Artists, Albums. | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `folder` | Item's folder | Shows, Artists |
| `record_label` | Record label | Albums |
| `studio` | Studio | Movies, Shows |
| `summary` | Summary | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `title` | Title | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `show_title` | Show title | Seasons, Episodes |
| `season_title` | Season title | Episodes |
| `tmdb_title` | Title from TMDb<br>[Missing items](#external-metadata-and-missing-items). | Movies, Shows |
| `tvdb_status` | Status from TVDb<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `tvdb_title` | Title from TVDb<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `video_codec` | Video codec<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `video_profile` | Video profile<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |

### Tag filters {#tag-filters}

Multiple values can be a YAML list or comma-separated string. Count modifiers compare the number of tags, rather than the tags themselves.

| Modifier | Matches | Value |
|:---------|:--------|:------|
| No modifier, `.not` | Matches / does not match a value | String, YAML list, or comma-separated string |
| `.regex` | One tag value matches the regex | Regex string |
| `.count_gt`, `.count_gte` | Tag count greater than / greater than or equal | Number |
| `.count_lt`, `.count_lte` | Tag count less than / less than or equal | Number |

<span id="tag-filter-attributes"></span>

| Attribute | Matches / constraints | Supports |
|:----------|:----------------------|:---------|
| `actor` | Actor | Movies, Shows, Episodes |
| `audio_language` | Audio language<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `collection` | Collection | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `content_rating` | Content rating | Movies, Shows, Episodes |
| `country` | Country | Movies, Artists |
| `director` | Director | Movies, Episodes |
| `genre` | Genre | Movies, Shows, Artists, Albums |
| `imdb_keyword` | Keywords from IMDb See [Special](#special-filters) for more attributes<br>[Missing items](#external-metadata-and-missing-items). | Movies, Shows |
| `label` | Label | Movies, Shows, Seasons, Episodes, Artists, Albums, Tracks |
| `network` | Network | Shows |
| `origin_country` | Uses TMDb origin country [ISO 3166-1 alpha-2 codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)<br>Example: `origin_country: us`<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `producer` | Producer tags | Movies, Episodes |
| `resolution` | Resolution<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `subtitle_language` | Subtitle language<br>[Child items](#child-item-filters): Shows, Seasons. | Movies, Shows, Seasons, Episodes |
| `tmdb_genre` | Genres from TMDb<br>[Missing items](#external-metadata-and-missing-items). | Movies, Shows |
| `tmdb_keyword` | Keywords from TMDb<br>[Missing items](#external-metadata-and-missing-items). | Movies, Shows |
| `tvdb_genre` | Genres from TVDb<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `writer` | Writer | Movies, Episodes |
| `year` | Year<br>[Current year](#external-metadata-and-missing-items). | Movies, Shows, Seasons, Episodes, Albums, Tracks |

### Special filters {#special-filters}

These filters use their own input forms. Child thresholds and external-metadata rules are explained after the tables.

<span id="attribute"></span>

| Attribute | Matches / constraints | Supports |
|:----------|:----------------------|:---------|
| `albums` | Filter album attributes; optional `percentage` or `count` threshold. | Artists |
| `episodes` | Filter episode attributes; optional `percentage` or `count` threshold. | Shows, Seasons |
| `history` | Match release dates in previous years: `day` for today's month/day; `month` for this month; `1`-`30` for today or that many previous days. | Movies, Shows, Episodes, Albums |
| `imdb_keyword` | Keyword list plus optional `minimum_votes`, `minimum_relevant`, and `minimum_percentage`; also supports tag modifiers.<br>[Missing items](#external-metadata-and-missing-items). | Movies, Shows |
| `original_language`, `original_language.not` | TMDb ISO 639-1 original-language codes, such as `"en,ko"`; `.not` excludes. See [language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).<br>[Child-item behaviour](#child-item-filters). | Movies, Shows |
| `seasons` | Filter season attributes; optional `percentage`, `count`, or `latest: true` (latest cannot combine with the thresholds). | Shows |
| `tmdb_status`, `tmdb_status.not` | TMDb status: `returning`, `planned`, `production`, `ended`, `canceled`, `pilot`; `.not` excludes.<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `tmdb_type`, `tmdb_type.not` | TMDb type: `documentary`, `news`, `production`, `miniseries`, `reality`, `scripted`, `talk_show`, `video`; `.not` excludes.<br>[Missing items](#external-metadata-and-missing-items). | Shows |
| `tracks` | Filter track attributes; optional `percentage` or `count` threshold. | Artists, Albums |

## Child-item filters

The special `albums`, `episodes`, `seasons`, and `tracks` filters test child-item
attributes rather than just the parent. Use `percentage` (0-100) or `count`
(1 or greater) as a threshold. The default percentage is 50%, controlled by the
[default_percent setting](settings.md#default-percent-example).

For filters marked "Child items" in the tables, the indicated parent media use
this special episodes/tracks behaviour with the default percentage. Direct
movie, episode, or track checks remain at their listed level.

`seasons` also accepts `latest: true` to test only the highest-numbered Plex season,
excluding Specials / season 0. It **cannot** be combined with `percentage` or `count`.

=== "Episode percentage"

    Includes shows where at least 75% of episodes have a user rating of 7 or
    higher. The percentage controls how many child episodes must pass the nested
    rating filter; it is not an audience rating.

    ```yaml
    collections:
      Consistently Highly Rated Shows:
        plex_all: true
        filters:
          episodes:
            percentage: 75
            user_rating.gte: 7
    ```

=== "Latest season"

    Includes shows whose latest non-special season has a user rating of at least
    8. `latest: true` is a boolean and selects only the highest-numbered season.

    ```yaml
    collections:
      Highly Rated Latest Seasons:
        plex_all: true
        filters:
          seasons:
            latest: true
            user_rating.gte: 8
    ```

## External metadata and missing items

Filters marked "Missing items" also prevent non-matching missing movies or shows
from being added to Radarr/Sonarr. Those attributes cannot use the tag `.count_*`
modifiers. Their source is external metadata, so the value can differ from Plex.

Year filters marked "Current year" accept `current_year` and relative forms such
as `current_year-2`.

`imdb_keyword` supports the normal tag modifiers as well as its special dictionary
options: `keywords`, `minimum_votes`, `minimum_relevant`, and `minimum_percentage`.
These respectively select keywords and require minimum vote counts, relevant
vote counts, and percentage of relevant votes.

## MediaStinger ratings

`has_stinger` checks whether a movie is listed by [MediaStinger](http://www.mediastinger.com/),
regardless of its rating. `stinger_rating` measures whether its during/after-credits
scene is worth staying for, using data from the
[Kometa MediaStinger repository](https://github.com/Kometa-Team/Mediastingers).

Positive, zero, and negative integer ratings are accepted. `stinger_rating.gt: 0`
requires a positive rating; a negative threshold such as `stinger_rating.gt: -1`
is also valid. Movies without a MediaStinger rating do **not** match any
`stinger_rating` filter, including `.not`.
