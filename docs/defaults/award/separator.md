# Award Separator Collections

The `separator_award` Default Metadata File is used to create a seperator collection for Awards.

**This file works with Movie and TV Libraries.**

![](../images/separators2.jpg)

## Collections Section 16

| Collection          |     Key     | Description                                                                 |
|:--------------------|:-----------:|:----------------------------------------------------------------------------|
| `Award Collections` | `separator` | [Separator Collection](../separators) to denote the Section of Collections. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: separator_award
  TV Shows:
    metadata_path:
      - pmm: separator_award
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

**[Shared Collection Variables](../variables) are NOT available to this default file.**

| Variable               | Description & Values                                                                                                                                                                                                                                                                                                                                                                  |
|:-----------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_separator`        | **Description:** Turn the [Separator Collection](../separators) off.<br>**Values:** `false` to turn of the collection                                                                                                                                                                                                                                                                 |
| `sep_style`            | **Description:** Choose the [Separator Style](../separators.md#separator-styles).<br>**Default:** `orig`<br>**Values:** `orig`, `red`, `blue`, `green`, `gray`, `purple`, or `stb`                                                                                                                                                                                                    |         
| `name_separator`       | **Description:** Changes the name of the specified key's collection.<br>**Values:** New Collection Name                                                                                                                                                                                                                                                                               |
| `summary_separator`    | **Description:** Changes the summary of the specified key's collection.<br>**Values:** New Collection Summary                                                                                                                                                                                                                                                                         |
| `collection_section`   | **Description:** Changes the sort order of the collection sections against other default collection sections.<br>**Values:** Any number                                                                                                                                                                                                                                               |
| `collection_mode`      | **Description:** Controls the collection mode of all collections in a Defaults file.<br>**Values:**<table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table> |
| `url_poster_separator` | **Description:** Changes the poster url of the specified key's collection.<br>**Values:** URL directly to the Image                                                                                                                                                                                                                                                                   |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: separator_award
        template_variables:
          use_separator: false
          sep_style: purple
```
