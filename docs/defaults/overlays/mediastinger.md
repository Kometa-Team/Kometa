# MediaStinger Overlay

The `mediastinger` Default Overlay File is used to create an overlay based on if there's an after/during credit scene on each movie within your library.

![](images/mediastinger.png)

## Requirements & Recommendations

Supported Overlay Level: Movie

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_files:
      - pmm: mediastinger
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Overlay Template Variables" tab for additional variables.

        | Variable            | Default / Values   |
        |:--------------------|:-------------------|
        | `horizontal_offset` | `200`              |
        | `horizontal_align`  | `right`            |
        | `vertical_offset`   | `15`               |
        | `vertical_align`    | `top`              |
        | `back_color`        | `#00000099`        |
        | `back_radius`       | `30`               |
        | `back_width`        | `105`              |
        | `back_height`       | `105`              |

    === "Overlay Template Variables"

        {%
           include-markdown "../overlay_variables.md"
        %}

    ### Example Template Variable Amendments

    The below is an example config.yml extract with some Template Variables added in to change how the file works.


    ```yaml
    libraries:
      Movies:
        overlay_files:
          - pmm: mediastinger
            template_variables:
              font_color: "#FFFFFF99"
    ```
