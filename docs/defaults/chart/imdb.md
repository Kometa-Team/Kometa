# IMDb Charts Collections

The `imdb` Default Metadata File is used to create collections based on IMDb Charts.

**The `IMDb Lowest Rated` Collection only works with Movie Libraries but the rest of the collections work with both Movie and TV libraries.**

![](../images/imdb.png)

## Collections Section 01

| Collection          |    Key    | Description                                          |
|:--------------------|:---------:|:-----------------------------------------------------|
| `IMDb Popular`      | `popular` | Collection of the most Popular Movies/Shows on IMDb. |
| `IMDb Top 250`      |   `top`   | Collection of Top 250 Movies/Shows on IMDb.          |
| `IMDb Lowest Rated` | `lowest`  | Collection of the lowest Rated Movies on IMDb.       |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: imdb
  TV Shows:
    metadata_path:
      - pmm: imdb
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable                   | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `collection_order`         | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
| `collection_order_<<key>>` | **Description:** Changes the Collection Order of the specified key's Collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: imdb
        template_variables:
          use_popular: false
          visible_library_top: true
          visible_home_top: true
          visible_shared_top: true
```
