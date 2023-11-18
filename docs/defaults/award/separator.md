# Award Separator Collections

The `separator_award` Default Metadata File is used to create a seperator collection for Awards.

![](../images/awardseparator.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 130

| Collection          | Key         | Description                                                                 |
|:--------------------|:------------|:----------------------------------------------------------------------------|
| `Award Collections` | `separator` | [Separator Collection](../separators.md) to denote the Section of Collections. |

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

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

**[Shared Collection Variables](../collection_variables.md) are NOT available to this default file.**

This file contains only a [Separator](../separators.md) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available.

### Example Template Variable Amendments

The below is an example config.yml extract with some Template Variables added in to change how the file works.

???+ tip

    Anywhere you see this icon:
   
    > :fontawesome-solid-circle-plus:
   
    That's a tooltip, you can press them to get more information.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: separator_award
        template_variables:
          sep_style: purple #(1)!
```

1.  Use the purple [Separator Style](../separators.md#separator-styles)


