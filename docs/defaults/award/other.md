# Other Awards Collections

The `other_award` Default Collection File is used to  create collections based on numerous other awards.

![](../images/awardother.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

Requirements: [Trakt Authentication](../../config/trakt.md)

## Collections Section 130

| Collection                         | Key         | Description                                                   |
|:-----------------------------------|:------------|:--------------------------------------------------------------|
| `Berlinale Golden Bears`           | `berlinale` | Collection of Berlinale Golden Bears Award Winners.           |
| `César Best Film Winners`          | `cesar`     | Collection of César Best Film Winners Award Winners.          |
| `Razzies Golden Raspberry Winners` | `razzie`    | Collection of Razzies Golden Raspberry Winners Award Winners. |
| `Venice Golden Lions`              | `venice`    | Collection of Venice Golden Lions Award Winners.              |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: other_award
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

| Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
| `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |

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
    collection_files:
      - pmm: other_award
        template_variables:
          use_berlinale: false #(1)!
          collection_order: alpha #(2)!
          radarr_add_missing: true #(3)!
```

1.  Do not create the "Berlinale Golden Bears" collection
2.  Sorts the collection items alphabetically
3.  Adds items from the source list which are not in Plex to Radarr
