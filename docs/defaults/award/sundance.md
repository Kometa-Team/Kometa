# Sundance Film Festival Awards Collections

The `sundance` Default Collection File is used to  create collections based on the Sundance Film Festival Awards.

![](../images/sundance.png)

## Requirements & Recommendations

Supported Library Types: Movie

Requirements: [Trakt Authentication](../../config/trakt.md)

## Collections Section 130

| Collection                                                                      | Key                               | Description                                                            |
|:--------------------------------------------------------------------------------|:----------------------------------|:-----------------------------------------------------------------------|
| `Sundance Grand Jury Winners`                                                   | `grand`                           | Collection of Sundance Film Festival Grand Jury Award Winners.         |
| `Sundance Film Festival <<year>>`<br>**Example:** `Sundance Film Festival 2022` | `<<year>>`<br>**Example:** `2022` | Collection of Sundance Film Festival Award Winners for the given year. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: sundance
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Shared Template Variables" tab for additional variables.

        | Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
        |:---------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `use_year_collections`                 | **Description:** Turn the individual year collections off.<br>**Values:** `false` to turn of the collections                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
        | `year_collection_section`              | **Description:** Change the collection section for year collections only. (Use quotes to not lose leading zeros `"05"`)<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
        | `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
        | `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
        | `data`                                 | **Description:** Replaces the `data` dynamic collection value.<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections<br><strong>Default:</strong> current_year-5<br><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections<br><strong>Default:</strong> current_year<br><strong>Values:</strong> Number greater than 1</td></tr><tr><td><code>increment</code></td><td>Controls the increment (i.e. every 5th year)<br><strong>Default:</strong> 1<br><strong>Values:</strong> Number greater than 0</td><td></td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>current_year</code></strong></li><li><strong>You can also use a value relative to the <code>current_year</code> by doing <code>current_year-5</code></strong></li></ul> |
        | `exclude`                              | **Description:** Exclude these Years from creating a Dynamic Collection.<br>**Values:** List of Years                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
        | `name_format`                          | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `Sundance Film Festival <<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `summary_format`                       | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `Sundance Film Festival of <<key_name>>.`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

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
          - pmm: sundance
            template_variables:
              collection_mode: show_items #(1)!
              collection_order: alpha #(2)!
              radarr_add_missing: true #(3)!
              name_format: Sundance Film Festival <<key_name>> Winners #(4)!
              data:
                starting: current_year-10 #(5)!
                ending: current_year #(6)!
    ```

    1.  Shows the collection and all of its items within the Library tab in Plex
    2.  Sorts the collection items alphabetically
    3.  Adds items from the source list which are not in Plex to Radarr
    4.  Change the name of the collections to "Sundance Film Festival yearhere Winners"
    5.  If today is 2024, then create collections for Sundance Film Festival 2014 onwards
    6.  If today is 2024, then the final collection is Sundance Film Festival 2024