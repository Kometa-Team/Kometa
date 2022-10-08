# Subtitle Language Default Metadata File

The `subtitle_language` Metadata File is used to dynamically create collections based on the subtitle languages available in your library.

Example Collections Created:

![](../images/subtitle_language.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: subtitle_language
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

All [Shared Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable         | Description & Values                                                                                                                                                |
|:-----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sort_by`        | **Description:** Controls the sort method for the collections<br>**Values:** Any sort method in the [Sorts Options Table](#sort-options)                            |
| `include`        | **Description:** Overrides the default include list<br>**Values:** Any list of [two-digit ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)   |
| `exclude`        | **Description:** Overrides the default exclude list<br>**Values:** Any list of [two-digit ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)   |
| `append_include` | **Description:** Appends to the existing include list<br>**Values:** Any list of [two-digit ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) |
| `append_exclude` | **Description:** Appends to the existing exclude list<br>**Values:** Any list of [two-digit ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: subtitle_language
        template_variables:
          exclude:
            - fr  # Exclude French
          sort_by: title.asc
          collection_section: 20
          collection_mode: show_items
          use_other: false
          use_separator: false
          sep_style: purple
```