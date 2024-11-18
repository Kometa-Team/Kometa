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
        | `tmdb_collection_<<key>>`<sup>1</sup> | **Description:** Adds the TMDb Collection IDs given to the specified key's collection. Overrides the [default tmdb_collection](#default-values) for that collection if used.<br>**Values:** List of TMDb Collection IDs                                                                         |
        | `tmdb_movie_<<key>>`<sup>1</sup>      | **Description:** Adds the TMDb Movie IDs given to the specified key's collection. Overrides the [default tmdb_movie](#default-values) for that collection if used.<br>**Values:** List of TMDb Movie IDs                                                                                             |
        | `imdb_list_<<key>>`<sup>1</sup>       | **Description:** Adds the Movies in the IMDb List to the specified key's collection.<br>**Values:** List of IMDb List URLs                                                                                                                                                                       |
        | `imdb_search_<<key>>`<sup>1</sup>     | **Description:** Adds the Movies in the IMDb Search to the specified key's collection. Overrides the [default imdb_search](#default-values) for that collection if used.<br>**Values:** List of IMDb List URLs                                                                                      |
        | `trakt_list_<<key>>`<sup>1</sup>      | **Description:** Adds the Movies in the Trakt List to the specified key's collection. Overrides the [default trakt_list](#default-values) for that collection if used.<br>**Values:** List of Trakt List URLs                                                                                        |
        | `mdblist_list_<<key>>`<sup>1</sup>    | **Description:** Adds the Movies in the MDb List to the specified key's collection. Overrides the [default mdblist_list](#default-values) for that collection if used.<br>**Values:** List of MDBList URLs                                                                                         |
        | `letterboxd_list_<<key>>`<sup>1</sup> | **Description:** Adds the Movies in the Letterboxd List to the specified key's collection.<br>**Values:** List of Letterboxd List URLs                                                                                                                                                           |
        | `emoji`                               | **Description:** Controls the Emoji Prefix for all Collections. Set to `""` to remove all emojis.<br>**Values:** Any String                                                                                                                                                                      |
        | `emoji_<<key>>`<sup>1</sup>           | **Description:** Controls the Emoji Prefix for the specified key's collection. Overrides the [default emoji](#default-values) for that collection if used.<br>**Values:** Any String                                                                                                                      |
        | `limit`                               | **Description:** Changes the Builder Limit for all collections in this file.<br>**Values:** Number Greater than 0                                                                                                                                                                                |
        | `limit_<<key>>`<sup>1</sup>           | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                                                       |
        | `sync_mode`                           | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sync_mode_<<key>>`<sup>1</sup>       | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sort_by`                             | **Description:** Changes the Smart Filter Sort for all collections in this file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                      |
        | `sort_by_<<key>>`<sup>1</sup>         | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                          |
        | `schedule`                            | **Description:** Changes the Schedule for all collections in this file. Use `daily` to have all collections show.<br>**Values:** [Any Schedule Option](../../config/schedule.md)                                                                                                                 |
        | `schedule_<<key>>`<sup>1</sup>        | **Description:** Changes the Schedule of the specified key's collection. Overrides the [default schedule](#default-values) for that collection if used.<br>**Values:** [Any Schedule Option](../../config/schedule.md)                                                                                 |
        | `data`                                | **Description:** Overrides the [default data dictionary](#default-values). Defines the data that the custom dynamic collection processes.<br>**Values:** Dictionary List of keys/names                                                                                                                     |
        | `append_data`                         | **Description:** Appends to the [default data dictionary](#default-values).<br>**Values:** Dictionary List of keys/names                                                                                                                                                                                   |
        | `remove_data`                         | **Description:** Removes from the [default data dictionary](#default-values).<br>**Values:** List of keys to remove                                                                                                                                                                                        |
        | `exclude`                             | **Description:** Exclude these Seasons from creating a Dynamic Collection.<br>**Values:** List of Seasons Keys                                                                                                                                                                                   |
        | `name_format`                         | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                              |
        | `summary_format`                      | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `A collection of <<key_name>> <<library_translation>>s that may relate to the season.`<br>**Values:** Any string.                                                                                        |

        1. Each default collection has a `key` [see here]() that you must replace 
        `<<key>>` with when using this template variable.

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
              tmdb_collection_years: #(4)!
                - 1234
                - 5678
              tmdb_movie_valentine: #(5)!
                - 4321
                - 8765
              imdb_list_patrick: https://www.imdb.com/list/ls089196478/ #(6)!
              imdb_search_easter: #(7)!
                list.any:
                  - ls075298827
                  - ls000099714
              trakt_list_mother:  #(8)!
                - https://trakt.tv/users/robertsnorlax/lists/arizona-westerns
                - https://trakt.tv/users/pullsa/lists/the-96th-academy-awards-oscars-2024
              mdblist_list_memorial: https://mdblist.com/lists/rizreflects/world-war-related-movies #(9)!
              letterboxd_list_father: https://letterboxd.com/patrickb15/list/fathers-day/ #(10)!
              append_data:
                apes: Planet of the Apes Day #(11)!
              schedule_apes: range(11/24-11/26) #(12)!
              imdb_list_apes: https://www.imdb.com/list/ls005126084/ #(13)!
              emoji_apes: "🐵 " #(14)!
    ```

    1.  Do not create the "Independence Day" collection
    2.  Set a custom schedule for the Thanksgiving Day collection
    3.  Sort the collections created by this file in random order
    4.  Add two TMDB collections to the "New Year's Day" collection
    5.  Add two movies to the "Valentine's Day" collection
    6.  Replace the IMDb List for the "St. Patrick's Day" collection
    7.  Add the contents of two IMDB lists to the "Easter" collection
    8.  Replace the lists for the "Mother's Day" collection with two Trakt lists
    9.  Replace the source list for the "Memorial Day" collection with a MDBList
    10.  Replace the source list for the "Father's Day" collection with a Letterboxd list
    11.  Create a new Seasonal collection called "Planet of the Apes Day", and set the key for this collection to `apes`
    12.  Set a scheduled range for the "Planet of the Apes Day" collection.  Planet Of The Apes Day is 11/25.
    13.  Add an IMDb List to be used for the "Planet of the Apes Day" collection
    14.  Add the 🐵 emoji to the "Planet of the Apes Day" collection so that the title in Plex is "🐵 Planet of the Apes 
    Day Movies"

## Default Values

Unless you customize them as described above, these collections use default lists and searches to create the collections.

If you are interested in customizing the default values, you can find that information [here](#template-variables).

If you are interested in seeing what those default builders are, you can find that information [here](../sources.md).
