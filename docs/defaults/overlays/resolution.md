---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Resolution/Edition", 
        "CODE_NAME": "resolution",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay based on the resolutions and editions available on each item within your library"
    }'
    end='<!--rec-sub-->'
%}

Recommendations: Editions overlay is designed to use the Editions field within Plex [which requires Plex Pass to use] or the 
[TRaSH Guides](https://trash-guides.info/) filename naming scheme.

## Supported Resolutions

| Resolution      | Key               | Weight |
|:----------------|:------------------|:-------|
| 4K DV/HDR10+    | `4k_dvhdrplus`    | `159`  |
| 4K DV/HDR       | `4k_dvhdr`        | `158`  |
| 4K HDR10+       | `4k_plus`         | `155`  |
| 4K DV           | `4k_dv`           | `150`  |
| 4K HDR          | `4k_hdr`          | `140`  |
| 4K              | `4k`              | `130`  |
| 1080p DV/HDR10+ | `1080p_dvhdrplus` | `129`  |
| 1080P DV/HDR    | `1080p_dvhdr`     | `128`  |
| 1080P HDR10+    | `1080p_plus`      | `125`  |
| 1080P DV        | `1080p_dv`        | `120`  |
| 1080P HDR       | `1080p_hdr`       | `110`  |
| 1080P           | `1080p`           | `100`  |
| 720P DV/HDR10+  | `720p_dvhdrplus`  | `99`   |
| 720P DV/HDR     | `720p_dvhdr`      | `98`   |
| 720P HDR10+     | `720p_plus`       | `95`   |
| 720P DV         | `720p_dv`         | `90`   |
| 720P HDR        | `720p_hdr`        | `80`   |
| 720P            | `720p`            | `70`   |
| 576P DV/HDR10+  | `576p_dvhdrplus`  | `69`   |
| 576P DV/HDR     | `576p_dvhdr`      | `68`   |
| 576P HDR10+     | `576p_plus`       | `65`   |
| 576P DV         | `576p_dv`         | `60`   |
| 576P HDR        | `576p_hdr`        | `50`   |
| 576P            | `576p`            | `40`   |
| 480P DV/HDR10+  | `480p_dvhdrplus`  | `39`   |
| 480P DV/HDR     | `480p_dvhdr`      | `38`   |
| 480P HDR10+     | `480p_plus`       | `35`   |
| 480P DV         | `480p_dv`         | `30`   |
| 480P HDR        | `480p_hdr`        | `20`   |
| 480P            | `480p`            | `10`   |
| DV/HDR10+       | `dvhdrplus`       | `9`    |
| DV/HDR          | `dvhdr`           | `8`    |
| HDR10+          | `plus`            | `7`    |
| DV              | `dv`              | `5`    |
| HDR             | `hdr`             | `1`    |

## Supported Editions

| Edition             | Key             | Weight |
|:--------------------|:----------------|:-------|
| Extended Edition    | `extended`      | `190`  |
| Uncut Edition       | `uncut`         | `180`  |
| Unrated Edition     | `unrated`       | `170`  |
| Special Edition     | `special`       | `160`  |
| Anniversary Edition | `anniversary`   | `150`  |
| Collector's Edition | `collector`     | `140`  |
| Diamond Edition     | `diamond`       | `130`  |
| Platinum Edition    | `platinum`      | `120`  |
| Director's Cut      | `directors`     | `110`  |
| Final Cut           | `final`         | `100`  |
| International Cut   | `international` | `90`   |
| Theatrical Cut      | `theatrical`    | `80`   |
| Ultimate Cut        | `ultimate`      | `70`   |
| Alternate Cut       | `alternate`     | `60`   |
| Coda Cut            | `coda`          | `50`   |
| IMAX Enhanced       | `enhanced`      | `40`   |
| IMAX                | `imax`          | `30`   |
| Remastered          | `remastered`    | `20`   |
| Criterion           | `criterion`     | `10`   |
| Richard Donner      | `richarddonner` | `9`    |
| Black and Chrome    | `blackchrome`   | `8`    |
| Definitive          | `definitive`    | `7`    |
| Open Matte          | `openmatte`     | `6`    |
| Ulysses             | `ulysses`       | `5`    |

## "Dovetail" versions

In the Kometa log, you may see references to versions of these overlays with `-Dovetail` appended:

```
|                             4K-Plus-Dovetail Overlay in Movies                             |
|                              4K-DV-Dovetail Overlay in Movies                              |
|                             4K-HDR-Dovetail Overlay in Movies                              |
|                               4K-Dovetail Overlay in Movies                                |
...
|                        Extended-Edition-Dovetail Overlay in Movies                         |
|                          Uncut-Edition-Dovetail Overlay in Movies                          |
|                         Unrated-Edition-Dovetail Overlay in Movies                         |
...
```

These `-Dovetail` variations are used when resolution and edition are combined so that one "dovetails" into the other.
This is not something you can enable or disable independently; it's an internal implementation detail.

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "resolution", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode|season' 
%}
    ```yaml
    libraries:
      4K Movies: #(5)!
        overlay_files:
          - default: resolution
            template_variables:
              use_dvhdrplus: false #(1)!
              use_dv: false #(2)!
              use_hdr: false #(3)!
              use_1080p: false #(4)!
              use_720p: false #(4)!
              use_576p: false #(4)!
              use_480p: false #(4)!
    ```

    1.  Stops the DV/HDR10+ overlay applying, regardless of resolution
    2.  Stops the DV overlay applying, regardless of resolution
    3.  Stops the HDR overlay applying, regardless of resolution
    4.  Stops this resolution overlay applying
    5.  Assuming that this library only contains 4K Movies, we will want to disable all non-4K overlays from processing to increase performance


        overlay_files:
          - default: status
            template_variables:
              text_canceled: "C A N C E L L E D"
              text_canceled: "C A N C E L L E D" #(1)!
    ```

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`15`",
        "HORIZONTAL_ALIGN": "`left`",
        "VERTICAL_OFFSET": "`15`",
        "VERTICAL_ALIGN": "`top`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`105`/`189`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="resolution-overlay|builder_level|weight"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Resolution/Edition Overlays"
    
        The Resolution/Edition overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) on resolutions and editions as set on items in Plex.
