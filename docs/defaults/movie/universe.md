# Universe Default Metadata File

The `- pmm: universe` Metadata File is used to  create collections based on popular Movie universes (such as the Marvel Cinematic Universe or Wizarding World)

This Default file requires [Trakt Authentication](https://metamanager.wiki/en/latest/config/trakt.html)

Example Collections Created:

![](../images/universe.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: universe
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
      - pmm: universe
        template_variables:
          collection_order: release
          radarr_add_missing: true
          radarr_folder: /mnt/local/Media/Movies
          radarr_tag: <<collection_name>>
          item_radarr_tag: <<collection_name>>
          use_separator: false
          sep_style: gray
```

