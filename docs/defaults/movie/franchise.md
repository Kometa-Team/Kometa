# Franchise Default Metadata File

The `- pmm: movie/franchise` Metadata File is used to  create collections based on popular Movie franchises, and can be used as a replacement to the TMDb Collections that Plex creates out-of-the-box.

Unlike most Default Metadata Files, Franchise works by placing collections inline with the main library items if your library allows it. For example, the "Iron Man" franchise collection will appear next to the "Iron Man" movies within your library.

Example Collections Created:

![](../images/moviefranchise.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: movie/franchise
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

Below are the available variables which can be used to customize the file.


| Variable           | Usage                                         | Default Value |                     Values                     |
|:-------------------|:----------------------------------------------|---------------|:----------------------------------------------:|
| collection_order   | Sets the collection order of the collection   | `release`     |         `release`, `alpha` or `custom`         |
| sort_title         | Sets the sort title                           |               |               Desired sort title               |
| minimum_items      | Sets the minimum items of the collection      | `2`           |                   Any number                   |
| build_collection   | Sets weather to actually build the collection | `true`        |               `true` or `false`                |
| radarr_add_missing | Adds missing from the collection to radarr    | `false`       |               `true` or `false`                |
| radarr_folder      | Radarr Folder to add to                       |               |         Folder to add missing items to         |
| radarr_tag         | Radarr Tag for added missing                  |               | list of tag(s) to be applied to existing items |
| item_radarr_tag    | Radarr Tag for existing items                 |               | list of tag(s) to be applied to existing items |

The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: movie/franchise
        template_variables:
          collection_order: alpha
          sort_title: "!10_<<collection_name>>"
          build_collection: false
          radarr_add_missing: true
          radarr_folder: /mnt/local/Media/TV
          radarr_tag: <<collection_name>>
          item_radarr_tag: <<collection_name>>
```

