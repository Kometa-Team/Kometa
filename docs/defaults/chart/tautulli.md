# Tautulli Charts Collections

The `tautulli` Default Metadata File is used to create collections based on Tautulli/Plex Charts.

![](../images/tautulli.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

Requirements: [Tautulli Authentication](../../config/tautulli)

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
    metadata_path:
      - pmm: tautulli
  TV Shows:
    metadata_path:
      - pmm: tautulli
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `list_days`                            | **Description:** Changes the `list_days` attribute of the builder for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                                                                                                                                                                                                                                                                               |
| `list_days_<<key>>`<sup>1</sup>        | **Description:** Changes the `list_days` attribute of the builder of the specified key's collection.<br>**Values:** Number Greater than 0                                                                                                                                                                                                                                                                                                                                                                                                    |
| `list_size`                            | **Description:** Changes the `list_size` attribute of the builder for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                                                                                                                                                                                                                                                                               |
| `list_size_<<key>>`<sup>1</sup>        | **Description:** Changes the `list_size` attribute of the builder of the specified key's collection.<br>**Values:** Number Greater than 0                                                                                                                                                                                                                                                                                                                                                                                                    |
| `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
| `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: tautulli
        template_variables:
          use_watched: false
          list_days_popular: 7
          list_size_popular: 10
          visible_library_watched: true
          visible_home_watched: true
          visible_shared_watched: true
```
