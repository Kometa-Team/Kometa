---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Audio Codec", 
        "CODE_NAME": "audio_codec",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay based on the audio codec available on each item within your library"
    }'
    replace-tags='{"rec-sub": "Recommendations: Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme."}'
%}
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

??? warning

    These overlays are based on the file name, assuming TRaSH naming, and the **titles** of the audio tracks found in the file.  This YAML file looks for text patterns in those two strings and bases the decision on "does this file qualify for this overlay" on those tests.  **NOTABLY**, Kometa does not examine the **format** or **codec** of any audio track.  If, for example, you have an audio track in the Opus format which is named "Dolby TrueHD", Kometa sees that as a "Dolby TrueHD" track.

    Further, Kometa looks at **all** the audio tracks in the file, not just the one that might be "default" or "primary".
    
    If you are seeing unexpected results, verify that the names of either or both the files and audio tracks accurately reflect their contents, and double-check the weights on the overlays.

{% include-markdown "./../../templates/snippets/standard_style.md" replace='{"CODE_NAME": "audio_codec"}' %}
{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "audio_codec", "collection_files": "overlay_files", "collections:": "overlays:"}' 
    include-tags='all|movie|show|episode|season' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: audio_codec
            template_variables:
              use_opus: false #(1)!
              use_mp3: false #(1)!
              style: standard #(2)!
    ```

    1.  This overlay will no be included and no items will receive this overlay
    2.  Sets to style to "standard"

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`0`",
        "HORIZONTAL_ALIGN": "`center`",
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
        include-tags="builder_level|regex|style|weight"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" replace='{"CODE_NAME": "audio_codec"}' %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Audio Codec Overlays"
    
        The Audio Codec overlays use the [`plex_all` Builder](../../../files/builders/plex#plex-all) with [filters](../../../files/filters) on both audio channel name and filepath.
