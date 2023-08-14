# Genre Collections

The `genre` Default Metadata File is used to dynamically create collections based on the genres available in your library.

This file also merges similarly named genres (such as "Sci-Fi", "SciFi" and "Sci-Fi & Fantasy") into one ("Science Fiction")

![](../images/genre.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 060

| Collection                                               | Key                              | Description                                                                 |
|:---------------------------------------------------------|:---------------------------------|:----------------------------------------------------------------------------|
| `Genre Collections`                                      | `separator`                      | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<Genre>> Movies/Shows`<br>**Example:** `Action Movies` | `<<Number>>`<br>**Example:** `5` | Collection of Movies/Shows that have this Genre.                            |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: genre
  TV Shows:
    metadata_path:
      - pmm: genre
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                      | Description & Values                                                                                                                                                                                                                                           |
|:------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                        |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                     |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                           |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                     |
| `exclude`                     | **Description:** Exclude these Genres from creating a Dynamic Collection.<br>**Values:** List of Genres found in your library                                                                                                                                  |
| `addons`                      | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Genres found in your library |
| `append_addons`               | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Genres found in your library                                                                                                                   |
| `remove_addons`               | **Description:** Removes from the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Genres found in your library                                                                                                                 |
| `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                            |
| `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s that have the genre <<key_name>>.`<br>**Values:** Any string.                                                                               |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: genre
        template_variables:
          use_separator: false
          sep_style: red
          exclude:
            - Politics
            - News
          append_addons:
            Horror:
              - Thriller  # Adds all thriller items to the Horror collection
          sort_by: title.asc
```

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `addons`

```yaml
addons:
  Action:
    - Action/Adventure
    - Action/adventure
    - Action & Adventure
    - Action & adventure
    - Action and Adventure
    - Action and adventure
  Adventure:
    - Action/Adventure
    - Action/adventure
    - Action & Adventure
    - Action & adventure
    - Action and Adventure
    - Action and adventure
  Biopic:
    - Biography
  Family:
    - Kids & Family
  Fantasy:
    - SciFi & Fantasy
    - Science Fiction & Fantasy
    - Science-Fiction & Fantasy
    - Sci-Fi & Fantasy
  Film Noir:
    Film-Noir
  Politics:
    - War & Politics
  Science Fiction:
    - SciFi
    - Sci-Fi
    - Science-Fiction
    - SciFi & Fantasy
    - Science Fiction & Fantasy
    - Sci-Fi & Fantasy
  Talk Show:
    - Talk
  War:
    - War & Politics
```