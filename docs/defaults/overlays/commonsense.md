# CommonSense Age Rating Overlay

The `commonsense` Default Overlay File is used to create an overlay based on the CommonSense Age Rating on each item within your library.

Use the [Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with either `mdb_commonsense` or `mdb_commonsense0` to update Plex to the Common Sense Rating.

**This file works with Movie and Show Libraries.**

![](images/commonsense.png)

## Supported CommonSense Age Rating

| Rating | Key  |
|:-------|:-----|
| 1+     | `1`  |
| 2+     | `2`  |
| 3+     | `3`  |
| 4+     | `4`  |
| 5+     | `5`  |
| 6+     | `6`  |
| 7+     | `7`  |
| 8+     | `8`  |
| 9+     | `9`  |
| 10+    | `10` |
| 11+    | `11` |
| 12+    | `12` |
| 13+    | `13` |
| 14+    | `14` |
| 15+    | `15` |
| 16+    | `16` |
| 17+    | `17` |
| 18+    | `18` |
| NR     | `nr` |

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: commonsense
  TV Shows:
    overlay_path:
      - pmm: commonsense
      - pmm: commonsense
        template_variables:
          overlay_level: season
      - pmm: commonsense
        template_variables:
          overlay_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

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

| Variable         | Description & Values                                                                                                                                                |
|:-----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `font`           | **Description:** Choose the font for the Overlay.<br>**Default:** `fonts/Inter-Medium.ttf`<br>**Values:** Path to font file                                         |
| `font_style`     | **Description:** Font style for Variable Fonts.<br>**Values:** Variable Font Style                                                                                  |
| `font_size`      | **Description:** Choose the font size for the Overlay.<br>**Default:** `55`<br>**Values:** Any Number greater then 0                                                |
| `font_color`     | **Description:** Choose the font color for the Overlay.<br>**Default:** `#FFFFFF`<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA` |
| `stroke_width`   | **Description:** Font Stroke Width for the Text Overlay.<br>**Values:** Any Number greater then 0                                                                   |
| `stroke_color`   | **Description:** Font Stroke Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`                          |
| `addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any Number greater then 0                                               |
| `addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `left`<br>**Values:** `left`, `right`, `top`, `bottom`                         |
| `pre_text`       | **Description:** Choose the text before the key for the Overlay.<br>**Values:** Any String                                                                          |
| `post_text`      | **Description:** Choose the text after the key for the Overlay.<br>**Default:** `+`<br>**Values:** Any String                                                       |
| `pre_nr_text`    | **Description:** Choose the text before the `nr` key for the Overlay.<br>**Values:** Any String                                                                     |
| `post_nr_text`   | **Description:** Choose the text after the `nr` key for the Overlay.<br>**Values:** Any String                                                                      |
| `overlay_level`  | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode`                                                                                     |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: commonsense
        template_variables:
          pre_text: "CS"
```
