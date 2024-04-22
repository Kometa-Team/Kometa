# Common Sense Media Content Rating Collections

The `content_rating_cs` Default Collection File is used to dynamically create collections based on the content ratings 
available in your library.

If you do not use the Common Sense-based rating system within Plex, this file will attempt to match the ratings in your 
library to the respective rating system.

![](../images/content_rating_cs.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

Recommendations: Use the 
[Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with either 
`mdb_commonsense` or `mdb_commonsense0` to update Plex to the Common Sense Rating.

## Collections Section 110

| Collection                                                        | Key                              | Description                                                                           |
|:------------------------------------------------------------------|:---------------------------------|:--------------------------------------------------------------------------------------|
| `Ratings Collections`                                             | `separator`                      | [Separator Collection](../separators.md) to denote the Section of Collections.        |
| `<<Content Rating>> Movies/Shows`<br>**Example:** `Age 5+ Movies` | `<<Number>>`<br>**Example:** `5` | Collection of Movies/Shows that have this Content Rating.                             |
| `Not Rated Movies/Shows`                                          | `other`                          | Collection of Movies/Shows that are Unrated, Not Rated or any other uncommon Ratings. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: content_rating_cs
  TV Shows:
    collection_files:
      - default: content_rating_cs
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

        | Variable                      | Description & Values                                                                                                                                                                                                                                            |
        |:------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                         |
        | `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                      |
        | `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                               |
        | `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                         |
        | `include`                     | **Description:** Overrides the [default include list](#include).<br>**Values:** List of Content Ratings found in your library                                                                                                                                   |
        | `append_include`              | **Description:** Appends to the [default include list](#include).<br>**Values:** List of Content Ratings found in your library                                                                                                                                  |
        | `remove_include`              | **Description:** Removes from the [default include list](#include).<br>**Values:** List of Content Ratings found in your library                                                                                                                                |
        | `exclude`                     | **Description:** Exclude these Content Ratings from creating a Dynamic Collection.<br>**Values:** List of Content Ratings found in your library                                                                                                                 |
        | `addons`                      | **Description:** Overrides the [default addons dictionary](#addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Content Ratings found in your library |
        | `append_addons`               | **Description:** Appends to the [default addons dictionary](#addons).<br>**Values:** Dictionary List of Content Ratings found in your library                                                                                                                   |
        | `remove_addons`               | **Description:** Removes from the [default addons dictionary](#addons).<br>**Values:** Dictionary List of Content Ratings found in your library                                                                                                                 |
        | `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `Age <<key_name>>+ <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                        |
        | `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s that are rated <<key_name>> accorfing to the Common Sense Rating System.`<br>**Values:** Any string.                                         |

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
          - default: content_rating_cs
            template_variables:
              sep_style: blue #(1)!
              use_other: false #(2)!
              append_addons:
                German 18: #(3)!
                  - "de/18" #(4)!
              sort_by: title.asc
    ```

    1.  Use the blue [Separator Style](../separators.md#separator-styles)
    2.  Do not create a "Not Rated Movies/Shows" collection
    3.  Defines a collection which will be called "German 18", this does not need to already exist in your library
    4.  Adds the "de/18" content rating to the "German 18" addon list, "de/18" must exist in your library if the "German
    18" content rating does not

## Default Values

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not 
show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default `include` (click to expand) <a class="headerlink" href="#include" title="Permanent link">¶</a>"

    <div id="include" />

    ```yaml
    include: {%    
      include-markdown "../../../defaults/both/content_rating_cs.yml" 
      comments=false
      preserve-includer-indent=false
      start="include:"
      end="addons:"
    %}
    ```

??? example "Default `addons` (click to expand) <a class="headerlink" href="#addons" title="Permanent link">¶</a>"

    <div id="addons" />

    ```yaml
    addons: {%    
      include-markdown "../../../defaults/both/content_rating_cs.yml" 
      comments=false
      preserve-includer-indent=false
      start="addons:"
    %}
    ```
