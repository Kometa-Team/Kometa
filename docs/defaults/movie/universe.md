# Universe Default Metadata File

The `- pmm: movie/universe` Metadata File is used to  create collections based on popular Movie universes (such as the Marvel Cinematic Universe or Wizarding World)

This Default file requires [Trakt Authentication](https://metamanager.wiki/en/latest/config/trakt.html)

Example Collections Created:

![](../images/universe.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: movie/universe
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

Below are the available variables which can be used to customize the file.


| Variable           | Usage                                        | Default Value |                         Values                          |
|:-------------------|:---------------------------------------------|---------------|:-------------------------------------------------------:|
| collection_order   | Sets the collection order of the collection  | `alpha`       |             `release`, `alpha` or `custom`              |
| radarr_add_missing | Adds missing from the collection to radarr   | `false`       |                    `true` or `false`                    |
| radarr_folder      | Radarr Folder to add to                      |               |             Folder to add missing items to              |
| radarr_tag         | Radarr Tag for added missing                 |               |      list of tag(s) to be applied to missing items      |
| item_radarr_tag    | Radarr Tag for existing items                |               |     list of tag(s) to be applied to existing items      |
| use_separator      | Controls whether a separator is created      | `true`        |                    `true` or `false`                    |
| sep_style          | Sets the theme of the separator              | `orig`        | `orig`, `blue`, `gray`, `green`, `purple`, `red`, `stb` |

The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: movie/universe
        template_variables:
          collection_order: release
          radarr_add_missing: true
          radarr_folder: /mnt/local/Media/TV
          radarr_tag: <<collection_name>>
          item_radarr_tag: <<collection_name>>
          use_separator: false
          sep_style: gray
```

