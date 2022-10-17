# Edition Overlays

The `audio_codec` Default Overlay File is used to create an overlay based on the audio codec available on each item within your library.

**This file only works with Movie Libraries.**

**Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme**

![](images/edition.png)

## Supported Editions

| Edition             |       Key       | Weight |
|:--------------------|:---------------:|:------:|
| Directors Cut       | `directorscut`  | `150`  |
| Extended Edition    |   `extended`    | `140`  |
| Uncut Edition       |     `uncut`     | `130`  |
| Unrated Edition     |    `unrated`    | `120`  |
| Special Edition     |    `special`    | `110`  |
| Final Cut           |   `finalcut`    | `100`  |
| Anniversary Edition |  `anniversary`  |  `90`  |
| Collectors Edition  |   `collector`   |  `80`  |
| International Cut   | `international` |  `70`  |
| Theatrical Cut      |  `theatrical`   |  `60`  |
| Ultimate Cut        |   `ultimate`    |  `50`  |
| IMAX                |     `imax`      |  `30`  |
| Remastered          |  `remastered`   |  `20`  |

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: edition
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

| Variable            |   Default   |
|:--------------------|:-----------:|
| `horizontal_offset` |    `15`     |
| `horizontal_align`  |   `left`    |
| `vertical_offset`   |  `15`/`99`  |
| `vertical_align`    |    `top`    |
| `back_color`        | `#00000099` |
| `back_radius`       |    `30`     |
| `back_width`        |    `305`    |
| `back_height`       |    `105`    |

| Variable         | Description & Values                                                                                         |
|:-----------------|:-------------------------------------------------------------------------------------------------------------|
| `weight_<<key>>` | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: edition
        template_variables:
          weight_ultimate: 95
          use_international: false
```
