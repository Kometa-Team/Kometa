# Streaming Default Metadata File

The `streaming` Metadata File is used to dynamically create collections based on the streaming Services that your media is available on.

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

All [Shared Variables](../variables) are available using the below keys.

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

The below is an example config.yml extract with some Template Variables added in to change how the file works.

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