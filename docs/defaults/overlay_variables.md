# Overlay Variables

<!--shared-content-start-->
When something in this table is noted as expecting a number, that number is expressed in pixels, assuming an image 1000x1500 in size.
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

| Variable | Description | Values |
|:---------|:------------|:-------|
| `back_align` | Controls the Alignment for the Text Overlay inside the backdrop. If `back_align` is not specified the Backdrop Centers the text. | `left`, `right`, `center`, `top`, or `bottom` |
| `back_color` | Controls the Backdrop Color for the Text Overlay. | Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`<br>`AA` is transparency; 00 [transparent] to FF [opaque] |
| `back_height` | Controls the Backdrop Height for the Text Overlay. If `back_height` is not specified the Backdrop Sizes to the text | Any number greater than 0 [pixels assuming a 1000x1500 image] |
| `back_line_color` | Controls the Backdrop Line Color for the Text Overlay. | Color Hex Code in format `#RGB`, `#RGBA`, `#RRGGBB` or `#RRGGBBAA`<br>`AA` is transparency; 00 [transparent] to FF [opaque] |
| `back_line_width` | Controls the Backdrop Line Width for the Text Overlay. | Any number greater than 0 [pixels assuming a 1000x1500 image] |
| `back_padding` | Controls the Backdrop Padding for the Text Overlay. | Any number greater than 0 [pixels assuming a 1000x1500 image] |
| `back_radius` | Controls the Backdrop Radius for the Text Overlay. | Any number greater than 0 [pixels assuming a 1000x1500 image] |
| `back_width` | Controls the Backdrop Width for the Text Overlay. If `back_width` is not specified the Backdrop Sizes to the text | Any number greater than 0 [pixels assuming a 1000x1500 image] |
| `file_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the image associated with this key's Overlay to a local file. | Filepath to Overlay Image |
| `file` | Controls the images associated with all the Overlays to a local file. | Filepath to Overlay Image |
| `git_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the image associated with this key's Overlay to the git repo. | Git Path to Overlay Image |
| `git` | Controls the images associated with all the Overlays to the git repo. | Git Path to Overlay Image |
| `horizontal_align` | Controls the Horizontal Alignment of the overlay. | `left`, `center`, or `right` |
| `horizontal_offset` | Controls the Horizontal Offset of this overlay. Can be a %. | Number 0 or greater or 0%-100% [pixels assuming a 1000x1500 image] |
| `repo_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the image associated with this key's Overlay to a custom repo. | Repo Path to Overlay Image |
| `repo` | Controls the images associated with all the Overlays to a custom repo. | Repo Path to Overlay Image |
| `url_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the image associated with this key's Overlay to a url. | URL to Overlay Image |
| `url` | Controls the images associated with all the Overlays to a url. | URL to Overlay Image |
| `use_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Turns off individual Overlays in a Defaults File. | `false` to turn off the overlay |
| `vertical_align` | Controls the Vertical Alignment of the overlay. | `top`, `center`, or `bottom` |
| `vertical_offset` | Controls the Vertical Offset of this overlay. Can be a %. | Number 0 or greater or 0%-100% [pixels assuming a 1000x1500 image] |
