---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Common Sense Age Rating", 
        "CODE_NAME": "audio_codec",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay based on the Common Sense Age Rating on each item within your library"
    }'
    replace-tags='{"rec-sub": "Requirements: Use the [Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with either `mdb_commonsense` or `mdb_commonsense0` to update Plex to the Common Sense Rating."}'
    end='<!--table-before-->'
%}

| Rating | Key  |
|:-------|:-----|
| 1+     | `1`  |
| 2+     | `2`  |
| 3+     | `3`  |
| 4+     | `4`  |
| 5+     | `5`  |
| 6+     | `6`  |
| 7+     | `7`  |
| 8+     | `8`  |
| 9+     | `9`  |
| 10+    | `10` |
| 11+    | `11` |
| 12+    | `12` |
| 13+    | `13` |
| 14+    | `14` |
| 15+    | `15` |
| 16+    | `16` |
| 17+    | `17` |
| 18+    | `18` |
| NR     | `nr` |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "commonsense", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode|season' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: commonsense
            template_variables:
              pre_text: "Age " #(1)!
    ```

    1.  Wlll prepend "CS" to the text of the overlays, for example "Age 1"

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`15`",
        "HORIZONTAL_ALIGN": "`left`",
        "VERTICAL_OFFSET": "`270`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="commonsense-overlay|addon_image|builder_level"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Common Sense Age Rating Overlays"
    
        The Common Sense Age Rating overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) with [filters](../../../files/filters) on a set of content ratings and map them into a single content rating as requested.
