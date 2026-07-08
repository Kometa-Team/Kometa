---
search:
  boost: 4
hide:
  - toc
---
# Library Operations

There are a variety of Library Operations that can be utilized in a library.

Within each library, operations can be defined by using the `operations` attribute, as demonstrated below.

When not using a list under `operations` the whole operations value is one block.

```yaml title="config.yml Operations sample"
libraries:
  Movies:
    collection_files:
      - default: imdb
    operations:
      mass_metadata_update:
        ratings:
          critic: tmdb
      split_duplicates: true
```

## Operation Blocks

You can create individual blocks of operations by using a list under `operations` with each item in the list being a "block" that can be individually scheduled.

```yaml title="config.yml Operation Blocks sample"
libraries:
  Movies:
    collection_files:
      - default: imdb
    operations:
      - schedule: weekly(friday)
        mass_metadata_update:
          ratings:
            critic: tmdb
      - schedule: weekly(saturday)
        split_duplicates: true
```

## A Note on Data Sources

Several of these operations use data from external sources such as MDBList. You will need to authenticate against each service you wish to use in these operations.

Some of these sources have free and paid tiers of access. Your entire library may not be able to be updated in a single run on a free tier; you may need to make multiple runs over some number of days.

For example, MDBList's free tier is limited [at time of writing] to 1000 API requests daily. Changes in external site paid/free status and limits are not under Kometa's control.

## A Note on Mass Operations

Several of these operations perform **mass** updates; these are just that, **mass** updates.  Except as shown below, they cannot be filtered to operate on only a subset of the items in your library.

## Operation Attributes

###### Mass Metadata Update

??? info "`mass_metadata_update` - Updates metadata fields, artwork, ratings, mappings, and metadata backup data."
    `mass_metadata_update` groups the legacy `mass_*_update` operations into one operation block.


    **Attribute:** `mass_metadata_update`

    | Attribute              | Description                                                                                                                    |
    | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
    | `added_at`             | Updates added at dates.                                                                                                        |
    | `background`           | Updates backgrounds.                                                                                                           |
    | `backup`               | Creates or maintains a metadata backup file.                                                                                   |
    | `collections`          | Updates collection modes. Use `mode` to set the Plex collection mode.                                                           |
    | `content_rating`       | Updates content ratings. Use `source` for update sources and `mappings` for content rating remapping.                          |
    | `genre`                | Updates genres. Use `source` for update sources and `mappings` for genre remapping.                                            |
    | `labels`               | Updates IMDb parental guide labels. Use `severity` to set the minimum IMDb parental guide severity.                             |
    | `logo`                 | Updates logos. Seasons and episodes are not supported.                                                                         |
    | `original_title`       | Updates original titles.                                                                                                       |
    | `originally_available` | Updates originally available dates.                                                                                            |
    | `poster`               | Updates posters.                                                                                                               |
    | `ratings`              | Updates item and episode ratings using `audience`, `critic`, `user`, `episode_audience`, `episode_critic`, and `episode_user`. |
    | `square_art`           | Updates square art. Seasons and episodes are not supported.                                                                    |
    | `studio`               | Update studios.                                                                                                                             |


    ??? example "Complete Example (click to expand)"

        ```yaml
        libraries:
          Movies:
            operations:
              mass_metadata_update:
                added_at: tmdb_digital
                background:
                  source: tmdb
                  language: en
                backup:
                  path: config/Movie_Backup.yml
                  exclude:
                    - title
                  sync_tags: false
                  add_blank_entries: true
                collections: hide
                content_rating:
                  source: mdb_commonsense
                  mappings:
                    TV-14: 14
                genre:
                  source: tmdb
                  mappings:
                    Action & Adventure: Action
                labels: moderate
                logo: tmdb
                original_title: mal_english
                originally_available: tmdb
                poster:
                  source: trakt
                  seasons: true
                  episodes: false
                ratings:
                  user: tmdb
                  critic: imdb
                  audience: mdb_tomatoesaudience
                  episode_user: tmdb
                  episode_critic: imdb
                  episode_audience: tmdb
                square_art: tvdb
                studio: tmdb
        ```

    ??? tip "Scheduling Mass Metadata Operations"

        `mass_metadata_update` can be scheduled as a whole operation block, or each top-level sub-attribute can be scheduled individually.
        
        When `schedule` is set on the `mass_metadata_update` operation block, that schedule applies to every sub-operation inside the block unless the sub-operation defines its own `schedule`.
        ```yaml
        operations:
          - schedule: weekly(monday)
            mass_metadata_update:
              genre:
                source: tmdb
              content_rating:
                source: mdb
              ratings:
                critic: imdb
        ```
        In this example, `genre`, `content_rating`, and `ratings.critic` all run on Monday.
        
        You can also schedule individual sub-attributes:
        ```yaml
        operations:
          mass_metadata_update:
            genre:
              schedule: weekly(monday)
              source: tmdb
              mappings:
                Action & Adventure: Action
            content_rating:
              schedule: weekly(tuesday)
              source: mdb
              mappings:
                TV-14: 14
            original_title:
              schedule: weekly(wednesday)
              source: mal_english
            studio:
              schedule: weekly(thursday)
              source: tmdb
        ```
        In this example:
        
        | Attribute | Schedule |
        | --- | --- |
        | `genre` | Monday |
        | `content_rating` | Tuesday |
        | `original_title` | Wednesday |
        | `studio` | Thursday |
        
        For attributes that support both a shorthand value and a dictionary, `source` is optional. These two examples are equivalent:
        ```yaml
        operations:
          mass_metadata_update:
            originally_available: tmdb
            added_at: tmdb_digital
        ```

        ```yaml
        operations:
          mass_metadata_update:
            originally_available:
              source: tmdb
            added_at:
              source: tmdb_digital
        ```
        Use the dictionary form when you need to add a `schedule`:
        ```yaml
        operations:
          mass_metadata_update:
            originally_available:
              schedule: weekly(friday)
              source: tmdb
            added_at:
              schedule: weekly(saturday)
              source: tmdb_digital
        ```
        The same pattern can be used for ratings:
        ```yaml
        operations:
          mass_metadata_update:
            ratings:
              user:
                schedule: weekly(monday)
                source: tmdb
              critic:
                schedule: weekly(tuesday)
                source: imdb
              audience:
                schedule: weekly(wednesday)
                source: mdb_tomatoesaudience
        ```
        If `schedule` is placed directly under `ratings`, it applies to every rating inside `ratings` unless that rating defines its own `schedule`.
        ```yaml
        operations:
          mass_metadata_update:
            ratings:
              user: tmdb
              critic:
                schedule: weekly(tuesday)
                source: imdb
              audience: mdb_tomatoesaudience
        ```
        In this example, `user` and `audience` run on every run, while `critic` only runs on Tuesday.
        ```

    === "Backup"



        `backup` creates or maintains a Kometa Metadata File with a full `metadata` mapping based on the library's item locked attributes.

        ???+ tip "Tip"

            If you point to an existing Metadata File then Kometa will sync the changes to the file, so you won't lose non-Plex changes in the file.

        ??? example "Example Backup Operation"

            ```yaml
            operations:
              mass_metadata_update:
                backup:
                  path: config/Movie_Backup.yml
                  exclude:
                    - title
                  sync_tags: true
                  add_blank_entries: false
            ```

        | Attribute | Description |
        | --- | --- |
        | `path` | Path to where the metadata will be saved or maintained. **Default:** `<<library_name>>_Metadata_Backup.yml` in your config folder. |
        | `exclude` | Exclude all listed attributes from being saved in the Metadata File. |
        | `sync_tags` | Tag attributes will use the `.sync` option and blank attributes will be added to sync. **Default:** `false`. |
        | `add_blank_entries` | Add a line for entries that have no metadata changes. **Default:** `true`. |


    === "Content Ratings"

        `source` accepts a source or an ordered list of fallback sources. `mappings` maps the final content rating value after source lookup.

        ???+ tip "Note on `mdb` sources"

            MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed.

        ??? example "Example Content Rating & Mapping Operations"

            ```yaml
            operations:
              mass_metadata_update:
                content_rating:
                  source:
                    - mdb_commonsense
                    - mdb_age_rating
                    - NR
                  mappings:
                    PG: Y-10
                    "PG-13": Y-10
                    R:
            ```

        | Source | Description |
        | --- | --- |
        | `mdb` | Use MDBList for content ratings. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_commonsense` | Use Common Sense rating through MDBList for content ratings. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_commonsense0` | Use Common Sense rating with zero padding through MDBList for content ratings. Requires [MDBList key](../config/mdblist.md). |
        | `plex_csm` | Use Common Sense Media age rating cached on the Plex item itself. Requires the new Plex Movie/Series agent; no external API key. |
        | `plex_csm0` | Use Common Sense Media age rating cached on the Plex item itself with zero padding. Requires the new Plex Movie/Series agent; no external API key. |
        | `mdb_age_rating` | Use MDBList age rating for content ratings. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_age_rating0` | Use MDBList age rating with zero padding for content ratings. Requires [MDBList key](../config/mdblist.md). |
        | `omdb` | Use IMDb through OMDb for content ratings. Requires [OMDB key](../config/omdb.md). |
        | `mal` | Use MyAnimeList for content ratings. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `lock` | Lock the content rating field. |
        | `unlock` | Unlock the content rating field. |
        | `remove` | Remove the content rating and lock the field. |
        | `reset` | Remove the content rating and unlock the field. |
        | Any string | Set an explicit content rating value. |

        | Mapping Attribute | Description |
        | --- | --- |
        | `key` | Content rating value to map from. |
        | `value` | Content rating value to map to. Leave blank to remove the source content rating. |


    === "Collections"

        `mode` updates every Collection in your library to the specified Collection Mode.

        ??? example "Example Collection Mode Operation"

            ```yaml
            operations:
              mass_metadata_update:
                collections:
                  mode: hide
            ```

        | Mode | Description |
        | --- | --- |
        | `default` | Library default. |
        | `hide` | Hide Collection. |
        | `hide_items` | Hide Items in this Collection. |
        | `show_items` | Show this Collection and its Items. |


    === "Dates"

        `originally_available` updates the item's originally available date. `added_at` updates the item's added at date.

        ???+ tip

            Plex does not allow `originally_available` to be empty. Using `remove` or `reset` will set the date to the Plex default date, which is `1969-12-31`.

        ???+ tip "Note on `mdb` sources"

            MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed.

        ??? example "Example Originally Available & Added At Operations"

            ```yaml
            operations:
              mass_metadata_update:
                originally_available:
                  - tmdb_digital
                  - tmdb_premiere
                  - tmdb
                  - 1900-01-01
                added_at:
                  - tmdb_digital
                  - tmdb_premiere
                  - tmdb
                  - 1900-01-01
            ```

        | Value | Description |
        | --- | --- |
        | `tmdb` | Use TMDb release date. |
        | `tmdb_premiere` | Use TMDb premiere release date. Movie libraries only. |
        | `tmdb_theatrical` | Use TMDb theatrical release date. Movie libraries only. |
        | `tmdb_theatricallimited` | Use TMDb theatrical limited release date. Movie libraries only. |
        | `tmdb_digital` | Use TMDb digital release date. Movie libraries only. |
        | `tmdb_physical` | Use TMDb physical release date. Movie libraries only. |
        | `tmdb_tv` | Use TMDb TV release date. Movie libraries only. |
        | `tvdb` | Use TVDb release date. |
        | `omdb` | Use IMDb release date through OMDb. Requires [OMDB key](../config/omdb.md). |
        | `mdb` | Use MDBList release date. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_digital` | Use MDBList digital release date. Requires [MDBList key](../config/mdblist.md). |
        | `anidb` | Use AniDB release date. |
        | `mal` | Use MyAnimeList release date. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `lock` | Lock the date field. |
        | `unlock` | Unlock the date field. |
        | `remove` | Remove the date and lock the field. |
        | `reset` | Remove the date and unlock the field. |
        | `YYYY-MM-DD` | Set an explicit date, for example `2022-05-28`. |


    === "Genres"

        `source` accepts a source or an ordered list of fallback sources. `mappings` maps the final genre values after source lookup.

        ??? example "Example Genre & Mapping Operation"

            ```yaml
            operations:
              mass_metadata_update:
                genre:
                  source:
                    - imdb
                    - tmdb
                    - ["Unknown"]
                  mappings:
                    "Action/Adventure": Action
                    "Action & Adventure": Action
            ```
        | Source | Description |
        | --- | --- |
        | `tmdb` | Use TMDb for genres. |
        | `tvdb` | Use TVDb for genres. |
        | `imdb` | Use IMDb for genres. |
        | `omdb` | Use IMDb through OMDb for genres. Requires [OMDB key](../config/omdb.md). |
        | `anidb` | Use AniDB main tags for genres. |
        | `anidb_3_0` | Use AniDB main tags and all 3 star tags and above for genres. |
        | `anidb_2_5` | Use AniDB main tags and all 2.5 star tags and above for genres. |
        | `anidb_2_0` | Use AniDB main tags and all 2 star tags and above for genres. |
        | `anidb_1_5` | Use AniDB main tags and all 1.5 star tags and above for genres. |
        | `anidb_1_0` | Use AniDB main tags and all 1 star tags and above for genres. |
        | `anidb_0_5` | Use AniDB main tags and all 0.5 star tags and above for genres. |
        | `mal` | Use MyAnimeList for genres. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `mal_all` | Use MyAnimeList for genres, including explicit genres, themes, and demographics. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `lock` | Lock the genre field. |
        | `unlock` | Unlock the genre field. |
        | `remove` | Remove all genres and lock the genre field. |
        | `reset` | Remove all genres and unlock the genre field. |
        | List of strings | Set explicit genre values, for example `["String 1", "String 2"]`. |

        | Mappings Attribute | Description |
        | --- | --- |
        | `key` | Genre value to map from. |
        | `value` | Genre value to map to. Leave blank to remove the source genre. |


    === "Images"

        Assets will be used over anything else. The image type keys are optional; only the configured image types are processed.

        ???+ warning

            When `poster` is used in combination with Overlays, this could cause Kometa to reset the poster and then reapply all overlays on each run, which will result in [image bloat](../kometa/scripts/imagemaid.md).

        ??? example "Example Image Operations"

            ```yaml
            operations:
              mass_metadata_update:
                poster:
                  source: trakt
                  seasons: true
                  episodes: true
                background:
                  source:
                    - trakt
                    - tmdb
                logo:
                  source: tmdb
                  language: en
                square_art:
                  source: tvdb
            ```
        | Attribute | Description | Values |
        | --- | --- | --- |
        | `poster` | Updates item posters. | Dictionary of poster options. |
        | `background` | Updates item backgrounds. | Dictionary of background options. |
        | `logo` | Updates item logos. Seasons and episodes are not supported. | Dictionary of logo options. |
        | `square_art` | Updates item square art. Seasons and episodes are not supported. | Dictionary of square art options. |

        | Poster Option | Description | Values |
        | --- | --- | --- |
        | `source` | Source of the poster update. Can be a single source or an ordered list of fallback sources. `tvdb` applies to top-level movie and show posters. `trakt` uses screenshots/title-card-style images for episodes. | `tmdb`, `trakt`, `tvdb`, `plex`, `lock`, or `unlock` |
        | `language` | Override the TMDb language for poster fetching. Only applies when `source` is `tmdb`. | ISO 639-1 language code, such as `en`, `de`, or `xx` for textless. |
        | `seasons` | Update season posters while updating shows. Ignored when `source` is `tvdb`. **Default:** `true` | `true` or `false` |
        | `episodes` | Update episode posters while updating shows. Ignored when `source` is `tvdb`. **Default:** `true` | `true` or `false` |
        | `ignore_locked` | Skip updating if the poster field is locked. **Default:** `false` | `true` or `false` |
        | `ignore_overlays` | Skip updating if the current poster has an Overlay. **Default:** `false` | `true` or `false` |

        | Background Option | Description | Values |
        | --- | --- | --- |
        | `source` | Source of the background update. Can be a single source or an ordered list of fallback sources. | `tmdb`, `trakt`, `tvdb`, `plex`, `lock`, or `unlock` |
        | `language` | Override the TMDb language for background fetching. Only applies when `source` is `tmdb`. | ISO 639-1 language code, such as `en`, `de`, or `xx` for textless. |
        | `seasons` | Update season backgrounds while updating shows. Ignored when `source` is `tvdb`. **Default:** `true` | `true` or `false` |
        | `episodes` | Update episode backgrounds while updating shows. Ignored when `source` is `tvdb` or `trakt`. **Default:** `true` | `true` or `false` |
        | `ignore_locked` | Skip updating if the background field is locked. **Default:** `false` | `true` or `false` |
        | `ignore_overlays` | Skip updating if the current background has an Overlay. **Default:** `false` | `true` or `false` |

        | Logo Option | Description | Values |
        | --- | --- | --- |
        | `source` | Source of the logo update. Can be a single source or an ordered list of fallback sources. | `tmdb`, `trakt`, `tvdb`, `plex`, `lock`, or `unlock` |
        | `language` | Override the TMDb language for logo fetching. Only applies when `source` is `tmdb`. | ISO 639-1 language code, such as `en`, `de`, or `xx` for language-neutral. |
        | `ignore_locked` | Skip updating if the logo field is locked. **Default:** `false` | `true` or `false` |

        | Square Art Option | Description | Values |
        | --- | --- | --- |
        | `source` | Source of the square art update. Can be a single source or an ordered list of fallback sources. | `tvdb`, `plex`, `lock`, or `unlock` |
        | `ignore_locked` | Skip updating if the square art field is locked. **Default:** `false` | `true` or `false` |


    === "Labels"

        `severity` updates every item's labels in the library to match the IMDb Parental Guide.

        ??? example "Example Labels Operation"

            ```yaml
            operations:
              mass_metadata_update:
                labels:
                  severity: severe
            ```

        | Severity | Description |
        | --- | --- |
        | `none` | Apply all Parental Labels with a value of `None`, `Mild`, `Moderate`, or `Severe`. |
        | `mild` | Apply all Parental Labels with a value of `Mild`, `Moderate`, or `Severe`. |
        | `moderate` | Apply all Parental Labels with a value of `Moderate` or `Severe`. |
        | `severe` | Apply all Parental Labels with a value of `Severe`. |


    === "Ratings"

        Use `ratings.audience`, `ratings.critic`, and `ratings.user` for item ratings. Use `ratings.episode_audience`, `ratings.episode_critic`, and `ratings.episode_user` for episode ratings.

        ???+ warning "Important Note"

            This does not affect the icons displayed in the Plex UI. This places the number of your choice in the relevant field in the Plex database. One primary use of this feature is to put ratings overlays on posters. More information on ratings can be found [here](../kometa/guides/ratings.md).

        ???+ tip "Note on `mdb` sources"

            MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed.

        ??? example "Example Rating & Episode Rating Operations"
    
            ```yaml
            operations:
              mass_metadata_update:
                ratings:
                  audience:
                    - mdb
                    - mdb_average
                    - 2.0
                  critic:
                    - imdb
                    - omdb
                    - 2.0
                  user:
                    - trakt_user
                    - 2.0
                  episode_audience:
                    - tmdb
                    - 2.0
                  episode_critic:
                    - imdb
                    - 2.0
            ```

        | Rating Value | Description |
        | --- | --- |
        | `anidb_average` | Use AniDB average. |
        | `anidb_rating` | Use AniDB rating. |
        | `anidb_score` | Use AniDB review score. |
        | `imdb` | Use IMDb rating. |
        | `mal` | Use MyAnimeList score. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `mdb` | Use MDBList score. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_average` | Use MDBList average score. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_imdb` | Use IMDb rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_letterboxd` | Use Letterboxd rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_metacritic` | Use Metacritic rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_metacriticuser` | Use Metacritic user rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_myanimelist` | Use MyAnimeList rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_tmdb` | Use TMDb rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_tomatoes` | Use Rotten Tomatoes rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_tomatoesaudience` | Use Rotten Tomatoes audience rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `mdb_trakt` | Use Trakt rating through MDBList. Requires [MDBList key](../config/mdblist.md). |
        | `omdb` | Use IMDb rating through OMDb. Requires [OMDB key](../config/omdb.md). |
        | `omdb_metascore` | Use Metacritic metascore through OMDb. Requires [OMDB key](../config/omdb.md). |
        | `omdb_tomatoes` | Use Rotten Tomatoes rating through OMDb. Requires [OMDB key](../config/omdb.md). |
        | `plex_imdb` | Use IMDb rating through Plex. |
        | `plex_tmdb` | Use TMDb rating through Plex. |
        | `plex_tomatoes` | Use Rotten Tomatoes rating through Plex. |
        | `plex_tomatoesaudience` | Use Rotten Tomatoes audience rating through Plex. |
        | `tmdb` | Use TMDb rating. |
        | `trakt` | Use Trakt rating. Requires [Trakt authentication](../config/trakt.md). |
        | `trakt_user` | Use Trakt user's personal rating. Requires [Trakt authentication](../config/trakt.md). |
        | `lock` | Lock the rating field. |
        | `unlock` | Unlock the rating field. |
        | `remove` | Remove rating and lock the field. |
        | `reset` | Remove rating and unlock the field. |
        | Number from `0.0` to `10.0` | Set an explicit rating value. |

        | Episode Rating Value | Description |
        | --- | --- |
        | `imdb` | Use IMDb rating. |
        | `plex_imdb` | Use IMDb rating through Plex. |
        | `plex_tmdb` | Use TMDb rating through Plex. |
        | `tmdb` | Use TMDb rating. |
        | `trakt` | Use Trakt rating. Requires [Trakt authentication](../config/trakt.md). |
        | `lock` | Lock the rating field. |
        | `unlock` | Unlock the rating field. |
        | `remove` | Remove rating and lock the field. |
        | `reset` | Remove rating and unlock the field. |
        | Number from `0.0` to `10.0` | Set an explicit rating value. |


    === "Studios"

        `studio` accepts a source, an ordered list of fallback sources, or an explicit string value.

        ??? example "Example Studio Operation"

            ```yaml
            operations:
              mass_metadata_update:
                studio:
                  - mal
                  - anidb
                  - Unknown
            ```

         | Value | Description |
        | --- | --- |
        | `anidb` | Use AniDB animation work. |
        | `mal` | Use MyAnimeList studio. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `tmdb` | Use TMDb studio. |
        | `lock` | Lock the studio field. |
        | `unlock` | Unlock the studio field. |
        | `remove` | Remove studio and lock the field. |
        | `reset` | Remove studio and unlock the field. |
        | Any string | Set an explicit studio. |


    === "Titles"

        `original_title` accepts a source, an ordered list of fallback sources, or an explicit string value.

        ??? example "Example Original Title Operation"

            ```yaml
            operations:
              mass_metadata_update:
                original_title:
                  - anidb_official
                  - anidb
                  - Unknown
            ```

        | Value | Description |
        | --- | --- |
        | `anidb` | Use AniDB main title. |
        | `anidb_official` | Use AniDB official title based on the language attribute in the config file. |
        | `mal` | Use MyAnimeList main title. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `mal_english` | Use MyAnimeList English title. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `mal_japanese` | Use MyAnimeList Japanese title. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `lock` | Lock the original title field. |
        | `unlock` | Unlock the original title field. |
        | `remove` | Remove original title and lock the field. |
        | `reset` | Remove original title and unlock the field. |
        | Any string | Set an explicit original title. |

        | `studio` Value | Description |
        | --- | --- |
        | `anidb` | Use AniDB animation work. |
        | `mal` | Use MyAnimeList studio. Requires [MyAnimeList authentication](../config/myanimelist.md). |
        | `tmdb` | Use TMDb studio. |
        | `lock` | Lock the studio field. |
        | `unlock` | Unlock the studio field. |
        | `remove` | Remove studio and lock the field. |
        | `reset` | Remove studio and unlock the field. |
        | Any string | Set an explicit studio. |


###### Assets For All

??? info "`assets_for_all` - Used to search the asset directories for images for all items in the library."
    Ordinarily, Kometa searches the asset directories for collection artwork. Enabling this Operation tells Kometa
    to searches the asset directories for images for all items [movies, shows, seasons, episodes, etc] in the library.

    **Attribute:** `assets_for_all`

    **Accepted Values:** `true` or `false`.

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              assets_for_all: false
        ```

###### Assets For All Collections

??? info "`assets_for_all_collections` - Used to search the asset directories for images for all unmanaged and/or unconfigured in the library."
    Enabling this Operation tells Kometa
    to search the asset directories for images for unmanaged and unconfigured collections in the library.

    **Attribute:** `assets_for_all_collections`

    **Accepted Values:** `true` or `false`.

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              assets_for_all_collections: false
        ```

###### Delete Collections

??? info "`delete_collections` - Deletes collections based on a set of given attribute."
    Deletes collections based on a set of given attributes. The Collection must match all set attributes to be deleted.

    **Attribute:** `delete_collections`

    **Accepted Values:** There are a few different options to determine how the `delete_collections` works.

    | Value | Description |
    | --- | --- |
    | `managed: true` | Collection must be Managed to be deleted. (collection has the `Kometa` label) |
    | `managed: false` | Collection must be Unmanaged to be deleted. (collection does not have the `Kometa` label) |
    | `configured: true` | Collection must be Configured to be deleted. (collection is in the config file of the specific Kometa run) |
    | `configured: false` | Collection must be Unconfigured to be deleted. (collection is not in the config file of the specific Kometa run) |
    | `less: ###` | Collection must contain less than the given number of items to be deleted. `###` is a Number greater than 0. Optional value which if undefined means collections will be deleted regardless of how many items they have. |
    | `ignore_empty_smart_collections: false` | Do not apply less check to empty smart collections. This allows retaining things like smart collections that show movies without subtitles or the like. |


    **The collection does not need to be scheduled to be considered configured and only needs to be in the config file.**

    **`configured` works correctly regardless of `run_order` position.** The configured check is based on your config file, not on what Kometa has processed so far in the current run, so placing `operations` before `collections` in `run_order` will not cause configured collections to be incorrectly deleted.

    ???+ example "Example"

        Removes all Managed Collections (Collections with the `Kometa` Label) that are not configured in the Current Run.

        ```yaml
        libraries:
          Movies:
            operations:
              delete_collections:
                configured: false
                managed: true
        ```

###### Update Blank Track Titles

??? info "`update_blank_track_titles` - Updates blank track titles of every item in the library."
    Search though every track in a music library and replace any blank track titles with the tracks sort title.

    **Attribute:** `update_blank_track_titles`

    **Accepted Values:** `true` or `false`.

    ???+ example "Example"

        ```yaml
        libraries:
          Music:
            operations:
              update_blank_track_titles: true
        ```

###### Remove Title Parentheses

??? info "`remove_title_parentheses` - Removes title parentheses of every item in the library."
    Search through every title and remove all ending parentheses in an items title if the title is not locked.

    **Attribute:** `remove_title_parentheses`

    **Accepted Values:** `true` or `false`.

    ???+ example "Example"

        ```yaml
        libraries:
          Music:
            operations:
              remove_title_parentheses: true
        ```

###### Ignore Labels

??? info "`ignore_labels` - Skips items from Library Operations when they have any of the given labels."
    Enabling this Operation tells Kometa to skip items from item-based Library Operations when the item has any label listed in `ignore_labels`.

    This applies to item-based Library Operations such as mass updates, asset updates, label updates, Radarr/Sonarr add-all operations, and similar operations that process every item in the library.

    The label must match the Plex label exactly.

    **Attribute:** `ignore_labels`

    **Accepted Values:** List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma separated string of labels.

    ???+ example "Example Usage"

        In this example, items with the `Do Not Update` or `Manual Metadata` label will be skipped during the `mass_metadata_update.ratings.critic` Library Operation.

        ```yaml
        libraries:
          Movies:
            operations:
              ignore_labels:
                - Do Not Update
                - Manual Metadata
              mass_metadata_update:
                ratings:
                  critic: tmdb
        ```

###### Respect Ignore IDs

??? info "`respect_ignore_ids` - Skips items from Library Operations when their IDs are ignored."
    Enabling this Operation tells Kometa to skip items from Library Operations when their TMDb/TVDb ID is listed in `ignore_ids` or their IMDb ID is listed in `ignore_imdb_ids`.

    This applies the library's configured `ignore_ids` and `ignore_imdb_ids` to item-based Library Operations such as mass updates, asset updates, label updates, Radarr/Sonarr add-all operations, and similar operations that process every item in the library.

    **Attribute:** `respect_ignore_ids`

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example Usage"

        In this example, the 2 IMDb IDs set to be ignored at the global level and the 2 TMDb IDs set to be ignored at the library level will be skipped during the `mass_metadata_update.ratings.critic` Library Operation.

        ```yaml
        libraries:
          Movies:
            operations:
              respect_ignore_ids: true
              mass_metadata_update:
                ratings:
                  critic: tmdb
            settings:
              ignore_ids:
                - 572802
                - 695721
        settings:
          ignore_imdb_ids:
            - tt6710474
            - tt1630029

        ```

###### Split Duplicates

??? info "`split_duplicates` - Splits all duplicate items found in this library."
    Splits all duplicate items found in this library.

    **Attribute:** `split_duplicates`

    **Accepted Values:** `true` or `false`.

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              split_duplicates: true
        ```

###### Radarr Add All

??? info "`radarr_add_all` - Adds every item in the library to Radarr."
    Adds every item in the library to Radarr.

    ???+ warning

        The existing paths in plex will be used as the root folder of each item, if the paths in Plex are not the same as your Radarr
        paths you can use the `plex_path` and `radarr_path` [Radarr](radarr.md) details to convert the paths.

    **Attribute:** `radarr_add_all`

    **Accepted Values:** `true` or `false`.

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              radarr_add_all: true
        ```

###### Radarr Remove By Tag

??? info "`radarr_remove_by_tag` - Removes every item from Radarr with the Tags given."
    Removes every item from Radarr with the Tags given.

    **Attribute:** `radarr_remove_by_tag`

    **Accepted Values:** List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma separated string of tags.

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              radarr_remove_by_tag: mytag1, mytag2
        ```

###### Sonarr Add All

??? info "`sonarr_add_all` - Adds every item in the library to Sonarr."
    Adds every item in the library to Sonarr.

    ???+ warning

        The existing paths in plex will be used as the root folder of each item, if the paths in Plex are not the same as your Sonarr
        paths you can use the `plex_path` and `sonarr_path` [Sonarr](sonarr.md) details to convert the paths.

    **Attribute:** `sonarr_add_all`

    **Accepted Values:** `true` or `false`.

    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              sonarr_add_all: true
        ```

###### Sonarr Remove By Tag

??? info "`sonarr_remove_by_tag` - Removes every item from Sonarr with the Tags given."
    Removes every item from Sonarr with the Tags given.

    **Attribute:** `sonarr_remove_by_tag`

    **Accepted Values:** List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma separated string of tags.

    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              sonarr_remove_by_tag: mytag1, mytag2
        ```

###### Plex Bulk Edits Batch Size

??? info "`plex_bulk_edit_batch_size` - Breaks up processing of operations into chunks of this many items."
    Setting this file tells Kometa to break up operations that require inspecting/modifying the entire library into chunks. Setting this can be particularly helpful for large libraries.

    If no value is set, the entire library is processed in one batch.

    For example, if your Movies library has 1000 items, by default all of them will be processed at once.
    If `plex_bulk_edit_batch_size=100`, then 100 items will be processed at once.

    **Attribute:** `plex_bulk_edit_batch_size`

    **Accepted Values:** None, or any number.

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              plex_bulk_edit_batch_size: 1000
              mass_metadata_update:
                ratings:
                  audience: imdb
        ```
