---
search:
  boost: 3
hide:
  - tags
tags:
  - addons
  - name
  - limit
  - template
  - schedule
  - run_again
  - sync_mode
  - builder_level
  - minimum_items
  - delete_below_minimum
  - delete_not_scheduled
  - tmdb_region
  - validate_builders
  - cache_builders
  - blank_collection
  - build_collection
  - server_preroll
  - missing_only_released
  - only_filter_missing
  - show_filtered
  - show_missing
  - save_report
  - ignore_ids
  - ignore_imdb_ids
  - name_mapping
  - test
  - tmdb_birthday
  - changes_webhooks
  - sync_to_trakt_list
  - sync_missing_to_trakt_list
  - run_definition
  - default_percent
  - ignore_blank_results
  - only_run_on_create
  - delete_collections_named
---

# Definition Settings

All the following attributes serve various functions as how the definition functions inside of Kometa.

| Attribute                    | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|:-----------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                       | **Description:** Used to specify the name of the definition in Plex as different than the mapping name.<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                         |
| `limit`                      | **Description:** Used to specify the max number of items for the definition<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                          | 
| `template`                   | **Description:** Used to specify a template and template variables to use for this definition. See the [Templates Page](templates.md) for more information.<br>**Values:** Dictionary                                                                                                                                                                                                                                                                                                                                     |
| `schedule`                   | **Description:** Used to specify the schedule when this definition will run.<br>**Default:** `daily`<br>**Values:** [Any Schedule Option](../config/schedule.md)                                                                                                                                                                                                                                                                                                                                                          |
| `run_again`                  | **Description:** Used to try and add all the missing items to the definition again after the daily run.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                          |
| `sync_mode`                  | **Description:** Used to change how builders sync with this definition.<br>**Default:** `sync_mode` [settings value](../config/settings.md) in the Configuration File<br>**Values:**<table class="clearTable"><tr><td>`append`</td><td>Only Add Items to the Collection</td></tr><tr><td>`sync`</td><td>Add & Remove Items from the Collection</td></tr></table>                                                                                                                                                          |
| `builder_level`              | **Description:** Make season, episode, album or track collections/overlays from `plex_all`, `plex_search`, `trakt_list`, or `imdb_list` Builders and Filters<br>**Values:**<table class="clearTable"><tr><td>`season`</td><td>Collection contains seasons</td></tr><tr><td>`episode`</td><td>Collection contains episodes</td></tr><tr><td>`album`</td><td>Collection contains albums</td></tr><tr><td>`track`</td><td>Collection contains tracks</td></tr></table>                                                       |
| `minimum_items`              | **Description:** Minimum items that must be found to add to a definition.<br>**Default:** `minimum_items` [settings value](../config/settings.md) in the Configuration File<br>**Values:** number greater than 0                                                                                                                                                                                                                                                                                                          |
| `delete_below_minimum`       | **Description:** Deletes the definition if below the minimum.<br>**Default:** `delete_below_minimum` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                   |
| `delete_not_scheduled`       | **Description:** Deletes the definition if its skipped because its not scheduled.<br>**Default:** `delete_not_scheduled` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                               |
| `tmdb_region`                | **Description:** Sets the region for `tmdb_popular`, `tmdb_now_playing`, `tmdb_top_rated`, and `tmdb_upcoming`                                                                                                                                                                                                                                                                                                                                                                                                            |
| `validate_builders`          | **Description:** When set to false the definition will not fail if one builder fails.<br>**Default:** `true`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                             |
| `cache_builders`             | **Description:** Caches the items found by the builders for a number of days. This is useful if you run the same configuration on multiple libraries/servers in one run just set the value to `1`.<br>**Default:** `0` <br>**Values:** number 0 or greater                                                                                                                                                                                                                                                                | 
| `blank_collection`           | **Description:** When set to true the collection will be created with no builders and no items added.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                            |
| `build_collection`           | **Description:** When set to false the collection won't be created but items can still be added to Radarr/Sonarr. Does not work for playlists.<br>**Default:** `true`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                    |
| `server_preroll`             | **Description:** Used to set the `Movie pre-roll video` Text box in Plex under Settings -> Extras.<br>You can run this with a [schedule](../config/schedule.md) to change the pre-rolls automatically.<br>**Values:** Any String                                                                                                                                                                                                                                                                                          |
| `missing_only_released`      | **Description:** definition Level `missing_only_released` toggle.<br>**Default:** `missing_only_released` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                              |
| `only_filter_missing`        | **Description:** definition Level `only_filter_missing` toggle.<br>**Default:** `only_filter_missing` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                  |
| `show_filtered`              | **Description:** definition level `show_filtered` toggle.<br>**Default:** `show_filtered` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                              |
| `show_missing`               | **Description:** definition level `show_missing` toggle.<br>**Default:** `show_missing` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                |
| `save_report`                | **Description:** definition level `save_report` toggle.<br>**Default:** `save_report` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                  |
| `ignore_ids`                 | **Description:** definition level `ignore_ids` which is combined with the library and global `ignore_ids`.<br>**Default:** `ignore_ids` [settings value](../config/settings.md) in the Configuration File<br>**Values:** List or comma-separated String of TMDb/TVDb IDs                                                                                                                                                                                                                                                  |
| `ignore_imdb_ids`            | **Description:** definition level `ignore_imdb_ids` which is combined with the library and global `ignore_imdb_ids`.<br>**Default:** `ignore_imdb_ids` [settings value](../config/settings.md) in the Configuration File<br>**Values:** List or comma-separated String of IMDb IDs                                                                                                                                                                                                                                        |
| `name_mapping`               | **Description:** Used to specify the folder name in the [Image Assets Directory](../kometa/guides/assets.md) i.e. if your definition name contains characters that are not allowed in file paths (i.e. for windows `<`, `>`, `:`, `"`, `/`, `\`, `?`, `*` cannot be in the file path), but you want them in your name you can this to specify the name in the file system.<br>**Values:** Any String                                                                                                                      |
| `test`                       | **Description:** When running in Test Mode (`--run-tests` [option](../kometa/environmental.md)) only definitions with `test: true` will be run.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                  |
| `tmdb_birthday`              | **Description:** Controls if the Definition is run based on `tmdb_person`'s Birthday. Has 3 possible attributes `this_month`, `before` and `after`.<br>**Values:**<table class="clearTable"><tr><td>`this_month`</td><td>Run's if Birthday is in current Month</td><td>`true`/`false`</td></tr><tr><td>`before`</td><td>Run if X Number of Days before the Birthday</td><td>Number 0 or greater</td></tr><tr><td>`after`</td><td>Run if X Number of Days after the Birthday</td><td>Number 0 or greater</td></tr></table> |
| `changes_webhooks`           | **Description:** Used to specify a definition changes webhook for just this definition.<br>**Values:** List of webhooks                                                                                                                                                                                                                                                                                                                                                                                                   |
| `sync_to_trakt_list`         | **Description:** Used to specify a trakt list you want the definition synced to.<br>**Values:** Trakt List Slug you want to sync to                                                                                                                                                                                                                                                                                                                                                                                       |
| `sync_missing_to_trakt_list` | **Description:** Used to also sync missing items to the Trakt List specified by `sync_to_trakt_list`.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                            |
| `run_definition`             | **Description:** Used to specify if this definition runs.<br>Multiple can be used for one definition as a list or comma separated string. One `false` or unmatched library type will cause it to fail.<br>**Values:** `movie`, `show`, `artist`, `true`, `false`                                                                                                                                                                                                                                                          |
| `default_percent`            | **Description:** Used to declare the default percent for `episodes`, `seasons`, `tracks`, and `albums` [special filters](filters.md#special-filters). Default is 50.<br>**Values:** Integer between 1 and 100                                                                                                                                                                                                                                                                                                             |
| `ignore_blank_results`       | **Description:** Used to not have Errors resulting from blank results from builders.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                             |
| `only_run_on_create`         | **Description:** Used to only run the collection definition if the collection doesn't already exist.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                             |
| `delete_collections_named`   | **Description:** Used to delete any collections in your plex named one of the given collections.<br>**Values:** List of Collection Names to delete                                                                                                                                                                                                                                                                                                                                                                        |

An example of using `default_percent` which is used in an external yml file and not within config.yml:

```yml
  HDR10Plus:
    default_percent: 35  #default default_percent is 50
    template:
      - name: Resolution
        weight: 400
        opt1: hdr10p
    plex_search:
      all:
        hdr: true
    filters:
      filepath.regex: 'HDR10\+|HDR10P'
```

An example of using `server_preroll` which is also used in an external yml file and not within config.yml:

```yml
templates:
  preroll:
    default:  # HERE
      location: "\\path\\to\\file"
    build_collection: false
    schedule: <<schedule>>
    server_preroll: <<location>>
collections:
  base:
    template: {name: preroll, location: "\\path\\to\\file", schedule: daily}
  date1:
    template: {name: preroll, location: "\\path\\to\\file", schedule: range(12/01-12/31)}
  date2:
    template: {name: preroll, location: "\\path\\to\\file2", schedule: range(01/01-01/31)}
```
