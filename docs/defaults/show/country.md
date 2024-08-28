# Country Collections

The `country` Default Collection File is used to dynamically create collections based on the countries available in your library.

**[This file has a Movie Library Counterpart.](../movie/country.md).**

![](../images/country1.png)

## Requirements & Recommendations

Supported Library Types: Show

## Collections Section 080

| Collection                              | Key                                                | Description                                                                    |
|:----------------------------------------|:---------------------------------------------------|:-------------------------------------------------------------------------------|
| `Country Collections`                   | `separator`                                        | [Separator Collection](../separators.md) to denote the Section of Collections. |
| `<<Country>>`<br>**Example:** `Germany` | `<<2 digit ISO 3166-1 code>>`<br>**Example:** `de` | Collection of TV Shows that have this Country.                                 |
| `Other Countries`                       | `other`                                            | Collection of TV Shows that are in other uncommon Countries.                   |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  TV Shows:
    collection_files:
      - default: country
```

## Color Style

Below is a screenshot of the alternative Color (`color`) style which can be set via the `style` template variable.

![](../images/country2.png)

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    === "File-Specific Template Variables"

        The below template variables are available specifically for this Kometa Defaults file.

        Be sure to also check out the "Shared Template Variables" tab for additional variables.

        This file contains a [Separator](../separators.md) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

        | Variable                        | Description & Values                                                                                                                                                                                                                                                                             |
        |:--------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `style`                         | **Description:** Controls the visual theme of the collections created<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>white</code></td><td>White Theme</td></tr><tr><td><code>color</code></td><td>Color Theme</td></tr></table>                                                 |
        | `limit`                         | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                                                          |
        | `limit_<<key>>`<sup>1</sup>     | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                                                       |
        | `sync_mode`                     | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sync_mode_<<key>>`<sup>1</sup> | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sort_by`                       | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                |
        | `sort_by_<<key>>`<sup>1</sup>   | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                          |
        | `include`                       | **Description:** Overrides the [default include list](#include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                                 |
        | `append_include`                | **Description:** Appends to the [default include list](#include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                                |
        | `remove_include`                | **Description:** Removes from the [default include list](#include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                              |
        | `exclude`                       | **Description:** Exclude these Countries from creating a Dynamic Collection.<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                     |
        | `addons`                        | **Description:** Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                   |
        | `append_addons`                 | **Description:** Appends to the [default addons dictionary](#addons).<br>**Values:** Dictionary List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                 |
        | `remove_addons`                 | **Description:** Removes from the [default addons dictionary](#addons).<br>**Values:** Dictionary List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                               |
        | `key_name_override`             | **Description:** Overrides the [default key_name_override dictionary](#key-name-override).<br>**Values:** Dictionary with `key: new_key_name` entries                                                                                                                                            |
        | `name_format`                   | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                        |
        | `summary_format`                | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s filmed in <<key_name>>.`<br>**Values:** Any string.                                                                                                                           |

        1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

    === "Shared Template Variables"

        {%
          include-markdown "../collection_variables.md"
        %}
    
    ???+ example "Example Template Variable Amendments"

        The below is an example config.yml extract with some Template Variables added in to change how the file works.
    
        Click the :fontawesome-solid-circle-plus: icon to learn more
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - default: country
                template_variables:
                  use_other: false #(1)!
                  use_separator: false #(2)!
                  style: color #(3)!
                  exclude:
                    - France #(4)!
                  sort_by: title.asc
        ```
    
        1.  Do not create the "Other Countries" collection
        2.  Do not create a "Country Collections" separator
        3.  Set the [Color Style](#color-style)
        4.  Exclude "France" from the list of collections that are created

## Default Values

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default `include` (click to expand) <a class="headerlink" href="#include" title="Permanent link">¶</a>"

    <div id="include" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    include: {%    
      include-markdown "../../../defaults/show/country.yml" 
      comments=false
      preserve-includer-indent=false
      start="include:"
      end="addons:"
    %}
    ```

??? example "Default `addons` (click to expand) <a class="headerlink" href="#addons" title="Permanent link">¶</a>"

    <div id="addons" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    addons: {%    
      include-markdown "../../../defaults/show/country.yml" 
      comments=false
      preserve-includer-indent=false
      start="addons:"
    %}
    ```
