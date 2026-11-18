# Overlay Text Variables

<!--shared-content-start-->
When something in this table is noted as expecting a number, typically that number is expressed in pixels, assuming an image 1000x1500 in size.

Color values should be wrapped in quotes in the YAML, as the `#` denotes a comment in YAML and if left unquoted will prevent the value from being seen by Kometa.

File paths need to be valid in the context where Kometa is running; this is primarily an issue when running in docker, as Kometa inside the container cannot see host paths.

| Variable | Description | Values |
|:---------|:------------|:-------|
| `font_<<key>>` | Choose the font for this key's Overlay. | **Default:** `fonts/Inter-Medium.ttf`<br>Path to font file |
| `font_color_<<key>>` | Choose the font color for this key's Overlay. | **Default:** `#FFFFFF`<br>Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA` |
| `font_color` | Choose the font color for the Overlay. | **Default:** `#FFFFFF`<br>Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA` |
| `font_size_<<key>>` | Choose the font size for this key's Overlay. | **Default:** `55`<br>Any number greater than 0 [pixels assuming a 1000x1500 image] |
| `font_size` | Choose the font size for the Overlay. | **Default:** `55`<br>Any number greater than 0 [pixels assuming a 1000x1500 image] |
| `font_style_<<key>>` | Font style for this key's Variable Fonts. The valid values depend on the font; the default font (`fonts/Inter-Medium.ttf`) exposes `Thin`, `ExtraLight`, `Light`, `Regular`, `Medium`, `SemiBold`, `Bold`, `ExtraBold`, `Black`. For other fonts, the runtime error message lists the valid options. | Variable Font Style |
| `font_style` | Font style for Variable Fonts. The valid values depend on the font; the default font (`fonts/Inter-Medium.ttf`) exposes `Thin`, `ExtraLight`, `Light`, `Regular`, `Medium`, `SemiBold`, `Bold`, `ExtraBold`, `Black`. For other fonts, the runtime error message lists the valid options. | Variable Font Style |
| `font` | Choose the font for the Overlay. | **Default:** `fonts/Inter-Medium.ttf`<br>Path to font file |
| `stroke_color_<<key>>` | Font Stroke Color for this key's Overlay. | Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA` |
| `stroke_color` | Font Stroke Color for the Overlay. | Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA` |
| `stroke_width_<<key>>` | Font Stroke Width for this key's Overlay. | Any number greater than 0 [pixels assuming a 1000x1500 image] |
| `stroke_width` | Font Stroke Width for the Overlay. | Any number greater than 0 [pixels assuming a 1000x1500 image] |
