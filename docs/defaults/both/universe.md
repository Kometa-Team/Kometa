# Universe Collections

The `universe` Default Metadata File is used to create collections based on popular Movie universes (such as the Marvel Cinematic Universe or Wizarding World).

![](../images/universe.png)

## Requirements & Recommendations

Supported Library Types: Movie & Show

## Collections Section 040

| Collection                   | Key         | Description                                                                 |
|:-----------------------------|:------------|:----------------------------------------------------------------------------|
| `Universe Collections`       | `separator` | [Separator Collection](../separators) to denote the Section of Collections. |
| `Alien / Predator`           | `avp`       | Collection of Movies in the Alien / Predator Universe                       |
| `Arrowverse`                 | `arrow`     | Collection of Movies in the The Arrow Universe                              |
| `DC Animated Universe`       | `dca`       | Collection of Movies in the DC Animated Universe                            |
| `DC Extended Universe`       | `dcu`       | Collection of Movies in the DC Extended Universe                            |
| `Fast & Furious`             | `fast`      | Collection of Movies in the Fast & Furious Universe                         |
| `In Association with Marvel` | `marvel`    | Collection of Movies in the Marvel Universe (but not part of MCU)           |
| `Marvel Cinematic Universe`  | `mcu`       | Collection of Movies in the Marvel Cinematic Universe                       |
| `Middle Earth`               | `middle`    | Collection of Movies in the Middle Earth Universe                           |
| `The Mummy Universe`         | `mummy`     | Collection of Movies in the The Mummy Universe                              |
| `Rocky / Creed`              | `rocky`     | Collection of Movies in the Rocky / Creed Universe                          |
| `Star Trek`                  | `trek`      | Collection of Movies in the Star Trek Universe                              |
| `Star Wars Universe`         | `star`      | Collection of Movies in the Star Wars Universe                              |
| `View Askewverse`            | `askew`     | Collection of Movies in the The View Askew Universe                         |
| `Wizarding World`            | `wizard`    | Collection of Movies in the Wizarding World Universe                        |
| `X-Men Universe`             | `xmen`      | Collection of Movies in the X-Men Universe                                  |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: universe
  TV Shows:
    metadata_path:
      - pmm: universe
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:---------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sync_mode`                            | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `sync_mode_<<key>>`<sup>1</sup>        | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>      |
| `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |
| `minimum_items`                        | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                       |
| `name_mapping_<<key>>`<sup>1</sup>     | **Description:** Sets the name mapping value for using assets of the specified key's collection. <br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `imdb_list_<<key>>`<sup>1</sup>        | **Description:** Adds the Movies in the IMDb List to the specified key's collection.<br>**Values:** List of IMDb List URLs                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `mdblist_list_<<key>>`<sup>1</sup>     | **Description:** Adds the Movies in the MDBList List to the specified key's collection. Overrides the [default mdblist_list](#default-mdblist_list) for that collection if used.<br>**Values:** List of MDBList List URLs                                                                                                                                                                                                                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `trakt_list_<<key>>`<sup>1</sup>       | **Description:** Adds the Movies in the Trakt List to the specified key's collection.<br>**Values:** List of Trakt List URLs                                                                                                                                                                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
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
          trakt_list_monster: https://trakt.tv/users/rzepkowski/lists/monsterverse-movies
```

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `data`

```yaml
data:
  avp: Alien / Predator
  arrow: Arrowverse
  dca: DC Animated Universe
  dcu: DC Extended Universe
  fast: Fast & Furious
  marvel: In Association With Marvel
  mcu: Marvel Cinematic Universe
  middle: Middle Earth
  mummy: The Mummy Universe
  rocky: Rocky / Creed
  trek: Star Trek
  star: Star Wars Universe
  askew: View Askewniverse
  wizard: Wizarding World
  xmen: X-Men Universe
```

### Default `mdblist_list`

```yaml
trakt_list:
    mcu: https://trakt.tv/users/donxy/lists/marvel-cinematic-universe
    middle: https://trakt.tv/users/oya-kesh/lists/middle-earth
    trek: https://trakt.tv/users/wdvhucb/lists/star-trek
mdblist_list:
    avp: https://mdblist.com/lists/plexmetamanager/external/9243
    arrow: https://mdblist.com/lists/plexmetamanager/external/15113
    dca: https://mdblist.com/lists/plexmetamanager/external/15405
    dcu: https://mdblist.com/lists/plexmetamanager/external/15107
    fast: https://mdblist.com/lists/plexmetamanager/external/9246
    marvel: https://mdblist.com/lists/plexmetamanager/external/15110
    mummy: https://mdblist.com/lists/plexmetamanager/external/9249
    rocky: https://mdblist.com/lists/plexmetamanager/external/9248
    star: https://mdblist.com/lists/plexmetamanager/external/15105
    askew: https://mdblist.com/lists/plexmetamanager/external/15362
    wizard: https://mdblist.com/lists/plexmetamanager/external/9242
    xmen: https://mdblist.com/lists/plexmetamanager/external/9244
```
