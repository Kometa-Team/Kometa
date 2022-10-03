# Streaming Default Metadata File

The `- pmm: streaming` Metadata File is used to dynamically create collections based on the streaming Services that your media is available on.

Example Collections Created:

![](../images/streaming.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: streaming
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

As this file is more complex than others, a key system is used to control each collection that is created by the file. Each key refers to one streaming service and is used to control multiple template variables.

Below are the keys and what they refer to:

| Key       | streaming Service |
|:----------|:------------------|
| all4      | All 4             |
| amazon    | Prime Video       |
| appletv   | Apple TV+         |
| bet       | BET+              |
| britbox   | BritBox           |
| disney    | Disney+           |
| hayu      | hayu              |
| hbomax    | HBO Max           |
| hulu      | Hulu              |
| netflix   | Netflix           |
| now       | NOW               |
| paramount | Paramount+        |
| peacock   | Peacock           |



Below are the available variables which can be used to customize the file. Note that any use of `key` within the variable should be replaced with the `key` from the above table (i.e. `use_all4` instead of `use_key`, `order_disney` instead of `order_key`)


| Variable                   | Usage                                                                          | Default Value      |                                                                             Values                                                                             |
|:---------------------------|:-------------------------------------------------------------------------------|--------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| use_key                | Turn the collection on/off                                                     | `true`             |                                                                       `true` or `false`                                                                        |
| order_key              | Determine collection order in its section                                      | Alphabetical Order |                                Any number (i.e. `01` for `order_disney` to put Disney+ first in the list of streaming services)                                |
| collection_order_key   | Determines collection order of the collection                                  |                    |                                                                                                                                                                |
| visible_library_key    | Set visible_library for the collection                                         | `false`            |                                                                       `true` or `false`                                                                        |
| visible_home_key       | Set visible_home for the collection                                            | `false`            |                                                                       `true` or `false`                                                                        |
| visible_shared_key     | Set visible_shared for the collection                                          | `false`            |                                                                       `true` or `false`                                                                        |
| sonarr_add_missing_key | Adds missing from the collection to sonarr                                     | `false`            |                                                                       `true` or `false`                                                                        |
| sonarr_folder_key      | Sonarr Folder to add to                                                        |                    |                                                                 Folder to add missing items to                                                                 |
| sonarr_tag_key         | Sonarr Tag for added missing                                                   |                    |                                                                 Tag(s) to add to missing items                                                                 |
| item_sonarr_tag_key    | Sonarr Tag for existing items                                                  | `false`            |                                                                Tag(s) to add to existing items                                                                 |
| radarr_add_missing_key | Adds missing from the collection to radarr                                     |                    |                                                                       `true` or `false`                                                                        |
| radarr_folder_key      | Radarr Folder to add to                                                        |                    |                                                                 Folder to add missing items to                                                                 |
| radarr_tag_key         | Radarr Tag for added missing                                                   |                    |                                                                 Tag(s) to add to missing items                                                                 |
| item_radarr_tag_key    | Radarr Tag for existing items                                                  |                    |                                                                Tag(s) to add to existing items                                                                 |
| sort_by                    | Controls the sort method for the collections                                   | `release.desc`     |                                                  Any sort method in the [Sorts Options Table](#sort-options)                                                   |
| collection_section         | Controls the sort order of these collections against other default collections | `10`               |                                                                           Any number                                                                           |
| collection_mode            | Controls the collection mode of these collections                              | `default`          | `default` - Library default<br/>`hide` - Hide Collection<br/>`hide_items`- Hide Items in this Collection<br/>`show_items` - Show this Collection and its Items |
| use_separator              | Controls whether a separator is created                                        | `true`             |                                                                       `true` or `false`                                                                        |
| sep_style                  | Sets the theme of the separator                                                | `orig`             |                                                    `orig`, `blue`, `gray`, `green`, `purple`, `red`, `stb`                                                     |

The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: streaming
        template_variables:
          use_all4: false
          order_britbox: 01
          visible_library_disney: true
          visible_home_disney: true
          visible_shared_disney: true
          sonarr_add_missing_hulu: true
          sonarr_folder_hulu: /mnt/local/Media/TV/
          sonarr_tag_hulu: Hulu Shows
          item_sonarr_tag_hulu: Hulu Shows
          radarr_add_missing_amazon: true
          sonarr_folder_amazon: /mnt/local/Media/TV/Prime Video Shows/
          sonarr_tag_amazon: Prime Video Shows
          item_sonarr_tag_amazon: Prime Video Shows
          sort_by: random
          collection_section: 1
          collection_mode: show_items
          use_separator: false
          sep_style: stb
```
Dynamic Collections attributes can also be edited to tweak the setup of the collections. The YAML file which creates the `streaming` collections can be found [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/defaults/defaults/both/streaming.yml)

An example of this is; to only run the Disney+ collection against the movie library, the following template variable can be used:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: streaming
        template_variables:
          use:
            disney: movie
```

Further information on editing Dynamic Collections using template variables can be found [here](https://metamanager.wiki/en/latest/home/guides/defaults.html#customizing-configs)
