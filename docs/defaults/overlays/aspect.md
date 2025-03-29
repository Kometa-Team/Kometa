---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Aspect", 
        "CODE_NAME": "aspect",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay on a show/movie detailing its aspect ratio"
    }'
%}
| 1.33 | `1.33` | `80` |
| 1.65 | `1.65` | `70` |
| 1.66 | `1.66` | `60` |
| 1.78 | `1.78` | `50` |
| 1.85 | `1.85` | `40` |
| 2.2  | `2.2`  | `30` |
| 2.35 | `2.35` | `20` |
| 2.77 | `2.77` | `10` |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "aspect", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode|season' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: aspect
            template_variables:
              text_1.33: "4:9" #(1)!
              text_1.77: "16:9" #(2)!
      TV Shows:
        overlay_files:
          - default: aspect
            template_variables:
              text_1.33: "4:9" #(1)!
              text_1.77: "16:9" #(2)!
          - default: aspect
            template_variables:
              overlay_level: episode #(3)!
              text_1.33: "4:9" #(1)!
              text_1.77: "16:9" #(2)!
          - default: aspect
            template_variables:
              overlay_level: season #(4)!
              text_1.33: "4:9" #(1)!
              text_1.77: "16:9" #(2)!
    ```

    1.  Changes the text for the 1.33 overlay to "4:9"
    2.  Changes the text for the 1.77 overlay to "16:9"
    3.  Applies the overlay to episodes
    4.  Applies the overlay to seasons

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    replace='{
        "HORIZONTAL_OFFSET": "`150`",
        "HORIZONTAL_ALIGN": "`center`",
        "VERTICAL_OFFSET": "`0`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="aspect-overlay|weight"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Aspect Overlays"
    
        The Aspect overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) with [filters](../../../files/filters) on a limited set of aspect ratios.
