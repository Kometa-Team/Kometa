# Golden Globes Default Metadata File

The `- pmm: award/golden` Metadata File is used to  create collections based on the Golden Globe Awards.

Example Collections Created:

![](../images/golden.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: award/golden
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

Below are the available variables which can be used to customize the file.


| Variable             | Usage                                                                          | Default Value      |                                                                             Values                                                                             |
|:---------------------|:-------------------------------------------------------------------------------|--------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| use_year_collections | Turn the individual year collections on/off                                    | `true`             |                                                                       `true` or `false`                                                                        |0
| imdb_sort            | Sets the sort of the IMDb Search                                               | `moviemeter,desc ` |                                                                  Any IMDb Search Sort Option                                                                   |0
| collection_section   | Controls the sort order of these collections against other default collections | `16`               |                                                                           Any number                                                                           |
| collection_mode      | Controls the collection mode of these collections                              | `default`          | `default` - Library default<br/>`hide` - Hide Collection<br/>`hide_items`- Hide Items in this Collection<br/>`show_items` - Show this Collection and its Items |
| collection_order     | Sets the collection order of the collection                                    | `custom`           |                                                                 `alpha`, `release` or `custom`                                                                 |
| radarr_add_missing   | Adds missing from the collection to Radarr                                     | `false`            |                                                                       `true` or `false`                                                                        |
| radarr_folder        | Radarr Folder to add to                                                        |                    |                                                                 Folder to add missing items to                                                                 |
| radarr_tag           | Radarr Tag for added missing                                                   |                    |                                                         list of tag(s) to be applied to missing items                                                          |
| item_radarr_tag      | Radarr Tag for existing items                                                  |                    |                                                         list of tag(s) to be applied to existing items                                                         |
| sonarr_add_missing   | Adds missing from the collection to Sonarr                                     | `false`            |                                                                       `true` or `false`                                                                        |
| sonarr_folder        | Sonarr Folder to add to                                                        |                    |                                                                 Folder to add missing items to                                                                 |
| sonrr_tag            | Sonarr Tag for added missing                                                   |                    |                                                         list of tag(s) to be applied to missing items                                                          |
| item_sonarr_tag      | Sonarr Tag for existing items                                                  |                    |                                                         list of tag(s) to be applied to existing items                                                         |


The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: award/golden
        template_variables:
          collection_section: 9
          collection_mode: show_items
          collection_order: alpha
          imdb_sort: moviemeter,asc
          radarr_add_missing: true
          radarr_folder: /mnt/local/Media/Movies
          radarr_tag: <<collection_name>>
          item_radarr_tag: <<collection_name>>
          sonarr_add_missing: true
          sonarr_folder: /mnt/local/Media/TV
          sonarr_tag: <<collection_name>>
          item_sonarr_tag: <<collection_name>>
```

