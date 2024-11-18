# Subtitle Language Collections

The `subtitle_language` Default Collection File is used to dynamically create collections based on the subtitle 
languages available in your library.

![](../images/subtitle_language.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 095

| Collection                                               | Key                                                                                       | Description                                                                    |
|:---------------------------------------------------------|:------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------|
| `Subtitle Language Collections`                          | `separator`                                                                               | [Separator Collection](../separators.md) to denote the Section of Collections. |
| `<<Subtitle Language>> Audio`<br>**Example:** `Japanese` | `<<ISO 639-1 Code>>`<br>**Example:** `ja` <br>`<<ISO 639-2 Code>>`<br>**Example:** `myn`  | Collection of Movies/Shows that have this Subtitle Language.                   |
| `Other Subtitles`                                        | `other`                                                                                   | Collection of Movies/Shows that are less common Languages.                     |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: subtitle_language
  TV Shows:
    collection_files:
      - default: subtitle_language
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

        | Variable                      | Description & Values                                                                                                                                                                                                                                                               |
        |:------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                                            |
        | `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                                         |
        | `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                  |
        | `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                            |
        | `include`                     | **Description:** Overrides the [default include list](#default-values)<br>**Values:** List of [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)<br>**Values:** List of [ISO 639-2 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)                    |
        | `exclude`                     | **Description:** Exclude these Audio Languages from creating a Dynamic Collection.<br>**Values:** List of [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)<br>**Values:** List of [ISO 639-2 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes) |
        | `append_include`              | **Description:** Appends to the [default include list](#default-values)<br>**Values:** List of [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)<br>**Values:** List of [ISO 639-2 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)                   |
        | `remove_include`              | **Description:** Removes from the [default include list](#default-values)<br>**Values:** List of [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)<br>**Values:** List of [ISO 639-2 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)                 |
        | `key_name_override`           | **Description:** Overrides the [default key_name_override dictionary](#default-values).<br>**Values:** Dictionary with `key: new_key_name` entries                                                                                                                              |
        | `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> Subtitles`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                |
        | `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s with <<key_name>> Subtitles.`<br>**Values:** Any string.                                                                                                        |

        1. Each default collection has a `key` [see here]() that you must replace 
        `<<key>>` with when using this template variable.

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
          - default: subtitle_language
            template_variables:
              use_other: false #(1)!
              use_separator: false #(2)!
              exclude:
                - fr  #(3)!
              sort_by: title.asc
    ```

    1.  Do not create an "Other Audio" collection
    2.  Do not create an "Audio Language Collections" separator
    3.  Exclude "French" from having an Audio Collection

## Default Values

Unless you customize them as described above, these collections use default lists and searches to create the collections.

If you are interested in customizing the default values, you can find that information [here](#template-variables).

If you are interested in seeing what those default builders are, you can find that information [here](../sources.md).
