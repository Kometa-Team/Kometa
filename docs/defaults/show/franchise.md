# Franchise Default Metadata File

The `- pmm: show/franchise` Metadata File is used to  create collections based on popular TV franchises

Unlike most Default Metadata Files, Franchise works by placing collections inline with the main library items if your library allows it. For example, the "Pretty Little Liars" franchise collection will appear next to the "Pretty Little Liars" show in your library so that you have easy access to the other shows in the franchise.

Example Collections Created:

![](../images/showfranchise.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: show/franchise
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
      - pmm: show/franchise
        template_variables:
          collection_order: alpha
          sort_title: "!10_<<collection_name>>"
          build_collection: false
          sonarr_add_missing: true
          sonarr_folder: /mnt/local/Media/TV
          sonarr_tag: <<collection_name>>
          item_sonarr_tag: <<collection_name>>
```

