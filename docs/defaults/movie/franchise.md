# Franchise Default Metadata File

The `franchise` Metadata File is used to  create collections based on popular Movie franchises, and can be used as a replacement to the TMDb Collections that Plex creates out-of-the-box.

Unlike most Default Metadata Files, Franchise works by placing collections inline with the main library items if your library allows it. For example, the "Iron Man" franchise collection will appear next to the "Iron Man" movies within your library.

Example Collections Created:

![](../images/moviefranchise.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: franchise
```


## Template Variables
Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

All [Shared Variables](../variables) are available

The below is an example config.yml extract with some template_variables changed  from their defaults.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: franchise
        template_variables:
          collection_order: alpha
          sort_title: "!10_<<collection_name>>"
          build_collection: false
          radarr_add_missing: true
          radarr_folder: /mnt/local/Media/Movies
          radarr_tag: <<collection_name>>
          item_radarr_tag: <<collection_name>>
```

