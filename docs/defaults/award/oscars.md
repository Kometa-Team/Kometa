# Academy Awards (Oscars) Default Metadata File

The `- pmm: oscars` Metadata File is used to create collections based on the Academy Awards (Oscars).

This file only works with Movie Libraries.

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: oscars
```

## Collections

| Collection                     |       Key       | Description                                            |
|:-------------------------------|:---------------:|:-------------------------------------------------------|
| `Oscars Best Picture Winners`  | `best_picture`  | Collection of Oscars Best Picture Award Winners.       |
| `Oscars Best Director Winners` | `best_director` | Collection of Oscars Best Director Award Winners.      |
| `Oscars Winners <<year>>`      |   `<<year>>`    | Collection of Oscars Award Winners for the given year. |

### Examples

![](../images/oscars.png)

## Template Variables

Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is just ignored.

All [Shared Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|:-----------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_year_collections` | **Description:** Turn the individual year collections off<br>**Values:** `false` to turn of the collections                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `collection_order`     | **Description:** Changes the Collection Order<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `data`                 | **Description:** Changes the following values of the collection builder<br><table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections</br><strong>Values:</strong> Number greater than 0</td><td><strong>Default:</strong> current_year-5</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections</br><strong>Values:</strong> Number greater than 1</td><td><strong>Default:</strong> current_year</td></tr><tr><td><code>increment</code></td><td>Controls the incriment (i.e. every 5th year)</br><strong>Values:</strong> Number greater than 0</td><td><strong>Default:</strong> 1</td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>current_year</code></strong></li><li><strong>You can also use a value relative to the <code>current_year</code> by doing <code>current_year-5</code></strong></li></ul> |

The below is an example config.yml extract with some template_variables changed  from their defaults.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: oscars
        template_variables:
          collection_section: 8
          collection_mode: show_items
          collection_order: alpha
          radarr_add_missing: true
```


