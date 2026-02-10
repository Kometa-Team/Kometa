---
hide:
  - tags
  - toc
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

Filters allow for you to filter every item added to the collection/overlay/playlist from every Builder using the `filters` attribute.

## Using Filters

Filters cannot do anything alone they require the use of at least one [Builder](builders/overview.md) to function.

You can have multiple filters in each set but an item must match at least one value from **each** filter to not be ignored. The values for each must match what Plex has including special characters in order to match.

```yaml
filters:
  genre: Action
  country: Germany
```

Anything that doesn't have both the Genre `Action` and the Country `Germany` will be ignored.

Multiple Filter Sets can be given as a list. With multiple sets only one of the sets must pass for the item to not be ignored.

```yaml
filters:
  - genre: Action
    country: Germany
  - genre: Comedy
    country: France
```

Anything that doesn't have either both the Genre `Action` and the Country `Germany` or the Genre `Comedy` and the Country `France` will be ignored.

All filter options are listed below.

To display items filtered out add `show_filtered: true` to the definition. To display items that make it through the filters add `show_unfiltered: true` to the definition.

You can use the `plex_all: true` Builder to filter from your entire library.

???+ warning

    Filters can be very slow, particularly on larger libraries. Try to build or narrow your items using a [Smart Label Collection](../files/settings.md#smart-label-definitions), [Plex Search](../files/builders/plex/search.md) or another [Builder](overview.md) if possible.

## Filter Options

=== "Boolean Filters"

    **Modifiers:** No Modifier

    ### Boolean Filter Attributes

    | Boolean Filters                                                                                          | Description                                                                                              | Allowed Media                                                                                                                                                                                                              |
    |:---------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `has_collection`                                                                                         | Matches every item that has or does not have a collection                                                | `Movies`<br>`Shows`<br>`Seasons`,<br>`Episodes`<br>`Artists`<br>`Albums`<br>`Tracks`                                                                                                                                       |
    | `has_dolby_vision` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-filters-boolean-1" } | Matches every item that has or does not have a dolby vision                                              | `Movies`<br>`Shows` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-filters-boolean-1" }<br>`Seasons` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-filters-boolean-1" }<br>`Episodes` |
    | `has_edition`                                                                                            | Matches every item that has or does not have an edition                                                  | `Movies`                                                                                                                                                                                                                   |
    | `has_overlay`                                                                                            | Matches every item that has or does not have an overlay                                                  | `Movies`<br>`Shows`<br>`Seasons`,<br>`Episodes`<br>`Artists`<br>`Albums`                                                                                                                                                   |
    | `has_stinger`                                                                                            | Matches every item that has a [media stinger](http://www.mediastinger.com/) (After/During Credits Scene) | `Movies`                                                                                                                                                                                                                   |

    #### Examples

    ```yaml
    collections:
     Movies with Mediastingers:
       plex_all: true
       filters:
         has_stinger: true
    ```
    ```yaml
    collections:
     Movies with Editions:
       plex_all: true
       filters:
         has_edition: true
    ```


=== "Date Filters"

    **Modifiers:** No Modifier, `.not`, `.before`, `.after`, or `.regex`

    Date filters can **NOT** take multiple values.

    ### Date Filter Attributes

    | Date Filters                                                                                                     | Description                                                                    | Allowed Media                                                                        |
    |:-----------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|
    | `added`                                                                                                          | Uses the date added attribute to match                                         | `Movies`<br>`Shows`<br>`Seasons`,<br>`Episodes`<br>`Artists`<br>`Albums`<br>`Tracks` |
    | `first_episode_aired` :material-numeric-2-circle:{ data-tooltip data-tooltip-id="tippy-filters-date-1" }         | Uses the first episode aired date to match                                     | `Shows`                                                                              |
    | `last_episode_aired_or_never` :material-numeric-2-circle:{ data-tooltip data-tooltip-id="tippy-filters-date-1" } | Similar to `last_episode_aired` but also includes those that haven't aired yet | `Shows`                                                                              |
    | `last_episode_aired` :material-numeric-2-circle:{ data-tooltip data-tooltip-id="tippy-filters-date-1" }          | Uses the last episode aired date to match                                      | `Shows`                                                                              |
    | `last_played`                                                                                                    | Uses the date last played attribute to match                                   | `Movies`<br>`Shows`<br>`Seasons`,<br>`Episodes`<br>`Artists`<br>`Albums`<br>`Tracks` |
    | `release`                                                                                                        | Uses the release date attribute (originally available) to match                | `Movies`<br>`Shows`<br>`Episodes`<br>`Albums`                                        |

    ???+ tip "Date Filter Modifiers"

        | Date Modifier | Description                                                           | Format                                                                     |
        |:--------------|:----------------------------------------------------------------------|:---------------------------------------------------------------------------|
        | No Modifier   | Matches every item where the date attribute is in the last X days     | **Format:** number of days<br>e.g. `30`                                    |
        | `.after`      | Matches every item where the date attribute is after the given date   | **Format:** MM/DD/YYYY or `today` for the current day<br>e.g. `01/01/2000` |
        | `.before`     | Matches every item where the date attribute is before the given date  | **Format:** MM/DD/YYYY or `today` for the current day<br>e.g. `01/01/2000` |
        | `.not`        | Matches every item where the date attribute is not in the last X days | **Format:** number of days<br>e.g. `30`                                    |
        | `.regex`      | Matches every item where the attribute matches the regex given        | N/A                                                                        |

    #### Examples

    ```yaml
    collections:
     Summer 2020 Movies:
       plex_all: true
       filters:
         release.after: 5/1/2020
         release.before: 8/31/2020
    ```
    ```yaml
    collections:
     Movies Released in the Last 180 Days:
       plex_all: true
       filters:
         release: 180
    ```

=== "Number Filters"

    **Modifiers:** No Modifier, `.not`, `.gt`, `.gte`, `.lt`, or `.lte`

    Number filters can **NOT** take multiple values.

    ### Number Filter Attributes

    | Number Filters                                                                                                                                                                      | Description                                                                                                                                                                 | Allowed Media                                                                                                                                                                                                                                                                                                                                                                                                              |
    |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | aspect :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }                                                                                         | Uses the aspect attribute to match<br>minimum: 0.0                                                                                                                          | Movies<br>Shows :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Seasons :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Episodes                                                                                                                                                                                                           |
    | audience_rating                                                                                                                                                                     | Uses the audience rating attribute to match<br>0.0 - 10.0                                                                                                                   | Movies<br>Shows<br>Episodes                                                                                                                                                                                                                                                                                                                                                                                                |
    | channels :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }                                                                                       | Uses the audio channels attribute to match<br>minimum: 0                                                                                                                    | Movies<br>Shows :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Seasons :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Episodes                                                                                                                                                                                                           |
    | critic_rating                                                                                                                                                                       | Uses the critic rating attribute to match<br>0.0 - 10.0                                                                                                                     | Movies<br>Shows<br>Episodes<br>Albums                                                                                                                                                                                                                                                                                                                                                                                      |
    | duration                                                                                                                                                                            | Uses the duration attribute to match using minutes<br>minimum: 0                                                                                                            | Movies<br>Shows<br>Episodes<br>Tracks                                                                                                                                                                                                                                                                                                                                                                                      |
    | height :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }                                                                                         | Uses the height attribute to match<br>minimum: 0                                                                                                                            | Movies<br>Shows :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Seasons :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Episodes                                                                                                                                                                                                           |
    | plays                                                                                                                                                                               | Uses the plays attribute to match<br>minimum: 1                                                                                                                             | Movies<br>Shows<br>Seasons,<br>Episodes<br>Artists<br>Albums<br>Tracks                                                                                                                                                                                                                                                                                                                                                     |
    | stinger_rating :material-numeric-6-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-4" }                                                                                 | Uses the [Mediastinger](http://www.mediastinger.com/) rating to match.<br>The media stinger rating is if the after/during credits scene is worth staying for.<br>minimum: 0 | Movies                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | tmdb_vote_average :material-numeric-4-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-2" }                                                                              | Uses the tmdb vote average rating to match<br>minimum: 0.0                                                                                                                  | Movies<br>Shows                                                                                                                                                                                                                                                                                                                                                                                                            |
    | tmdb_vote_count :material-numeric-4-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-2" }                                                                                | Uses the tmdb vote count to match<br>minimum: 1                                                                                                                             | Movies<br>Shows                                                                                                                                                                                                                                                                                                                                                                                                            |
    | tmdb_year :material-numeric-4-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-2" } :material-numeric-3-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-1" } | Uses the year on TMDb to match<br>minimum: 1                                                                                                                                | Movies<br>Shows                                                                                                                                                                                                                                                                                                                                                                                                            |
    | user_rating                                                                                                                                                                         | Uses the user rating attribute to match<br>0.0 - 10.0                                                                                                                       | Movies<br>Shows<br>Seasons,<br>Episodes<br>Artists<br>Albums<br>Tracks                                                                                                                                                                                                                                                                                                                                                     |
    | versions :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }                                                                                       | Uses the number of versions found to match<br>minimum: 0                                                                                                                    | Movies<br>Shows :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Seasons :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" },<br>Episodes<br>Artists :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Albums :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Tracks |
    | width :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }                                                                                          | Uses the width attribute to match<br>minimum: 0                                                                                                                             | Movies<br>Shows :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Seasons :material-numeric-5-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-3" }<br>Episodes                                                                                                                                                                                                           |
    | year :material-numeric-3-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-1" }                                                                                           | Uses the year attribute to match<br>minimum: 1                                                                                                                              | Movies<br>Shows<br>Seasons,<br>Episodes<br>Albums<br>Tracks                                                                                                                                                                                                                                                                                                                                                                |
    
    ???+ tip "Number Filter Modifiers"

        | Number Modifier | Description                                                                                | Format                                            |
        |:----------------|:-------------------------------------------------------------------------------------------|:--------------------------------------------------|
        | No Modifier     | Matches every item where the number attribute is equal to the given number                 | **Format:** number<br>e.g. `30`, `1995`, or `7.5` |
        | `.gt`           | Matches every item where the number attribute is greater than the given number             | **Format:** number<br>e.g. `30`, `1995`, or `7.5` |
        | `.gte`          | Matches every item where the number attribute is greater than or equal to the given number | **Format:** number<br>e.g. `30`, `1995`, or `7.5` |
        | `.lt`           | Matches every item where the number attribute is less than the given number                | **Format:** number<br>e.g. `30`, `1995`, or `7.5` |
        | `.lte`          | Matches every item where the number attribute is less than or equal to the given number    | **Format:** number<br>e.g. `30`, `1995`, or `7.5` |
        | `.not`          | Matches every item where the number attribute is not equal to the given number             | **Format:** number<br>e.g. `30`, `1995`, or `7.5` |

    #### Examples

    ```yaml
    collections:
     9.0 Movies:
       plex_all: true
       filters:
         user_rating.gte: 9
    ```
    ```yaml
    collections:
     Good Adam Sandler Romantic Comedies:
       plex_search:
         all:
           genre: Romance
           actor: Adam Sandler
       filters:
         genre: Comedy
         user_rating.gte: 7
    ```

=== "String Filters"

    **Modifiers:** No Modifier, `.not`, `.is`, `.isnot`, `.begins`, `.ends`, or `.regex`

    String filters can take multiple values **only as a list**.

    ### String Filter Attributes

    | String Filter                                                                                          | Description                              | Allowed Media                                                                                                                                                                                                                                                                                                                                                                                                             |
    |:-------------------------------------------------------------------------------------------------------|:-----------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | audio_codec :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }       | Uses the audio codec tags to match       | Movies<br>Shows :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Seasons :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Episodes                                                                                                                                                                                                          |
    | audio_profile :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }     | Uses the audio profile tags to match     | Movies<br>Shows :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Seasons :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Episodes                                                                                                                                                                                                          |
    | audio_track_title :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" } | Uses the audio track titles to match     | Movies<br>Shows :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Seasons :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Episodes<br>Artists :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Albums :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Tracks |
    | edition                                                                                                | Uses the edition attribute to match      | Movies                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | filepath :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }          | Uses the item's filepath to match        | Movies<br>Shows :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Seasons :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Episodes<br>Artists :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Albums :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Tracks |
    | folder                                                                                                 | Uses the item's folder to match          | Shows<br>Artists                                                                                                                                                                                                                                                                                                                                                                                                          |
    | record_label                                                                                           | Uses the record label attribute to match | Albums                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | studio                                                                                                 | Uses the studio attribute to match       | Movies<br>Shows                                                                                                                                                                                                                                                                                                                                                                                                           |
    | summary                                                                                                | Uses the summary attribute to match      | Movies<br>Shows<br>Seasons<br>Episodes<br>Artists<br>Albums<br>Tracks                                                                                                                                                                                                                                                                                                                                                     |
    | title                                                                                                  | Uses the title attribute to match        | Movies<br>Shows<br>Seasons<br>Episodes<br>Artists<br>Albums<br>Tracks                                                                                                                                                                                                                                                                                                                                                     |
    | show_title                                                                                             | Uses the show title attribute to match   | Seasons<br>Episodes                                                                                                                                                                                                                                                                                                                                                                                                       |
    | season_title                                                                                           | Uses the season title attribute to match | Episodes                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | tmdb_title :material-numeric-7-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-1" }        | Uses the title from TMDb to match        | Movies<br>Shows                                                                                                                                                                                                                                                                                                                                                                                                           |
    | tvdb_status :material-numeric-7-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-1" }       | Uses the status from TVDb to match       | Shows                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | tvdb_title :material-numeric-7-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-1" }        | Uses the title from TVDb to match        | Shows                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | video_codec :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }       | Uses the video codec tags to match       | Movies<br>Shows :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Seasons :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Episodes                                                                                                                                                                                                          |
    | video_profile :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }     | Uses the video profile tags to match     | Movies<br>Shows :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Seasons :material-numeric-8-circle:{ data-tooltip data-tooltip-id="tippy-filters-string-2" }<br>Episodes                                                                                                                                                                                                          |


    ???+ tip "String Filter Modifiers"

        | String Modifier | Description                                                                    |
        |:----------------|:-------------------------------------------------------------------------------|
        | No Modifier     | Matches every item where the attribute contains the given string               |
        | `.begins`       | Matches every item where the attribute begins with the given string            |
        | `.ends`         | Matches every item where the attribute ends with the given string              |
        | `.is`           | Matches every item where the attribute exactly matches the given string        |
        | `.isnot`        | Matches every item where the attribute does not exactly match the given string |
        | `.not`          | Matches every item where the attribute does not contain the given string       |
        | `.regex`        | Matches every item where the attribute matches the regex given                 |

    #### Examples

    ```yaml
    collections:
      Movies with Commentary:
        plex_all: true
        filters:
          audio_track_title: Commentary
    ```
    ```yaml
    collections:
      Movies with Audio Codecs containing DTS:
        plex_all: true
        filters:
          audio_codec: DTS
    ```
=== "Tag Filters"

    **Modifiers:** No Modifier, `.not`, `.regex`, `.count_lt`, `.count_lte`, `.count_gt`, or `.count_gte`

    Tag filters can take multiple values as a **list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string**.

    ### Tag Filter Attributes

    | Tag Filters                                                                                            | Description                                                                                                                                     | Allowed Media                                                                                                                                                                                                          |
    |:-------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `actor`                                                                                                | Uses the actor tags to match                                                                                                                    | `Movies`<br>`Shows`<br>`Episodes`                                                                                                                                                                                      |
    | `audio_language` :material-numeric-10-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-2" }    | Uses the audio language tags to match                                                                                                           | `Movies`<br>`Shows` :material-numeric-10-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-2" }<br>`Seasons` :material-numeric-10-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-2" }<br>`Episodes`   |
    | `collection`                                                                                           | Uses the collection tags to match                                                                                                               | `Movies`<br>`Shows`<br>`Seasons`,<br>`Episodes`<br>`Artists`<br>`Albums`<br>`Tracks`                                                                                                                                   |
    | `content_rating`                                                                                       | Uses the content rating tags to match                                                                                                           | `Movies`<br>`Shows`<br>`Episodes`                                                                                                                                                                                      |
    | `country`                                                                                              | Uses the country tags to match                                                                                                                  | `Movies`<br>`Artists`                                                                                                                                                                                                  |
    | `director`                                                                                             | Uses the director tags to match                                                                                                                 | `Movies`<br>`Episodes`                                                                                                                                                                                                 |
    | `genre`                                                                                                | Uses the genre tags to match                                                                                                                    | `Movies`<br>`Shows`<br>`Artists`<br>`Albums`                                                                                                                                                                           |
    | `imdb_keyword` :material-numeric-1-box:{ data-tooltip data-tooltip-id="tippy-filters-tag-3" }          | Uses the keywords from IMDb to match See [Special](#special-filters) for more attributes                                                        | `Movies`<br>`Shows`                                                                                                                                                                                                    |
    | `label`                                                                                                | Uses the label tags to match                                                                                                                    | `Movies`<br>`Shows`<br>`Seasons`,<br>`Episodes`<br>`Artists`<br>`Albums`<br>`Tracks`                                                                                                                                   |
    | `network`                                                                                              | Uses the network tags to match                                                                                                                  | `Shows`                                                                                                                                                                                                                |
    | `origin_country` :material-numeric-1-box:{ data-tooltip data-tooltip-id="tippy-filters-tag-3" }        | Uses TMDb origin country [ISO 3166-1 alpha-2 codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) to match<br>Example: `origin_country: us` | `Shows`                                                                                                                                                                                                                |
    | `producer`                                                                                             | Uses the actor tags to match                                                                                                                    | `Movies`<br>`Episodes`                                                                                                                                                                                                 |
    | `resolution` :material-numeric-10-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-2" }        | Uses the resolution tag to match                                                                                                                | `Movies`<br>`Shows` :material-numeric-3-circle:{ data-tooltip data-tooltip-id="tippy-filters-number-1" }<br>`Seasons` :material-numeric-10-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-2" }<br>`Episodes` |
    | `subtitle_language` :material-numeric-10-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-2" } | Uses the subtitle language tags to match                                                                                                        | `Movies`<br>`Shows` :material-numeric-10-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-2" }<br>`Seasons` :material-numeric-10-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-2" }<br>`Episodes`   |
    | `tmdb_genre` :material-numeric-1-box:{ data-tooltip data-tooltip-id="tippy-filters-tag-3" }            | Uses the genres from TMDb to match                                                                                                              | `Movies`<br>`Shows`                                                                                                                                                                                                    |
    | `tmdb_keyword` :material-numeric-1-box:{ data-tooltip data-tooltip-id="tippy-filters-tag-3" }          | Uses the keywords from TMDb to match                                                                                                            | `Movies`<br>`Shows`                                                                                                                                                                                                    |
    | `tvdb_genre` :material-numeric-1-box:{ data-tooltip data-tooltip-id="tippy-filters-tag-3" }            | Uses the genres from TVDb to match                                                                                                              | `Shows`                                                                                                                                                                                                                |
    | `writer`                                                                                               | Uses the writer tags to match                                                                                                                   | `Movies`<br>`Episodes`                                                                                                                                                                                                 |
    | `year` :material-numeric-9-circle:{ data-tooltip data-tooltip-id="tippy-filters-tag-1" }               | Uses the year tag to match                                                                                                                      | `Movies`<br>`Shows`<br>`Seasons`,<br>`Episodes`<br>`Albums`<br>`Tracks`                                                                                                                                                |

    ???+ tip "Tag Filter Modifiers"

        | Tag Modifier | Description                                                                               |
        |:-------------|:------------------------------------------------------------------------------------------|
        | No Modifier  | Matches every item where the attribute matches the given string                           |
        | `.count_gt`  | Matches every item where the attribute count is greater than the given number             |
        | `.count_gte` | Matches every item where the attribute count is greater than or equal to the given number |
        | `.count_lt`  | Matches every item where the attribute count is less than the given number                |
        | `.count_lte` | Matches every item where the attribute count is less than the given number                |
        | `.not`       | Matches every item where the attribute does not match the given string                    |
        | `.regex`     | Matches every item where one value of this attribute matches the regex.                   |

    #### Examples

    ```yaml
    collections:
     Daniel Craig only James Bonds:
       imdb_list:
         list_id: ls006405458
       filters:
         actor: Daniel Craig
    ```
    ```yaml
    collections:
     French Romance:
       plex_search:
         all:
           genre: Romance
       filters:
         audio_language: Français
    ```


=== "Special Filters"

    Special Filters each have their own set of rules for how they're used.

    ### Attribute

    | Special Filters                                                                                                                                                                                                    | Description                                                                                                                                                                                                                                                                                                                                                                                | Allowed Media                                 |
    |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------|
    | `albums`                                                                                                                                                                                                           | Uses the item's albums attributes to match.<br> Also `percentage` or `count` can be applied to set a threshold, a default of 50% will be used if neither specified.<br>`percentage`: (0-100) Percentage of albums that must match.<br>`count`: (1+) Minimum number of albums that must match                                                                                                        | `Artists`                                     |
    | `episodes`                                                                                                                                                                                                         | Uses the item's episodes attributes to match.<br> Also `percentage` or `count` can be applied to set a threshold, a default of 50% will be used if neither specified.<br>`percentage`: (0-100) Percentage of episodes that must match.<br>`count`: (1+) Minimum number of episodes that must match                                                                                                  | `Shows`<br>`Seasons`                          |
    | `history`                                                                                                                                                                                                          | Uses the release date attribute (originally available) to match dates throughout history<br>`day`: Match the Day and Month to Today's Date<br>`month`: Match the Month to Today's Date<br>`1-30`: Match the Day and Month to Today's Date or `1-30` days before                                                                                                                            | `Movies`<br>`Shows`<br>`Episodes`<br>`Albums` |
    | `imdb_keyword` :material-numeric-3-box:{ data-tooltip data-tooltip-id="tippy-filter-special-2" } :material-numeric-4-box:{ data-tooltip data-tooltip-id="tippy-filter-special-3" }                                 | Uses the keywords from IMDb to match<br>`keywords`: list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of keywords to match<br>`minimum_votes`: minimum number of votes keywords must have<br>`minimum_relevant`: minimum number of relevant votes keywords must have<br>`minimum_percentage`: minimum percentage of relevant votes keywords must have | `Movies`<br>`Shows`                           |
    | `original_language` :material-numeric-2-box:{ data-tooltip data-tooltip-id="tippy-filter-special-1" }<br>`original_language.not` :material-numeric-2-box:{ data-tooltip data-tooltip-id="tippy-filter-special-1" } | Uses TMDb original language [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) to match<br>Example: `original_language: en, ko`                                                                                                                                                                                                                                      | `Movies`<br>`Shows`                           |
    | `seasons`                                                                                                                                                                                                          | Uses the item's seasons attributes to match.<br> Also `percentage` or `count` can be applied to set a threshold, a default of 50% will be used if neither specified.<br>`percentage`: (0-100) Percentage of seasons that must match.<br>`count`: (1+) Minimum number of seasons that must match                                                                                                      | `Shows`                                       |
    | `tmdb_status` :material-numeric-3-box:{ data-tooltip data-tooltip-id="tippy-filter-special-2" }<br>`tmdb_status.not` :material-numeric-3-box:{ data-tooltip data-tooltip-id="tippy-filter-special-2" }             | Uses TMDb Status to match<br>**Values:** `returning`, `planned`, `production`, `ended`, `canceled`, `pilot`                                                                                                                                                                                                                                                                                | `Shows`                                       |
    | `tmdb_type` :material-numeric-3-box:{ data-tooltip data-tooltip-id="tippy-filter-special-2" }<br>`tmdb_type.not` :material-numeric-3-box:{ data-tooltip data-tooltip-id="tippy-filter-special-2" }                 | Uses TMDb Type to match<br>**Values:** `documentary`, `news`, `production`, `miniseries`, `reality`, `scripted`, `talk_show`, `video`                                                                                                                                                                                                                                                      | `Shows`                                       |
    | `tracks`                                                                                                                                                                                                           | Uses the item's tracks attributes to match.<br> Also `percentage` or `count` can be applied to set a threshold, a default of 50% will be used if neither specified.<br>`percentage`: (0-100) Percentage of tracks that must match.<br>`count`: (1+) Minimum number of tracks that must match                                                                                                                                              | `Artists`<br>`Albums`                         |

    #### Examples

    ```yaml
    collections:
     Shows That Finished Too Soon:
       plex_all: true
       filters:
         tmdb_status: canceled
    ```
    ```yaml
    collections:
     On This Day in Previous Years:
       plex_all: true
       filters:
         history: day
    ```
