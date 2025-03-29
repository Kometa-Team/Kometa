---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Audio/Subtitle Language Count", 
        "CODE_NAME": "language_count",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay based on the number of audio/subtitle languages available on each item within your library"
    }'
%}
| Dual  | `dual`  | `20` |
| Multi | `multi` | `10` |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "language_count", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode|season' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: language_count
            template_variables:
              use_subtitles: true #(1)!
    ```

    1.  Display dual/multi subtitle images rather than audio languages

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`0`",
        "HORIZONTAL_ALIGN": "`center`",
        "VERTICAL_OFFSET": "`30`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`188`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="builder_level|language_count-overlay|weight"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Audio/Subtitle Language Count Overlays"
    
        The Audio/Subtitle Language Count overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) for items with any number or <3 audio tracks.
