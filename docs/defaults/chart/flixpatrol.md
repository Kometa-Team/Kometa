# FlixPatrol Charts Collections

The `flixpatrol` Default Collection File is used to create collections based on FlixPatrol Charts.

![](../images/flixpatrol.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 020

| Collection                        | Key         | Description                                                                |
|:----------------------------------|:------------|:---------------------------------------------------------------------------|
| `Netflix Top 10 Movies/Shows`     | `netflix`   | Collection of the Top Movies/Shows on Netflix according to FlixPatrol.     |
| `Disney+ Top 10 Movies/Shows`     | `disney`    | Collection of the Top Movies/Shows on Disney+ according to FlixPatrol.     |
| `MAX Top 10 Movies/Shows`         | `max`       | Collection of the Top Movies/Shows on MAX according to FlixPatrol.         |
| `Hulu Top 10 Movies/Shows`        | `hulu`      | Collection of the Top Movies/Shows on Hulu according to FlixPatrol.        |
| `Paramount+ Top 10 Movies/Shows`  | `paramount` | Collection of the Top Movies/Shows on Paramount+ according to FlixPatrol.  |
| `Prime Video Top 10 Movies/Shows` | `prime`     | Collection of the Top Movies/Shows on Prime Video according to FlixPatrol. |
| `Apple+ Top 10 Movies/Shows`      | `apple`     | Collection of the Top Movies/Shows on Apple+ according to FlixPatrol.      |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: flixpatrol
  TV Shows:
    collection_files:
      - pmm: flixpatrol
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Shared Template Variables" tab for additional variables.

        ???+ warning

            Due to Flixpatrol data limitations, Apple TV only works with the `world` location. If you set a country-specific location, Apple TV will fall-back to using the `world` location.

        | Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
        |:---------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `limit`                                | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Default:** `10`<br>**Values:** Any Number 1-10                                                                                                                                                                                                                                                                                                                                                                                                      |
        | `limit_<<key>>`<sup>1</sup>            | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Any Number 1-10                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `in_the_last`                          | **Description:** Changes How many days of daily Top 10 Lists to look at.<br>**Default:** `1`<br>**Values:** Any Number 1-30                                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `in_the_last_<<key>>`<sup>1</sup>      | **Description:** Changes How many days of daily Top 10 Lists to look at.<br>**Default:** `in_the_last`<br>**Values:** Any Number 1-30                                                                                                                                                                                                                                                                                                                                                                                                       |
        | `location`                             | **Description:** Changes the Builder Location for all collections in a Defaults file.<br>**Default:** `world`<br>**Values:** [`location` Attribute Options](../../files/builders/flixpatrol.md#top-platform-attributes)                                                                                                                                                                                                                                                                                                                           |
        | `location_<<key>>`<sup>1</sup>         | **Description:** Changes the Builder Location of the specified key's collection.<br>**Default:** `location`<br>**Values:** [`location` Attribute Options](../../files/builders/flixpatrol.md#top-platform-attributes)                                                                                                                                                                                                                                                                                                                             |
        | `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                            |
        | `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                            |
        | `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>              |
        | `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>         |

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
          - pmm: flixpatrol
            template_variables:
              location: united_states #(1)!
    ```

    1.  Change the location of the FlixPatrol  collections to the United States of America
