# Anime Studio Collections

The `studio_anime` Default Metadata File is used to dynamically create collections based on the studios available in your library.

**This file works with Show Libraries only.**

![](../images/studio_anime.png)

## Collections Section 07

| Collection                                           |                         Key                          | Description                                                                 |
|:-----------------------------------------------------|:----------------------------------------------------:|:----------------------------------------------------------------------------|
| `Studio Collections`                                 |                     `separator`                      | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<Studio>>`<br>**Example:** `Blumhouse Productions` | `<<Studio>>`<br>**Example:** `Blumhouse Productions` | Collection of Movies/Shows that have this Studio.                           |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio_anime
  TV Shows:
    metadata_path:
      - pmm: studio_anime
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable                      | Description & Values                                                                                                                                                                                                                                            |
|:------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_separator`               | **Description:** Turn the [Separator Collection](../separators) off.<br>**Values:** `false` to turn of the collection                                                                                                                                           |
| `sep_style`                   | **Description:** Choose the [Separator Style](../separators.md#separator-styles).<br>**Default:** `orig`<br>**Values:** `orig`, `red`, `blue`, `green`, `gray`, `purple`, or `stb`                                                                              |
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                         |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                      |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                            |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                      |
| `include`                     | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of Studios found in your library                                                                                                                                   |
| `exclude`                     | **Description:** Exclude these Studios from creating a Dynamic Collection.<br>**Values:** List of Studios found in your library                                                                                                                                 |
| `addons`                      | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Studios found in your library |
| `append_include`              | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of Studios found in your library                                                                                                                                  |
| `append_addons`               | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Studios found in your library                                                                                                                   |
| `resolution_name`             | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                             |
| `resolution_summary`          | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s that have the resolution <<key_name>>.`<br>**Values:** Any string.                                                                           |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio_anime
        template_variables:
          append_include:
            - Bandai Namco Entertainment
          sort_by: title.asc
          collection_section: 4
          collection_mode: show_items
          use_separator: false
          sep_style: gray
```

## Default `include`

```yaml
include:
  - 8bit
  - A-1 Pictures
  - Bones
  - Brain`s Base
  - Clover Works
  - Doga Kobo
  - Gainax
  - J.C.Staff
  - Kinema Citrus
  - Kyoto Animation
  - Madhouse
  - MAPPA
  - P.A. Works
  - Production I.G
  - Shaft
  - Silver Link
  - Studio DEEN
  - Studio Ghibli
  - Sunrise
  - Studio Pierrot
  - Toei Animation
  - Trigger
  - Ufotable
  - White Fox
  - Wit Studio
```

## Default `addons`

```yaml
addons:
  8bit:
    - 8-bit
  Studio DEEN:
    - Studio Deen
```