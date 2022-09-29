# Studio Default Metadata File

The `- pmm: studio` Metadata File is used to dynamically create collections based on the studios available in your library.

This file also merges similarly named studios (such as "20th Century Fox" and "20th Century Animation") into one ("20th Century Studios")

Example Collections Created:

![](images/studio.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

Below are the available variables which can be used to customize the file.


| Variable           | Usage                                                                          | Default Value  |                                                                             Values                                                                             |
|:-------------------|:-------------------------------------------------------------------------------|----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| sort_by            | Controls the sort method for the collections                                   | `release.desc` |                                                  Any sort method in the [Sorts Options Table](#sort-options)                                                   |
| collection_section | Controls the sort order of these collections against other default collections | `07`           |                                                                           Any number                                                                           |
| collection_mode    | Controls the collection mode of these collections                              | `default`      | `default` - Library default<br/>`hide` - Hide Collection<br/>`hide_items`- Hide Items in this Collection<br/>`show_items` - Show this Collection and its Items |
| use_separator      | Controls whether a separator is created                                        | `true`         |                                                                       `true` or `false`                                                                        |
| sep_style          | Sets the theme of the separator                                                | `orig`         |                                                    `orig`, `blue`, `gray`, `green`, `purple`, `red`, `stb`                                                     |
| item_radarr_tag    | Radarr Tag for existing items                                                  |                |                                                         list of tag(s) to be applied to existing items                                                         |
| item_sonarr_tag    | Sonarr Tag for existing items                                                  |                |                                                         list of tag(s) to be applied to existing items                                                         |

The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio
        template_variables:
          sort_by: title.asc
          collection_section: 4
          collection_mode: show_items
          use_separator: false
          sep_style: gray
```

Dynamic Collections attributes can also be edited to tweak the setup of the collections. The YAML file which creates the `studio` collections can be found [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/defaults/defaults/both/studio.yml)

An example of this is; to include the "ABC Pictures" studio and map the "ABC News" studio to it, the following template variables can be used:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio
        template_variables:
          include:
            - ABC Pictures
          addons:
            ABC Picture:
              - ABC News
```

Further information on editing Dynamic Collections using template variables can be found [here](https://metamanager.wiki/en/latest/home/guides/defaults.html#customizing-configs)
