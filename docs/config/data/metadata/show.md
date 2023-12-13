# TV Show Library Metadata

You can have the script edit the metadata of Shows, Seasons, and Episodes by adding them to the `metadata` mapping of a Metadata File.

An example of multiple metadata edits in a show library is below:
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

## Matching Shows

The `match` attribute is used to match shows within Plex to that definition within the Metadata file. One definition can match and edit multiple shows. The available matching options are outlined below.

| Attribute                      | Allowed Values                                                                                                    |
|:-------------------------------|:------------------------------------------------------------------------------------------------------------------|
| `title`<sup>1</sup>            | Only matches shows that exactly match the show's Title. Can be a list (only one needs to match).                  |
| `year`                         | Only matches shows that were released in the given year.                                                          |
| `mapping_id`<sup>2</sup>       | Only matches shows that have the given TVDb or IMDb ID.                                                           |

1. When `title` is not provided and the mapping name was not specified as an ID, the default behaviour is to use the mapping name as `title` for matching.
2. When `mapping_id` is not provided and the mapping name was specified as an ID, the default behaviour is to use the mapping name as `mapping_id` for matching.

### Examples

Below are some examples on how shows can be matched.

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

**Note:** to search for a show titled with a number from the mapping name you must surround the number in quotes like in the example below. Otherwise, it will look for the show associated with that TVDb ID.

#### Example 2 - `title` and `year`

The below example shows how `title` and `year` can be used to match shows. 

In this example, there are two shows in the library called "Vikings", so the `year` attribute is used to identify which show is being matched.

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

## Metadata Edits

The available attributes for editing shows, seasons, and episodes are as follows

### Special Attributes

| Attribute         | Description                                                                                                                                                                                                                                       |                   Shows                    |                  Seasons                   |                 Episodes                 |
|:------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:----------------------------------------:|
| `f1_season`       | F1 Season Year to make the Show represent a Season of F1 Races. See [Formula 1 Metadata Guide](../../../pmm/install/guides/formula.md) for more information.                                                                                      | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |
| `round_prefix`    | Used only with `f1_season` to add the round as a prefix to the Season (Race) Titles i.e. `Australian Grand Prix` --> `01 - Australian Grand Prix`.                                                                                                | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |
| `shorten_gp`      | Used only with `f1_season` to shorten `Grand Prix` to `GP` in the Season (Race) Titles i.e. `Australian Grand Prix` --> `Australian GP`.                                                                                                          | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |
| `seasons`         | Attribute used to edit season metadata. The mapping name is the season number (use 0 for specials) or the season name.                                                                                                                            | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |
| `episodes`        | Attribute used to edit episode metadata. The mapping name is the episode number in that season, the title of the episode, or the Originally Available date in the format `MM/DD`.                                                                 |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| `run_definition`  | Used to specify if this definition runs.<br>Multiple can be used for one definition as a list or comma separated string. One `false` or unmatched library type will cause it to fail.<br>**Values:** `movie`, `show`, `artist`, `true`, `false`   | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |
| `update_seasons`  | Used to specify if this definition's seasons metadata will update.<br>Multiple can be used for one definition as a list or comma separated string. One `false` will cause it to fail.<br>**Values:** `true`, `false`                              | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |
| `update_episodes` | Used to specify if this definition's episodes metadata will update.<br>Multiple can be used for one definition as a list or comma separated string. One `false` will cause it to fail.<br>**Values:** `true`, `false`                             | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } |

### General Attributes

| Attribute              | Allowed Values                                                 |                   Shows                    |                  Seasons                   |                  Episodes                  |
|:-----------------------|:---------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| `title`                | Text to change Title.                                          | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| `sort_title`           | Text to change Sort Title.                                     | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| `original_title`       | Text to change Original Title.                                 | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| `originally_available` | Date to change Originally Available.<br>**Format:** YYYY-MM-DD | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| `content_rating`       | Text to change Content Rating.                                 | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| `user_rating`          | Number to change User Rating.                                  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| `audience_rating`      | Number to change Audience Rating.                              | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| `critic_rating`        | Number to change Critic Rating.                                | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| `studio`               | Text to change Studio.                                         | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| `tagline`              | Text to change Tagline.                                        | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| `summary`              | Text to change Summary.                                        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

### Tag Attributes

You can add `.remove` to any tag attribute to only remove those tags i.e. `genre.remove`.

You can add `.sync` to any tag attribute to sync all tags vs just appending the new ones i.e. `genre.sync`.

| Attribute    | Allowed Values                                       |                   Shows                    |                  Seasons                   |                  Episodes                  |
|:-------------|:-----------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| `director`   | List or comma-separated text of each Director Tag.   |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| `genre`      | List or comma-separated text of each Genre Tag.      | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |
| `writer`     | List or comma-separated text of each Writer Tag.     |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| `collection` | List or comma-separated text of each Collection Tag. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| `label`      | List or comma-separated text of each Label Tag.      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

### Image Attributes

| Attribute         | Allowed Values                                   |                   Shows                    |                  Seasons                   |                  Episodes                  |
|:------------------|:-------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| `url_poster`      | URL of image publicly available on the internet. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| `file_poster`     | Path to image in the file system.                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| `url_background`  | URL of image publicly available on the internet. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| `file_background` | Path to image in the file system.                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

### Advanced Attributes

All these attributes only work with Shows.

| Attribute                        | Allowed Values                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|:---------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `episode_sorting`                | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`oldest`</td><td>Oldest first</td></tr><tr><td>`newest`</td><td>Newest first</td></tr></tbody></table>                                                                                                                                                                                                                                                                        |
| `keep_episodes`                  | <table class="clearTable"><tbody><tr><td>`all`</td><td>All episodes</td></tr><tr><td>`5_latest`</td><td>5 latest episodes</td></tr><tr><td>`3_latest`</td><td>3 latest episodes</td></tr><tr><td>`latest`</td><td>Latest episodes</td></tr><tr><td>`past_3`</td><td>Episodes added in the past 3 days</td></tr><tr><td>`past_7`</td><td>Episodes added in the past 7 days</td></tr><tr><td>`past_30`</td><td>Episodes added in the past 30 days</td></tr></tbody></table> |
| `delete_episodes`                | <table class="clearTable"><tbody><tr><td>`never`</td><td>Never</td></tr><tr><td>`day`</td><td>After a day</td></tr><tr><td>`week`</td><td>After a week</td></tr><tr><td>`refresh`</td><td>On next refresh</td></tr></tbody></table>                                                                                                                                                                                                                                       |
| `season_display`                 | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`show`</td><td>Show</td></tr><tr><td>`hide`</td><td>Hide</td></tr></tbody></table>                                                                                                                                                                                                                                                                                            |
| `episode_ordering`               | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`tmdb_aired`</td><td>The Movie Database (Aired)</td></tr><tr><td>`tvdb_aired`</td><td>TheTVDb (Aired)</td></tr><tr><td>`tvdb_dvd`</td><td>TheTVDb (DVD)</td></tr><tr><td>`tvdb_absolute`</td><td>TheTVDb (Absolute)</td></tr></tbody></table>                                                                                                                                 |
| `metadata_language`<sup>1</sup>  | `default`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-TW`                                                                       |
| `use_original_title`<sup>1</sup> | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`no`</td><td>No</td></tr><tr><td>`yes`</td><td>Yes</td></tr></tbody></table>                                                                                                                                                                                                                                                                                                  |

1. Must be using the **New Plex TV Agent**