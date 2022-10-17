# Shared Overlay Template Variables

There are some `templates_variables` that all the PMM Defaults expect `franchise` can use to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

Below are the available variables which can be used to customize the file.

| Variable                  | Description & Values                                                                                                                                                                                           |
|:--------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_<<key>>`<sup>1</sup><sup>1</sup> | **Description:** Turns off individual Overlays in a Defaults file.<br>**Values:** `false` to turn off the overlay                                                                                              |
| `file`                    | **Description:** Controls the image associated with the Overlay to a local file. Use `pmm: null` with this to no use the default image.<br>**Values:** Filepath to Overlay Image                               |
| `url`                     | **Description:** Controls the image associated with the Overlay to a url. Use `pmm: null` with this to no use the default image.<br>**Values:** URL to Overlay Image                                           |
| `git`                     | **Description:** Controls the image associated with the Overlay to the git repo. Use `pmm: null` with this to no use the default image.<br>**Values:** Git Path to Overlay Image                               |
| `repo`                    | **Description:** Controls the image associated with the Overlay to a custom repo. Use `pmm: null` with this to no use the default image.<br>**Values:** Repo Path to Overlay Image                             |
| `pmm`                     | **Description:** Controls the image associated with the Overlay to a pmm file.<br>**Values:** PMM Overlay Image                                                                                                |
| `horizontal_offset`       | **Description:** Controls the Horizontal Offset of this overlay. Can be a %.<br>**Values:** Number 0 or greater or 0%-100%                                                                                     |
| `horizontal_align`        | **Description:** Controls the Horizontal Alignment of the overlay.<br>**Values:** `left`, `center`, or `right`                                                                                                 |
| `vertical_offset`         | **Description:** Controls the Vertical Offset of this overlay. Can be a %.<br>**Values:** Number 0 or greater or 0%-100%                                                                                       |
| `vertical_align`          | **Description:** Controls the Vertical Alignment of the overlay.<br>**Values:** `top`, `center`, or `bottom`                                                                                                   |
| `back_color`              | **Description:** Controls the Backdrop Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`                                                           |
| `back_width`              | **Description:** Controls the Backdrop Width for the Text Overlay. If `back_width` is not specified the Backdrop Sizes to the text<br>**Values:** Any Number greater then 0                                    |
| `back_height`             | **Description:** Controls the Backdrop Height for the Text Overlay. If `back_height` is not specified the Backdrop Sizes to the text<br>**Values:** Any Number greater then 0                                  |
| `back_align`              | **Description:** Controls the Alignment for the Text Overlay inside the backdrop. If `back_align` is not specified the Backdrop Centers the text.<br>**Values:** `left`, `right`, `center`, `top`, or `bottom` |
| `back_padding`            | **Description:** Controls the Backdrop Padding for the Text Overlay.<br>**Values:** Any Number greater then 0                                                                                                  |
| `back_radius`             | **Description:** Controls the Backdrop Radius for the Text Overlay.<br>**Values:** Any Number greater then 0                                                                                                   |
| `back_line_color`         | **Description:** Controls the Backdrop Line Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`                                                      |
| `back_line_width`         | **Description:** Controls the Backdrop Line Width for the Text Overlay.<br>**Values:** Any Number greater then 0                                                                                               |

1. Each default overlay has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.