# Basic Charts Collections

The `basic` Default Metadata File is used to create collections based on recently released media in your library.

**This file works with Movie and TV Libraries.**

![](../images/basic.png)

## Collections Section 01

| Collection       |    Key     | Description                                                    |
|:-----------------|:----------:|:---------------------------------------------------------------|
| `Newly Released` | `released` | Collection of Movies or TV Shows released in the last 90 days. |
| `New Episodes`   | `episodes` | Collection of Episodes released in the last 7 days.            |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: basic
  TV Shows:
    metadata_path:
      - pmm: basic
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable              | Description & Values                                                                                                                                                                                                                            |
|:----------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`               | **Description:** Changes the Smart Filter Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                    |
| `limit_<<key>>`       | **Description:** Changes the Smart Filter Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                 |
| `sort_by`             | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                            |
| `sort_by_<<key>>`     | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                      |
| `in_the_last_<<key>>` | **Description:** Changes how far back the Smart Filter looks.<table class="clearTable"><tr><td>**Default:**</td></tr><tr><td>`released`</td><td>`90`</td></tr><tr><td>`episodes`</td><td>`7`</td></tr></table>**Values:** Number Greater then 0 |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: basic
        template_variables:
          use_released: false
          in_the_last_episodes: 14
          visible_library_released: true
          visible_home_released: true
          visible_shared_released: true
```
