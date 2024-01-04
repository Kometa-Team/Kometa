# Network Overlay

The `network` Default Overlay File is used to create an overlay based on the show network on each item within your library.

![](images/Network_color.png)

## Requirements & Recommendations

Supported library types: Show

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  TV Shows:
    overlay_files:
      - pmm: network
      - pmm: network
        template_variables:
          builder_level: season
      - pmm: network
        template_variables:
          builder_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Overlay Template Variables" tab for additional variables.

        | Variable            | Default / Values                                                                                       |
        |:--------------------|:-------------------------------------------------------------------------------------------------------|
        | `horizontal_offset` | `15`                                                                                                   |
        | `horizontal_align`  | `left`                                                                                                 |
        | `vertical_offset`   | `510`                                                                                                  |
        | `vertical_align`    | `bottom`                                                                                               |
        | `back_color`        | `#00000099`                                                                                            |
        | `back_radius`       | `30`                                                                                                   |
        | `back_width`        | `305`                                                                                                  |
        | `back_height`       | `105`                                                                                                  |
        | `style`             | **Description:** Choose between the default color version or the **white** one.<br>**Values:** `white` |

        Preview of the white style

        ![](images/Network_white.png)

    === "Overlay Template Variables"

        {%
           include-markdown "../overlay_variables.md"
        %}

    ### Example Template Variable Amendments

    The below is an example config.yml extract with some Template Variables added in to change how the file works.


    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - pmm: network
            template_variables:
              style: white
              vertical_offset: 390
          - pmm: network
            template_variables:
              vertical_offset: 390
              builder_level: season
          - pmm: network
            template_variables:
              vertical_offset: 390
              builder_level: episode
    ```
