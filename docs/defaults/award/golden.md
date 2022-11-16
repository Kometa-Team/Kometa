# Golden Globes Awards Collections

The `golden` Default Metadata File is used to create collections based on the Golden Globe Awards.

**The `Golden Globe Best Motion Pictures` Collection only works with Movie Libraries but the year collections work with both Movie and Show libraries.**

![](../images/golden.png)

## Collections Section 16

| Collection                                                  | Key                               | Description                                                   |
|:------------------------------------------------------------|:----------------------------------|:--------------------------------------------------------------|
| `Golden Globe Best Motion Pictures`                         | `best`                            | Collection of Golden Globe Best Motion Picture Award Winners. |
| `Golden Globe <<year>>`<br>**Example:** `Golden Globe 2022` | `<<year>>`<br>**Example:** `2022` | Collection of Golden Globe Award Winners for the given year.  |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: golden
  TV Shows:
    metadata_path:
      - pmm: golden
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable                               | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|:---------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_year_collections`                 | **Description:** Turn the individual year collections off.<br>**Values:** `false` to turn of the collections                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults file.<br>**Default:** `custom`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `collection_order_<<key>>`<sup>1</sup> | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `data`                                 | **Description:** Replaces the `data` dynamic collection value.<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections<hr><strong>Default:</strong> current_year-5<hr><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections<hr><strong>Default:</strong> current_year<hr><strong>Values:</strong> Number greater than 1</td></tr><tr><td><code>increment</code></td><td>Controls the increment (i.e. every 5th year)<hr><strong>Default:</strong> 1<hr><strong>Values:</strong> Number greater than 0</td><td></td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>current_year</code></strong></li><li><strong>You can also use a value relative to the <code>current_year</code> by doing <code>current_year-5</code></strong></li></ul> |
| `exclude`                              | **Description:** Exclude these Years from creating a Dynamic Collection.<br>**Values:** List of Years                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: golden
        template_variables:
          collection_mode: show_items
          collection_order: alpha
          radarr_add_missing: true
          data:
            starting: current_year-10
            ending: current_year
```


