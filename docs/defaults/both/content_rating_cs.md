# Common Sense Media Content Rating Collections

The `content_rating_cs` Default Metadata File is used to dynamically create collections based on the content ratings available in your library.

If you do not use the Common Sense-based rating system within Plex, this file will attempt to match the ratings in your library to the respective rating system.

![](../images/content_rating_cs.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

Recommendations: Use the [Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with either `mdb_commonsense` or `mdb_commonsense0` to update Plex to the Common Sense Rating.

## Collections Section 110

| Collection                                                        | Key                              | Description                                                                           |
|:------------------------------------------------------------------|:---------------------------------|:--------------------------------------------------------------------------------------|
| `Ratings Collections`                                             | `separator`                      | [Separator Collection](../separators) to denote the Section of Collections.           |
| `<<Content Rating>> Movies/Shows`<br>**Example:** `Age 5+ Movies` | `<<Number>>`<br>**Example:** `5` | Collection of Movies/Shows that have this Content Rating.                             |
| `Not Rated Movies/Shows`                                          | `other`                          | Collection of Movies/Shows that are Unrated, Not Rated or any other uncommon Ratings. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: content_rating_cs
  TV Shows:
    metadata_path:
      - pmm: content_rating_cs
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                       | Description & Values                                                                                                                                                                                                                                                    |
|:-------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                        | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                                 |
| `limit_<<key>>`<sup>1</sup>    | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                              |
| `sort_by`                      | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                    |
| `sort_by_<<key>>`<sup>1</sup>  | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                              |
| `include`                      | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of Content Ratings found in your library                                                                                                                                   |
| `exclude`                      | **Description:** Exclude these Content Ratings from creating a Dynamic Collection.<br>**Values:** List of Content Ratings found in your library                                                                                                                         |
| `addons`                       | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Content Ratings found in your library |
| `append_include`               | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of Content Ratings found in your library                                                                                                                                  |
| `append_addons`                | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Content Ratings found in your library                                                                                                                   |
| `content_rating_cs_name`       | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `Age <<key_name>>+ <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                |
| `content_rating_other_name`    | **Description:** Changes the Other Collection name.<br>**Default:** `Not Rated <<library_translationU>>s`<br>**Values:** Any string.                                                                                                                                    |
| `content_rating_cs_summary`    | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s that are rated <<key_name>> accorfing to the Common Sense Rating System.`<br>**Values:** Any string.                                                 |
| `content_rating_other_summary` | **Description:** Changes the Other Collection summary.<br>**Default:** `<<library_translationU>>s that are Unrated, Not Rated or any other uncommon Ratings.`<br>**Values:** Any string.                                                                                |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: content_rating_cs
        template_variables:
          use_separator: false
          sep_style: blue
          use_other: false
          append_addons:
            German 18:  # this doesn't have to exist already
              - de/18 # adds "de/18" to the existing "18" addon list
          sort_by: title.asc
```

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.


### Default `include`

```yaml
include:
  - 1
  - 2
  - 3
  - 4
  - 5
  - 6
  - 7
  - 8
  - 9
  - 10
  - 11
  - 12
  - 13
  - 14
  - 15
  - 16
  - 17
  - 18
```

### Default `addons`

```yaml
addons:
  1:
    - gb/U
    - gb/0+
    - G
    - TV-Y
    - E
    - gb/E
    - G - All Ages
    - "01"
  2:
    - gb/U
    - gb/0+
    - G
    - TV-Y
    - E
    - gb/E
    - G - All Ages
    - "02"
  3:
    - gb/U
    - gb/0+
    - G
    - TV-Y
    - E
    - gb/E
    - G - All Ages
    - "03"
  4:
    - gb/U
    - gb/0+
    - G
    - TV-Y
    - E
    - gb/E
    - G - All Ages
    - "04"
  5:
    - gb/U
    - gb/0+
    - G
    - TV-Y
    - E
    - gb/E
    - G - All Ages
    - "05"
  6:
    - gb/U
    - gb/0+
    - G
    - TV-Y
    - E
    - gb/E
    - G - All Ages
    - "06"
  7:
    - gb/PG
    - TV-PG
    - TV-Y7
    - TV-Y7-FV
    - PG
    - PG - Children
    - "07"
  8:
    - gb/PG
    - TV-PG
    - TV-Y7
    - TV-Y7-FV
    - PG
    - PG - Children
    - "08"
  9:
    - gb/PG
    - TV-PG
    - TV-Y7
    - TV-Y7-FV
    - PG
    - PG - Children
    - gb/9+
    - "09"
  10:
    - gb/PG
    - TV-PG
    - TV-Y7
    - TV-Y7-FV
    - PG
    - PG - Children
    - gb/9+
  11:
    - gb/PG
    - TV-PG
    - TV-Y7
    - TV-Y7-FV
    - PG
    - PG - Children
    - gb/9+
  12:
    - gb/12
    - gb/12A
    - 12+
    - PG
    - PG - Children
  13:
    - gb/12
    - gb/12A
    - 12+
    - PG-13
    - PG-13 - Teens 13 or older
  14:
    - gb/12
    - 12
    - gb/12A
    - 12+
    - PG-13
    - TV-14
    - 13
    - PG-13 - Teens 13 or older
  15:
    - gb/15
    - gb/14+
    - TV-14
    - 13
    - 14
    - PG-13 - Teens 13 or older
  16:
    - gb/15
    - gb/14+
    - TV-14
    - 13
    - 14
    - 15
    - PG-13 - Teens 13 or older
  17:
    - gb/15
    - gb/14+
    - TV-14
    - 13
    - 14
    - 15
    - 16
    - R - 17+ (violence & profanity)
  18:
    - gb/18
    - MA-17
    - TVMA
    - TV-MA
    - R
    - 16
    - 17
    - gb/R18
    - gb/X
    - X
    - NC-17
    - R - 17+ (violence & profanity)
    - R+ - Mild Nudity
    - Rx - Hentai
```