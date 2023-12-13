# US Content Rating Collections

The `content_rating_us` Default Collection File is used to dynamically create collections based on the content ratings available in your library.

If you do not use the US-based rating system within Plex, this file will attempt to match the ratings in your library to the respective rating system.

**This file has a Show Library [Counterpart](../show/content_rating_us.md).**

![](../images/moviecontent_rating_us.png)

## Requirements & Recommendations

Supported Library Types: Movie

Recommendation: Set the Certification Country within your library's advanced settings to "United States".

## Collections Section 110

| Collection                                             | Key                                      | Description                                                                       |
|:-------------------------------------------------------|:-----------------------------------------|:----------------------------------------------------------------------------------|
| `Country Collections`                                  | `separator`                              | [Separator Collection](../separators.md) to denote the Section of Collections.    |
| `<<Content Rating>> Movies`<br>**Example:** `R Movies` | `<<Content Rating>>`<br>**Example:** `R` | Collection of Movies that have this Content Rating.                               |
| `Not Rated Movies`                                     | `other`                                  | Collection of Movies that are Unrated, Not Rated or any other uncommon Ratings.   |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: content_rating_us
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

This file contains a [Separator](../separators.md) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                      | Description & Values                                                                                                                                                                                                                                                    |
|:------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                                 |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                              |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../builders/smart.md#sort-options)                                                             |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../builders/smart.md#sort-options)                                                                       |
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

{%
   include-markdown "../collection_variables.md"
%}
### Example Template Variable Amendments

The below is an example config.yml extract with some Template Variables added in to change how the file works.

???+ tip

    Anywhere you see this icon:
   
    > :fontawesome-solid-circle-plus:
   
    That's a tooltip, you can press them to get more information.

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: content_rating_us
        template_variables:
          sep_style: blue #(1)!
          use_other: false #(2)!
          append_addons:
            R: #(3)!
              - "de/18" #(4)!
          sort_by: title.asc
```

1.  Use the blue [Separator Style](../separators.md#separator-styles)
2.  Do not create a "Not Rated Movies" collection
3.  Defines a collection which will be called "R", this does not need to already exist in your library
4.  Adds the "de/18" content rating to the "R" addon list, "de/18" must exist in your library if the "R" content rating does not

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
include:
  - G
  - PG
  - PG-13
  - R
  - NC-17
```

### Default `addons`

```yaml
addons:
  G:
    - gb/U
    - gb/0+
    - U
    - TV-Y
    - TV-G
    - E
    - gb/E
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
    - gb/PG
    - gb/9+
    - TV-PG
    - TV-Y7
    - TV-Y7-FV
    - 7
    - 8
    - 9
    - "07"
    - "08"
    - "09"
    - "10"
    - "11"
    - PG - Children
  PG-13:
    - gb/12A
    - gb/12
    - 12+
    - TV-13
    - gb/14+
    - gb/15
    - TV-14
    - 12
    - 13
    - 14
    - 15
    - 16
    - PG-13 - Teens 13 or older
  R:
    - 17
    - 18
    - gb/18
    - MA-17
    - TVMA
    - TV-MA
    - R - 17+ (violence & profanity)
    - R+ - Mild Nudity
  NC-17:
    - gb/R18
    - gb/X
    - R18
    - X
    - Rx - Hentai
```
