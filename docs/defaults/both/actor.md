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


| Variable      | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|:--------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `style `      | **Description:** Controls the visual theme of the collections created<br>**Values:**`bw` - Black and white theme or</br>`rainier` - Rainier theme                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `sort_by`     | **Description:** Controls the sort method for the collections<br>**Values:** Any sort method in the [Sorts Options Table](#sort-options)                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `data`        | **Description:** Changes the following values of the collection builder<br>**Values:**<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>depth</code></td><td>Controls the depth within the casting credits to search for common actors</br><strong>Values:</strong> Number greater than 0</td><td><strong>Default:</strong> 5</td></tr><tr><td><code>limit</code></td><td>Controls the maximum number of collections to create</br><strong>Values:</strong> Number greater than 0</td><td><strong>Default:</strong> 25</td></tr></table> |


The below shows an example config.yml with all the template_variables set away from their defaults:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: actor
        template_variables:
          data:
            depth: 10
            limit: 20
          style: rainier
          sort_by: title.asc
          collection_section: 12
          collection_mode: show_items
          use_separator: false
          sep_style: purple
```
