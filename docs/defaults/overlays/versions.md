# Versions Overlay

The `versions` Default Overlay File is used to create an overlay based on if there's multiple versions on each item within your library.

![](images/version.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show, Season, Episode

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_files:
      - pmm: versions
  TV Shows:
    overlay_files:
      - pmm: versions
      - pmm: versions
        template_variables:
          builder_level: season
      - pmm: versions
        template_variables:
          builder_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    ??? example "Default Templatye Variable Values (click to expand)"

        | Variable            | Default          |
        |:--------------------|:-----------------|
        | `horizontal_offset` | `15`/`235`       |
        | `horizontal_align`  | `right`/`center` |
        | `vertical_offset`   | `1050`/`15`      |
        | `vertical_align`    | `top`            |
        | `back_color`        | `#00000099`      |
        | `back_radius`       | `30`             |
        | `back_width`        | `105`            |
        | `back_height`       | `105`            |
        
    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Overlay Template Variables" tab for additional variables.

        | Variable        | Description & Values                                                            |
        |:----------------|:--------------------------------------------------------------------------------|
        | `builder_level` | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode` |

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
          - pmm: versions
            template_variables:
              back_color: "#FFFFFF99"
    ```
