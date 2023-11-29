# MediaStinger Overlay

The `mediastinger` Default Overlay File is used to create an overlay based on if there's an after/during credit scene on each movie within your library.

![](images/mediastinger.png)

## Requirements & Recommendations

Supported Overlay Level: Movie

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: mediastinger
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

| Variable            | Default / Values   |
|:--------------------|:-------------------|
| `horizontal_offset` | `200`              |
| `horizontal_align`  | `right`            |
| `vertical_offset`   | `15`               |
| `vertical_align`    | `top`              |
| `back_color`        | `#00000099`        |
| `back_radius`       | `30`               |
| `back_width`        | `105`              |
| `back_height`       | `105`              |

{%
   include-markdown "../overlay_variables.md"
%}

## Example Template Variable Amendments

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: mediastinger
        template_variables:
          font_color: "#FFFFFF99"
```
