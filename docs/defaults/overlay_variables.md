When something in this table is noted as expecting a number, that number is expressed in pixels, assuming an image 1000x1500 in size.  If the number is an `offset`, the value is relative to the corresponding `alignment`.  Percentages are also relative to the `alignment`.

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

| Variable                   | Description & Values                                                                                                                                                                                                                  |
|:---------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_<<key>>`<sup>1</sup>  | **Description:** Turns off individual Overlays in a Defaults file.<br>**Values:** `false` to turn off the overlay                                                                                                                     |
| `file`                     | **Description:** Controls the images associated with all the Overlays to a local file.<br>**Values:** Filepath to Overlay Image                                                                                                       |
| `file_<<key>>`<sup>1</sup> | **Description:** Controls the image associated with this key's Overlay to a local file.<br>**Values:** Filepath to Overlay Image                                                                                                      |
| `url`                      | **Description:** Controls the images associated with all the Overlays to a url.<br>**Values:** URL to Overlay Image                                                                                                                   |
| `url_<<key>>`<sup>1</sup>  | **Description:** Controls the image associated with this key's Overlay to a url.<br>**Values:** URL to Overlay Image                                                                                                                  |
| `git`                      | **Description:** Controls the images associated with all the Overlays to the git repo.<br>**Values:** Git Path to Overlay Image                                                                                                       |
| `git_<<key>>`<sup>1</sup>  | **Description:** Controls the image associated with this key's Overlay to the git repo.<br>**Values:** Git Path to Overlay Image                                                                                                      |
| `repo`                     | **Description:** Controls the images associated with all the Overlays to a custom repo.<br>**Values:** Repo Path to Overlay Image                                                                                                     |
| `repo_<<key>>`<sup>1</sup> | **Description:** Controls the image associated with this key's Overlay to a custom repo.<br>**Values:** Repo Path to Overlay Image                                                                                                    |
| `horizontal_offset`        | **Description:** Controls the Horizontal Offset of this overlay. Can be a %.<br>**Values:** Number 0 or greater or 0%-100% [pixels assuming a 1000x1500 image]                                                                        |
| `horizontal_align`         | **Description:** Controls the Horizontal Alignment of the overlay.<br>**Values:** `left`, `center`, or `right`                                                                                                                        |
| `vertical_offset`          | **Description:** Controls the Vertical Offset of this overlay. Can be a %.<br>**Values:** Number 0 or greater or 0%-100% [pixels assuming a 1000x1500 image]                                                                          |
| `vertical_align`           | **Description:** Controls the Vertical Alignment of the overlay.<br>**Values:** `top`, `center`, or `bottom`                                                                                                                          |
| `back_color`               | **Description:** Controls the Backdrop Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`<br>`AA` is transparency; 00 [transparent] to FF [opaque]                         |
| `back_width`               | **Description:** Controls the Backdrop Width for the Text Overlay. If `back_width` is not specified the Backdrop Sizes to the text<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]                       |
| `back_height`              | **Description:** Controls the Backdrop Height for the Text Overlay. If `back_height` is not specified the Backdrop Sizes to the text<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]                     |
| `back_align`               | **Description:** Controls the Alignment for the Text Overlay inside the backdrop. If `back_align` is not specified the Backdrop Centers the text.<br>**Values:** `left`, `right`, `center`, `top`, or `bottom`                        |
| `back_padding`             | **Description:** Controls the Backdrop Padding for the Text Overlay.<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]                                                                                     |
| `back_radius`              | **Description:** Controls the Backdrop Radius for the Text Overlay.<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]                                                                                      |
| `back_line_color`          | **Description:** Controls the Backdrop Line Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA``AA` is transparency; 00 [transparent] to FF [opaque]                        |
| `back_line_width`          | **Description:** Controls the Backdrop Line Width for the Text Overlay.<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]                                                                                  |

1. Each default overlay has a `key` that when calling to effect a specific collection you must replace `<<key>>` with 
when calling.