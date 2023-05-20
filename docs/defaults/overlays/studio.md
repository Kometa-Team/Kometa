# Studio Overlay

The `studio` Default Overlay File is used to create an overlay based on the show studio on each item within your library.

![](images/studio.png)

## Requirements & Recommendations

Supported library types: Movie / Show

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: studio
  TV Shows:
    overlay_path:
      - pmm: studio
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

| Variable            | Default     |
|:--------------------|:------------|
| `horizontal_offset` | `15`        |
| `horizontal_align`  | `left`      |
| `vertical_offset`   | `150`       |
| `vertical_align`    | `bottom`    |
| `back_color`        | `#00000099` |
| `back_radius`       | `30`        |
| `back_width`        | `305`       |
| `back_height`       | `105`       |

| Variable                     | Description & Values                                                                                                                                                                                                                                                                                                                                                                                         |
|:-----------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `builder_level`              | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode`                      |                                                                                                                                                                                                                                    


The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: studio
        template_variables:
          vertical_offset: 390
  TV Shows:
    overlay_path:
      - pmm: studio
      - pmm: studio
        template_variables:
          builder_level: season
          vertical_align: bottom
          vertical_offset: 15
          horizontal_align: left
          horizontal_offset: 15
      - pmm: studio
        template_variables:
          builder_level: episode
          vertical_align: top
          vertical_offset: 15
```
