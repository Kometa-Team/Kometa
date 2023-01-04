# Runtimes Overlay

The `runtimes` Default Overlay File is used to create an overlay on of the movie or episodes runtime for all items in your library.

**This file works with Movie and Show Libraries.**

![](images/runtimes.png)

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: runtimes
  TV Shows:
    overlay_path:
      - pmm: runtimes
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

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

| Variable       | Description & Values                                                                                                                                                |
|:---------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `text`         | **Description:** Choose the text for the Overlay.<br>**Default:** `Runtime`<br>**Values:** Any String                                                               |
| `font`         | **Description:** Choose the font for the Overlay.<br>**Default:** `fonts/Inter-Medium.ttf`<br>**Values:** Path to font file                                         |
| `font_style`   | **Description:** Font style for Variable Fonts.<br>**Values:** Variable Font Style                                                                                  |
| `font_size`    | **Description:** Choose the font size for the Overlay.<br>**Default:** `55`<br>**Values:** Any Number greater then 0                                                |
| `font_color`   | **Description:** Choose the font color for the Overlay.<br>**Default:** `#FFFFFF`<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA` |
| `stroke_width` | **Description:** Font Stroke Width for the Text Overlay.<br>**Values:** Any Number greater then 0                                                                   |
| `stroke_color` | **Description:** Font Stroke Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`                          |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  TV Shows:
    overlay_path:
      - pmm: runtimes
        font: fonts/Inter-Bold.ttf
```
