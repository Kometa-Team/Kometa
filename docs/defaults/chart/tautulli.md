# Tautulli Chart Default Metadata File

The `- pmm: pmm: tautulli` Metadata File is used to create collections based on Tautulli/Plex Charts.

Example Collections Created:

![](../images/tautulli.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: pmm: tautulli
```

## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

As this file is more complex than tautullis, a key system is used to control each collection that is created by the file. Each key refers to one chart and is used to control multiple template variables.

Below are the keys and what they refer to:

| Key      | Chart        |
|:---------|:-------------|
| popular  | Plex Popular |
| watched  | Plex Watched |


Below are the available variables which can be used to customize the file. Note that any use of `key` within the variable should be replaced with the `key` from the above table (i.e. `use_watched` instead of `use_key`, `order_watched` instead of `order_key`)


| Variable               | Usage                                                                             | Default Value      |                                                                             Values                                                                             |
|:-----------------------|:----------------------------------------------------------------------------------|--------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| use_key                | Turn the collection on/off                                                        | `true`             |                                                                       `true` or `false`                                                                        |
| order_key              | Determine collection order in its section                                         | Alphabetical Order |                                 Any number (i.e. `01` for `order_watched` to put watched first in the list of tautulli charts)                                 |
| summary_key            | Determines summary of collection                                                  |                    |                                                                        Any summary text                                                                        |
| limit_key              | Determines limit of collection                                                    | `100`              |                                                                           Any number                                                                           |
| list_days_key          | Set list_days for the collection                                                  | `30`               |                                                                           Any number                                                                           |
| list_size_key          | Set list_size for the collection                                                  | `20`               |                                                                           Any number                                                                           |
| collection_order_key   | Determines collection order of the collection                                     |                    |                                                                                                                                                                |
| visible_library_key    | Set visible_library for the collection                                            | `false`            |                                                                       `true` or `false`                                                                        |
| visible_home_key       | Set visible_home for the collection                                               | `false`            |                                                                       `true` or `false`                                                                        |
| visible_shared_key     | Set visible_shared for the collection                                             | `false`            |                                                                       `true` or `false`                                                                        |
| item_sonarr_tag_key    | Sonarr Tag for existing items                                                     | `false`            |                                                                Tag(s) to add to existing items                                                                 |
| item_radarr_tag_key    | Radarr Tag for existing items                                                     |                    |                                                                Tag(s) to add to existing items                                                                 |
| collection_section     | Controls the sort order of these collections against tautulli default collections | `01`               |                                                                           Any number                                                                           |
| collection_mode        | Controls the collection mode of these collections                                 | `default`          | `default` - Library default<br/>`hide` - Hide Collection<br/>`hide_items`- Hide Items in this Collection<br/>`show_items` - Show this Collection and its Items |

The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: tautulli
        template_variables:
          use_watched: false
          order_watched: 01
          summary_watched: "Things that have been watched on Plex in the past 7 days"
          list_days_watched: 7
          list_size_watched: 10
          visible_library_watched: true
          visible_home_watched: true
          visible_shared_watched: true
          item_sonarr_tag_watched: Plex Watched
          item_radarr_tag_season: Plex Watched
          collection_section: 09
          collection_mode: show_items
```
