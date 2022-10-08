# FlixPatrol Charts Default Metadata File

The `flixpatrol` Metadata File is used to create collections based on FlixPatrol Charts.

The `IMDb Lowest Rated` Collection only works with Movie Libraries but the rest of the collections work with both Movie and TV libraries.

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: flixpatrol
  TV Shows:
    metadata_path:
      - pmm: flixpatrol
```

## Collections

| Collection                          |     Key     | Description                                                                   |
|:------------------------------------|:-----------:|:------------------------------------------------------------------------------|
| `Netflix Top 10 Moves/Shows`        |  `netflix`  | Collection of the Top Movies/Shows on Netflix according to FlixPatrol.        |
| `Disney Top 10 Moves/Shows`         |  `disney`   | Collection of the Top Movies/Shows on Disney Plus according to FlixPatrol.    |
| `HBO Top 10 Moves/Shows`            |    `hbo`    | Collection of the Top Movies/Shows on HBO according to FlixPatrol.            |
| `Hulu Top 10 Moves/Shows`           |   `hulu`    | Collection of the Top Movies/Shows on Hulu according to FlixPatrol.           |
| `Paramount Plus Top 10 Moves/Shows` | `paramount` | Collection of the Top Movies/Shows on Paramount Plus according to FlixPatrol. |
| `Prime Video Top 10 Moves/Shows`    |   `prime`   | Collection of the Top Movies/Shows on Prime Video according to FlixPatrol.    |

### Examples

![](../images/flixpatrol.png)

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable                   | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|:---------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                    | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Default:** `10`<br>**Values:** Number Greater then 0                                                                                                                                                                                                                                                                                                                                                                                                  |
| `limit_<<key>>`            | **Description:** Changes the Builder Limit of the specified key's Collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                                                                                                                                                                                                                                                                                                    |
| `location`                 | **Description:** Changes the Builder Location for all collections in a Defaults file.<br>**Default:** `world`<br>**Values:** [`location` Attribute Options](../../metadata/builders/flixpatrol.md#top-platform-attributes)                                                                                                                                                                                                                                                                                                                    |
| `location_<<key>>`         | **Description:** Changes the Builder Location of the specified key's Collection.<br>**Default:** `location`<br>**Values:** [`location` Attribute Options](../../metadata/builders/flixpatrol.md#top-platform-attributes)                                                                                                                                                                                                                                                                                                                      |
| `time_window`              | **Description:** Changes the Builder Time Window for all collections in a Defaults file.<br>**Default:** `last_week`<br>**Values:** [`time_window` Attribute Options](../../metadata/builders/flixpatrol.md#top-platform-attributes)                                                                                                                                                                                                                                                                                                          |
| `time_window_<<key>>`      | **Description:** Changes the Builder Time Window of the specified key's Collection.<br>**Default:** `time_window`<br>**Values:** [`time_window` Attribute Options](../../metadata/builders/flixpatrol.md#top-platform-attributes)                                                                                                                                                                                                                                                                                                             |
| `collection_order`         | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>       |
| `collection_order_<<key>>` | **Description:** Changes the Collection Order of the specified key's Collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>  |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: flixpatrol
        template_variables:
          location: united_states
          time_window: last_month
```
