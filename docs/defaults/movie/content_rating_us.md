# US Content Rating Default Metadata File

The `content_rating_us` Metadata File is used to dynamically create collections based on the content ratings available in your library.

If you do not use the US-based rating system within Plex, this file will attempt to match the international ratings (such as "gb/12A") to the respective US rating system (such as "PG-13")

Example Collections Created:

![](../images/moviecontent_rating_us.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: content_rating_us
```

ohhh   
## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

All [Shared Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable         | Description & Values                                                                                                                                                                          |
|:-----------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sort_by`        | **Description:** Controls the sort method for the collections<br>**Values:** Any sort method in the [Sorts Options Table](#sort-options)                                                      |
| `include`        | **Description:** Overrides the default include list<br>**Values:** Any Content Rating found in your library                                                                                   |
| `exclude`        | **Description:** Overrides the default exclude list<br>**Values:** Any Content Rating found in your library                                                                                   |
| `addons`         | **Description:** Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Any Content Rating found in your library   |
| `append_include` | **Description:** Appends to the existing include list<br>**Values:** Any Content Rating found in your library                                                                                 |
| `append_exclude` | **Description:** Appends to the existing exclude list<br>**Values:** Any Content Rating found in your library                                                                                 |
| `append_addons`  | **Description:** Appends to the existing addons list<br>**Values:** Any Content Rating found in your library                                                                                  |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: content_rating_us
        template_variables:
          addons:
            R:
              - "de/18"
          sort_by: title.asc
          collection_section: 25
          collection_mode: show_items
          use_other: false
          use_separator: false
          sep_style: blue
```

