# Other Charts Collections

The `other_chart` Default Collection File is used to create collections based on other Charts.

![](../images/chartother.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

Recommendations: The `StevenLu's Popular Movies` and `Top 10 Pirated Movies of the Week` Collections only work with Movie Libraries

## Collections Section 020

| Collection                          | Key           | Description                                          |
|:------------------------------------|:--------------|:-----------------------------------------------------|
| `AniDB Popular`                     | `anidb`       | Collection of the most Popular Anime on AniDB.       |
| `Common Sense Selection`            | `commonsense` | Collection of Common Sense Selection Movies/Shows.   |
| `StevenLu's Popular Movies`         | `stevenlu`    | Collection of StevenLu's Popular Movies.             |
| `Top 10 Pirated Movies of the Week` | `pirated`     | Collection of the Top 10 Pirated Movies of the Week. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: other_chart
  TV Shows:
    collection_files:
      - default: other_chart
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this Kometa Defaults file.

    * **Shared Template Variables** are additional variables shared across the Kometa Defaults.

    === "File-Specific Template Variables"

        | Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        |:---------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `limit_anidb`                          | **Description:** Changes the Builder Limit of the AniDB Popular Collection.<br>**Default:** `30`<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                     |
        | `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
        | `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |

        1. Each default collection has a `key` that when calling to effect a specific collection you must replace 
        `<<key>>` with when calling.

    === "Shared Template Variables"

        {%
          include-markdown "../collection_variables.md"
        %}
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    Click the :fontawesome-solid-circle-plus: icon to learn more
    
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: other_chart
            template_variables:
              use_anidb: false #(1)!
              visible_library_commonsense: true #(2)!
              visible_home_commonsense: true #(3)!
              visible_shared_commonsense: true #(4)!
    ```

    1.  Do not create the "AniDB Popular" collection
    2.  Pin the "Common Sense Selection" collection to the Recommended tab of the library
    3.  Pin the "Common Sense Selection" collection to the home screen of the server owner
    4.  Pin the "Common Sense Selection" collection to the home screen of other users of the server
