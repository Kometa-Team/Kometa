# Versions Overlay

The `versions` Default Overlay File is used to create an overlay based on if there's multiple versions on each item within your library.

![](images/version.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show, Season, Episode

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_files:
      - pmm: versions
  TV Shows:
    overlay_files:
      - pmm: versions
      - pmm: versions
        template_variables:
          builder_level: season
      - pmm: versions
        template_variables:
          builder_level: episode
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

| Variable            | Default / Values                                                                |
|:--------------------|:--------------------------------------------------------------------------------|
| `horizontal_offset` | `15`/`235`                                                                      |
| `horizontal_align`  | `right`/`center`                                                                |
| `vertical_offset`   | `1050`/`15`                                                                     |
| `vertical_align`    | `top`                                                                           |
| `back_color`        | `#00000099`                                                                     |
| `back_radius`       | `30`                                                                            |
| `back_width`        | `105`                                                                           |
| `back_height`       | `105`                                                                           |
| `builder_level`     | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode` |

{%
   include-markdown "../overlay_variables.md"
%}

## Example Template Variable Amendments

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_files:
      - pmm: versions
        template_variables:
          back_color: "#FFFFFF99"
```
