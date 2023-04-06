# Actor Collections

The `actor` Default Metadata File is used to dynamically create collections based on the most popular actors/actresses in your library.

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 140

| Collection                                      | Key                                             | Description                                                                 |
|:------------------------------------------------|:------------------------------------------------|:----------------------------------------------------------------------------|
| `Actors Collections`                            | `separator`                                     | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<actor_name>>`<br>**Example:** `Frank Welker` | `<<actor_name>>`<br>**Example:** `Frank Welker` | Collection of Movies/Shows the actor is top billing in.                     |

```{include} ../people.md
```

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: actor
  TV Shows:
    metadata_path:
      - pmm: actor
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                      | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|:------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `style`                       | **Description:** Controls the visual theme of the collections created.<br>**Default:** `bw`<br>**Values:** `bw`, `rainier`, `signature`, `diiivoy`, or `diiivoycolor`                                                                                                                                                                                                                                                                                                                                                                              |
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                                                                                                                                                                                                                                                                                                         |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                                                                                                                                                                                                                                                                                               |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                                                                                                                                                                                                                                                                                                         |
| `data`                        | **Description:** Replaces the `data` dynamic collection value.<table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>depth</code></td><td>Controls the depth within the casting credits to search for common actors<hr><strong>Default:</strong> 5<hr><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>limit</code></td><td>Controls the maximum number of collections to create<hr><strong>Default:</strong> 25<hr><strong>Values:</strong> Number greater than 0</td></tr></table> |
| `include`                     | **Description:** Force these Actors to be included to create a Dynamic Collection.<br>**Values:** List of Actor Names                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `exclude`                     | **Description:** Exclude these Actors from creating a Dynamic Collection.<br>**Values:** List of Actor Names                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `actor_name`                  | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                                                          |
| `actor_summary`               | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s with <<key_name>>.`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                        |
| `tmdb_person_offset`          | **Description:** Changes the summary `tmdb_person_offset` for specific People.<br>**Default:** `0`<br>**Values:** Dictionary of Actor Name as the keys and the `tmdb_person_offset` as the value.                                                                                                                                                                                                                                                                                                                                                  |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: actor
        template_variables:
          data:
            depth: 10
            limit: 20
          style: diiivoy
          sort_by: title.asc
          use_separator: false
          sep_style: purple
          tmdb_person_offset:
            Richard Brooks: 1
```
