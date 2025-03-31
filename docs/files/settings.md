---
search:
  boost: 3
hide:
  - tags
  - toc
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
  - show_unfiltered
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

| Attribute                    | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|:-----------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `blank_collection`           | **Description:** When set to true the collection will be created with no builders and no items added.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `build_collection`           | **Description:** When set to false the collection won't be created but items can still be added to Radarr/Sonarr. Does not work for playlists.<br>**Default:** `true`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `builder_level`              | **Description:** Make season, episode, album or track collections/overlays from `plex_all`, `plex_search`, `trakt_list`, or `imdb_list` Builders and Filters<br>**Values:**<table class="clearTable"><tr><td>`season`</td><td>Collection contains seasons</td></tr><tr><td>`episode`</td><td>Collection contains episodes</td></tr><tr><td>`album`</td><td>Collection contains albums</td></tr><tr><td>`track`</td><td>Collection contains tracks</td></tr></table>                                                                                                                                                                            |
| `cache_builders`             | **Description:** Caches the items found by the builders for a number of days. This is useful if you run the same configuration on multiple libraries/servers in one run just set the value to `1`.<br>**Default:** `0` <br>**Values:** number 0 or greater                                                                                                                                                                                                                                                                                                                                                                                     |
| `changes_webhooks`           | **Description:** Used to specify a definition changes webhook for just this definition.<br>**Values:** List of webhooks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `default_percent`            | **Description:** Used to declare the default percent for `episodes`, `seasons`, `tracks`, and `albums` [special filters](filters.md#special-filters). See [Example](#default-percent-example) below.<br>**Default:** `50`.<br>**Values:** Integer between 1 and 100                                                                                                                                                                                                                                                                                                                                                                            |
| `delete_below_minimum`       | **Description:** Deletes the definition if below the minimum.<br>**Default:** `delete_below_minimum` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `delete_collections_named`   | **Description:** Used to delete any collections in your plex named one of the given collections.<br>**Values:** List of Collection Names to delete                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `delete_not_scheduled`       | **Description:** Deletes the definition if its skipped because its not scheduled.<br>**Default:** `delete_not_scheduled` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `ignore_blank_results`       | **Description:** Used to not have Errors resulting from blank results from builders.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `ignore_ids`                 | **Description:** definition level `ignore_ids` which is combined with the library and global `ignore_ids`.<br>**Default:** `ignore_ids` [settings value](../config/settings.md) in the Configuration File<br>**Values:** List or comma-separated String of TMDb/TVDb IDs                                                                                                                                                                                                                                                                                                                                                                       |
| `ignore_imdb_ids`            | **Description:** definition level `ignore_imdb_ids` which is combined with the library and global `ignore_imdb_ids`.<br>**Default:** `ignore_imdb_ids` [settings value](../config/settings.md) in the Configuration File<br>**Values:** List or comma-separated String of IMDb IDs                                                                                                                                                                                                                                                                                                                                                             |
| `limit`                      | **Description:** Used to specify the max number of items for the definition<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `minimum_items`              | **Description:** Minimum items that must be found to add to a definition.<br>**Default:** `minimum_items` [settings value](../config/settings.md) in the Configuration File<br>**Values:** number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `missing_only_released`      | **Description:** definition Level `missing_only_released` toggle.<br>**Default:** `missing_only_released` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `name_mapping`               | **Description:** Used to specify the folder name in the [Image Assets Directory](../kometa/guides/assets.md) i.e. if your definition name contains characters that are not allowed in file paths (i.e. for windows `<`, `>`, `:`, `"`, `/`, `\`, `?`, `*` cannot be in the file path), but you want them in your name you can this to specify the name in the file system.<br>**Values:** Any String                                                                                                                                                                                                                                           |
| `name`                       | **Description:** Used to specify the name of the definition in Plex as different than the mapping name.<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `only_filter_missing`        | **Description:** definition Level `only_filter_missing` toggle.<br>**Default:** `only_filter_missing` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `only_run_on_create`         | **Description:** Used to only run the collection definition if the collection doesn't already exist.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `run_again`                  | **Description:** Used to try and add all the missing items to the definition again after the daily run.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `run_definition`             | **Description:** Used to specify if this definition runs.<br>Multiple can be used for one definition as a list or comma separated string. One `false` or unmatched library type will cause it to fail.<br>**Values:** `movie`, `show`, `artist`, `true`, `false`                                                                                                                                                                                                                                                                                                                                                                               |
| `save_report`                | **Description:** definition level `save_report` toggle.<br>**Default:** `save_report` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `schedule`                   | **Description:** Used to specify the schedule when this definition will run.<br>**Default:** `daily`<br>**Values:** [Any Schedule Option](../config/schedule.md)                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `server_preroll`             | **Description:** Used to set the `Movie pre-roll video` Text box in Plex under Settings -> Extras.<br>See the [Movie pre-roll video section on the Plex Extras Page](https://support.plex.tv/articles/202920803-extras/) for what the semicolons `;` and commas `,` mean to Plex.<br>You can run this with a [schedule](../config/schedule.md) to change the pre-rolls automatically.<br>See [Example](#server-preroll-example) below.<br>**Values:** Any String or a List of Strings/Nested List of Strings<br> \* When using a list the top level elements are separated by semicolons `;` and the nested lists are separated by commas `,`. |
| `show_filtered`              | **Description:** definition level `show_filtered` toggle.<br>**Default:** `show_filtered` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `show_missing`               | **Description:** definition level `show_missing` toggle.<br>**Default:** `show_missing` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `show_unfiltered`            | **Description:** definition level `show_unfiltered` toggle.<br>**Default:** `show_unfiltered` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `smart_label`                | **Description:** Adds a label to all items found by the builder, which is then used to create a Smart Collection searching for the label<br>See [Smart Label Definitions](#smart-label-defintiions) for more information and use-cases                                                                                                                                                                                                                                                                                                                                                                                                         |
| `sync_missing_to_trakt_list` | **Description:** Used to also sync missing items to the Trakt List specified by `sync_to_trakt_list`.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `sync_mode`                  | **Description:** Used to change how builders sync with this definition.<br>**Default:** `sync_mode` [settings value](../config/settings.md) in the Configuration File<br>**Values:** `sync` or `append`<br>See main [settings page](../config/settings.md#sync-mode)                                                                                                                                                                                                                                                                                                                                                                           |
| `sync_to_trakt_list`         | **Description:** Used to specify a trakt list you want the definition synced to.<br>**Values:** Trakt List Slug you want to sync to                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `template`                   | **Description:** Used to specify a template and Template Variables to use for this definition. See the [Templates Page](templates.md) for more information.<br>**Values:** Dictionary                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `test`                       | **Description:** When running in Test Mode (`--run-tests` [option](../kometa/environmental.md)) only definitions with `test: true` will be run.<br>**Default:** `false`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `tmdb_birthday`              | **Description:** Controls if the Definition is run based on `tmdb_person`'s Birthday. Has 3 possible attributes `this_month`, `before` and `after`.<br>**Values:**<table class="clearTable"><tr><td>`this_month`</td><td>Run's if Birthday is in current Month</td><td>`true`/`false`</td></tr><tr><td>`before`</td><td>Run if X Number of Days before the Birthday</td><td>Number 0 or greater</td></tr><tr><td>`after`</td><td>Run if X Number of Days after the Birthday</td><td>Number 0 or greater</td></tr></table>                                                                                                                      |
| `tmdb_deathday`              | **Description:** Controls if the Definition is run based on `tmdb_person`'s Deathday. Has 3 possible attributes `this_month`, `before` and `after`.<br>**Values:**<table class="clearTable"><tr><td>`this_month`</td><td>Run's if Deathday is in current Month</td><td>`true`/`false`</td></tr><tr><td>`before`</td><td>Run if X Number of Days before the Deathday</td><td>Number 0 or greater</td></tr><tr><td>`after`</td><td>Run if X Number of Days after the Deathday</td><td>Number 0 or greater</td></tr></table>                                                                                                                      |
| `tmdb_region`                | **Description:** Sets the region for `tmdb_popular`, `tmdb_now_playing`, `tmdb_top_rated`, and `tmdb_upcoming`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `validate_builders`          | **Description:** When set to false the definition will not fail if one Builder fails.<br>**Default:** `true`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

## Smart Label Definitions

Smart Labels are a process that Kometa uses to build [Smart Collections](builders/plex.md#understanding-smart-vs-manual-collections) using non-Plex builders.

Instead of building a Manual (also known as Dumb or non-Smart) Collection with items from third-party builders, 
Kometa applies a label to every item that is discovered by the builder.

This label is then used as part of a [Smart Filter Builder](builders/plex.md#smart-filter-builder) to create a Smart Collection showing any item that has that label.

The result is a Smart Collection which only updates when the specific label is added/removed from items within Plex (either by the user or Kometa adding or remove the label).

Here is an example of a Smart Label definition being used to create a Smart Collection.

```yaml
collections:
  Marvel Cinematic Universe:
    trakt_list: https://trakt.tv/users/jawann2002/lists/marvel-cinematic-universe-movies?sort=rank,asc
    smart_label: release.desc
```

The above can also be defined as:
```yaml
collections:
  Marvel Cinematic Universe:
    trakt_list: https://trakt.tv/users/jawann2002/lists/marvel-cinematic-universe-movies?sort=rank,asc
    smart_label:
      sort_by: release.desc
      all:
        label: <<smart_label>>
```

The processing for both of the above examples are identical: Kometa fetches all the items within that Trakt list and applies a 
"Marvel Cinematic Universe" label to each of the items in Plex.

It then uses the Smart Label definition (which is effectively a `smart_filter` builder) which searches for items which has the label of `<<smart_label>>` 
(equating to a search of `label: Marvel Cinematic Universe`) and then sorts those results by `release.desc`.

Smart Label definitions can be used with any other Smart Builder search criteria, allowing for additional filtering and views that otherwise would not be possible.

Let's add some new criteria to our previous example:

```yaml
collections:
  Unplayed Marvel Cinematic Universe with Robert Downey Jr:
    trakt_list: https://trakt.tv/users/jawann2002/lists/marvel-cinematic-universe-movies?sort=rank,asc
    smart_label:
      sort_by: release.desc
      all:
        label: <<smart_label>>
        unplayed: true
        actor: "Robert Downey Jr."
```

The above workflow would still happen as described (note that the label applied to the items would now be "Unplayed Marvel Cinematic Universe with Robert Downey Jr."), 
but the Smart Filter now includes two new criteria; that the item must be unplayed and must feature Robert Downey Jr.

### Smart Labels & Plex Collectionless 

Smart Label definitions are especially powerful because Smart Collections are not subject to the usual show/hide rules that affect Manual collections. 
As such, it can help resolve issues like those described in [Plex Collectionless](builders/plex.md#plex-collectionless). 

For example, if Marvel Cinematic Universe is set up using the smart label method, and all other Marvel-related collections are Manual collections, 
Plex will handle the visibility correctly across grouped collections.

To fully take advantage of this method and eliminate the need for Plex Collectionless, it’s important to commit to using this system consistently. 
A good rule of thumb is: each item in your library should belong to no more than one non-smart collection.

The only downside of using smart collections is that they are unable to be sorted by `custom` (which uses the order of the original builder). 
In order to have a custom ordered Marvel Cinematic Universe Collection  with the show/hide of the collection to work correctly you will have to use
[Plex Collectionless](builders/plex.md#plex-collectionless).

## Default Percent Example

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

### Server Preroll Example

An example of using `server_preroll` with a schedule which is also used in an external yml file and not within config.yml:

```yml
collections:
  january:
    build_collection: false
    server_preroll: "\\path\\to\\file"
    schedule: range(01/01-01/31)
  base:
    build_collection: false
    server_preroll: "\\path\\to\\file2;\\path\\to\\file3"
    schedule: range(02/01-11/31)
  december:
    build_collection: false
    server_preroll: "\\path\\to\\file4"
    schedule: range(12/01-12/31)
```

An example of using `server_preroll` as a list with nested lists. The double dash (`- -`) denotes the start of a nested list 

```yml
collections:
  base:
    build_collection: false
    server_preroll: 
      - "\\path\\to\\file1"
      - - "\\path\\to\\file2"
        - "\\path\\to\\file3"
      - "\\path\\to\\file4"
```

When Kometa adds this to Plex the translated string will be `\\path\\to\\file1;\\path\\to\\file2,\\path\\to\\file3;\\path\\to\\file4`. 
(Notice that some separators are semicolons `;` and some are commas `,`)

Plex preroll videos and this setting are covered at [Plex Extras](https://support.plex.tv/articles/202920803-extras/).

In a nutshell, this will play **one of** the files in the list before the movie starts:
```yml
collections:
  base:
    build_collection: false
    server_preroll: 
      - "\\path\\to\\file1"
      - "\\path\\to\\file2"
      - "\\path\\to\\file3"
      - "\\path\\to\\file4"
```

While this will play **all of** the files in the list before the movie starts:
```yml
collections:
  base:
    build_collection: false
    server_preroll: 
      - - "\\path\\to\\file1"
        - "\\path\\to\\file2"
        - "\\path\\to\\file3"
        - "\\path\\to\\file4"
```

And a mixed example like this:

```yml
collections:
  base:
    build_collection: false
    server_preroll: 
      - "\\path\\to\\file1"
      - - "\\path\\to\\file2"
        - "\\path\\to\\file3"
      - "\\path\\to\\file4"
```

would play one of these three options before the movie starts:

- `file1`
- both `file2` and `file3`
- `file4`
