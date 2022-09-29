# Genre Default Metadata File

The `- pmm: genre` Metadata File is used to dynamically create collections based on the genres available in your library.

This file also merges similarly named genres (such as "Sci-Fi", "SciFi" and "Sci-Fi & Fantasy") into one ("Science Fiction")

Example Collections Created:

![](images/genre.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: genre
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
      - pmm: genre
        template_variables:
          sort_by: title.asc
          collection_section: 5
          collection_mode: show_items
          use_separator: false
          sep_style: red
```

# UK Content Rating Default Metadata File

The `- pmm: content_rating_uk` Metadata File is used to dynamically create collections based on the content ratings available in your library.

If you do not use the UK-based rating system within Plex, this file will attempt to match the standard ratings (such as PG-13) to the respective UK rating system (such as 12)

Example Collections Created:

![](images/content_rating_uk.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: content_rating_uk
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

Below are the available variables which can be used to customize the file.


| Variable           | Usage                                                                                                | Default Value  |                                                                             Values                                                                             |
|:-------------------|:-----------------------------------------------------------------------------------------------------|----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| sort_by            | Controls the sort method for the collections                                                         | `release.desc` |                                                  Any sort method in the [Sorts Options Table](#sort-options)                                                   |
| collection_section | Controls the sort order of these collections against other default collections                       | `10`           |                                                                           Any number                                                                           |
| collection_mode    | Controls the collection mode of these collections                                                    | `default`      | `default` - Library default<br/>`hide` - Hide Collection<br/>`hide_items`- Hide Items in this Collection<br/>`show_items` - Show this Collection and its Items |
| use_other          | Controls whether an "Other" collection is created for any items not included in the initial criteria | `true`         |                                                                       `true` or `false`                                                                        |
| use_separator      | Controls whether a separator is created                                                              | `true`         |                                                                       `true` or `false`                                                                        |
| sep_style          | Sets the theme of the separator                                                                      | `orig`         |                                                    `orig`, `blue`, `gray`, `green`, `purple`, `red`, `stb`                                                     |
| item_radarr_tag    | Radarr Tag for existing items                                                                        |                |                                                         list of tag(s) to be applied to existing items                                                         |
| item_sonarr_tag    | Sonarr Tag for existing items                                                                        |                |                                                         list of tag(s) to be applied to existing items                                                         |

The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: content_rating_uk
        template_variables:
          sort_by: title.asc
          collection_section: 21
          collection_mode: show_items
          use_other: false
          use_separator: false
          sep_style: blue
```

Dynamic Collections attributes can also be edited to tweak the setup of the collections. The YAML file which creates the `genre` collections can be found [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/defaults/defaults/both/genre.yml)

An example of this is; to map the "Children" genre to "Family", the following template variable can be used:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: genre
        template_variables:
          addons:
            Family:
              - Children
```

Further information on editing Dynamic Collections using template variables can be found [here](https://metamanager.wiki/en/latest/home/guides/defaults.html#customizing-configs)
