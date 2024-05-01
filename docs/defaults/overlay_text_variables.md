When something in this table is noted as expecting a number, typically that number is expressed in pixels, assuming an image 1000x1500 in size.

Color values should be wrapped in quotes in the YAML, as the `#` denotes a comment in YAML and if left unquoted will prevent the value from being seen by Kometa.

File paths need to be valid in the context where Kometa is running; this is primarily an issue when running in docker, as Kometa inside the container cannot see host paths.

| Variable               | Description & Values                                                                                                                                                       |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `font`                 | **Description:** Choose the font for the Overlay.<br>**Default:** `fonts/Inter-Medium.ttf`<br>**Values:** Path to font file                                                |
| `font_style`           | **Description:** Font style for Variable Fonts.<br>**Values:** Variable Font Style                                                                                         |
| `font_size`            | **Description:** Choose the font size for the Overlay.<br>**Default:** `55`<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]                   |
| `font_color`           | **Description:** Choose the font color for the Overlay.<br>**Default:** `#FFFFFF`<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`        |
| `stroke_width`         | **Description:** Font Stroke Width for the Overlay.<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]                                           |
| `stroke_color`         | **Description:** Font Stroke Color for the Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`                                      |
| `font_<<key>>`         | **Description:** Choose the font for this key's Overlay.<br>**Default:** `fonts/Inter-Medium.ttf`<br>**Values:** Path to font file                                         |
| `font_style_<<key>>`   | **Description:** Font style for this key's Variable Fonts.<br>**Values:** Variable Font Style                                                                              |
| `font_size_<<key>>`    | **Description:** Choose the font size for this key's Overlay.<br>**Default:** `55`<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]            |
| `font_color_<<key>>`   | **Description:** Choose the font color for this key's Overlay.<br>**Default:** `#FFFFFF`<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA` |
| `stroke_width_<<key>>` | **Description:** Font Stroke Width for this key's Overlay.<br>**Values:** Any number greater than 0 [pixels assuming a 1000x1500 image]                                    |
| `stroke_color_<<key>>` | **Description:** Font Stroke Color for this key's Overlay.<br>**Values:** Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`                               |