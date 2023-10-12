# Shared Overlay Template Variables

IMPORTANT: The variables in this table are only valid in the context of the [`PMM default metadata files`](guide).

There are some `template_variables` that all the PMM Defaults except `franchise` can use to manipulate the file from the default settings which are provided.   This page is not an exhaustive list of all such template variables.

The variables listed on this page are common to all default overlay files [aside from `franchise`]; each individual overlay *may* have other template variables available.  Those will be listed on the wiki page for each individual default overlay file.

Some of these template variables may have default values depending on the specific overlay.  Those default values will also be listed on the individual overlay page.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

Below are the common variables which can be used to customize the file.

| Variable                   | Description & Values                                                                                                                                                                                           |
|:---------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_<<key>>`<sup>1</sup>  | **Description:** Turns off individual Overlays in a Defaults file.<br>**Values:** `false` to turn off the overlay                                                                                              |
| `file`                     | **Description:** Controls the images associated with all the Overlays to a local file.<br>**Values:** Filepath to Overlay Image                                                                                |
| `file_<<key>>`<sup>1</sup> | **Description:** Controls the image associated with this key's Overlay to a local file.<br>**Values:** Filepath to Overlay Image                                                                               |
| `url`                      | **Description:** Controls the images associated with all the Overlays to a url.<br>**Values:** URL to Overlay Image                                                                                            |
| `url_<<key>>`<sup>1</sup>  | **Description:** Controls the image associated with this key's Overlay to a url.<br>**Values:** URL to Overlay Image                                                                                           |
| `git`                      | **Description:** Controls the images associated with all the Overlays to the git repo.<br>**Values:** Git Path to Overlay Image                                                                                |
| `git_<<key>>`<sup>1</sup>  | **Description:** Controls the image associated with this key's Overlay to the git repo.<br>**Values:** Git Path to Overlay Image                                                                               |
| `repo`                     | **Description:** Controls the images associated with all the Overlays to a custom repo.<br>**Values:** Repo Path to Overlay Image                                                                              |
| `repo_<<key>>`<sup>1</sup> | **Description:** Controls the image associated with this key's Overlay to a custom repo.<br>**Values:** Repo Path to Overlay Image                                                                             |
| `horizontal_offset`        | **Description:** Controls the Horizontal Offset of this overlay. Can be a %.<br>**Values:** Number 0 or greater or 0%-100%                                                                                     |
| `horizontal_align`         | **Description:** Controls the Horizontal Alignment of the overlay.<br>**Values:** `left`, `center`, or `right`                                                                                                 |
| `vertical_offset`          | **Description:** Controls the Vertical Offset of this overlay. Can be a %.<br>**Values:** Number 0 or greater or 0%-100%                                                                                       |
| `vertical_align`           | **Description:** Controls the Vertical Alignment of the overlay.<br>**Values:** `top`, `center`, or `bottom`                                                                                                   |
| `back_color`               | **Description:** Controls the Backdrop Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`<br>`AA` is transparency; 00 [transparent] to FF [opaque]|
| `back_width`               | **Description:** Controls the Backdrop Width for the Text Overlay. If `back_width` is not specified the Backdrop Sizes to the text<br>**Values:** Any number greater than 0                                    |
| `back_height`              | **Description:** Controls the Backdrop Height for the Text Overlay. If `back_height` is not specified the Backdrop Sizes to the text<br>**Values:** Any number greater than 0                                  |
| `back_align`               | **Description:** Controls the Alignment for the Text Overlay inside the backdrop. If `back_align` is not specified the Backdrop Centers the text.<br>**Values:** `left`, `right`, `center`, `top`, or `bottom` |
| `back_padding`             | **Description:** Controls the Backdrop Padding for the Text Overlay.<br>**Values:** Any number greater than 0                                                                                                  |
| `back_radius`              | **Description:** Controls the Backdrop Radius for the Text Overlay.<br>**Values:** Any number greater than 0                                                                                                   |
| `back_line_color`          | **Description:** Controls the Backdrop Line Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA``AA` is transparency; 00 [transparent] to FF [opaque]|
| `back_line_width`          | **Description:** Controls the Backdrop Line Width for the Text Overlay.<br>**Values:** Any number greater than 0                                                                                               |

1. Each default overlay has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.
