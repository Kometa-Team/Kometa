# Other Awards Collections

The `other_award` Default Metadata File is used to  create collections based on numerous other awards.

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
    metadata_path:
      - pmm: other_award
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables.md) are available as well as the additional Variables below which can be used to customize the file.

| Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
| `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below shows an example config.yml with template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: other_award
        template_variables:
          collection_mode: show_items
          collection_order: alpha
          radarr_add_missing: true
```
