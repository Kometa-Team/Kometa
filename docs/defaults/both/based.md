# Based On... Collections

The `based` Default Collection File is used to create collections with items that are based on or inspired by various 
media outlets (such as Books or Video Games).

![](../images/based.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 085

| Collection                 | Key           | Description                                                                    |
|:---------------------------|:--------------|:-------------------------------------------------------------------------------|
| `Based on...  Collections` | `separator`   | [Separator Collection](../separators.md) to denote the Section of Collections. |
| `Based on a Book`          | `books`       | Collection of Movies/Shows based on or inspired by books                       |
| `Based on a Comic`         | `comics`      | Collection of Movies/Shows based on or inspired by comics                      |
| `Based on a True Story`    | `true_story`  | Collection of Movies/Shows based on or inspired by true stories                |
| `Based on a Video Game`    | `video_games` | Collection of Movies/Shows based on or inspired by video games                 |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: based
  TV Shows:
    collection_files:
      - default: based
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

        | Variable                        | Description & Values                                                                                                                                                                                                                                                                             |
        |:--------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `limit`                         | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                                                          |
        | `limit_<<key>>`<sup>1</sup>     | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                                                       |
        | `sort_by`                       | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                |
        | `sort_by_<<key>>`<sup>1</sup>   | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                          |
        | `sync_mode`                     | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sync_mode_<<key>>`<sup>1</sup> | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `exclude`                       | **Description:** Exclude these Media Outlets from creating a Dynamic Collection.<br>**Values:** List of Media Outlet Keys                                                                                                                                                                        |
        | `name_format`                   | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `Based on a <<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                             |
        | `summary_format`                | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s based on or inspired by <<translated_key_name>>s.`<br>**Values:** Any string.                                                                                                 |

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
          - default: based
            template_variables:
              sep_style: navy #(1)!
              use_comics: false #(2)!
              order_true_story: 01 #(3)!
              visible_library_video_games: true #(4)!
              visible_home_video_games: true #(5)!
              visible_shared_video_games: true #(6)!
    ```

    1.  Use the navy [Separator Style](../separators.md#separator-styles)
    2.  Do not create a "Based on a Comic" collection
    3.  Make the "Based on a True Story" collection appear in the collection list before the other collections in this 
    file
    4.  Pin the "Based on a Video Game" collection to the Recommended tab of the library
    5.  Pin the "Based on a Video Game" collection to the home screen of the server owner
    6.  Pin the "Based on a Video Game" collection to the home screen of other users of the server
