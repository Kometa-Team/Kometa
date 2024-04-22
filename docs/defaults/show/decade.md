# Decade Collections

The `decade` Collection File is used to dynamically create collections based on the decades available in your library, 
sorted by critic rating to create a "best of <decade>"

**[This file has a Movie Library Counterpart.](../movie/decade.md)**

![](../images/decade.png)

## Requirements & Recommendations

Supported Library Types: Show

## Collections Section 100

| Collection                                           | Key                               | Description                                                                    |
|:-----------------------------------------------------|:----------------------------------|:-------------------------------------------------------------------------------|
| `Decade Collections`                                 | `separator`                       | [Separator Collection](../separators.md) to denote the Section of Collections. |
| `Best of <<Decade>>`<br>**Example:** `Best of 2020s` | `<<Year>>`<br>**Example:** `2020` | Collection of Shows released in this Decade.                                   |
 
## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  TV Shows:
    collection_files:
      - default: decade
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this Kometa Defaults file.

    * **Shared Template Variables** are additional variables shared across the Kometa Defaults.

    * **Shared Separator Variables** are additional variables available since this Default contains a 
    [Separator](../separators.md).

    === "File-Specific Template Variables"

        | Variable                      | Description & Values                                                                                                                                                                                                    |
        |:------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Default:** `100`<br>**Values:** Number Greater than 0                                                                           |
        | `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                              |
        | `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `critic_rating.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options) |
        | `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                 |
        | `exclude`                     | **Description:** Exclude these Decades from creating a Dynamic Collection.<br>**Values:** List of Decades found in your library                                                                                         |
        | `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `Best of <<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                       |
        | `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `Top <<limit>> <<library_translation>>s of the <<key_name>>.`<br>**Values:** Any string.                                        |

        1. Each default collection has a `key` that when calling to effect a specific collection you must replace 
        `<<key>>` with when calling.

    === "Shared Template Variables"

        {%
          include-markdown "../collection_variables.md"
        %}

    === "Shared Separator Variables"

        {%
          include-markdown "../separator_variables.md"
        %}
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    Click the :fontawesome-solid-circle-plus: icon to learn more
    
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: year
            template_variables:
              sep_style: purple #(1)!
              sort_by: title.asc 
              sort_by_2020: release.desc #(2)!
    ```

    1.  Use the purple [Separator Style](../separators.md#separator-styles)
    2.  Set the sort order for "Best of 2020s" to release date descending
