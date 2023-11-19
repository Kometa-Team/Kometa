# MAL Content Rating Collections

The `content_rating_mal` Default Metadata File is used to dynamically create collections based on the content ratings available in your library.

If you do not use the MAL-based rating system within Plex, this file will attempt to match the ratings in your library to the respective rating system.

![](../images/content_rating_mal.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

Recommendations: Use the [Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with `mal` to update Plex to the MyAnimeList Content Rating.

## Collections Section 110

| Collection                                                      | Key                                          | Description                                                                    |
|:----------------------------------------------------------------|:---------------------------------------------|:-------------------------------------------------------------------------------|
| `Ratings Collections`                                           | `separator`                                  | [Separator Collection](../separators.md) to denote the Section of Collections.    |
| `<<Content Rating>> Movies/Shows`<br>**Example:** `PG-13 Shows` | `<<Content Rating>>`<br>**Example:** `PG-13` | Collection of Shows that have this Content Rating.                             |
| `Not Rated Movies/Shows`                                        | `other`                                      | Collection of Shows that are Unrated, Not Rated or any other uncommon Ratings. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: content_rating_mal
  TV Shows:
    metadata_path:
      - pmm: content_rating_mal
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables.md) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators.md) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                      | Description & Values                                                                                                                                                                                                                                                    |
|:------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                                 |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                              |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../builders/smart.md#sort-options)                                                    |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../builders/smart.md#sort-options)                                                              |
| `include`                     | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of Content Ratings found in your library                                                                                                                                   |
| `exclude`                     | **Description:** Exclude these Content Ratings from creating a Dynamic Collection.<br>**Values:** List of Content Ratings found in your library                                                                                                                         |
| `addons`                      | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Content Ratings found in your library |
| `append_include`              | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of Content Ratings found in your library                                                                                                                                  |
| `remove_include`              | **Description:** Removes from the [default include list](#default-include).<br>**Values:** List of Content Ratings found in your library                                                                                                                                |
| `append_addons`               | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Content Ratings found in your library                                                                                                                   |
| `remove_addons`               | **Description:** Removes from the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Content Ratings found in your library                                                                                                                 |
| `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                     |
| `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s that are rated <<key_name>>.`<br>**Values:** Any string.                                                                                             |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

### Example Template Variable Amendments

The below is an example config.yml extract with some Template Variables added in to change how the file works.

???+ tip

    Anywhere you see this icon:
   
    > :fontawesome-solid-circle-plus:
   
    That's a tooltip, you can press them to get more information.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: content_rating_mal
        template_variables:
          sep_style: tan #(1)!
          use_other: false #(2)!
          append_addons:
            "R+ - Mild Nudity": #(3)!
              - "de/18" #(4)!
          sort_by: title.asc
```

1.  Use the tan [Separator Style](../separators.md#separator-styles)
2.  Do not create a "Not Rated Movies/Shows" collection
3.  Defines a collection which will be called "R+ - Mild Nudity", this does not need to already exist in your library
4.  Adds the "de/18" content rating to the "R+ - Mild Nudity" addon list, "de/18" must exist in your library if the "R+ - Mild Nudity" content rating does not

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
include:
  - "G"
  - "PG"
  - "PG-13"
  - "R"
  - "R+"
  - "Rx"
```

### Default `addons`

```yaml
    addons:
      G:
        - gb/U
        - gb/0+
        - U
        - G
        - 1
        - 2
        - 3
        - 4
        - 5
        - 6
        - "01"
        - "02"
        - "03"
        - "04"
        - "05"
        - "06"
        - G - All Ages
      PG:
        - TV-Y7
        - TV-Y7-FV
        - 7
        - 8
        - 9
        - "07"
        - "08"
        - "09"
        - gb/PG
        - gb/9+
        - 10
        - 11
        - 12
        - PG - Children
      PG-13:
        - 13
        - gb/12A
        - 12+
        - PG-13
        - TV-13
        - gb/14+
        - gb/15
        - 14
        - 15
        - 16
        - PG-13 - Teens 13 or older
      R:
        - 17
        - 18
        - gb/18
        - MA-17
        - NC-17
        - R
        - TVMA
        - R - 17+ (violence & profanity)
      R+:
        - R+ - Mild Nudity
      Rx:
        - Rx - Hentai
```
