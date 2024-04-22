# TMDb Charts Collections

The `tmdb` Default Collection File is used to create collections based on TMDb Charts.

![](../images/tmdb.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

Recommendations: The `TMDb Airing Today` and `TMDb On The Air` Collections only work with Show Libraries

## Collections Section 020

| Collection          | Key        | Description                                          |
|:--------------------|:-----------|:-----------------------------------------------------|
| `TMDb Popular`      | `popular`  | Collection of the Most Popular Movies/Shows on TMDb. |
| `TMDb Top Rated`    | `top`      | Collection of the Top Rated Movies/Shows on TMDb.    |
| `TMDb Trending`     | `trending` | Collection of Trending Movies/Shows on TMDb.         |
| `TMDb Airing Today` | `airing`   | Collection of Shows Airing Today on TMDb.            |
| `TMDb On The Air`   | `air`      | Collection of Shows currently On The Air on TMDb.    |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: tmdb
  TV Shows:
    collection_files:
      - default: tmdb
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
        | `limit`                                | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Default:** `100`<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                             |
        | `limit_<<key>>`<sup>1</sup>            | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                |
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
          - default: tmdb
            template_variables:
              use_trending: false #(1)!
              limit_popular: 20 #(2)!
              visible_library_popular: true #(3)!
              visible_home_popular: true #(4)!
              visible_shared_popular: true #(5)!
    ```

    1.  Do not create the "TMDb Trending" collection
    2.  Change "TMDb Popular" to have a maximum of 20 items
    3.  Pin the "TMDb Popular" collection to the Recommended tab of the library
    4.  Pin the "TMDb Popular" collection to the home screen of the server owner
    5.  Pin the "TMDb Popular" collection to the home screen of other users of the server
