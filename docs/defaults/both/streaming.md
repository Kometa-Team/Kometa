# Streaming Collections

The `streaming` Default Collection File is used to dynamically create collections based on the streaming Services that 
your media is available on.

![](../images/streaming.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 030

!!! important

    As of Plex Meta Manager release 1.21, the keys associated with this Defaults file has changed.

    If you are setting custom images, you will need to use `<<originals_key>>`

| Collection                 | Key           | `originals_key`  | Description                                                                    |
|:---------------------------|---------------|:-----------------|:-------------------------------------------------------------------------------|
| `Streaming Collections`    | `separator`   | `separator`      | [Separator Collection](../separators.md) to denote the Section of Collections. |
| `All 4 Movies/Shows`       | `103`         | `all4`           | Collection of Movies/Shows Streaming on All 4.                                 |
| `Apple TV+ Movies/Shows`   | `350`         | `appletv`        | Collection of Movies/Shows Streaming on Apple TV+.                             |
| `BET+ Movies/Shows`        | `1759`        | `bet`            | Collection of Movies/Shows Streaming on BET+.                                  |
| `BritBox Movies/Shows`     | `151`         | `britbox`        | Collection of Movies/Shows Streaming on BritBox.                               |
| `Crave Movies/Shows`       | `230`         | `crave`          | Collection of Movies/Shows Streaming on Crave.                                 |
| `Crunchyroll Shows`        | `283`         | `crunchyroll`    | Collection of Shows Streaming on Crunchyroll.                                  |
| `discovery+ Shows`         | `510`         | `discovery`      | Collection of Shows Streaming on discovery+.                                   |
| `Disney+ Movies/Shows`     | `337`         | `disney`         | Collection of Movies/Shows Streaming on Disney+.                               |
| `Max Movies/Shows`         | `1189`        | `max`            | Collection of Movies/Shows Streaming on Max.                                   |
| `Hayu Shows`               | `223`         | `hayu`           | Collection of Shows Streaming on Hulu.                                         |
| `Hulu Movies/Shows`        | `15`          | `hulu`           | Collection of Movies/Shows Streaming on Hulu.                                  |
| `Netflix Movies/Shows`     | `8`           | `netflix`        | Collection of Movies/Shows Streaming on Netflix.                               |
| `NOW Movies/Shows`         | `39`          | `now`            | Collection of Movies/Shows Streaming on NOW.                                   |
| `Paramount+ Movies/Shows`  | `531`         | `paramount`      | Collection of Movies/Shows Streaming on Paramount+.                            |
| `Peacock Movies/Shows`     | `387`         | `peacock`        | Collection of Movies/Shows Streaming on Peacock.                               |
| `Prime Video Movies/Shows` | `9`           | `amazon`         | Collection of Movies/Shows Streaming on Prime Video.                           |
| `Showtime Movies/Shows`    | `37`          | `showtime`       | Collection of Movies/Shows Streaming on Showtime.                              |
| `YouTube Movies/Shows`     | `188`         | `youtube`        | Collection of Movies/Shows Streaming on YouTube.                               |

## Regional Variants

Some logic is applied for specific regions to prevent collections appearing which do not exist in said region.

| Region           | Key                              | Description                                                                                                                               |
|:-----------------|:---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| any besides `GB` | `all4`, `britbox`, `hayu`, `now` | These collections will not be created if the region is not `GB` as these streaming services are UK-focused                                |
| any besides `CA` | `crave`                          | These collections will not be created if the region is not `CA` as these streaming services are Canada-focused                            |
| `CA`             | `max`, `showtime`                | These collections will not be created if the region is `CA` as these streaming services are part of the Crave streaming service in Canada |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - pmm: streaming
  TV Shows:
    collection_files:
      - pmm: streaming
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this PMM Defaults file.

    * **Shared Template Variables** are additional variables shared across the PMM Defaults.

    * **Shared Separator Variables** are additional variables available since this Default contains a 
    [Separator](../separators.md).

    === "File-Specific Template Variables"

        | Variable                        | Description & Values                                                                                                                                                                                                                                                                                                         |
        |:--------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `region`                        | **Description:** Changes some Streaming Service lists to regional variants (see below table for more information.<br>**Default:** `us`<br>**Values:** Any [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) of the region where the streaming information should be based on.                                                                                                           |
        | `limit`                         | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Default:** `500`<br>**Values:** Number Greater than 0                                                                                                                                                                                                      |
        | `limit_<<key>>`<sup>1</sup>     | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                                                                                   |
        | `sort_by`                       | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                                            |
        | `sort_by_<<key>>`<sup>1</sup>   | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                                                      |
        | `sync_mode`                     | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                             |
        | `sync_mode_<<key>>`<sup>1</sup> | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                             |
        | `exclude`                       | **Description:** Exclude these Streaming Services from creating a Dynamic Collection.<br>**Values:** List of Streaming Service Keys                                                                                                                                                                                          |
        | `originals_only`                | **Description:** Changes  Streaming Service lists to only show original content produced by the service.<br>**Note**: Cannot be used with `region`, and only produces collections for `amazon`, `appletv`, `disney`, `max`, `hulu`, `netflix`, `paramount`, `peacock`<br>**Default:** `false`<br>**Values:** `true`, `false` |
        | `name_format`                   | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                          |
        | `summary_format`                | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s streaming on <<key_name>>.`<br>**Values:** Any string.                                                                                                                                                    |

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
          - pmm: streaming
            template_variables:
              region: FR #(1)!
              sep_style: amethyst #(2)!
              visible_library_disney: true #(3)!
              visible_home_disney: true #(4)!
              visible_shared_disney: true #(5)!
              sonarr_add_missing_hulu: true #(6)!
              radarr_add_missing_amazon: true #(7)!
              sort_by: random #(8)!
    ```

    1.  Use French region to determine streaming data from JustWatch/TMDb.
    2.  Use the amethyst [Separator Style](../separators.md#separator-styles)
    3.  Pin the "Disney+ Movies/Shows" collection to the Recommended tab of the library
    4.  Pin the "Disney+ Movies/Shows" collection to the home screen of the server owner
    5.  Pin the "Disney+ Movies/Shows" collection to the home screen of other users of the server
    6.  Add missing shows in your library from the "Hulu Shows" list to your Sonarr
    7.  Add missing movies in your library from the "Prime Video Movies" list to your Radarr
    8.  Sort all the collections created by this file randomly
