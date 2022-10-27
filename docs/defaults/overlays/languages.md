# Audio/Subtitle Language Flags Overlay

The `languages` Default Overlay File is used to create an overlay of a flag and [ISO 639-1 Code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) based on the audio/subtitle languages available on each item within your library.

**This file works with Movie and Show Libraries.**

**Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme**

![](images/languages.png)

## Supported Audio/Subtitle Language Flags

| Audio/Subtitle Languages | Key  | Weight |
|:-------------------------|:----:|:------:|
| German                   | `de` | `610`  |
| English                  | `en` | `600`  |
| French                   | `fr` | `590`  |
| Japanese                 | `ja` | `580`  |
| Korean                   | `ko` | `570`  |
| Chinese                  | `zh` | `560`  |
| Danish                   | `da` | `550`  |
| Russian                  | `ru` | `540`  |
| Spanish                  | `es` | `530`  |
| Italian                  | `it` | `520`  |
| Portuguese               | `pt` | `510`  |
| Hindi                    | `hi` | `500`  |
| Telugu                   | `te` | `490`  |
| Farsi                    | `fa` | `480`  |
| Thai                     | `th` | `470`  |
| Dutch                    | `nl` | `460`  |
| Norwegian                | `no` | `450`  |
| Icelandic                | `is` | `440`  |
| Swedish                  | `sv` | `430`  |
| Turkish                  | `tr` | `420`  |
| Polish                   | `pl` | `410`  |
| Czech                    | `cs` | `400`  |
| Ukrainian                | `uk` | `390`  |
| Hungarian                | `hu` | `380`  |
| Arabic                   | `ar` | `370`  |
| Bulgarian                | `bg` | `360`  |
| Bengali                  | `bn` | `350`  |
| Bosnian                  | `bs` | `340`  |
| Catalan                  | `ca` | `330`  |
| Welsh                    | `cy` | `320`  |
| Greek                    | `el` | `310`  |
| Estonian                 | `et` | `300`  |
| Basque                   | `eu` | `290`  |
| Finnish                  | `fi` | `280`  |
| Filipino                 | `fi` | `270`  |
| Galician                 | `gl` | `260`  |
| Hebrew                   | `he` | `250`  |
| Croatian                 | `hr` | `240`  |
| Indonesian               | `id` | `230`  |
| Georgian                 | `ka` | `220`  |
| Kazakh                   | `kk` | `210`  |
| Kannada                  | `kn` | `200`  |
| Latin                    | `la` | `190`  |
| Lithuanian               | `lt` | `180`  |
| Latvian                  | `lv` | `170`  |
| Macedonian               | `mk` | `160`  |
| Malayalam                | `ml` | `150`  |
| Marathi                  | `mr` | `140`  |
| Malay                    | `ms` | `130`  |
| Norwegian Nokmål         | `nb` | `120`  |
| Norwegian Nynorsk        | `nn` | `110`  |
| Punjabi                  | `pa` | `100`  |
| Romanian                 | `ro` |  `90`  |
| Slovak                   | `sk` |  `80`  |
| Slovenian                | `sv` |  `70`  |
| Albanian                 | `sq` |  `60`  |
| Serbian                  | `sr` |  `50`  |
| Swahili                  | `sw` |  `40`  |
| Tamil                    | `ta` |  `30`  |
| Urdu                     | `ur` |  `20`  |
| Vietnamese               | `vi` |  `10`  |

#### Square Style

Below is a screenshot of the alternative Square (`square`) style which can be set via the `style` template variable.

![](../images/languages2.png)

#### Half Style

Below is a screenshot of the alternative Half (`half`) style which can be set via the `style` template variable.

![](../images/languages3.png)

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: languages
  TV Shows:
    overlay_path:
      - pmm: languages
      - pmm: languages
        template_variables:
          overlay_level: season
      - pmm: languages
        template_variables:
          overlay_level: episode
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

| Variable            |           Default           |
|:--------------------|:---------------------------:|
| `horizontal_offset` |            `15`             |
| `horizontal_align`  |       `left`/`right`        |
| `vertical_offset`   | `15`/`75`/`135`/`195`/`255` |
| `vertical_align`    |            `top`            |
| `back_color`        |         `#00000099`         |
| `back_radius`       |           `26`/``           |
| `back_width`        |            `190`            |
| `back_height`       |            `105`            |
| `back_align`        |           `left`            |
| `font`              |   `fonts/Inter-Bold.ttf`    |
| `font_size`         |            `50`             |

| Variable                     | Description & Values                                                                                                                                                                                                                                                                                                          |
|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `position`                   | **Description:** Changes the position of the Overlays.<br>**Default:** `left`<br>**Values:** `left`, `right`, `half`, or List of Coordinates                                                                                                                                                                                  |
| `style`                      | **Description:** Controls the visual theme of the overlays created.<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>round</code></td><td>Round Theme</td></tr><tr><td><code>square</code></td><td>Square Theme</td></tr><tr><td><code>half</code></td><td>Square Flag with Round Background</td></tr></table> |
| `offset`                     | **Description:** Controls the offset between the flag and the text.<br>**Default:** `10`<br>**Values:** Any Integer 0 or greater                                                                                                                                                                                              |
| `use_lowercase`              | **Description:** Controls if the overlay display is in lowercase.<br>**Values:** `true` to use lowercase text                                                                                                                                                                                                                 |
| `use_subtitles`              | **Description:** Controls if the overlay is based on subtitle language instead of audio language.<br>**Values:** `true` to look at subtitle language instead of audio language                                                                                                                                                |
| `overlay_level`              | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode`                                                                                                                                                                                                                                               |
| `weight_<<key>>`<sup>1</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number                                                                                                                                                                                                                  |

1. Each default overlay has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: languages
        template_variables:
          use_subtitles: true
          style: square
```
