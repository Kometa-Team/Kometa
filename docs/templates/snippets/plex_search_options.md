
=== "Search Options"

    When using a Plex Builder, there are three elements that correlate to Plex's Advanced Filters in the Web UI.
    
    -  **Attribute:** What attribute you wish to filter.
    -  **Modifier:** Which modifier to use.
    -  **Value:** Actual value to filter.
    
    These three elements combined would look like `attribute.modifier: value`, in a Builder this may be something like `title.not: Harry Potter` or `episode_added: 7`.

    Attribute and Value elements are mandatory, whilst modifiers are optional. Typically speaking, Plex will have a default modifier of "is" or "contains" if you do not specify a modifier.

    The majority of Smart and Manual Builders utilize the same Search Options, meaning that the criteria for the builders is largely interchangeable between the two. Any deviation from this will be highlighted against the specific Builder.

    === "Boolean Filters"
        
        Boolean Filters take no modifier and can only be either `true` or `false`.
        
        #### Boolean Filter Attributes
        
        | Boolean Search      | Description            |             Movie<br>Libraries             |             Show<br>Libraries              |             Music<br>Libraries             |
        |:--------------------|:-----------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
        | `hdr`               | Is HDR                 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `unmatched`         | Is Unmatched           | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `duplicate`         | Is Duplicate           | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `unplayed`          | Is Unplayed            | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `progress`          | Is In Progress         | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `trash`             | Is Trashed             | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `unplayed_episodes` | Has Unplayed Episodes  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_unplayed`  | Has Episodes Unplayed  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_duplicate` | Has Duplicate Episodes |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_progress`  | Has Episode Progress   |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_unmatched` | Has Episodes Unmatched |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `show_unmatched`    | Has Shows Unmatched    |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `artist_unmatched`  | Is Artist's Unmatched  |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_unmatched`   | Is Album's Unmatched   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_trash`       | Is Track Trashed       |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        
    === "Date Filters"
        
        Date filters can be used with either no modifier or with `.not`, `.before`, or `.after`.
        
        No date filter can take multiple values.
        

        #### Date Filter Attributes
        
        | Date Search           | Description                                                                        |             Movie<br>Libraries             |             Show<br>Libraries              |             Music<br>Libraries             |
        |:----------------------|:-----------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
        | `added`               | Uses the date added attribute to match                                             | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_added`       | Uses the date added attribute of the show's episodes to match                      |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `release`             | Uses the release date attribute (originally available) to match                    | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_air_date`    | Uses the air date attribute (originally available) of the show's episodes to match |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `last_played`         | Uses the date last played attribute to match                                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_last_played` | Uses the date last played attribute of the show's episodes to match                |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `artist_added`        | Uses the Artist's date added attribute to match                                    |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `artist_last_played`  | Uses the Artist's last played attribute to match                                   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_last_played`   | Uses the Album's last played attribute to match                                    |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_added`         | Uses the Album's date added attribute to match                                     |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_released`      | Uses the Album's release date attribute to match                                   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_last_played`   | Uses the Track's date last played attribute to match                               |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_last_skipped`  | Uses the Track's date last skipped attribute to match                              |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_last_rated`    | Uses the Track's date last rated attribute to match                                |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_added`         | Uses the Track's date added attribute to match                                     |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        
        ???+ tip "Date Filter Modifiers"
            
            | Date Modifier | Description                                                                                                                                                | Plex Web UI Display  |
            |:--------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------:|
            | No Modifier   | Matches every item where the date attribute is in the last X days<br>**Format:** number of days<br>**Example:** `30`                                       |   `is in the last`   |
            | `.not`        | Matches every item where the date attribute is not in the last X days<br>**Format:** number of days<br>**Example:** `30`                                   | `is not in the last` |
            | `.before`     | Matches every item where the date attribute is before the given date<br>**Format:** MM/DD/YYYY or `today` for the current day<br>**Example:** `01/01/2000` |     `is before`      |
            | `.after`      | Matches every item where the date attribute is after the given date<br>**Format:** MM/DD/YYYY or `today` for the current day<br>**Example:** `01/01/2000`  |      `is after`      |
            
    === "Number Filters"
    
        Number filters must use `.gt`, `.gte`, `.lt`, or `.lte` as a modifier only the rating filters can use `.rated`.
        
        No number filter can take multiple values.
        
        #### Number Filter Attributes
        
        | Number Search              | Description                                                                                 |             Movie<br>Libraries             |             Show<br>Libraries              |             Music<br>Libraries             |
        |:---------------------------|:--------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
        | `duration`                 | Uses the duration attribute to match using minutes<br>**Minimum:** `0`                      | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `plays`                    | Uses the plays attribute to match<br>**Minimum:** `0`                                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_plays`            | Uses the Episode's plays attribute to match<br>**Minimum:** `0`                             |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `critic_rating`            | Uses the critic rating attribute to match<br>**Range:** `0.0` - `10.0`                      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `audience_rating`          | Uses the audience rating attribute to match<br>**Range:** `0.0` - `10.0`                    | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `user_rating`              | Uses the user rating attribute to match<br>**Range:** `0.0` - `10.0`                        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_user_rating`      | Uses the user rating attribute of the show's episodes to match<br>**Range:** `0.0` - `10.0` |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `year`<sup>**1**</sup>         | Uses the year attribute to match<br>**Minimum:** `0`                                        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_year`<sup>**1**</sup> | Uses the Episode's year attribute to match<br> **Minimum:** `0`                             |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `album_year`<sup>**1**</sup>   | Uses the Album's year attribute to match<br>**Minimum:** `0`                                |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_decade`<sup>**1**</sup> | Uses the Album's decade attribute to match<br>**Minimum:** `0`                              |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_plays`              | Uses the Album's plays attribute to match<br>**Minimum:** `0`                               |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_plays`              | Uses the Track's plays attribute to match<br>**Minimum:** `0`                               |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_skips`              | Uses the Track's skips attribute to match<br>**Minimum:** `0`                               |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `artist_user_rating`       | Uses the Artist's user rating attribute to match<br>**Range:** `0.0` - `10.0`               |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_user_rating`        | Uses the Album's user rating attribute to match<br>**Range:** `0.0` - `10.0`                |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_critic_rating`      | Uses the Album's critic rating attribute to match<br>**Range:** `0.0` - `10.0`              |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_user_rating`        | Uses the Track's user rating attribute to match<br>**Range:** `0.0` - `10.0`                |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        
        <sup>**1**</sup> You can use `current_year` to have Kometa use the current years value. This can be combined with a 
        `-#` at the end to subtract that number of years. i.e. `current_year-2`

        ???+ tip "Number Filter Modifiers"
        
            | Number Modifier | Description                                                                                                                                             | Plex Web UI Display |
            |:----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------:|
            | `.gt`           | Matches every item where the number attribute is greater than the given number<br>**Format:** number<br>**Example:** `30`, `1995`, or `7.5`             |  `is greater than`  |
            | `.gte`          | Matches every item where the number attribute is greater than or equal to the given number<br>**Format:** number<br>**Example:** `30`, `1995`, or `7.5` |         N/A         |
            | `.lt`           | Matches every item where the number attribute is less than the given number<br>**Format:** number<br>**Example:** `30`, `1995`, or `7.5`                |   `is less than`    |
            | `.lte`          | Matches every item where the number attribute is less than or equal to the given number<br>**Format:** number<br>**Example:** `30`, `1995`, or `7.5`    |         N/A         |
            | `.rated`        | Matches every item either rated or not rated<br>**Format:** `true` or `false`                                                                           |         N/A         |
            
            * `.rated` only works for rating filters

    === "String Filters"
    
        String filters can be used with either no modifier or with `.not`, `.is`, `.isnot`, `.begins`, or `.ends`.
        
        String filter can take multiple values **only as a list**.
        
        #### String Filter Attributes
        
        | String Search        | Description                                              |             Movie<br>Libraries             |             Show<br>Libraries              |             Music<br>Libraries             |
        |:---------------------|:---------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
        | `title`              | Uses the title attribute to match                        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_title`      | Uses the title attribute of the show's episodes to match |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `studio`             | Uses the studio attribute to match                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `edition`            | Uses the edition attribute to match                      | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `artist_title`       | Uses the Artist's Title attribute to match               |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_title`        | Uses the Album's Title attribute to match                |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_title`        | Uses the Track's Title attribute to match                |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_record_label` | Uses the Album's Record Label attribute to match         |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |

        ???+ tip "String Filter Modifiers"
        
            | String Modifier | Description                                                                    | Plex Web UI Display |
            |:----------------|:-------------------------------------------------------------------------------|:-------------------:|
            | No Modifier     | Matches every item where the attribute contains the given string               |     `contains`      |
            | `.not`          | Matches every item where the attribute does not contain the given string       | `does not contain`  |
            | `.is`           | Matches every item where the attribute exactly matches the given string        |        `is`         |
            | `.isnot`        | Matches every item where the attribute does not exactly match the given string |      `is not`       |
            | `.begins`       | Matches every item where the attribute begins with the given string            |    `begins with`    |
            | `.ends`         | Matches every item where the attribute ends with the given string              |     `ends with`     |

    === "Tag Filters"
        
        Tag filters can be used with either no modifier or with `.not` except for `decade` and `resolution` which can only be 
        used with no modifier.
        
        Tag filter can take multiple values as a **list or a comma-separated string**.
         
        #### Tag Filter Attributes
        
        | Tag Search                 | Description                                                                 |             Movie<br>Libraries             |             Show<br>Libraries              |             Music<br>Libraries             |
        |:---------------------------|:----------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
        | `actor`                    | Uses the actor tags to match                                                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_actor`            | Uses the episode actor tags to match                                        |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `audio_language`           | Uses the audio language tags to match                                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `collection`               | Uses the collection tags to match for top level collections                 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `season_collection`        | Uses the collection tags to match for season collections                    |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_collection`       | Uses the collection tags to match for episode collections                   |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `content_rating`           | Uses the content rating tags to match                                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `country`                  | Uses the country tags to match                                              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `decade`<sup>**1**</sup>       | Uses the year tag to match the decade                                       | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `director`                 | Uses the director tags to match                                             | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `genre`                    | Uses the genre tags to match                                                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `label`                    | Uses the label tags to match for top level collections                      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `season_label`             | Uses the label tags to match for season collections                         |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_label`            | Uses the label tags to match for episode collections                        |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `network`                  | Uses the network tags to match<br>**Only works with the New Plex TV Agent** |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `producer`                 | Uses the actor tags to match                                                | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `resolution`               | Uses the resolution tags to match                                           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `subtitle_language`        | Uses the subtitle language tags to match                                    | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `writer`                   | Uses the writer tags to match                                               | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `year`<sup>**1**</sup>         | Uses the year tag to match                                                  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `episode_year`<sup>**1**</sup> | Uses the year tag to match                                                  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
        | `artist_genre`             | Uses the Artist's Genre attribute to match                                  |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `artist_collection`        | Uses the Artist's Collection attribute to match                             |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `artist_country`           | Uses the Artist's Country attribute to match                                |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `artist_mood`              | Uses the Artist's Mood attribute to match                                   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `artist_style`             | Uses the Artist's Style attribute to match                                  |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `artist_label`             | Uses the Artist's Label attribute to match                                  |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_genre`              | Uses the Album's Genre attribute to match                                   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_mood`               | Uses the Album's Mood attribute to match                                    |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_style`              | Uses the Album's Style attribute to match                                   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_format`             | Uses the Album's Format attribute to match                                  |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_type`               | Uses the Album's Type attribute to match                                    |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_collection`         | Uses the Album's Collection attribute to match                              |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_source`             | Uses the Album's Source attribute to match                                  |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `album_label`              | Uses the Album's Label attribute to match                                   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_mood`               | Uses the Track's Mood attribute to match                                    |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_source`             | Uses the Track's Source attribute to match                                  |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        | `track_label`              | Uses the Track's Label attribute to match                                   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
        
        <sup>**1**</sup> You can use `current_year` to have Kometa use the current years value. This can be combined with a 
        `-#` at the end to subtract that number of years. i.e. `current_year-2`

        ???+ tip "Tag Filter Modifiers" 

            | Tag Modifier | Description                                                            | Plex Web UI Display |
            |:-------------|:-----------------------------------------------------------------------|:-------------------:|
            | No Modifier  | Matches every item where the attribute matches the given string        |        `is`         |
            | `.not`       | Matches every item where the attribute does not match the given string |      `is not`       |

