# Content Rating US Show Overlay

The `content_rating_us_show` Default Overlay File is used to create an overlay based on the MPAA Age Rating on each item 
within your library.

![](images/content_rating_us_show.png)

## Requirements & Recommendations

Supported library types: Show

Requirements: Use the [Mass Content Rating Update Library 
Operation](../../config/operations.md#mass-content-rating-update) with either `mdb` or `omdb` to update Plex to the MPAA
Rating.

## Supported Content Rating US

| Rating | Key     |
|:-------|:--------|
| TV-G   | `tv-g`  |
| TV-Y   | `tv-y`  |
| TV-PG  | `tv-pg` |
| TV-14  | `tv-14` |
| TV-MA  | `tv-ma` |
| NR     | `nr`    |

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  TV Shows:
    overlay_files:
      - default: content_rating_us_show
      - default: content_rating_us_show
        template_variables:
          builder_level: season
      - default: content_rating_us_show
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

    ??? example "Default Template Variable Values (click to expand)"

        | Variable            | Default  |
        |:--------------------|:---------|
        | `color`             | ``       |
        | `horizontal_offset` | `15`     |
        | `horizontal_align`  | `left`   |
        | `vertical_offset`   | `270`    |
        | `vertical_align`    | `bottom` |
        
    === "File-Specific Template Variables"

        | Variable         | Description & Values                                                                                                                        |
        |:-----------------|:--------------------------------------------------------------------------------------------------------------------------------------------|
        | `color`          | **Description:** Color version of the content rating images<br>**Default:**`` Set to `false` if you want b&w version.                       |
        | `back_color`     | **Description:** Choose the back color in RGBA for the overlay lozenge.<br>**Default:**`#00000099`                                          |
        | `back_radius`    | **Description:** Choose the back radius for the overlay lozenge.<br>**Default:**`30`                                                        |
        | `back_width`     | **Description:** Choose the back width for the overlay lozenge.<br>**Default:**`305`                                                        |
        | `back_height`    | **Description:** Choose the back height for the overlay lozenge.<br>**Default:**`105`                                                       |
        | `addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                       |
        | `addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `left`<br>**Values:** `left`, `right`, `top`, `bottom` |

    === "Overlay Template Variables"

        {%
           include-markdown "../overlay_variables.md"
        %}
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.
    
    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - default: content_rating_us_show
            template_variables:
              color: false
          - default: content_rating_us_show
            template_variables:
              color: false
              builder_level: season
          - default: content_rating_us_show
            template_variables:
              color: false
              builder_level: episode
    ```
