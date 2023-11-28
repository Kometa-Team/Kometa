# Runtimes Overlay

The `runtimes` Default Overlay File is used to create an overlay of the movie runtime, episode runtime, or average episode runtime for all items in your library.

![](images/runtimes.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show, Season, Episode

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
      - pmm: runtimes
        template_variables:
          builder_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables.md) are available with the default values below as well as the additional Variables below which can be used to customize the file.

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

| Variable       | Description & Values                                                                                                                                                 |
|:---------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `text`         | **Description:** Choose the text for the Overlay.<br>**Default:** `Runtime: `<br>**Values:** Any String                                                              |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  TV Shows:
    overlay_path:
      - pmm: runtimes
        template_variables:
          builder_level: episode
        font: fonts/Inter-Bold.ttf
```
