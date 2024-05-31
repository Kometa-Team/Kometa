# Runtimes Overlay

The `runtimes` Default Overlay File is used to create an overlay of the movie runtime, episode runtime, or average 
episode runtime for all items in your library.

![](images/runtimes.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show, Season, Episode

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_files:
      - default: runtimes
  TV Shows:
    overlay_files:
      - default: runtimes
      - default: runtimes
        template_variables:
          builder_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this Kometa Defaults file.

    * **Overlay Template Variables** are additional variables shared across the Kometa Overlay Defaults.

    * **Overlay Text Template Variables** are additional variables shared across the Kometa Text Overlay Defaults.

    ??? example "Default Template Variable Values (click to expand)"

        | Variable            | Default     |
        |:--------------------|:------------|
        | `horizontal_offset` | `15`        |
        | `horizontal_align`  | `right`     |
        | `vertical_offset`   | `30`        |
        | `vertical_align`    | `bottom`    |
        | `back_color`        | `#00000099` |
        | `back_radius`       | `30`        |
        | `back_width`        | `600`       |
        | `back_height`       | `105`       |
        
    === "File-Specific Template Variables"

        | Variable | Description & Values                                                                                                                     |
        |:---------|:-----------------------------------------------------------------------------------------------------------------------------------------|
        | `text`   | **Description:** Choose the text that appears prior to the runtime on the Overlay.<br>**Default:** `Runtime: `<br>**Values:** Any String |
        | `format` | **Description:** Choose the format of the the displayed runtime.<br>**Default:** `<<runtimeH>>h <<runtimeM>>m`<br>**Values:** Any String |

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
          - default: runtimes
            template_variables:
              builder_level: episode
            font: fonts/Inter-Bold.ttf
    ```
