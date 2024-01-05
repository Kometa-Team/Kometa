# Direct Play Overlay

The `direct_play` Default Overlay File is used to create an overlay to indicate items that cannot be transcoded and instead only support Direct Play (i.e. if you use Tautulli to kill 4K transcoding)

![](images/direct_play.png)

## Requirements & Recommendations

Supported library types: Movie & Show

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_files:
      - pmm: direct_play
  TV Shows:
    overlay_files:
      - pmm: direct_play
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    ??? example "Default Templatye Variable Values (click to expand)"

        | Variable            | Default     |
        |:--------------------|:------------|
        | `horizontal_offset` | `0`         |
        | `horizontal_align`  | `center`    |
        | `vertical_offset`   | `150`       |
        | `vertical_align`    | `bottom`    |
        | `back_color`        | `#00000099` |
        | `back_radius`       | `30`        |
        | `back_width`        | `305`       |
        | `back_height`       | `170`       |
        
    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Overlay Template Variables" tab for additional variables.

        | Variable        | Description & Values                                                            |
        |:----------------|:--------------------------------------------------------------------------------|
        | `builder_level` | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode` |

    === "Overlay Template Variables"

        {%
           include-markdown "../overlay_text_variables.md"
        %}

        {%
           include-markdown "../overlay_variables.md"
        %}

    ### Example Template Variable Amendments

    The below is an example config.yml extract with some Template Variables added in to change how the file works.


    ```yaml
    libraries:
      Movies:
        overlay_files:
          - pmm: direct_play
            template_variables:
              builder_level: episode
    ```
