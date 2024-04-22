# Audio Codec Overlay

The `audio_codec` Default Overlay File is used to create an overlay based on the audio codec available on each item 
within your library.

![](images/audio_codec.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show, Season, Episode

Recommendations: Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme

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
    overlay_files:
      - default: audio_codec
  TV Shows:
    overlay_files:
      - default: audio_codec
      - default: audio_codec
        template_variables:
          builder_level: season
      - default: audio_codec
        template_variables:
          builder_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this Kometa Defaults file.

    * **Overlay Template Variables** are additional variables shared across the Kometa Overlay Defaults.

    ??? example "Default Template Variable Values (click to expand)"

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
        
    === "File-Specific Template Variables"

        | Variable                     | Description & Values                                                                                         |
        |:-----------------------------|:-------------------------------------------------------------------------------------------------------------|
        | `style`                      | **Description:** Choose the Overlay Style.<br>**Default:** `compact`<br>**Values:** `compact` or `standard`  |
        | `builder_level`              | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode`                              |
        | `weight_<<key>>`<sup>1</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number |
        | `regex_<<key>>`<sup>1</sup>  | **Description:** Controls the regex of the Overlay Search.<br>**Values:** Any Proper Regex                   |

        1. Each default overlay has a `key` that when calling to effect a specific overlay you must replace `<<key>>` 
        with when calling.

    === "Overlay Template Variables"

        {%
           include-markdown "../overlay_variables.md"
        %}
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.
    
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: audio_codec
            template_variables:
              use_opus: false
              use_mp3: false
              style: standard
    ```
