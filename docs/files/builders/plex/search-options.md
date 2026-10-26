# Search Options

<!--shared-content-start-->
## Plex search options

Use `attribute.modifier: value`, such as `title.not: "Harry Potter"`.
The attribute and value are required; modifiers depend on the filter type below.
These options are shared by `plex_search` and `smart_filter`.

=== "Boolean filters"

    Boolean Filters take no modifier and can only be either `true` or `false`.

    #### Boolean attributes

    | Attribute | Matches / constraints | Supports |
    |:----------|:----------------------|:---------|
    | `hdr` | Is HDR | Movies, Shows |
    | `hdr10plus` | Has HDR10+ | Movies, Shows |
    | `atmos` | Has Dolby Atmos | Movies, Shows |
    | `unmatched` | Is Unmatched (Music: Artist) | Movies, Music |
    | `duplicate` | Is Duplicate | Movies |
    | `unplayed` | Is Unplayed | Movies |
    | `progress` | Is In Progress | Movies |
    | `trash` | Is Trashed (Music: Track) | Movies, Shows, Music |
    | `unplayed_episodes` | Has Unplayed Episodes | Shows |
    | `episode_unplayed` | Has Episodes Unplayed | Shows |
    | `episode_duplicate` | Has Duplicate Episodes | Shows |
    | `episode_progress` | Has Episode Progress | Shows |
    | `episode_unmatched` | Has Episodes Unmatched | Shows |
    | `show_unmatched` | Has Shows Unmatched | Shows |
    | `artist_unmatched` | Is Artist's Unmatched | Music |
    | `album_unmatched` | Is Album's Unmatched | Music |
    | `track_trash` | Is Track Trashed | Music |
    | `dovi` | Has Dolby Vision | Movies, Shows |

=== "Date filters"

    Date filters can be used with no modifier or with `.last`, `.notlast`, `.before`, or `.after`. The legacy `.not` modifier is also accepted as `.notlast`.

    No date filter can take multiple values.


    #### Date attributes

    | Attribute | Matches / constraints | Supports |
    |:----------|:----------------------|:---------|
    | `added` | date added | Movies, Shows |
    | `episode_added` | date added | Shows |
    | `release` | release date attribute (originally available) to match | Movies, Shows |
    | `episode_air_date` | air date attribute (originally available) of the show's episodes to match | Shows |
    | `last_played` | date last played | Movies, Shows |
    | `episode_last_played` | date last played | Shows |
    | `artist_added` / `date_artist_added` | Artist's date added | Music |
    | `artist_last_played` | Artist's last played | Music |
    | `album_last_played` | Album's last played | Music |
    | `album_added` / `date_album_added` | Album's date added | Music |
    | `album_released` / `date_album_released` | Album's release date | Music |
    | `track_last_played` | Track's date last played | Music |
    | `track_last_skipped` | Track's date last skipped | Music |
    | `track_last_rated` | Track's date last rated | Music |
    | `track_added` / `track_added_at` | Track's date added | Music |

    ???+ tip "Date Filter Modifiers"

        | Date Modifier | Description                                                                                                                                                | Plex Web UI Display  |
        |:--------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------:|
        | No Modifier / `.last` | In the last given interval; days by default, or suffix `s`, `min`, `h`, `d`, `m`, `y`. Example: `10h`. | `is in the last` |
        | `.notlast` / `.not` | Not in the last given interval; same format as `.last`. Example: `30` days. | `is not in the last` |
        | `.before` | Before a date as `MM/DD/YYYY`, or `today`. | `is before` |
        | `.after` | After a date as `MM/DD/YYYY`, or `today`. | `is after` |

        For example, `date_album_added.last: 10h` matches albums added in the last 10 hours.

=== "Number filters"

    Number filters can use `.is`, `.isnot`, `.gt`, `.gte`, `.lt`, or `.lte` as a modifier. Only rating filters can use `.rated`.

    No number filter can take multiple values.

    #### Number attributes

    | Attribute | Matches / constraints | Supports |
    |:----------|:----------------------|:---------|
    | `duration` | duration using minutes<br>Minimum: `0` | Movies |
    | `year` | year (Music: Album)<br>Minimum: `0` | Movies, Shows, Music |
    | `plays` | plays<br>Minimum: `0` | Movies, Shows |
    | `critic_rating` | critic rating<br>Range: `0.0` - `10.0` | Movies, Shows |
    | `audience_rating` | audience rating<br>Range: `0.0` - `10.0` | Movies, Shows |
    | `user_rating` | user rating<br>Range: `0.0` - `10.0` | Movies, Shows |
    | `commonsense_rating` | Uses Plex's Common Sense Media age rating to match<br>Range: `1` - `18` | Movies, Shows |
    | `episode_year` | Episode's year<br> Minimum: `0` | Shows |
    | `episode_plays` | Episode's plays<br>Minimum: `0` | Shows |
    | `episode_critic_rating` | critic rating<br>Range: `0.0` - `10.0` | Shows |
    | `episode_audience_rating` | audience rating<br>Range: `0.0` - `10.0` | Shows |
    | `episode_user_rating` | user rating<br>Range: `0.0` - `10.0` | Shows |
    | `album_year` | Album's year<br>Minimum: `0` | Music |
    | `album_decade` | Album's decade<br>Minimum: `0` | Music |
    | `album_plays` | Album's plays<br>Minimum: `0` | Music |
    | `track_plays` | Track's plays<br>Minimum: `0` | Music |
    | `track_skips` | Track's skips<br>Minimum: `0` | Music |
    | `artist_rating` / `artist_user_rating` | Artist's user rating<br>Range: `0.0` - `10.0` | Music |
    | `album_rating` / `album_user_rating` | Album's user rating<br>Range: `0.0` - `10.0` | Music |
    | `album_critic_rating` | Album's critic rating<br>Range: `0.0` - `10.0` | Music |
    | `track_rating` / `track_user_rating` | Track's user rating<br>Range: `0.0` - `10.0` | Music |

    ???+ tip "Number Filter Modifiers"

        | Number Modifier | Description                                                                                                                                             | Plex Web UI Display |
        |:----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------:|
        | `.is` | Equal to the number. | `is` |
        | `.isnot` | Not equal to the number. | `is not` |
        | `.gt` | Greater than the number. | `is greater than` |
        | `.gte` | Greater than or equal to the number. | N/A |
        | `.lt` | Less than the number. | `is less than` |
        | `.lte` | Less than or equal to the number. | N/A |
        | `.rated` | Rated / unrated; takes `true` or `false`, and only applies to rating filters. | N/A |

        * `.rated` only works for rating filters

=== "String filters"

    String filters can be used with either no modifier or with `.not`, `.is`, `.isnot`, `.begins`, or `.ends`.

    String filter can take multiple values **only as a list**.

    #### String attributes

    | Attribute | Matches / constraints | Supports |
    |:----------|:----------------------|:---------|
    | `title` | title | Movies, Shows |
    | `episode_title` | title | Shows |
    | `studio` | studio | Movies, Shows |
    | `edition` | edition | Movies, Shows |
    | `artist_title` | Artist's Title | Music |
    | `album_title` | Album's Title | Music |
    | `track_title` | Track's Title | Music |
    | `record_label` / `album_record_label` | Album's Record Label | Music |
    | `audio_codec` | Track's audio codec | Music |

    ???+ tip "String Filter Modifiers"

        | String Modifier | Description                                                                    | Plex Web UI Display |
        |:----------------|:-------------------------------------------------------------------------------|:-------------------:|
        | No Modifier | Contains the string. | `contains` |
        | `.not` | Does not contain the string. | `does not contain` |
        | `.is` | Exactly matches the string. | `is` |
        | `.isnot` | Does not exactly match the string. | `is not` |
        | `.begins` | Begins with the string. | `begins with` |
        | `.ends` | Ends with the string. | `ends with` |

=== "Tag filters"

    Tag filters can be used with either no modifier or with `.not` except for `decade` and `resolution` which can only be
    used with no modifier.

    Tag filter can take multiple values as a **list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string**.

    #### Tag attributes

    | Attribute | Matches / constraints | Supports |
    |:----------|:----------------------|:---------|
    | `actor` | actor | Movies, Shows |
    | `episode_actor` | episode actor | Shows |
    | `audio_language` | audio language | Movies, Shows |
    | `collection` | collection for top level collections | Movies, Shows |
    | `season_collection` | collection for season collections | Shows |
    | `episode_collection` | collection for episode collections | Shows |
    | `content_rating` | content rating | Movies, Shows |
    | `country` | country | Movies, Shows |
    | `decade` | year tag to match the decade | Movies |
    | `director` | director | Movies |
    | `folder_location` | Plex library root folder location to match | Movies, Shows, Music |
    | `genre` | genre | Movies, Shows |
    | `label` | label for top level collections; in Music, matches the selected artist, album, or track type | Movies, Shows, Music |
    | `season_label` | label for season collections | Shows |
    | `episode_label` | label for episode collections | Shows |
    | `network` | network<br>**Only works with the New Plex TV Agent** | Shows |
    | `producer` | Producer tags | Movies |
    | `resolution` | resolution | Movies, Shows |
    | `subtitle_language` | subtitle language | Movies, Shows |
    | `writer` | writer | Movies |
    | `year` | year tag to match (Music: Album) | Movies, Shows, Music |
    | `episode_year` | year tag to match | Shows |
    | `artist_genre` | Artist's Genre | Music |
    | `artist_collection` | Artist's Collection | Music |
    | `artist_country` | Artist's Country | Music |
    | `artist_mood` | Artist's Mood | Music |
    | `artist_style` | Artist's Style | Music |
    | `artist_label` | Artist's Label | Music |
    | `album_genre` | Album's Genre | Music |
    | `album_mood` | Album's Mood | Music |
    | `album_style` | Album's Style | Music |
    | `album_format` | Album's Format | Music |
    | `album_type` | Album's Type | Music |
    | `album_collection` | Album's Collection | Music |
    | `album_source` | Album's Source | Music |
    | `album_label` | Album's Label | Music |
    | `track_mood` | Track's Mood | Music |
    | `track_genre` | Track's Genre | Music |
    | `track_source` | Track's Source | Music |
    | `track_label` | Track's Label | Music |

    You can use `current_year` to have Kometa use the current year. This can be combined with a
    `-#` at the end to subtract that number of years. i.e. `current_year-2`

    `folder_location` values must match a root folder configured in the Plex library. Plex does not expose nested
    subfolders as Folder Location filter choices. In music libraries, `folder_location` is only available with
    `builder_level: track`.

    ???+ tip "Tag Filter Modifiers"

        | Tag Modifier | Description                                                            | Plex Web UI Display |
        |:-------------|:-----------------------------------------------------------------------|:-------------------:|
        | No Modifier | Matches the value. | `is` |
        | `.not` | Does not match the value. | `is not` |
