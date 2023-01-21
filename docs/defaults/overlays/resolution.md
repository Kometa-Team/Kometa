# Resolution/Edition Overlay

The `resolution` Default Overlay File is used to create an overlay based on the resolutions and editions available on each item within your library.

![](images/resolution.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show, Episode

## Supported Resolutions

| Resolution     | Key       |
|:---------------|:----------|
| 4K             | `4k`      |
| 1080P          | `1080p`   |
| 720P           | `720p`    |
| 576P           | `576p`    |
| 480P           | `480p`    |
| DV             | `dv`      |
| HDR            | `hdr`     |

## Supported Editions

| Edition             | Key             | Weight |
|:--------------------|:----------------|:-------|
| Director's Cut      | `directorscut`  | `150`  |
| Extended Edition    | `extended`      | `140`  |
| Uncut Edition       | `uncut`         | `130`  |
| Unrated Edition     | `unrated`       | `120`  |
| Special Edition     | `special`       | `110`  |
| Final Cut           | `finalcut`      | `100`  |
| Anniversary Edition | `anniversary`   | `90`   |
| Collector's Edition | `collector`     | `80`   |
| International Cut   | `international` | `70`   |
| Theatrical Cut      | `theatrical`    | `60`   |
| Ultimate Cut        | `ultimate`      | `50`   |
| IMAX Enhanced       | `enhanced`      | `40`   |
| IMAX                | `imax`          | `30`   |
| Remastered          | `remastered`    | `20`   |
| Criterion           | `criterion`     | `10`   |

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: resolution
  TV Shows:
    overlay_path:
      - pmm: resolution
      - pmm: resolution
        template_variables:
          overlay_level: season
      - pmm: resolution
        template_variables:
          overlay_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

| Variable            | Default     |
|:--------------------|:------------|
| `horizontal_offset` | `15`        |
| `horizontal_align`  | `left`      |
| `vertical_offset`   | `15`        |
| `vertical_align`    | `top`       |
| `back_color`        | `#00000099` |
| `back_radius`       | `30`        |
| `back_width`        | `305`       |
| `back_height`       | `105`/`189` |

| Variable                     | Description & Values                                                                                                                           |
|:-----------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| `use_resolution`             | **Description:** Turns off all Resolution Overlays in the Defaults file.<br>**Values:** `false` to turn off the overlays                       |
| `use_edition`                | **Description:** Turns off all Edition Overlays in the Defaults file.<br>**Values:** `false` to turn off the overlays                          |
| `overlay_level`              | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode`                                                                |
| `weight_<<key>>`<sup>1</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority. **Only works with Edition keys.**<br>**Values:** Any Number |

1. Each default overlay has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: resolution
        template_variables:
          use_dv: false
          use_hdr: false
          use_1080p: false
          use_720p: false
          use_576p: false
          use_480p: false
```
