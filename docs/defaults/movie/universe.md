# Universe Collections

The `universe` Default Metadata File is used to create collections based on popular Movie universes (such as the Marvel Cinematic Universe or Wizarding World).

This Default file requires [Trakt Authentication](../../config/trakt)

**This file only works with Movie Libraries.**

![](../images/universe.png)

## Collections Section 02

| Collection                  |     Key     | Description                                                                 |
|:----------------------------|:-----------:|:----------------------------------------------------------------------------|
| `Universe Collections`      | `separator` | [Separator Collection](../separators) to denote the Section of Collections. |
| `Star Wars Universe`        |   `star`    | Collection of Movies in the Star Wars Universe                              |
| `DC Animated Universe`      |    `dca`    | Collection of Movies in the DC Animated Universe                            |
| `DC Extended Universe`      |    `dcu`    | Collection of Movies in the DC Extended Universe                            |
| `Marvel Cinematic Universe` |    `mcu`    | Collection of Movies in the Marvel Cinematic Universe                       |
| `Wizarding World`           |  `wizard`   | Collection of Movies in the Wizarding World Universe                        |
| `Alien / Predator`          |    `avp`    | Collection of Movies in the Alien / Predator Universe                       |
| `X-Men Universe`            |   `xmen`    | Collection of Movies in the X-Men Universe                                  |
| `Middle Earth`              |  `middle`   | Collection of Movies in the Middle Earth Universe                           |
| `Fast & Furious`            |   `fast`    | Collection of Movies in the Fast & Furious Universe                         |
| `Star Trek`                 |   `trek`    | Collection of Movies in the Star Trek Universe                              |
| `Rocky / Creed`             |   `rocky`   | Collection of Movies in the Rocky / Creed Universe                          |
| `The Mummy Universe`        |   `mummy`   | Collection of Movies in the The Mummy Universe                              |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: universe
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
| `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |
| `minimum_items`                        | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                       |
| `name_mapping_<<key>>`<sup>1</sup>     | **Description:** Sets the name mapping value for using assets of the specified key's collection. <br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `imdb_list_<<key>>`<sup>1</sup>        | **Description:** Adds the Movies in the IMDb List to the specified key's collection.<br>**Values:** List of IMDb List URLs                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `trakt_list_<<key>>`<sup>1</sup>       | **Description:** Adds the Movies in the Trakt List to the specified key's collection. Overrides the [default trakt_list](#default-trakt_list) for that collection if used.<br>**Values:** List of Trakt List URLs                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `data`                                 | **Description:** Overrides the [default data dictionary](#default-data). Defines the data that the custom dynamic collection processes.<br>**Values:** Dictionary List of keys/names                                                                                                                                                                                                                                                                                                                                                         |
| `append_data`                          | **Description:** Appends to the [default data dictionary](#default-data).<br>**Values:** Dictionary List of keys/names                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `exclude`                              | **Description:** Exclude these Universes from creating a Dynamic Collection.<br>**Values:** List of Universes                                                                                                                                                                                                                                                                                                                                                                                                                                |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: universe
        template_variables:
          use_separator: false
          sep_style: gray
          collection_order: release
          radarr_add_missing: true
          # Add a custom universe
          append_data:
            monster: MonsterVerse
          trakt_list_veteran: https://trakt.tv/users/rzepkowski/lists/monsterverse-movies
```

## Default `data`

```yaml
data:
  star: Star Wars Universe
  dca: DC Animated Universe
  dcu: DC Extended Universe
  mcu: Marvel Cinematic Universe
  wizard: Wizarding World
  avp: Alien / Predator
  xmen: X-Men Universe
  middle: Middle Earth
  fast: Fast & Furious
  trek: Star Trek
  rocky: Rocky / Creed
  mummy: The Mummy Universe
```

## Default `trakt_list`

```yaml
trakt_list:
  star: https://trakt.tv/users/zorge88/lists/star-wars
  dca: https://trakt.tv/users/donxy/lists/dc-animated-movie-universe
  dcu: https://trakt.tv/users/donxy/lists/dc-extended-universe
  mcu: https://trakt.tv/users/donxy/lists/marvel-cinematic-universe
  wizard: https://trakt.tv/users/strangerer/lists/harry-potter
  avp: https://trakt.tv/users/donxy/lists/alien-predator-timeline
  xmen: https://trakt.tv/users/donxy/lists/x-men-universe
  middle: https://trakt.tv/users/dybro/lists/lord-of-the-rings
  fast: https://trakt.tv/users/vargajoe/lists/fast-and-furious-chronology
  trek: https://trakt.tv/users/arachn0id/lists/star-trek-movies
  rocky: https://trakt.tv/users/strangerer/lists/rocky
  mummy: https://trakt.tv/users/rzepkowski/lists/the-mummy-movies
```
