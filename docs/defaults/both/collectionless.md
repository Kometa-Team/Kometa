# Collectionless Collection

The `collectionless` Default Metadata File is used to create a [Collectionless collection](../../metadata/builders/plex.md#plex-collectionless) to help Show/Hide Movies/Shows properly in your library.

**For this file to work it needs to run last under `metadata_path` and all other normal collections must use `collection_mode: hide_items`.**

**This file works with Movie and Show Libraries.**

![](../images/collectionless.png)

## Collection

| Collection       | Description                                                                                                                                |
|:-----------------|:-------------------------------------------------------------------------------------------------------------------------------------------|
| `Collectionless` | [Collectionless collection](../../metadata/builders/plex.md#plex-collectionless) to help Show/Hide Movies/Shows properly in your library.. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    template_variables:
      collection_mode: hide_items
    metadata_path:
      - pmm: collectionless
  TV Shows:
    template_variables:
      collection_mode: hide_items
    metadata_path:
      - pmm: collectionless
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

**[Shared Collection Variables](../collection_variables) are NOT available to this default file.**

| Variable                 | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|:-------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name_collectionless`    | **Description:** Changes the name of the collection.<br>**Values:** New Collection Name                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `summary_collectionless` | **Description:** Changes the summary of the collection.<br>**Values:** New Collection Summary                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `sort_title`             | **Description:** Sets the sort title for the collection.<br>**Default:** `~_Collectionless`<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                            |
| `collection_order`       | **Description:** Changes the Collection Order for all collections in this file.<br>**Default:** `alpha`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |
| `url_poster`             | **Description:** Changes the poster url of thecollection.<br>**Values:** URL directly to the Image                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `exclude`                | **Description:** Exclude these Collections from being considered for collectionless.<br>**Values:** List of Collections                                                                                                                                                                                                                                                                                                                                                                                                          |
| `exclude_prefix`         | **Description:** Overrides the [default exclude_prefix list](#default-exclude_prefix). Exclude Collections with one of these prefixes from being considered for collectionless.<br>**Default:** [default exclude_prefix list](#default-exclude_prefix)<br>**Values:** List of Prefixes                                                                                                                                                                                                                                           |                                                                                                                                                                                                                                                                                                                                                 |


The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    template_variables:
      collection_mode: hide_items
    metadata_path:
      - pmm: collectionless
        template_variables:
          exclude:
            - Marvel Cinematic Universe
          collection_order: release
```

## Default `exclude_prefix`

```yaml
exclude_prefix:
  - "!"
  - "~"
```