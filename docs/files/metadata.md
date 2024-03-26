# Metadata Files

You can have the script edit the metadata of Items by adding them to the `metadata` mapping of a Metadata File.

??? example "Examples of multiple metadata edits in each library type (click to expand)"
    === "Movies"
        ```yaml
        metadata:
          Godzilla (1954):
            match:
              title: Godzilla
              year: 1954
            content_rating: R
          Godzilla (1998):
            match:
              title: Godzilla
              year: 1998
            sort_title: Godzilla 03
            content_rating: PG-13
          Shin Godzilla:
            sort_title: Godzilla 06
            content_rating: R
          Godzilla 1985:
            content_rating: PG
          "Godzilla 2000: Millennium":
            originally_available: 1999-08-18
          Godzilla Against MechaGodzilla:
            originally_available: 2002-03-23
          Godzilla Raids Again:
            content_rating: G
            originally_available: 1955-05-21
          Godzilla vs. Biollante:
            content_rating: PG
          Godzilla vs. Destoroyah:
            content_rating: PG
            originally_available: 1995-01-19
          Godzilla vs. Gigan:
            content_rating: G
            originally_available: 1972-09-14
          Godzilla vs. Hedorah:
            content_rating: G
            originally_available: 1971-04-01
          Godzilla vs. King Ghidorah:
            content_rating: PG
            originally_available: 1991-04-28
          Godzilla vs. Mechagodzilla:
            content_rating: G
            originally_available: 1974-03-24
          Godzilla vs. Mechagodzilla II:
            content_rating: PG
          Godzilla vs. Megaguirus:
            content_rating: PG
            originally_available: 2000-08-31
          Godzilla vs. Megalon:
            content_rating: G
            originally_available: 1973-03-17
          Godzilla vs. Mothra:
            content_rating: PG
            originally_available: 1992-04-28
          Godzilla vs. SpaceGodzilla:
            content_rating: PG
            originally_available: 1994-01-19
          Godzilla, King of the Monsters!:
            content_rating: G
          "Godzilla, Mothra and King Ghidorah: Giant Monsters All-Out Attack":
            content_rating: PG
            originally_available: 2001-08-31
          "Godzilla: Final Wars":
            content_rating: PG
            originally_available: 2004-12-13
          "Godzilla: Tokyo S.O.S.":
            originally_available: 2003-12-14
          Halloween (Rob Zombie):
            match:
              title: 
                - Halloween (Rob Zombie)
                - Halloween
            year: 2007
          "Halo 4: Forward Unto Dawn":
            match:
              title:
                - Halo 4: Forward Unto Dawn
                - Halo 4 Forward Unto Dawn
            tmdb_show: 56295
            content_rating: R
        ```
    
    === "TV Shows"
        ```yaml
        metadata:
          "Avatar: The Last Airbender":
            sort_title: Avatar 01
            seasons:
              1:
                title: "Book One: Water"
                summary: >-
                      After a lapse of 100 years, the Avatar-spiritual master of the elements-has returned. And just in
                      the nick of time. The Four Nations (Water, Earth, Fire, and Air) have become unbalanced. The Fire
                      Nation wants to rule the world, and its first conquest will be the Northern Water Tribe. It's up to
                      a 12-year-old Airbender named Aang to find a way to stop it. Join Aang, Katara, Sokka, Momo, and
                      Appa as they head north on the adventure of a lifetime.
                episodes:
                  1:
                    user_rating: 9.1
              2:
                title: "Book Two: Earth"
                summary: >-
                      Avatar Aang continues his quest to master the four elements before the end of summer. Together with
                      Katara, Sokka, Momo, and Appa, he journeys across the Earth Kingdom in search of an Earthbending
                      mentor. Along the way, he confronts Princess Azula, treacherous  daughter of Firelord Ozai and
                      sister to Prince Zuko. More powerful than her brother, Azula will stop nothing to defeat the Avatar.
                      But Aang and the gang find plenty of Earth Kingdom allies to help them along the way. From the swamps
                      of the South to the Earth King's palace, Avatar: Book 2 is an adventure like no other.
              3:
                title: "Book Three: Fire"
                summary: >-
                      Having survived the terrible battle with Azula, Aang faces new challenges as he and his brave
                      friends secretly enter the Fire Nation. Their quest is to find and defeat Firelord Ozai. Along
                      the way, they discover that Ozai has plans of his own. The leader of the Fire Nation intends to
                      use the massive power of Sozin's comet to spread his dominion permanently across the four nations.
                      Short on time, Aang has a lot of bending to learn and no master to help him learn it. However, his
                      friends are there to help, and he finds unexpected allies deep in the heart of the Fire Nation. In
                      the spectacular four-part conclusion, Aang must fulfill his destiny and become a fully realized
                      Avatar, or watch the world go up in smoke.
                episodes:
                  21:
                    summary: The Epic Series Final of Avatar The Last Airbender
          "Avatar: The Legend of Korra":
            match:
              title: 
                - "Avatar: The Legend of Korra"
                - The Legend of Korra
            sort_title: Avatar 02
            original_title: The Legend of Korra
            seasons:
              1:
                title: "Book One: Air"
              2:
                title: "Book Two: Spirits"
              3:
                title: "Book Three: Change"
              4:
                title: "Book Four: Balance"
        ```
    
    === "Music"
        ```yaml
        metadata:
          "Linkin Park":
            country: "United States of America"
            album_sorting: newest
            albums:
              "Hybrid Theory":
                originally_available: "2000-10-24"
                tracks:
                  1:
                    user_rating: 5
                  "One Step Closer":
                    user_rating: 5
              "Meteora":
                originally_available: "2003-03-25"
                album_sorting: newest
                tracks:
                  9:
                    user_rating: 5
                  "Numb":
                    user_rating: 5
              "Minutes To Midnight":
                originally_available: "2007-05-14"
        ```

## Matching Items

The `match` attribute is used to match movies within Plex to that definition within the Metadata file. One definition 
can match and edit multiple items. The available matching options are outlined below.

=== "Movies"
    | <div style="width:165px">Attribute</div> | Description                                                                                                   |
    |:-----------------------------------------|:--------------------------------------------------------------------------------------------------------------|
    | `title`<sup>1</sup>                      | Only matches movies that exactly match the movie's Title.<br>Can be a list (only one needs to match).         |
    | `year`                                   | Only matches movies that were released in the given year.                                                     |
    | `mapping_id`<sup>2</sup>                 | Only matches movies that have the given TMDb or IMDb ID.                                                      |
    | `edition`<sup>3</sup>                    | Only matches movies that exactly match the movie's Edition.<br>Can be a list (only one needs to match).       |
    | `edition_contains`<sup>3</sup>           | Only matches where the movie's Edition contains the given string.<br>Can be a list (only one needs to match). |
    | `blank_edition`<sup>3</sup>              | Only matches movies that have no Edition.<br>**Default:** `false`<br>**Values:** `true` or `false`            |

=== "TV Shows"
    | <div style="width:165px">Attribute</div> | Allowed Values                                                                                      |
    |:-----------------------------------------|:----------------------------------------------------------------------------------------------------|
    | `title`<sup>1</sup>                      | Only matches shows that exactly match the show's Title.<br>Can be a list (only one needs to match). |
    | `year`                                   | Only matches shows that were released in the given year.                                            |
    | `mapping_id`<sup>2</sup>                 | Only matches shows that have the given TVDb or IMDb ID.                                             |

=== "Music"
    | <div style="width:165px">Attribute</div> | Allowed Values                                                                                          |
    |:-----------------------------------------|:--------------------------------------------------------------------------------------------------------|
    | `title`<sup>1</sup>                      | Only matches artists that exactly match the artist's Title.<br>Can be a list (only one needs to match). |

1. When `title` is not provided and the mapping name was not specified as an ID, the default behaviour is to use the 
mapping name as `title` for matching.

2. When `mapping_id` is not provided and the mapping name was specified as an ID, the default behaviour is to use the 
mapping name as `mapping_id` for matching.

3. When the server does not have a Plex Pass then the Edition Field is not accessible. In this scenario, PMM will check 
the movie's filepath for `{edition-...}` to determine what the edition is.

??? example "Matching Examples (click to expand)"
    === "Movies"
        #### Example 1 - `title` and `mapping_id` 
        
        The below example shows how `title` and `mapping_id` can be used to match movies.
        
        ```yaml
        metadata:
          movie1:                   # Matches via the title "Star Wars"
            match:
              title: Star Wars
            edits...
          movie2:                   # Matches via TMDb ID: 299534
            match:
              mapping_id: 299534
            edits...
          movie3:                   # Matches via IMDb ID: tt4154756
            match:
              mapping_id: tt4154756
            edits...
          movie4:                   # Matches via the title "9" 
            match:
              title: 9
            edits...
        ```
        
        The Mapping Name can also be used to reduce line-count, as shown here:
        
        ```yaml
        metadata:
          Star Wars:    # Matches via the title "Star Wars"
            edits...
          299534:       # Matches via TMDb ID: 299534
            edits...
          tt4154756:    # Matches via IMDb ID: tt4154756
            edits...
          "9":          # Matches via the title "9" 
            edits...
        ```
        
        **Note:** to search for a movie titled with a number from the mapping name you must surround the number in 
        quotes like in the example below. Otherwise, it will look for the movie associated with that TMDb ID.
        
        #### Example 2 - `title` and `year`
        
        The below example shows how `title` and `year` can be used to match movies. 
        
        In this example, there are two movies in the library called "Godzilla", so the `year` attribute is used to 
        identify which movie is being matched.
        
        ```yaml
        metadata:
          Godzilla (1954):                   # Matches via the title "Godzilla" released in 1954
            match:
              title: Godzilla
              year: 1954
            edits...
          Godzilla (1998):                   # Matches via the title "Godzilla" released in 1998
            match:
              title: Godzilla
              year: 1998
            edits...
        ```
        
        #### Example 3 - using `editions`
        
        The edition attributes can be used to further specify which version of a movie should be matched within Plex.
        
        This can be combined with Example 1 as follows
        
        ```yaml
        metadata:
          movie1:                   # Matches via the title "Star Wars" and edition containing "4K77"
            match:
              title: Star Wars
              edition_contains: 4K77
            edits...
        ```
        
        If you wanted to specify the version of Star Wars which does not have an edition, then the `blank_edition` 
        attribute can be used as shown below:
        
        ```yaml
        metadata:
          movie1:                   # Matches via the title "Star Wars" and checks for no edition version
            match:
              title: Star Wars
              blank_edition: true
            edits...
        ```

    === "TV Shows"
        #### Example 1 - `title` and `mapping_id` 
        
        The below example shows how `title` and `mapping_id` can be used to match shows.
        
        ```yaml
        metadata:
          show1:                   # Matches via the title "Game of Thrones"
            match:
              title: Game of Thrones
            edits...
          show2:                   # Matches via TVDb ID: 366524
            match:
              mapping_id: 366524
            edits...
          show3:                   # Matches via IMDb ID: tt10234724
            match:
              mapping_id: tt10234724
            edits...
          show4:                   # Matches via the title "24" 
            match:
              title: 24
            edits...
        ```
        
        The Mapping Name can also be used to reduce line-count, as shown here:
        
        ```yaml
        metadata:
          Game of Thrones:  # Matches via the Name "Game of Thrones"
            edits...
          366524:           # Matches via TVDb ID: 366524
            edits...
          tt10234724:       # Matches via IMDb ID: tt10234724
            edits...
          "24":             # Matches via the Name "24" 
            edits...
        ```
        
        **Note:** to search for a show titled with a number from the mapping name you must surround the number in quotes 
        like in the example below. Otherwise, it will look for the show associated with that TVDb ID.
        
        #### Example 2 - `title` and `year`
        
        The below example shows how `title` and `year` can be used to match shows. 
        
        In this example, there are two shows in the library called "Vikings", so the `year` attribute is used to 
        identify which show is being matched.
        
        ```yaml
        metadata:
          Vikings (2012):                   # Matches via the title "Vikings" released in 2012
            match:
              title: Vikings
              year: 2012
            edits...
          Vikings (2013):                   # Matches via the title "Vikings" released in 2013
            match:
              title: Vikings
              year: 2013
            edits...
        ```

    === "Music"
        #### Example 1 - `title`
        
        The below example shows how `title` can be used to match artists.
        
        ```yaml
        metadata:
          artist1:                   # Matches via the title "Ke$ha"
            match:
              title: Ke$ha
            edits...
          artist2:                   # Matches via the title "311" 
            match:
              title: 311
            edits...
        ```
        
        The Mapping Name can also be used to reduce line-count, as shown here:
        
        ```yaml
        metadata:
          Ke$ha:             # Matches via the Name "Ke$ha"
            edits...
          "311":             # Matches via the Name "311" 
            edits...
        ```

## Metadata Edits

The available attributes for editing movies are as follows

### Special Attributes

| Attribute         | Description                                                                                                                                                                                                                                                                              | Item Types                   |
|:------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------|
| `run_definition`  | Used to specify if this definition runs.<br>Multiple can be used for one definition as a list or comma separated string. One `false` or unmatched library type will cause it to fail.<br>**Values:** `movie`, `show`, `artist`, `true`, `false`                                          | `Movies`, `Shows`, `Artists` |
| `tmdb_show`       | TMDb Show ID to use for metadata. Used when the Movie in your library is actually a miniseries on TMDb. (Example: [Halo 4: Forward Unto Dawn](https://www.themoviedb.org/tv/56295) or [IT](https://www.themoviedb.org/tv/19614)) **This is not used to say this movie is the given ID.** | `Movies`                     |
| `f1_season`       | F1 Season Year to make the Show represent a Season of F1 Races. See [Formula 1 Metadata Guide](../pmm/guides/formula.md) for more information.                                                                                                                                           | `Shows`                      |
| `round_prefix`    | Used only with `f1_season` to add the round as a prefix to the Season (Race) Titles i.e. `Australian Grand Prix` --> `01 - Australian Grand Prix`.                                                                                                                                       | `Shows`                      |
| `shorten_gp`      | Used only with `f1_season` to shorten `Grand Prix` to `GP` in the Season (Race) Titles i.e. `Australian Grand Prix` --> `Australian GP`.                                                                                                                                                 | `Shows`                      |
| `seasons`         | Attribute used to edit season metadata. The mapping name is the season number (use 0 for specials) or the season name.                                                                                                                                                                   | `Shows`                      |
| `episodes`        | Attribute used to edit episode metadata. The mapping name is the episode number in that season, the title of the episode, or the Originally Available date in the format `MM/DD`.                                                                                                        | `Seasons`                    |
| `update_seasons`  | Used to specify if this definition's seasons metadata will update.<br>Multiple can be used for one definition as a list or comma separated string. One `false` will cause it to fail.<br>**Values:** `true`, `false`                                                                     | `Shows`                      |
| `update_episodes` | Used to specify if this definition's episodes metadata will update.<br>Multiple can be used for one definition as a list or comma separated string. One `false` will cause it to fail.<br>**Values:** `true`, `false`                                                                    | `Shows`                      |
| `albums`          | Attribute used to edit album metadata. The mapping name is the album name.                                                                                                                                                                                                               | `Artists`                    |
| `tracks`          | Attribute used to edit track metadata. The mapping name is the track number on that Album, or the title of the Track.                                                                                                                                                                    | `Albums`                     |

1. If the server does not have a Plex Pass then the Edition Field is not accessible. In this case PMM will check the 
movies filepath for `{edition-MOVIES EDITION}` to determine what the edition is.

### General Attributes

| Attribute              | <div style="width:295px">Allowed Values</div>                  | Item Types                                                              |
|:-----------------------|:---------------------------------------------------------------|:------------------------------------------------------------------------|
| `title`                | Text to change Title.                                          | `Movies`, `Shows`, `Seasons`, `Episodes`, `Tracks`                      |
| `sort_title`           | Text to change Sort Title.                                     | `Movies`, `Shows`, `Episodes`, `Artists`, `Albums`, `Tracks`            |
| `edition`<sup>1</sup>  | Text to change Edition.                                        | `Movies`                                                                |
| `original_title`       | Text to change Original Title.                                 | `Movies`, `Shows`                                                       |
| `originally_available` | Date to change Originally Available.<br>**Format:** YYYY-MM-DD | `Movies`, `Shows`, `Episodes`, `Albums`                                 |
| `content_rating`       | Text to change Content Rating.                                 | `Movies`, `Shows`, `Episodes`                                           |
| `user_rating`          | Number to change User Rating.                                  | `Movies`, `Shows`, `Seasons`, `Episodes`, `Artists`, `Albums`, `Tracks` |
| `audience_rating`      | Number to change Audience Rating.                              | `Movies`, `Shows`, `Episodes`                                           |
| `critic_rating`        | Number to change Critic Rating.                                | `Movies`, `Shows`, `Episodes`, `Albums`                                 |
| `studio`               | Text to change Studio.                                         | `Movies`, `Shows`                                                       |
| `tagline`              | Text to change Tagline.                                        | `Movies`, `Shows`                                                       |
| `summary`              | Text to change Summary.                                        | `Movies`, `Shows`, `Seasons`, `Episodes`, `Artists`, `Albums`, `Tracks` |
| `record_label`         | Text to change Record Label.                                   | `Albums`                                                                |
| `track`                | Text to change Track.                                          | `Tracks`                                                                |
| `disc`                 | Text to change Disc.                                           | `Tracks`                                                                |
| `original_artist`      | Text to change Original Artist.                                | `Tracks`                                                                |

1. Requires Plex Pass

### Tag Attributes

You can add `.remove` to any tag attribute to only remove those tags i.e. `genre.remove`.

You can add `.sync` to any tag attribute to sync all tags vs just appending the new ones i.e. `genre.sync`.

| Attribute        | <div style="width:440px">Allowed Values</div>            | Item Types                                                              |
|:-----------------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| `director`       | List or comma-separated text of each Director Tag.       | `Movies`, `Episodes`                                                    |
| `country`        | List or comma-separated text of each Country Tag.        | `Movies`                                                                |
| `genre`          | List or comma-separated text of each Genre Tag.          | `Movies`, `Shows`, `Artists`, `Albums`                                  |
| `writer`         | List or comma-separated text of each Writer Tag.         | `Movies`, `Episodes`                                                    |
| `producer`       | List or comma-separated text of each Producer Tag.       | `Movies`                                                                |
| `collection`     | List or comma-separated text of each Collection Tag.     | `Movies`, `Shows`, `Seasons`, `Episodes`, `Artists`, `Albums`, `Tracks` |
| `label`          | List or comma-separated text of each Label Tag.          | `Movies`, `Shows`, `Seasons`, `Episodes`, `Artists`, `Albums`, `Tracks` |
| `style`          | List or comma-separated text of each Style Tag.          | `Artists`, `Albums`                                                     |
| `mood`           | List or comma-separated text of each Mood Tag.           | `Artists`, `Albums`, `Tracks`                                           |
| `country`        | List or comma-separated text of each Country Tag.        | `Artists`                                                               |
| `similar_artist` | List or comma-separated text of each Similar Artist Tag. | `Artists`                                                               |

### Image Attributes

| Attribute         | <div style="width:365px">Allowed Values</div>    | Item Types                                                    |
|:------------------|:-------------------------------------------------|:--------------------------------------------------------------|
| `url_poster`      | URL of image publicly available on the internet. | `Movies`, `Shows`, `Seasons`, `Episodes`, `Artists`, `Albums` |
| `file_poster`     | Path to image in the file system.                | `Movies`, `Shows`, `Seasons`, `Episodes`, `Artists`, `Albums` |
| `url_background`  | URL of image publicly available on the internet. | `Movies`, `Shows`, `Seasons`, `Episodes`, `Artists`, `Albums` |
| `file_background` | Path to image in the file system.                | `Movies`, `Shows`, `Seasons`, `Episodes`, `Artists`, `Albums` |

### Advanced Attributes

| <div style="width:200px">Attribute</div> | Allowed Values                                                                                                                                                                                                                                                                                                                                                                                                                                                            | <div style="width:110px">Item Types</div> |
|:-----------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------|
| `episode_sorting`                        | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`oldest`</td><td>Oldest first</td></tr><tr><td>`newest`</td><td>Newest first</td></tr></tbody></table>                                                                                                                                                                                                                                                                        | `Shows`                                   |
| `keep_episodes`                          | <table class="clearTable"><tbody><tr><td>`all`</td><td>All episodes</td></tr><tr><td>`5_latest`</td><td>5 latest episodes</td></tr><tr><td>`3_latest`</td><td>3 latest episodes</td></tr><tr><td>`latest`</td><td>Latest episodes</td></tr><tr><td>`past_3`</td><td>Episodes added in the past 3 days</td></tr><tr><td>`past_7`</td><td>Episodes added in the past 7 days</td></tr><tr><td>`past_30`</td><td>Episodes added in the past 30 days</td></tr></tbody></table> | `Shows`                                   |
| `delete_episodes`                        | <table class="clearTable"><tbody><tr><td>`never`</td><td>Never</td></tr><tr><td>`day`</td><td>After a day</td></tr><tr><td>`week`</td><td>After a week</td></tr><tr><td>`refresh`</td><td>On next refresh</td></tr></tbody></table>                                                                                                                                                                                                                                       | `Shows`                                   |
| `season_display`                         | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`show`</td><td>Show</td></tr><tr><td>`hide`</td><td>Hide</td></tr></tbody></table>                                                                                                                                                                                                                                                                                            | `Shows`                                   |
| `episode_ordering`                       | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`tmdb_aired`</td><td>The Movie Database (Aired)</td></tr><tr><td>`tvdb_aired`</td><td>TheTVDb (Aired)</td></tr><tr><td>`tvdb_dvd`</td><td>TheTVDb (DVD)</td></tr><tr><td>`tvdb_absolute`</td><td>TheTVDb (Absolute)</td></tr></tbody></table>                                                                                                                                 | `Shows`                                   |
| `metadata_language`<sup>1</sup>          | `default`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-TW`                                                                       | `Movies`, `Shows`                         |
| `use_original_title`<sup>1</sup>         | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`no`</td><td>No</td></tr><tr><td>`yes`</td><td>Yes</td></tr></tbody></table>                                                                                                                                                                                                                                                                                                  | `Movies`, `Shows`                         |
| `credits_detection`<sup>1</sup>          | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`disabled`</td><td>Disabled</td></tr></tbody></table>                                                                                                                                                                                                                                                                                                                         | `Movies`, `Shows`                         |
| `audio_language`<sup>1</sup>             | `default`, `en`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-TW`                                                                 | `Shows`, `Seasons`                        |
| `subtitle_language`<sup>1</sup>          | `default`, `en`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-TW`                                                                 | `Shows`, `Seasons`                        |
| `subtitle_mode`<sup>1</sup>              | <table class="clearTable"><tbody><tr><td>`default`</td><td>Account default</td></tr><tr><td>`no`</td><td>No</td></tr><tr><td>`yes`</td><td>Yes</td></tr></tbody></table>                                                                                                                                                                                                                                                                                                  | `Shows`, `Seasons`                        |
| `album_sorting`                          | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`manual`</td><td>Manually selected</td></tr><tr><td>`foreign`</td><td>Shown with foreign audio</td></tr><tr><td>`always`</td><td>Always enabled</td></tr></tbody></table>                                                                                                                                                                                                     | `Artists`                                 |

1. Must be using the **New Plex Movie Agent** or the **New Plex TV Agent**
