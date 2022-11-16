# Award Separator Collections

The `separator_award` Default Metadata File is used to create a seperator collection for Awards.

**This file works with Movie and Show Libraries.**

![](../images/awardseparator.png)

## Collections Section 16

| Collection          | Key         | Description                                                                 |
|:--------------------|:------------|:----------------------------------------------------------------------------|
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

**[Shared Collection Variables](../collection_variables) are NOT available to this default file.**

This file contains only a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available.

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
