# Award Separator Collections

The `separator_award` Default Collection File is used to create a seperator collection for Awards.

![](../images/awardseparator.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 130

| Collection          | Key         | Description                                                                    |
|:--------------------|:------------|:-------------------------------------------------------------------------------|
| `Award Collections` | `separator` | [Separator Collection](../separators.md) to denote the Section of Collections. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: separator_award
  TV Shows:
    collection_files:
      - default: separator_award
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **Shared Separator Variables** are additional variables available since this Default contains a 
    [Separator](../separators.md).

    === "Shared Separator Variables"

        {%
          include-markdown "../separator_variables.md"
        %}

???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    Click the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: separator_award
            template_variables:
              sep_style: purple #(1)!
    ```

    1.  Use the purple [Separator Style](../separators.md#separator-styles)
