---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Video Format", 
        "CODE_NAME": "video_format",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay based on the video format available on each item within your library"
    }'
    replace-tags='{"rec-sub": "Recommendations: Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme."}'
%}
| REMUX    | `remux`    | `60` |
| BLU-RAY  | `bluray`   | `50` |
| WEB      | `web`      | `40` |
| HDTV     | `hdtv`     | `30` |
| DVD      | `dvd`      | `20` |
| SDTV     | `sdtv`     | `10` |
| TELESYNC | `telesync` | `9`  |
| CAM      | `cam`      | `8`  |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "video_format", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode|season' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: video_format
            template_variables:
              text_bluray: BLURAY #(1)1
              use_sdtv: false #(2)!
              use_dvd: false #(3)!
    ```

    1.  Changes the text from "BLU-RAY" to "BLURAY"
    2.  Stops the "SDTV" overlay from applying
    3.  Stops the "DVD" ovelay from applying

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    replace='{
        "HORIZONTAL_OFFSET": "`15`",
        "HORIZONTAL_ALIGN": "`left`",
        "VERTICAL_OFFSET": "`30`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="video_format-overlay|builder_level|regex|weight"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Video Format Overlays"
    
        The Video Format overlays use the [`plex_all` Builder](../../../files/builders/plex#plex-all) with [filters](../../../files/filters) on filepath.
