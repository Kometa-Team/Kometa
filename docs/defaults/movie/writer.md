# Writer Default Metadata File

The `- pmm: movie/writer` Metadata File is used to dynamically create collections based on the most popular writers in your library.

Example Collections Created:

![](../images/writer1.png)

The below YAML in your config.yml will create the writer collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: movie/writer
```

## Rainier Style
Below is a screenshot of the alternative `Rainier` style which can be set via template variables

![](../images/writer2.png)


## Template Variables
Template Variables can be used to manipulate the writer file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

Below are the available variables which can be used to customize the file.


| Variable           | Usage                                                                          | Default Value  |                                                                             Values                                                                             |
|:-------------------|:-------------------------------------------------------------------------------|----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| style              | Controls the visual theme of the collections created                           | `bw`           |                                                 `bw` - Black and white theme or<br/>`rainier` - Rainier theme                                                  |
| sort_by            | Controls the sort method for the collections                                   | `release.desc` |                                                  Any sort method in the [Sorts Options Table](#sort-options)                                                   |
| collection_section | Controls the sort order of these collections against other default collections | `17`           |                                                                           Any number                                                                           |
| collection_mode    | Controls the collection mode of these collections                              | `default`      | `default` - Library default<br/>`hide` - Hide Collection<br/>`hide_items`- Hide Items in this Collection<br/>`show_items` - Show this Collection and its Items |
| use_separator      | Controls whether a separator is created                                        | `true`         |                                                                       `true` or `false`                                                                        |
| sep_style          | Sets the theme of the separator                                                | `orig`         |                                                    `orig`, `blue`, `gray`, `green`, `purple`, `red`, `stb`                                                     |
| item_radarr_tag    | Radarr Tag for existing items                                                  |                |                                                         list of tag(s) to be applied to existing items                                                         |

The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: movie/writer
        template_variables:
          style: rainier
          sort_by: title.asc
          collection_section: 12
          collection_mode: show_items
          use_separator: false
          sep_style: purple
```

Dynamic Collections attributes can also be edited to tweak the setup of the collections. The YAML file which creates the `writer` collections can be found [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/defaults/defaults/movie/writer.yml)

An example of this is; To amend the maximum amount of collections that are created (default is 25), the following template variable can be used:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: movie/writer
        template_variables:
          data:
            limit: 25
```

Further information on editing Dynamic Collections using template variables can be found [here](https://metamanager.wiki/en/latest/home/guides/defaults.html#customizing-configs)

