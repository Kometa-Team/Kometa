# Seasonal Collections

The `seasonal` Default Collection File is used to dynamically create seasonal collections based on holidays .

![](../images/seasonal.png)

## Requirements & Recommendations

Supported Library Types: Movie

## Collections Section 000

| Collection                                    | Key             | Description                                                                    |
|:----------------------------------------------|:----------------|:-------------------------------------------------------------------------------|
| `Seasonal Collections`                        | `separator`     | [Separator Collection](../separators.md) to denote the Section of Collections. |
| `🎊 New Year's Day Movies`                    | `years`         | Collection of Movies related to New Year's Day.                                |
| `💘 Valentine's Day Movies`                   | `valentine`     | Collection of Movies related to Valentine's Day.                               |
| `☘ St. Patrick's Day Movies`                  | `patrick`       | Collection of Movies related to St. Patrick's Day.                             |
| `🐰 Easter Movies`                            | `easter`        | Collection of Movies related to Easter.                                        |
| `🤱 Mother's Day Movies`                      | `mother`        | Collection of Movies related to Mother's Day.                                  |
| `🪖 Memorial Day Movies`                      | `memorial`      | Collection of Movies related to Memorial Day.                                  |
| `👨 Father's Day Movies`                      | `father`        | Collection of Movies related to Father's Day.                                  |
| `🎆 Independence Day Movies`                  | `independence`  | Collection of Movies related to Independence Day.                              |
| `⚒ Labor Day Movies`                          | `labor`         | Collection of Movies related to Labor Day.                                     |
| `🎃 Halloween Movies`                         | `halloween`     | Collection of Movies related to Halloween.                                     |
| `🎖 Veteran's Day Movies`                     | `veteran`       | Collection of Movies related to Veteran's Day.                                 |
| `🦃 Thanksgiving Movies`                      | `thanksgiving`  | Collection of Movies related to Thanksgiving.                                  |
| `🎅 Christmas Movies`                         | `christmas`     | Collection of Movies related to Christmas.                                     |
| `🌊🌺 Asian American Pacific Islander Movies` | `aapi`          | Collection of Movies related to Asian American Pacific Islander Month          |
| `♿ Disability Month Movies`                   | `disabilities`  | Collection of Movies related to Disability Month                               |
| `✊ 🏿 Black History Month Movies`             | `black_history` | Collection of Movies related to Black History Month                            | 
| `🏳️‍🌈 LGBTQ Month Movies`                   | `lgbtq`         | Collection of Movies related to LGBTQ Month                                    | 
| `🪅 National Hispanic Heritage Movies`        | `latinx`        | Collection of Movies related to National Hispanic Heritage Month               |
| `🚺 Women's History Month Movies`             | `women`         | Collection of Movies related to Women's History Month                          |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: seasonal
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this Kometa Defaults file.

    * **Shared Template Variables** are additional variables shared across the Kometa Defaults.

    * **Shared Separator Variables** are additional variables available since this Default contains a 
    [Separator](../separators.md).

    === "File-Specific Template Variables"

        | Variable                              | Description & Values                                                                                                                                                                                                                                                                             |
        |:--------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `tmdb_collection_<<key>>`<sup>1</sup> | **Description:** Adds the TMDb Collection IDs given to the specified key's collection. Overrides the [default tmdb_collection](#tmdb-collection) for that collection if used.<br>**Values:** List of TMDb Collection IDs                                                                         |
        | `tmdb_movie_<<key>>`<sup>1</sup>      | **Description:** Adds the TMDb Movie IDs given to the specified key's collection. Overrides the [default tmdb_movie](#tmdb-movie) for that collection if used.<br>**Values:** List of TMDb Movie IDs                                                                                             |
        | `imdb_list_<<key>>`<sup>1</sup>       | **Description:** Adds the Movies in the IMDb List to the specified key's collection.<br>**Values:** List of IMDb List URLs                                                                                                                                                                       |
        | `imdb_search_<<key>>`<sup>1</sup>     | **Description:** Adds the Movies in the IMDb Search to the specified key's collection. Overrides the [default imdb_search](#imdb-search) for that collection if used.<br>**Values:** List of IMDb List URLs                                                                                      |
        | `trakt_list_<<key>>`<sup>1</sup>      | **Description:** Adds the Movies in the Trakt List to the specified key's collection. Overrides the [default trakt_list](#trakt-list) for that collection if used.<br>**Values:** List of Trakt List URLs                                                                                        |
        | `mdblist_list_<<key>>`<sup>1</sup>    | **Description:** Adds the Movies in the MDb List to the specified key's collection. Overrides the [default mdblist_list](#mdblist-list) for that collection if used.<br>**Values:** List of MDBList URLs                                                                                         |
        | `emoji`                               | **Description:** Controls the Emoji Prefix for all Collections. Set to `""` to remove all emojis.<br>**Values:** Any String                                                                                                                                                                      |
        | `emoji_<<key>>`<sup>1</sup>           | **Description:** Controls the Emoji Prefix for the specified key's collection. Overrides the [default emoji](#emoji) for that collection if used.<br>**Values:** Any String                                                                                                                      |
        | `limit`                               | **Description:** Changes the Builder Limit for all collections in this file.<br>**Values:** Number Greater than 0                                                                                                                                                                                |
        | `limit_<<key>>`<sup>1</sup>           | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                                                       |
        | `sync_mode`                           | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sync_mode_<<key>>`<sup>1</sup>       | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sort_by`                             | **Description:** Changes the Smart Filter Sort for all collections in this file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                      |
        | `sort_by_<<key>>`<sup>1</sup>         | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                          |
        | `schedule`                            | **Description:** Changes the Schedule for all collections in this file. Use `daily` to have all collections show.<br>**Values:** [Any Schedule Option](../../config/schedule.md)                                                                                                                 |
        | `schedule_<<key>>`<sup>1</sup>        | **Description:** Changes the Schedule of the specified key's collection. Overrides the [default schedule](#schedule) for that collection if used.<br>**Values:** [Any Schedule Option](../../config/schedule.md)                                                                                 |
        | `data`                                | **Description:** Overrides the [default data dictionary](#data). Defines the data that the custom dynamic collection processes.<br>**Values:** Dictionary List of keys/names                                                                                                                     |
        | `append_data`                         | **Description:** Appends to the [default data dictionary](#data).<br>**Values:** Dictionary List of keys/names                                                                                                                                                                                   |
        | `remove_data`                         | **Description:** Removes from the [default data dictionary](#data).<br>**Values:** List of keys to remove                                                                                                                                                                                        |
        | `exclude`                             | **Description:** Exclude these Seasons from creating a Dynamic Collection.<br>**Values:** List of Seasons Keys                                                                                                                                                                                   |
        | `name_format`                         | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                              |
        | `summary_format`                      | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `A collection of <<key_name>> <<library_translation>>s that may relate to the season.`<br>**Values:** Any string.                                                                                        |

        1. Each default collection has a `key` that when calling to effect a specific collection you must replace 
        `<<key>>` with when calling.

    === "Shared Template Variables"

        {%
          include-markdown "../collection_variables.md"
        %}

    === "Shared Separator Variables"

        {%
          include-markdown "../separator_variables.md"
        %}
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    Click the :fontawesome-solid-circle-plus: icon to learn more
    
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: seasonal
            template_variables:
              use_independence: false #(1)!
              schedule_thanksgiving: range(10/01-10/30) #(2)!
              sort_by: random #(3)!
              append_data:
                apes: Planet of the Apes Day #(4)!
              schedule_apes: range(11/24-11/26) #(5)!
              imdb_list_apes: https://www.imdb.com/list/ls005126084/ #(6)!
              emoji_veteran: "🐵 " #(7)!
    ```

    1.  Do not create the "Independence Day" collection
    2.  Set a custom schedule for the Thanksgiving Day collection
    3.  Sort the collections created by this file in random order
    4.  Create a new Seasonal collection called "Planet of the Apes Day", and set the key for this collection to `apes`
    5.  Set a scheduled range for the "Planet of the Apes Day" collection.  Planet Of The Apes Day is 11/25.
    6.  Add an IMDb List to be used for the "Planet of the Apes Day" collection
    7.  Add the 🐵 emoji to the "Planet of the Apes Day" collection so that the title in Plex is "🐵 Planet of the Apes 
    Day Movies"

## Default Values

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not 
show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default `data` (click to expand) <a class="headerlink" href="#data" title="Permanent link">¶</a>"

    <div id="data" />

    ```yaml
    data: {%    
      include-markdown "../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=false
      start="data:"
      end="title_format:"
    %}
    ```

??? example "Default Template Variable `emoji` (click to expand) <a class="headerlink" href="#emoji" title="Permanent link">¶</a>"

    <div id="emoji" />
    
    ???+ tip 
    
        Pass `emoji_<<key>>` to the file as template variables to change this value per collection.

    ```yaml
    {%    
      include-markdown "../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check1"
      end="# check2"
    %}
    ```

??? example "Default Template Variable `schedule` (click to expand) <a class="headerlink" href="#schedule" title="Permanent link">¶</a>"

    <div id="schedule" />
    
    ???+ tip 
    
        Pass `schedule_<<key>>` to the file as template variables to change this value per collection.

    ```yaml
    {%    
      include-markdown "../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check2"
      end="# check3"
    %}
    ```

??? example "Default Template Variable `imdb_search` (click to expand) <a class="headerlink" href="#imdb-search" title="Permanent link">¶</a>"

    <div id="imdb-search" />
    
    ???+ tip 
    
        Pass `imdb_search_<<key>>` to the file as template variables to change this value per collection.

    ```yaml
    {%    
      include-markdown "../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check4"
      end="# check5"
    %}
    ```

??? example "Default Template Variable `tmdb_collection` (click to expand) <a class="headerlink" href="#tmdb-collection" title="Permanent link">¶</a>"

    <div id="tmdb-collection" />
    
    ???+ tip 
    
        Pass `tmdb_collection_<<key>>` to the file as template variables to change this value per collection.

    ```yaml
    {%    
      include-markdown "../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check5"
      end="# check6"
    %}
    ```

??? example "Default Template Variable `tmdb_movie` (click to expand) <a class="headerlink" href="#tmdb-movie" title="Permanent link">¶</a>"

    <div id="tmdb-movie" />
    
    ???+ tip 
    
        Pass `tmdb_movie_<<key>>` to the file as template variables to change this value per collection.

    ```yaml
    {%    
      include-markdown "../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check6"
      end="# check7"
    %}
    ```

??? example "Default Template Variable `mdblist_list` (click to expand) <a class="headerlink" href="#mdblist-list" title="Permanent link">¶</a>"

    <div id="mdblist-list" />
    
    ???+ tip 
    
        Pass `mdblist_list_<<key>>` to the file as template variables to change this value per collection.

    ```yaml
    {%    
      include-markdown "../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check7"
      end="# check8"
    %}
    ```

??? example "Default Template Variable `trakt_list` (click to expand) <a class="headerlink" href="#trakt-list" title="Permanent link">¶</a>"

    <div id="trakt-list" />
    
    ???+ tip 
    
        Pass `trakt_list_<<key>>` to the file as template variables to change this value per collection.

    ```yaml
    {%    
      include-markdown "../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check8"
      end="# check9"
    %}
    ```
