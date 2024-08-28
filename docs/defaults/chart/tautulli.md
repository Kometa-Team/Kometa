# Tautulli Charts Collections

The `tautulli` Default Collection File is used to create collections based on Tautulli/Plex Charts.

![](../images/tautulli.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show


Requirements: [Tautulli Authentication](../../config/tautulli.md)

## Collections Section 020

| Collection     | Key       | Description                                          |
|:---------------|:----------|:-----------------------------------------------------|
| `Plex Popular` | `popular` | Collection of the most Popular Movies/Shows on Plex. |
| `Plex Watched` | `watched` | Collection of the most Watched Movies/Shows on Plex. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: tautulli
  TV Shows:
    collection_files:
      - default: tautulli
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
        | `list_days`                            | **Description:** Changes the `list_days` attribute of the builder for all collections in a Defaults file.<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                            |
        | `list_days_<<key>>`<sup>1</sup>        | **Description:** Changes the `list_days` attribute of the builder of the specified key's collection.<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `list_size`                            | **Description:** Changes the `list_size` attribute of the builder for all collections in a Defaults file.<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                            |
        | `list_size_<<key>>`<sup>1</sup>        | **Description:** Changes the `list_size` attribute of the builder of the specified key's collection.<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
        | `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |

        1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

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
          - default: tautulli
            template_variables:
              use_watched: false #(1)!
              list_days_popular: 7 #(2)!
              list_size_popular: 10 #(3)!
              visible_library_popular: true #(4)!
              visible_home_popular: true #(5)!
              visible_shared_popular: true #(6)!
    ```

    1.  Do not create the "Plex Watched" collection
    2.  Change "Plex Popular" to look at items from the past 7 days
    3.  Change "Plex Popular" to have a maximum of 10 items
    4.  Pin the "Plex Popular" collection to the Recommended tab of the library
    5.  Pin the "Plex Popular" collection to the home screen of the server owner
    6.  Pin the "Plex Popular" collection to the home screen of other users of the server
