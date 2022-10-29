# Audio/Subtitle Language Flags Overlay

The `languages` Default Overlay File is used to create an overlay of a flag and [ISO 639-1 Code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) based on the audio/subtitle languages available on each item within your library.

**This file works with Movie and Show Libraries.**

**Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme.**

![](images/languages.png)

## Supported Audio/Subtitle Language Flags

| Audio/Subtitle Languages | Key  | Weight | Default Flag |
|:-------------------------|:----:|:------:|:------------:|
| English                  | `en` | `610`  |     `us`     |
| German                   | `de` | `600`  |     `de`     |
| French                   | `fr` | `590`  |     `fr`     |
| Japanese                 | `ja` | `580`  |     `jp`     |
| Korean                   | `ko` | `570`  |     `kr`     |
| Chinese                  | `zh` | `560`  |     `cn`     |
| Danish                   | `da` | `550`  |     `dk`     |
| Russian                  | `ru` | `540`  |     `ru`     |
| Spanish                  | `es` | `530`  |     `es`     |
| Italian                  | `it` | `520`  |     `it`     |
| Portuguese               | `pt` | `510`  |     `pt`     |
| Hindi                    | `hi` | `500`  |     `in`     |
| Telugu                   | `te` | `490`  |     `in`     |
| Farsi                    | `fa` | `480`  |     `ir`     |
| Thai                     | `th` | `470`  |     `th`     |
| Dutch                    | `nl` | `460`  |     `nl`     |
| Norwegian                | `no` | `450`  |     `no`     |
| Icelandic                | `is` | `440`  |     `is`     |
| Swedish                  | `sv` | `430`  |     `se`     |
| Turkish                  | `tr` | `420`  |     `tr`     |
| Polish                   | `pl` | `410`  |     `pl`     |
| Czech                    | `cs` | `400`  |     `cz`     |
| Ukrainian                | `uk` | `390`  |     `ua`     |
| Hungarian                | `hu` | `380`  |     `hu`     |
| Arabic                   | `ar` | `370`  |     `eg`     |
| Bulgarian                | `bg` | `360`  |     `bg`     |
| Bengali                  | `bn` | `350`  |     `bd`     |
| Bosnian                  | `bs` | `340`  |     `ba`     |
| Catalan                  | `ca` | `330`  |     `es`     |
| Welsh                    | `cy` | `320`  |     `uk`     |
| Greek                    | `el` | `310`  |     `gr`     |
| Estonian                 | `et` | `300`  |     `ee`     |
| Basque                   | `eu` | `290`  |     `es`     |
| Finnish                  | `fi` | `280`  |     `fi`     |
| Filipino                 | `fl` | `270`  |     `ph`     |
| Galician                 | `gl` | `260`  |     `es`     |
| Hebrew                   | `he` | `250`  |     `il`     |
| Croatian                 | `hr` | `240`  |     `hr`     |
| Indonesian               | `id` | `230`  |     `id`     |
| Georgian                 | `ka` | `220`  |     `ge`     |
| Kazakh                   | `kk` | `210`  |     `kz`     |
| Kannada                  | `kn` | `200`  |     `in`     |
| Latin                    | `la` | `190`  |     `it`     |
| Lithuanian               | `lt` | `180`  |     `lt`     |
| Latvian                  | `lv` | `170`  |     `lv`     |
| Macedonian               | `mk` | `160`  |     `mk`     |
| Malayalam                | `ml` | `150`  |     `in`     |
| Marathi                  | `mr` | `140`  |     `in`     |
| Malay                    | `ms` | `130`  |     `my`     |
| Norwegian Nokmål         | `nb` | `120`  |     `no`     |
| Norwegian Nynorsk        | `nn` | `110`  |     `no`     |
| Punjabi                  | `pa` | `100`  |     `in`     |
| Romanian                 | `ro` |  `90`  |     `ro`     |
| Slovak                   | `sk` |  `80`  |     `sk`     |
| Slovenian                | `sv` |  `70`  |     `si`     |
| Albanian                 | `sq` |  `60`  |     `al`     |
| Serbian                  | `sr` |  `50`  |     `rs`     |
| Swahili                  | `sw` |  `40`  |     `tz`     |
| Tamil                    | `ta` |  `30`  |     `in`     |
| Urdu                     | `ur` |  `20`  |     `pk`     |
| Vietnamese               | `vi` |  `10`  |     `vn`     |

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
| `vertical_offset`   | `15`/`76`/`137`/`198`/`259` |
| `vertical_align`    |            `top`            |
| `back_color`        |         `#00000099`         |
| `back_radius`       |          `26`/` `           |
| `back_width`        |            `190`            |
| `back_height`       |            `105`            |
| `back_align`        |       `left`/`right`        |
| `font`              |   `fonts/Inter-Bold.ttf`    |
| `font_size`         |            `50`             |

| Variable                      | Description & Values                                                                                                                                                                                                                                                                                                          |
|:------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `position`                    | **Description:** Changes the position of all Overlay Queues in this File.<br>**Default:** `left`<br>**Values:** `left`, `right`, `half`, or List of Coordinates                                                                                                                                                               |
| `position_audio_flags`        | **Description:** Changes the position of the audio flags Overlays.<br>**Default:** `left`<br>**Values:** `left`, `right`, `half`, or List of Coordinates                                                                                                                                                                      |
| `position_subtitle_flags`     | **Description:** Changes the position of the subtitle flags Overlays.<br>**Default:** `left`<br>**Values:** `left`, `right`, `half`, or List of Coordinates                                                                                                                                                                   |
| `style`                       | **Description:** Controls the visual theme of the overlays created.<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>round</code></td><td>Round Theme</td></tr><tr><td><code>square</code></td><td>Square Theme</td></tr><tr><td><code>half</code></td><td>Square Flag with Round Background</td></tr></table> |
| `offset`                      | **Description:** Controls the offset between the flag and the text.<br>**Default:** `10`<br>**Values:** Any Integer 0 or greater                                                                                                                                                                                              |
| `align`                       | **Description:** Controls the flag alignment in the backdrop.<br>**Default:** `left`<br>**Values:** `left` or `right`                                                                                                                                                                                                         |
| `country_<<key>>`<sup>1</sup> | **Description:** Controls the country image for the Overlay.<br>**Default:** Listed in the [Table](#supported-audiosubtitle-language-flags) above<br>**Values:** [ISO 3166-1 Country Code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) for the flag desired                                                 |
| `use_lowercase`               | **Description:** Controls if the overlay display is in lowercase.<br>**Values:** `true` to use lowercase text                                                                                                                                                                                                                 |
| `use_subtitles`               | **Description:** Controls if the overlay is based on subtitle language instead of audio language.<br>**Values:** `true` to look at subtitle language instead of audio language                                                                                                                                                |
| `overlay_level`               | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode`                                                                                                                                                                                                                                               |
| `weight_<<key>>`<sup>1</sup>  | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number                                                                                                                                                                                                                  |

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
