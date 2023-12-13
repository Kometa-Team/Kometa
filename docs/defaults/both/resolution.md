# Resolution Collections

The `resolution` Default Collection File is used to dynamically create collections based on the resolutions available in your library.

![](../images/resolution.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 120

| Collection                                                   | Key                                 | Description                                                                    |
|:-------------------------------------------------------------|:------------------------------------|:-------------------------------------------------------------------------------|
| `Resolution Collections`                                     | `separator`                         | [Separator Collection](../separators.md) to denote the Section of Collections. |
| `<<Resolution>> Movies/Shows`<br>**Example:** `1080p Movies` | `<<Number>>`<br>**Example:** `1080` | Collection of Movies/Shows that have this Resolution.                          |

### Standards Style

Below is a screenshot of the alternative Standards (`standards`) style which can be set via the `style` template variable.

Standards Style takes the base resolutions ("4K" and "720p") and turns them into the commonly-known standards name ("Ultra HD" and "HD Ready")

![](../images/resolution_standards.png)

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: resolution
  TV Shows:
    collection_files:
      - pmm: resolution
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

This file contains a [Separator](../separators.md) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                      | Description & Values                                                                                                                                                                                                                                                |
|:------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `style`                       | **Description:** Controls the visual theme of the collections created.<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>default</code></td><td>Default Theme</td></tr><tr><td><code>standards</code></td><td>Standards Theme</td></tr></table>       |
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                             |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                          |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../builders/smart.md#sort-options)                                                         |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../builders/smart.md#sort-options)                                                                   |
| `include`                     | **Description:** Overrides the [default include list](#default-include).<br>**Values:** Any Resolutions found in your library                                                                                                                                       |
| `exclude`                     | **Description:** Exclude these Resolutions from creating a Dynamic Collection.<br>**Values:** List of Resolutions found in your library                                                                                                                             |
| `addons`                      | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Resolutions found in your library |
| `append_include`              | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of Resolutions found in your library                                                                                                                                  |
| `remove_include`              | **Description:** Removes from the [default include list](#default-include).<br>**Values:** List of Resolutions found in your library                                                                                                                                |
| `append_addons`               | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Resolutions found in your library                                                                                                                   |
| `remove_addons`               | **Description:** Removes from the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Resolutions found in your library                                                                                                                 |
| `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                 |
| `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s that have the resolution <<key_name>>.`<br>**Values:** Any string.                                                                               |

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
      - pmm: resolution
        template_variables:
          sep_style: green #(1)!
          exclude:
            - sd #(2)!
          sort_by: title.asc
```

1.  Use the green [Separator Style](../separators.md#separator-styles)
2.  Do not use the "sd" resolution as part of the "480p Movies/Shows" Collections

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
include:
  - 4k
  - 1080
  - 720
  - 480
```

### Default `addons`

```yaml
addons:
  4k:
    - 8k
  1080:
    - 2k
  480:
    - 144
    - 240
    - 360
    - sd
    - 576
```