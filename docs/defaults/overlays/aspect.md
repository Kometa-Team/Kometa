# Status Overlay

The `aspect` Default Overlay File is used to create an overlay on a show detailing its Current Airing Status for all shows in your library.

![](images/aspect.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show

## Supported Status

| Status | Key    | Weight |
|:-------|:-------|:-------|
| 1.33   | `1.33` | `80`   |
| 1.65   | `1.65` | `70`   |
| 1.66   | `1.66` | `60`   |
| 1.78   | `1.78` | `50`   |
| 1.85   | `1.85` | `40`   |
| 2.2    | `2.2`  | `30`   |
| 2.35   | `2.35` | `20`   |
| 2.77   | `2.77` | `10`   |

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: aspect
  TV Shows:
    overlay_path:
      - pmm: aspect
      - pmm: aspect
        template_variables:
          builder_level: episode
      - pmm: aspect
        template_variables:
          builder_level: season
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

| Variable            | Default     |
|:--------------------|:------------|
| `horizontal_offset` | `150`       |
| `horizontal_align`  | `center`    |
| `vertical_offset`   | `0`         |
| `vertical_align`    | `bottom`    |
| `back_color`        | `#00000099` |
| `back_radius`       | `30`        |
| `back_width`        | `305`       |
| `back_height`       | `105`       |

| Variable                     | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|:-----------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `text_<<key>>`<sup>1</sup>   | **Description:** Choose the text for the Overlay.<br>**Default:** <table class="clearTable"><tr><th>Key</th><th>Default</th></tr><tr><td>`1.33`</td><td>`1.33`</td></tr><tr><td>`1.65`</td><td>`1.65`</td></tr><tr><td>`1.66`</td><td>`1.66`</td></tr><tr><td>`1.78`</td><td>`1.78`</td></tr><tr><td>`1.85`</td><td>`1.85`</td></tr><tr><td>`2.2`</td><td>`2.2`</td></tr><tr><td>`2.35`</td><td>`2.35`</td></tr><tr><td>`2.77`</td><td>`2.77`</td></tr></table>**Values:** Any String |
| `weight_<<key>>`<sup>1</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number                                                                                                                                                                                                                                                                                                                                                                          |
| `font`                       | **Description:** Choose the font for the Overlay.<br>**Default:** `fonts/Inter-Medium.ttf`<br>**Values:** Path to font file                                                                                                                                                                                                                                                                                                                                                           |
| `font_style`                 | **Description:** Font style for Variable Fonts.<br>**Values:** Variable Font Style                                                                                                                                                                                                                                                                                                                                                                                                    |
| `font_size`                  | **Description:** Choose the font size for the Overlay.<br>**Default:** `50`<br>**Values:** Any number greater than 0                                                                                                                                                                                                                                                                                                                                                                  |
| `font_color`                 | **Description:** Choose the font color for the Overlay.<br>**Default:** `#FFFFFF`<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`                                                                                                                                                                                                                                                                                                                   |
| `stroke_width`               | **Description:** Font Stroke Width for the Text Overlay.<br>**Values:** Any number greater than 0                                                                                                                                                                                                                                                                                                                                                                                     |
| `stroke_color`               | **Description:** Font Stroke Color for the Text Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`                                                                                                                                                                                                                                                                                                                                            |

1. Each default overlay has a `key` that when calling to effect a specific overlay you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: aspect
        template_variables:
          text_1.33: "4:9"
          text_1.77: "16:9"
  TV Shows:
    overlay_path:
      - pmm: aspect
        template_variables:
          text_1.33: "4:9"
          text_1.77: "16:9"
      - pmm: aspect
        template_variables:
          overlay_level: episode
          text_1.33: "4:9"
          text_1.77: "16:9"
      - pmm: aspect
        template_variables:
          overlay_level: season
          text_1.33: "4:9"
          text_1.77: "16:9"
```
