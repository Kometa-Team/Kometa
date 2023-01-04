# Audio Codec Overlay

The `audio_codec` Default Overlay File is used to create an overlay based on the audio codec available on each item within your library.

**This file works with Movie and Show Libraries.**

**Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme.**

![](images/audio_codec.png)

## Supported Audio Codecs

| Audio Codec            | Key            | Weight |
|:-----------------------|:---------------|:-------|
| Dolby TrueHD Atmos     | `truehd_atmos` | `160`  |
| DTS-X                  | `dtsx`         | `150`  |
| Dolby Digital+ / E-AC3 | `plus_atmos`   | `140`  |
| Dolby Atmos            | `dolby_atmos`  | `130`  |
| Dolby TrueHD           | `truehd`       | `120`  |
| DTS-HD-MA              | `ma`           | `110`  |
| FLAC                   | `flac`         | `100`  |
| PCM                    | `pcm`          | `90`   |
| DTS-HD-HRA             | `hra`          | `80`   |
| Dolby Digital+         | `plus`         | `70`   |
| DTS-ES                 | `dtses`        | `60`   |
| DTS                    | `dts`          | `50`   |
| Dolby Digital          | `digital`      | `40`   |
| AAC                    | `aac`          | `30`   |
| MP3                    | `mp3`          | `20`   |
| Opus                   | `opus`         | `10`   |

### Standard Style

Below is a screenshot of the alternative Standard (`standard`) style which can be set via the `style` template variable.

![](images/audio_codec2.png)

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: audio_codec
  TV Shows:
    overlay_path:
      - pmm: audio_codec
      - pmm: audio_codec
        template_variables:
          overlay_level: season
      - pmm: audio_codec
        template_variables:
          overlay_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

| Variable            | Default     |
|:--------------------|:------------|
| `horizontal_offset` | `0`         |
| `horizontal_align`  | `center`    |
| `vertical_offset`   | `15`        |
| `vertical_align`    | `top`       |
| `back_color`        | `#00000099` |
| `back_radius`       | `30`        |
| `back_width`        | `305`       |
| `back_height`       | `105`/`189` |

| Variable                     | Description & Values                                                                                         |
|:-----------------------------|:-------------------------------------------------------------------------------------------------------------|
| `style`                      | **Description:** Choose the Overlay Style.<br>**Default:** `compact`<br>**Values:** `compact` or `standard`  |
| `overlay_level`              | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode`                              |
| `weight_<<key>>`<sup>1</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number |
| `regex_<<key>>`<sup>1</sup>  | **Description:** Controls the regex of the Overlay Search.<br>**Values:** Any Proper Regex                   |

1. Each default overlay has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: audio_codec
        template_variables:
          use_opus: false
          use_mp3: false
          style: standard
```
