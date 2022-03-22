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
    sort_title: Avatar 02
    alt_title: The Legend of Korra
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

## Shows

Each show is defined by the mapping name which must be the same as the show name in the library unless an `alt_title` is specified.

### Seasons

To edit the metadata of a particular Season in a Show use the `seasons` attribute on its show.

The mapping name is the season number (use 0 for specials) or the season name.

### Episodes

To edit the metadata of a particular Episode in a Season use the `episodes` attribute on its season.

The mapping name is the episode number in that season or the title of the episode.

## Metadata Edits

The available attributes for editing shows, seasons, and episodes are as follows

### Special Attributes

| Attribute      | Values                                                                                                                                            |  Shows   | Seasons  | Episodes |
|:---------------|:--------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|:--------:|:--------:|
| `title`        | Title if different from the mapping value useful when you have multiple shows with the same name                                                  | &#9989;  | &#9989;  | &#9989;  |
| `alt_title`    | Alternative title to look for                                                                                                                     | &#9989;  | &#10060; | &#10060; |
| `year`         | Year of show for better identification                                                                                                            | &#9989;  | &#10060; | &#10060; |
| `tmdb_show`    | TMDb Show ID to use for metadata useful for miniseries that have been compiled into a movie                                                       | &#9989;  | &#10060; | &#10060; |
| `tmdb_movie`   | TMDb Movie ID to use for metadata useful for movies that have been split into segments                                                            | &#9989;  | &#10060; | &#10060; |
| `f1_season`    | F1 Season Year to make the Show represent a Season of F1 Races                                                                                    | &#9989;  | &#10060; | &#10060; |
| `round_prefix` | Used only with `f1_season` to add the round as a prefix to the Season (Race) Titles i.e. `Australian Grand Prix` --> `01 - Australian Grand Prix` | &#9989;  | &#10060; | &#10060; |
| `shorten_gp`   | Used only with `f1_season` to shorten `Grand Prix` to `GP` in the Season (Race) Titles i.e. `Australian Grand Prix` --> `Australian GP`           | &#9989;  | &#10060; | &#10060; |
| `seasons`      | Mapping to define Seasons                                                                                                                         | &#9989;  | &#10060; | &#10060; |
| `episodes`     | Mapping to define Episodes                                                                                                                        | &#10060; | &#9989;  | &#10060; |

* YAML files cannot have two items with the same mapping name so if you have two shows with the same name you would change the mapping values to whatever you want. Then use the `title` attribute to specify the real title and use the `year` attribute to specify which of the multiple shows to choose.
    ```yaml
    metadata:
      Godzilla1:
        title: Godzilla
        year: 1954
        content_rating: R
      Godzilla2:
        title: Godzilla
        year: 1998
        content_rating: PG-13
    ```

* If you know of another Title your show might exist under, but you want it titled differently you can use `alt_title` to specify another title to look under and then be changed to the mapping name. For Example TMDb uses the name `The Legend of Korra`, but I want it as `Avatar: The Legend of Korra` (Which must be surrounded by quotes since it uses the character `:`):
    ```yaml
    metadata:
      "Avatar: The Legend of Korra":
        alt_title: The Legend of Korra
    ```
    This would change the name of the TMDb default `The Legend of Korra` to `Avatar: The Legend of Korra` and would not mess up any subsequent runs.

### General Attributes

| Attribute              | Values                                                        |  Shows   | Seasons  | Episodes |
|:-----------------------|:--------------------------------------------------------------|:--------:|:--------:|:--------:|
| `title`                | Text to change Title                                          | &#10060; | &#9989;  | &#9989;  |
| `sort_title`           | Text to change Sort Title                                     | &#9989;  | &#10060; | &#9989;  |
| `original_title`       | Text to change Original Title                                 | &#9989;  | &#10060; | &#9989;  |
| `originally_available` | Date to change Originally Available<br>**Format:** YYYY-MM-DD | &#9989;  | &#10060; | &#9989;  |
| `content_rating`       | Text to change Content Rating                                 | &#9989;  | &#10060; | &#10060; |
| `user_rating`          | Number to change User Rating                                  | &#9989;  | &#9989;  | &#9989;  |
| `audience_rating`      | Number to change Audience Rating                              | &#9989;  | &#10060; | &#9989;  |
| `critic_rating`        | Number to change Critic Rating                                | &#9989;  | &#10060; | &#9989;  |
| `studio`               | Text to change Studio                                         | &#9989;  | &#10060; | &#10060; |
| `tagline`              | Text to change Tagline                                        | &#9989;  | &#10060; | &#10060; |
| `summary`              | Text to change Summary                                        | &#9989;  | &#9989;  | &#9989;  |

### Tag Attributes

You can add `.remove` to any tag attribute to only remove those tags i.e. `genre.remove`.

You can add `.sync` to any tag attribute to sync all tags vs just appending the new ones i.e. `genre.sync`.

| Attribute    | Values                                              |  Shows   | Seasons  | Episodes |
|:-------------|:----------------------------------------------------|:--------:|:--------:|:--------:|
| `director`   | List or comma-separated text of each Director Tag   | &#10060; | &#10060; | &#9989;  |
| `genre`      | List or comma-separated text of each Genre Tag      | &#9989;  | &#10060; | &#10060; |
| `writer`     | List or comma-separated text of each Writer Tag     | &#10060; | &#10060; | &#9989;  |
| `collection` | List or comma-separated text of each Collection Tag | &#9989;  | &#10060; | &#10060; |
| `label`      | List or comma-separated text of each Label Tag      | &#9989;  | &#10060; | &#10060; |

### Image Attributes

| Attribute         | Values                                          |  Shows  | Seasons | Episodes |
|:------------------|:------------------------------------------------|:-------:|:-------:|:--------:|
| `url_poster`      | URL of image publicly available on the internet | &#9989; | &#9989; | &#9989;  |
| `file_poster`     | Path to image in the file system                | &#9989; | &#9989; | &#9989;  |
| `url_background`  | URL of image publicly available on the internet | &#9989; | &#9989; | &#10060; |
| `file_background` | Path to image in the file system                | &#9989; | &#9989; | &#10060; |

### Advanced Attributes

All these attributes only work with Shows.

| Attribute                        | Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|:---------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `episode_sorting`                | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`oldest`</td><td>Oldest first</td></tr><tr><td>`newest`</td><td>Newest first</td></tr></tbody></table>                                                                                                                                                                                                                                                                        |
| `keep_episodes`                  | <table class="clearTable"><tbody><tr><td>`all`</td><td>All episodes</td></tr><tr><td>`5_latest`</td><td>5 latest episodes</td></tr><tr><td>`3_latest`</td><td>3 latest episodes</td></tr><tr><td>`latest`</td><td>Latest episodes</td></tr><tr><td>`past_3`</td><td>Episodes added in the past 3 days</td></tr><tr><td>`past_7`</td><td>Episodes added in the past 7 days</td></tr><tr><td>`past_30`</td><td>Episodes added in the past 30 days</td></tr></tbody></table> |
| `delete_episodes`                | <table class="clearTable"><tbody><tr><td>`never`</td><td>Never</td></tr><tr><td>`day`</td><td>After a day</td></tr><tr><td>`week`</td><td>After a week</td></tr><tr><td>`refresh`</td><td>On next refresh</td></tr></tbody></table>                                                                                                                                                                                                                                       |
| `season_display`                 | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`show`</td><td>Show</td></tr><tr><td>`hide`</td><td>Hide</td></tr></tbody></table>                                                                                                                                                                                                                                                                                            |
| `episode_ordering`               | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`tmdb_aired`</td><td>The Movie Database (Aired)</td></tr><tr><td>`tvdb_aired`</td><td>TheTVDb (Aired)</td></tr><tr><td>`tvdb_dvd`</td><td>TheTVDb (DVD)</td></tr><tr><td>`tvdb_absolute`</td><td>TheTVDb (Absolute)</td></tr></tbody></table>                                                                                                                                 |
| `metadata_language`<sup>1</sup>  | `default`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-TW`                                                                       |
| `use_original_title`<sup>1</sup> | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`no`</td><td>No</td></tr><tr><td>`yes`</td><td>Yes</td></tr></tbody></table>                                                                                                                                                                                                                                                                                                  |

<sup>1</sup> Must be using the **New Plex TV Agent**
