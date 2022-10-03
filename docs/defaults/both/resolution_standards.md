# Resolution Standards Default Metadata File

The `- pmm: resolution_standards` Metadata File is used to dynamically create collections based on the resolutions available in your library.

This file takes the base resolutions ("4K" and "720p") and turns them into the commonly-known standards name ("Ultra HD" and "HD Ready")

To avoid duplication, this file should not be used in combination with `- pmm: resolution`

Example Collections Created:

![](../images/resolution_standards.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: resolution_standards
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

Below are the available variables which can be used to customize the file.


| Variable           | Usage                                                                          | Default Value  |                                                                             Values                                                                             |
|:-------------------|:-------------------------------------------------------------------------------|----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| sort_by            | Controls the sort method for the collections                                   | `release.desc` |                                                  Any sort method in the [Sorts Options Table](#sort-options)                                                   |
| collection_section | Controls the sort order of these collections against other default collections | `10`           |                                                                           Any number                                                                           |
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
      - pmm: resolution_standards
        template_variables:
          sort_by: title.asc
          collection_section: 16
          collection_mode: show_items
          use_separator: false
          sep_style: stb
```
Dynamic Collections attributes can also be edited to tweak the setup of the collections. The YAML file which creates the `resolution_standards` collections can be found [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/defaults/defaults/both/resolution_standards.yml)

An example of this is; to map the collection title of the "4k" resolution to "4K Ultra HD", the following template variable can be used:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: resolution_standards
        template_variables:
          title_override:
            4k: 4K Ultra HD
```

Further information on editing Dynamic Collections using template variables can be found [here](https://metamanager.wiki/en/latest/home/guides/defaults.html#customizing-configs)
