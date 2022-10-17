# Writer Collections

The `writer` Default Metadata File is used to dynamically create collections based on the most popular writers in your library.

**This file only works with Movie Libraries.**

![](../images/writer1.png)

## Collections Section 20

| Collection                                       |                       Key                        | Description                                                                 |
|:-------------------------------------------------|:------------------------------------------------:|:----------------------------------------------------------------------------|
| `Writers Collections`                            |                   `separator`                    | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<writer_name>>`<br>**Example:** `Frank Welker` | `<<writer_name>>`<br>**Example:** `Frank Welker` | Collection of Movies by the Writer.                                         |

#### Rainier Style

Below is a screenshot of the alternative Rainier (`rainier`) style which can be set via the `style` template variable.

![](../images/writer2.png)

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: writer
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable          | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|:------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_separator`   | **Description:** Turn the [Separator Collection](../separators) off.<br>**Values:** `false` to turn of the collection                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `sep_style`       | **Description:** Choose the [Separator Style](../separators.md#separator-styles).<br>**Default:** `orig`<br>**Values:** `orig`, `red`, `blue`, `green`, `gray`, `purple`, or `stb`                                                                                                                                                                                                                                                                                                                                                                 |         
| `style `          | **Description:** Controls the visual theme of the collections created<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>bw</code></td><td>Black & White Theme</td></tr><tr><td><code>rainier</code></td><td>Rainier Theme</td></tr></table>                                                                                                                                                                                                                                                                                          |
| `limit`           | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `limit_<<key>>`   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                                                                                                                                                                                                                                                                                                         |
| `sort_by`         | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                                                                                                                                                                                                                                                                                               |
| `sort_by_<<key>>` | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                                                                                                                                                                                                                                                                                                         |
| `data`            | **Description:** Replaces the `data` dynamic collection value.<table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>depth</code></td><td>Controls the depth within the casting credits to search for common actors<hr><strong>Default:</strong> 5<hr><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>limit</code></td><td>Controls the maximum number of collections to create<hr><strong>Default:</strong> 25<hr><strong>Values:</strong> Number greater than 0</td></tr></table> |
| `exclude`         | **Description:** Exclude these Writers from creating a Dynamic Collection.<br>**Values:** List of Writer Names                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `writer_name`     | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> (Writer)`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                                                 |
| `writer_summary`  | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s written by <<key_name>>.`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                                                                                                                                                                                                                                  |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: writer
        template_variables:
          style: rainier
          use_separator: false
          sep_style: purple
          data:
            depth: 10
            limit: 20
          sort_by: title.asc
```