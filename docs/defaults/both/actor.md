# Actor Default Metadata File

The `- pmm: actor` Metadata File is used to dynamically create collections based on the most popular actors/actresses in your library.

Example Collections Created:

![](../images/actor1.png)

The below YAML in your config.yml will create the collections:
```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: actor
```

## Rainier Style
Below is a screenshot of the alternative `Rainier` style which can be set via template variables

![](../images/actor2.png)


## Template Variables
Template Variables can be used to manipulate the actor file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

Below are the available variables which can be used to customize the actor file.


| Variable    | Description & Values                                                                                                                                                                                                                                                                                                                                                                                              |
|:------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `style `    | **Description:** Controls the visual theme of the collections created<br>**Values:** `bw` - Black and white theme or<br/>`rainier` - Rainier theme                                                                                                                                                                                                                                                                |
| `sort_by`   | **Description:** Controls the sort method for the collections<br>**Values:** Any sort method in the [Sorts Options Table](#sort-options)                                                                                                                                                                                                                                                                          |
| `data`      | **Description:** Changes the Collection Order<br>**Values:**<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>depth</code></td><td><strong>Values:</strong> Number greater than 0</td><td><strong>Default:</strong> 0</td></tr><tr><td><code>limit</code></td><td><strong>Values:</strong> Number greater than 1</td><td><strong>Default:</strong> 1</td></tr>  |

test



| Variable             | Usage                                                                          | Default Value  |                                                                             Values                                                                             |
|:---------------------|:-------------------------------------------------------------------------------|----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| style                |                            | `bw`           |                                                 `bw` - Black and white theme or<br/>`rainier` - Rainier theme                                                  |
| sort_by              | Controls the sort method for the collections                                   | `release.desc` |                                                                                                     |
| `data`               | **Description:** Changes the Collection Order<br>**Values:**<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>starting</code></td><td><strong>Values:</strong> Number greater than 0</td><td><strong>Default:</strong> 0</td></tr><tr><td><code>ending</code></td><td><strong>Values:</strong> Number greater than 1</td><td><strong>Default:</strong> 1</td></tr><tr><td><code>increment</code></td><td><strong>Values:</strong> Number greater than 0</td><td><strong>Default:</strong> 1</td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>current_year</code></strong></li><li><strong>You can also use a value relative to the <code>current_year</code> by doing <code>current_year-5</code></strong></li></ul> |

The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: actor
        template_variables:
          style: rainier
          sort_by: title.asc
          collection_section: 12
          collection_mode: show_items
          use_separator: false
          sep_style: purple
```

Dynamic Collections attributes can also be edited to tweak the setup of the collections. The YAML file which creates the `actor` collections can be found [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/defaults/defaults/both/actor.yml)

An example of this is; To amend the maximum amount of collections that are created (default is 25), the following template variable can be used:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: actor
        template_variables:
          data:
            limit: 10
```

Further information on editing Dynamic Collections using template variables can be found [here](https://metamanager.wiki/en/latest/home/guides/defaults.html#customizing-configs)