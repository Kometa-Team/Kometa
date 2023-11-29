# Academy Awards (Oscars) Collections

The `oscars` Default Metadata File is used to create collections based on the Academy Awards (Oscars).

![](../images/oscars.png)

## Requirements & Recommendations

Supported Library Types: Movie

## Collections Section 130

| Collection                                                      | Key                               | Description                                            |
|:----------------------------------------------------------------|:----------------------------------|:-------------------------------------------------------|
| `Oscars Best Picture Winners`                                   | `best_picture`                    | Collection of Oscars Best Picture Award Winners.       |
| `Oscars Best Director Winners`                                  | `best_director`                   | Collection of Oscars Best Director Award Winners.      |
| `Oscars Winners <<year>>`<br>**Example:** `Oscars Winners 2022` | `<<year>>`<br>**Example:** `2022` | Collection of Oscars Award Winners for the given year. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: oscars
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

| Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|:---------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_year_collections`                 | **Description:** Turn the individual year collections off.<br>**Values:** `false` to turn of the collections                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `year_collection_section`              | **Description:** Change the collection section for year collections only. (Use quotes to not lose leading zeros `"05"`)<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `data`                                 | **Description:** Replaces the `data` dynamic collection value.<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections<hr><strong>Default:</strong> current_year-6<hr><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections<hr><strong>Default:</strong> current_year-1<hr><strong>Values:</strong> Number greater than 1</td></tr><tr><td><code>increment</code></td><td>Controls the increment (i.e. every 5th year)<hr><strong>Default:</strong> 1<hr><strong>Values:</strong> Number greater than 0</td><td></td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>current_year</code></strong></li><li><strong>You can also use a value relative to the <code>current_year</code> by doing <code>current_year-5</code></strong></li></ul> |
| `exclude`                              | **Description:** Exclude these Years from creating a Dynamic Collection.<br>**Values:** List of Years                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `name_format`                          | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `Oscars Winners <<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `summary_format`                       | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `Academy Awards (Oscars) Winners for <<key_name>>.`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

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
    metadata_path:
      - pmm: oscars
        template_variables:
          collection_mode: show_items #(1)!
          collection_order: alpha #(2)!
          radarr_add_missing: true #(3)!
          name_format: Emmys <<key_name>> Winners #(4)!
          data:
            starting: current_year-10 #(5)!
            increment: 2 #(6)!
            ending: current_year #(7)!
```

1.  Shows the collection and all of its items within the Library tab in Plex
2.  Sorts the collection items alphabetically
3.  Adds items from the source list which are not in Plex to Radarr
4.  Change the name of the collections to "Oscars yearhere Winners"
5.  If today is 2024, then create collections for Oscars 2014 onwards
6.  If starting year is 2014, then create collections for 2014, 2016, 2018, 2020, etc.
7.  If today is 2024, then the final collection is Oscars 2024
