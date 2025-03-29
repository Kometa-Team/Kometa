=== "Overlay Template Variables"

    <!--title-sub--><!--title-sub-->

    When something in this table is noted as expecting a number, typically that number is expressed in pixels, assuming an image 1000x1500 in size.

    If the number is an `offset`, the value is relative to the corresponding `alignment`. Percentages are also relative to the `alignment`.
    
    For example:
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: resolution
            template_variables:
              horizontal_align: left
              horizontal_offset: 247
              vertical_align: bottom
              vertical_offset: 40%
    ```
    That would place the resolution overlay 247 pixels in from the left edge of the poster, and 40% of the way up from the bottom.
    
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: resolution
            template_variables:
              back_width: 198
              back_height: 47
    ```
    That would set the resolution overlay background to 198 pixels wide by 47 pixels high.
    
    Color values should be wrapped in quotes in the YAML, as the `#` denotes a comment in YAML and if left unquoted will prevent the value from being seen by Kometa.
    
    File paths need to be valid in the context where Kometa is running; this is primarily an issue when running in docker, as Kometa inside the container cannot see host paths.
    
    <!--notes-sub--><!--notes-sub-->

    | Attribute                         | Description                                                                                                   | Allowed Values (default in **bold**)                                                                                                  |
    |:----------------------------------|:--------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
    | `back_align`                     | Controls the alignment for the text overlay inside the backdrop. If not specified, text is centered.          | `left`, `right`, `center`, `top`, `bottom`                                                                                            |
    | `back_color`                     | Controls the backdrop color for the text overlay.                                                             | Color hex: `#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`<br>`AA` = 00 [transparent] to FF [opaque]                                           |
    | `back_height`                    | Controls the backdrop height. If not specified, backdrop sizes to the text.                                   | Any number > 0 (pixels, assuming a 1000x1500 image)                                                                                   |
    | `back_line_color`               | Controls the line color of the backdrop.                                                                      | Color hex: `#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`<br>`AA` = 00 [transparent] to FF [opaque]                                           |
    | `back_line_width`               | Controls the backdrop line width.                                                                             | Any number > 0 (pixels, assuming a 1000x1500 image)                                                                                   |
    | `back_padding`                  | Controls the backdrop padding.                                                                                | Any number > 0 (pixels, assuming a 1000x1500 image)                                                                                   |
    | `back_radius`                   | Controls the backdrop radius.                                                                                 | Any number > 0 (pixels, assuming a 1000x1500 image)                                                                                   |
    | `back_width`                    | Controls the backdrop width. If not specified, backdrop sizes to the text.                                    | Any number > 0 (pixels, assuming a 1000x1500 image)                                                                                   |
    | `file_<<key>>`<sup>**1**</sup>  | Sets the image for this key's overlay to a local file.                                                        | Filepath to overlay image                                                                                                              |
    | `file`                          | Sets all overlay images to a local file.                                                                      | Filepath to overlay image                                                                                                              |
    | `git_<<key>>`<sup>**1**</sup>   | Sets the image for this key's overlay to a Git repo file.                                                     | Git path to overlay image                                                                                                              |
    | `git`                           | Sets all overlay images from a Git repo.                                                                      | Git path to overlay image                                                                                                              |
    | `horizontal_align`             | Controls horizontal alignment of the overlay.                                                                 | `left`, `center`, `right`                                                                                                              |
    | `horizontal_offset`            | Controls horizontal offset. Can use percent.                                                                  | Number ≥ 0 or `0%`–`100%` (pixels assuming 1000x1500 image)                                                                            |
    | `repo_<<key>>`<sup>**1**</sup> | Sets the image for this key's overlay from a custom repo.                                                     | Repo path to overlay image                                                                                                             |
    | `repo`                          | Sets all overlay images from a custom repo.                                                                   | Repo path to overlay image                                                                                                             |
    | `url_<<key>>`<sup>**1**</sup>  | Sets the image for this key's overlay via URL.                                                                | URL to overlay image                                                                                                                   |
    | `url`                           | Sets all overlay images via URL.                                                                              | URL to overlay image                                                                                                                   |
    | `use_<<key>>`<sup>**1**</sup>  | Turns off an individual overlay in the Defaults file.                                                         | `false` to turn off the overlay                                                                                                        |
    | `vertical_align`               | Controls vertical alignment of the overlay.                                                                   | `top`, `center`, `bottom`                                                                                                              |
    | `vertical_offset`              | Controls vertical offset. Can use percent.                                                                    | Number ≥ 0 or `0%`–`100%` (pixels assuming 1000x1500 image)                                                                            |

    <sup>**1**</sup> Each default overlay has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.
    <!--text-variables-->

=== "Overlay Text Template Variables"

    <!--title-sub--><!--title-sub-->

    When something in this table is noted as expecting a number, typically that number is expressed in pixels, assuming an image 1000x1500 in size.
    
    Color values should be wrapped in quotes in the YAML, as the `#` denotes a comment in YAML and if left unquoted will prevent the value from being seen by Kometa.
    
    File paths need to be valid in the context where Kometa is running; this is primarily an issue when running in docker, as Kometa inside the container cannot see host paths.
    
    | Attribute                         | Description                                                                                                   | Allowed Values (default in **bold**)                                                                                                  |
    |:----------------------------------|:--------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
    | `font_<<key>>`<sup>**1**</sup>   | Choose the font for this key’s overlay.                                                                      | Path to font file<br>**`fonts/Inter-Medium.ttf`**                                                                                     |
    | `font_color_<<key>>`<sup>**1**</sup> | Choose the font color for this key’s overlay.                                                             | Color hex: `#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`<br>**`#FFFFFF`**                                                                   |
    | `font_color`                     | Choose the font color for the overlay.                                                                       | Color hex: `#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`<br>**`#FFFFFF`**                                                                   |
    | `font_size_<<key>>`<sup>**1**</sup> | Choose the font size for this key’s overlay.                                                             | Any number > 0 (pixels assuming a 1000x1500 image)<br>**`55`**                                                                        |
    | `font_size`                      | Choose the font size for the overlay.                                                                        | Any number > 0 (pixels assuming a 1000x1500 image)<br>**`55`**                                                                        |
    | `font_style_<<key>>`<sup>**1**</sup> | Font style for this key’s variable fonts.                                                               | Variable font style                                                                                                                    |
    | `font_style`                     | Font style for variable fonts.                                                                               | Variable font style                                                                                                                    |
    | `font`                           | Choose the font for the overlay.                                                                             | Path to font file<br>**`fonts/Inter-Medium.ttf`**                                                                                     |
    | `stroke_color_<<key>>`<sup>**1**</sup> | Font stroke color for this key’s overlay.                                                            | Color hex: `#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`                                                                                     |
    | `stroke_color`                   | Font stroke color for the overlay.                                                                           | Color hex: `#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`                                                                                     |
    | `stroke_width_<<key>>`<sup>**1**</sup> | Font stroke width for this key’s overlay.                                                           | Any number > 0 (pixels assuming a 1000x1500 image)                                                                                     |
    | `stroke_width`                   | Font stroke width for the overlay.                                                                           | Any number > 0 (pixels assuming a 1000x1500 image)                                                                                     |

    <sup>**1**</sup> Each default overlay has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

