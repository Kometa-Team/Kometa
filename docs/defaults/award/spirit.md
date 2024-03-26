# Independent Spirit Awards Collections

The `spirit` Default Collection File is used to  create collections based on the Independent Spirit Awards.

![](../images/spirit.png)

## Requirements & Recommendations

Supported Library Types: Movie

## Collections Section 130

| Collection                                                                            | Key                               | Description                                                        |
|:--------------------------------------------------------------------------------------|:----------------------------------|:-------------------------------------------------------------------|
| `Independent Spirit Best Feature Winners`                                             | `best`                            | Collection of Independent Spirit Best Feature Award Winners.       |
| `Independent Spirit Awards <<year>>`<br>**Example:** `Independent Spirit Awards 2022` | `<<year>>`<br>**Example:** `2022` | Collection of Independent Spirit Award Winners for the given year. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: spirit
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this PMM Defaults file.

    * **Shared Template Variables** are additional variables shared across the PMM Defaults.

    === "File-Specific Template Variables"

        | Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
        |:---------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `use_year_collections`                 | **Description:** Turn the individual year collections off.<br>**Values:** `false` to turn of the collections                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
        | `year_collection_section`              | **Description:** Change the collection section for year collections only. (Use quotes to not lose leading zeros `"05"`)<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
        | `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
        | `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
        | `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                               |
        | `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                          |
        | `data`                                 | **Description:** Replaces the `data` dynamic collection value.<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections<br><strong>Default:</strong> latest-5<br><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections<br><strong>Default:</strong> latest<br><strong>Values:</strong> Number greater than 1</td></tr><tr><td><code>increment</code></td><td>Controls the increment (i.e. every 5th year)<br><strong>Default:</strong> 1<br><strong>Values:</strong> Number greater than 0</td><td></td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>latest</code></strong></li><li><strong>You can also use a value relative to the <code>latest</code> by doing <code>latest-5</code></strong></li></ul> |
        | `exclude`                              | **Description:** Exclude these Years from creating a Dynamic Collection.<br>**Values:** List of Years                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
        | `name_format`                          | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `Independent Spirit Awards <<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
        | `summary_format`                       | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<key_name>> Independent Spirit Awards.`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

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
          - pmm: spirit
            template_variables:
              collection_mode: show_items #(1)!
              collection_order: alpha #(2)!
              radarr_add_missing: true #(3)!
              name_format: Independent Spirit Awards <<key_name>> Winners #(4)!
              data: #(5)!
                starting: latest-10
                ending: latest
    ```

    1.  Shows the collection and all of its items within the Library tab in Plex
    2.  Sorts the collection items alphabetically
    3.  Adds items from the source list which are not in Plex to Radarr
    4.  Change the name of the collections to "Independent Spirit Awards yearhere Winners"
    5.  Creates collections from 10 award shows back to the latest award show.
