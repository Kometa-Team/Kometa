# Trakt Charts Collections

The `trakt` Default Collection File is used to create collections based on Trakt Charts.

![](../images/trakt.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

Requirements: [Trakt Authentication](../../config/trakt.md)

## Collections Section 020

| Collection          | Key           | Description                                                |
|:--------------------|:--------------|:-----------------------------------------------------------|
| `Trakt Anticipated` | `anticipated` | Collection of the Most Anticipated Movies/Shows on Trakt.  |
| `Trakt Collected`   | `collected`   | Collection of the Most Collected Movies/Shows on Trakt.    |
| `Trakt Popular`     | `popular`     | Collection of the Most Popular Movies/Shows on Trakt.      |
| `Trakt Recommended` | `recommended` | Collection of Recommended Movies/Shows on Trakt.           |
| `Trakt Trending`    | `trending`    | Collection of Trending Movies/Shows on Trakt.              |
| `Trakt Watched`     | `watched`     | Collection of the Most Watched Movies/Shows on Trakt.      |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: trakt
  TV Shows:
    collection_files:
      - pmm: trakt
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Shared Template Variables" tab for additional variables.

        | Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        |:---------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `limit`                                | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Default:** `100`<br>**Values:** Number Greater than 0                                                                                                                                                                                                                                                                                                                                                                                             |
        | `limit_<<key>>`<sup>1</sup>            | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                                                                                                                                                                                                                                                                                                |
        | `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
        | `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |

        1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

    === "Shared Template Variables"

        {%
          include-markdown "../collection_variables.md"
        %}

    ### Example Template Variable Amendments

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    ???+ tip

        Anywhere you see this icon:
      
        > :fontawesome-solid-circle-plus:
      
        That's a tooltip, you can press them to get more information.

    ```yaml
    libraries:
      Movies:
        collection_files:
          - pmm: trakt
            template_variables:
              use_collected: false #(1)!
              use_recommended: false #(2)!
              limit: 20 #(3)!
              visible_library_popular: true #(4)!
              visible_home_popular: true #(5)!
              visible_shared_popular: true #(6)!
    ```

    1.  Do not create the "Trakt Collected" collection
    2.  Do not create the "Trakt Recommended" collection
    3.  Change all collections built by this file to have a maximum of 20 items
    4.  Pin the "Trakt Popular" collection to the Recommended tab of the library
    5.  Pin the "Trakt Popular" collection to the home screen of the server owner
    6.  Pin the "Trakt Popular" collection to the home screen of other users of the server
