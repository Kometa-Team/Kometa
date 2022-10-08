# Decade Default Metadata File

The `decade` Metadata File is used to dynamically create collections based on the decades available in your library, sorted by critic rating to create a "best of <decade>"

Example Collections Created:

![](../images/decade.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: decade
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

All [Shared Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable         | Description & Values                                                                                                                                                |
|:-----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sort_by`        | **Description:** Controls the sort method for the collections<br>**Values:** Any sort method in the [Sorts Options Table](#sort-options)                            |

The below is an example config.yml extract with some Template Variables added in to change how the file works.


```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: decade
        template_variables:
          sort_by: title.asc
          collection_section: 18
          collection_mode: show_items
          use_other: false
          use_separator: false
          sep_style: purple
```