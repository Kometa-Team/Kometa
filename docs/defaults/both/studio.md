# Studio Collections

The `studio` Default Metadata File is used to dynamically create collections based on the studios available in your library.

This file also merges similarly named studios (such as "20th Century Fox" and "20th Century Animation") into one ("20th Century Studios")

**This file works with Movie and Show Libraries.**

![](../images/studio.png)

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
      - pmm: studio
  TV Shows:
    metadata_path:
      - pmm: studio
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
      - pmm: studio
        template_variables:
          append_include:
            - Big Bull Productions
          sort_by: title.asc
          collection_section: 4
          collection_mode: show_items
          use_separator: false
          sep_style: gray
```

## Default `include`

```yaml
include:
  - 20th Century Studios
  - Amazon Studios
  - Amblin Entertainment
  - Blue Sky Studios
  - Blumhouse Productions
  - Chernin Entertainment
  - Columbia Pictures
  - Constantin Film
  - DreamWorks Studios
  - Grindstone Entertainment Group
  - Happy Madison Productions
  - Illumination Entertainment
  - Ingenious Media
  - Legendary Pictures
  - Lionsgate
  - Lucasfilm Ltd
  - Malevolent Films
  - Marvel Studios
  - Metro-Goldwyn-Mayer
  - Millennium Films
  - Miramax
  - New Line Cinema
  - Original Film
  - Orion Pictures
  - Paramount Pictures
  - Pixar
  - PlanB Entertainment
  - Sony Pictures
  - Studio Ghibli
  - Summit Entertainment
  - Universal Pictures
  - Village Roadshow Pictures
  - Walt Disney Pictures
  - Warner Bros. Pictures
```

## Default `addons`

```yaml
addons:
  20th Century Studios:
    - 20th Century
    - 20th Century Animation
    - 20th Century Fox
  Amazon Studios:
    - Amazon
  Amblin Entertainment:
    - Amblin Entertainment
  Blue Sky Studios:
    - Blue Sky Films
  Blumhouse Productions:
    - Blumhouse Productions
  Chernin Entertainment:
    - Chernin Entertainment
  Columbia Pictures:
    - Columbia TriStar
    - TriStar
  Constantin Film:
    - Constantin Film
  DreamWorks Studios:
    - DreamWorks
    - DreamWorks Animation
  Grindstone Entertainment Group:
    - Grindstone Entertainment Group
  Happy Madison Productions:
    - Happy Madison Productions
  Illumination Entertainment:
    - Illumination Films
  Ingenious Media:
    - Ingenious Media
  Legendary Pictures:
    - Legendary Pictures
  Lucasfilm Ltd:
    - Lucasfilm
  Malevolent Films:
    - Malevolent Films
  Marvel Studios:
    - Marvel Animation
    - Marvel Enterprises
    - Marvel Entertainment
    - Marvel
  Metro-Goldwyn-Mayer:
    - MGM
  Millennium Films:
    - Millennium Films
  Miramax:
    - Miramax
  New Line Cinema:
    - New Line
  Original Film:
    - Original Film
  Orion Pictures:
    - Orion Pictures
  Paramount Pictures:
    - Paramount
    - Paramount Animation
  Pixar:
    - Pixar Animation Studios
  PlanB Entertainment:
    - PlanB Entertainment
  Sony Pictures:
    - Sony
    - Sony Pictures Animation
  Summit Entertainment:
    - Summit Entertainment
  Universal Pictures:
    - Universal
    - Universal Animation Studios
  Village Roadshow Pictures:
    - Village Roadshow Pictures
  Walt Disney Pictures:
    - Disney
    - Walt Disney Animation Studios
  Warner Bros. Pictures:
    - Warner
    - Warner Animation Group
```