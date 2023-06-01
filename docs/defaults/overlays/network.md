# Network Overlay

The `network` Default Overlay File is used to create an overlay based on the show network on each item within your library.

![](images/network.png)

## Requirements & Recommendations

Supported library types: Show

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  TV Shows:
    overlay_path:
      - pmm: network
      - pmm: network
        template_variables:
          builder_level: season
      - pmm: network
        template_variables:
          builder_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

| Variable            | Default     |
|:--------------------|:------------|
| `horizontal_offset` | `15`        |
| `horizontal_align`  | `left`      |
| `vertical_offset`   | `510`       |
| `vertical_align`    | `bottom`    |
| `back_color`        | `#00000099` |
| `back_radius`       | `30`        |
| `back_width`        | `305`       |
| `back_height`       | `105`       |


The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  TV Shows:
    overlay_path:
      - pmm: network
        template_variables:
          vertical_offset: 390
      - pmm: network
        template_variables:
          vertical_offset: 390
          builder_level: season
      - pmm: network
        template_variables:
          vertical_offset: 390
          builder_level: episode
```
