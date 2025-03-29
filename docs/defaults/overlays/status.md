---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAMEs": "Status",
        "OVERLAY_NAME": "Status",
        "CODE_NAME": "status",
        "OVERLAY_LEVEL": "Show",
        "DESCRIPTION": "an overlay on a show detailing its Current Airing Status for all shows in your library"
    }'
%}
| AIRING    | `airing`    | `40`   |
| RETURNING | `returning` | `30`   |
| CANCELED  | `canceled`  | `20`   |
| ENDED     | `ended`     | `10`   |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "status", "collection_files": "overlay_files"}' 
    include-tags='all|show'
%}
    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - default: status
            template_variables:
              text_canceled: "C A N C E L L E D" #(1)!
    ```

    1.  Changes the text for the canceled overlay to "C A N C E L L E D"



{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    replace='{
        "HORIZONTAL_OFFSET": "`15`",
        "HORIZONTAL_ALIGN": "`left`",
        "VERTICAL_OFFSET": "`330`",
        "VERTICAL_ALIGN": "`top`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="status-overlay|weight"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Status Overlays"
    
        The Status overlays use the [`plex_all` Builder](../../../files/builders/plex#plex-all) with [filters](../../../files/filters) on `tmdb_status`.
