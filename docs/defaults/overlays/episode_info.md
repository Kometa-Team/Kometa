# Episode Info Overlay

The `episode_info` Default Overlay File is used to create an overlay on the episode title card on the episode numbering 
within a given series in your library.

![](images/episode_info.png)

## Requirements & Recommendations

Supported library types: Show

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  TV Shows:
    overlay_files:
      - default: episode_info
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **Overlay Template Variables** are additional variables shared across the Kometa Overlay Defaults.

    * **Overlay Text Template Variables** are additional variables shared across the Kometa Text Overlay Defaults.

    ??? example "Default Template Variable Values (click to expand)"

        | Variable            | Default     |
        |:--------------------|:------------|
        | `horizontal_offset` | `15`        |
        | `horizontal_align`  | `left`      |
        | `vertical_offset`   | `270`       |
        | `vertical_align`    | `bottom`    |
        | `back_color`        | `#00000099` |
        | `back_radius`       | `30`        |
        | `back_width`        | `305`       |
        | `back_height`       | `105`       |

    === "Overlay Template Variables"

        {%
           include-markdown "../overlay_variables.md"
        %}

    === "Overlay Text Template Variables"

        {%
           include-markdown "../overlay_text_variables.md"
        %}
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.
    
    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - default: episode_info
            template_variables:
              font_color: "#FFFFFF99"
    ```
