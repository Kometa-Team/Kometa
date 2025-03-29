---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "DE Content Rating", 
        "CODE_NAME": "content_rating_de",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay based on the FSK Rating on each item within your library"
    }'
    replace-tags='{"rec-sub": "Requirements: Use the [Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with either `mdb` or `omdb` to update Plex to the FSK Rating."}'
    end='<!--table-before-->'
%}

| Rating | Key    |
|:-------|:-------|
| 0      | `0`    |
| 6      | `6`    |
| 12     | `12`   |
| 16     | `16`   |
| 18     | `18`   |
| BPjM   | `bpjm` |
| NR     | `nr`   |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "content_rating_de", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode|season' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: content_rating_de
            template_variables:
              color: false #(1)!
    ```

    1.  Will set a white variant of the overlay images

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
        include-tags="addon_image|builder_level|color"
        rewrite-relative-urls=false
    %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "DE Content Rating Overlays"
    
        The DE Content Rating overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) with [filters](../../../files/filters) on a set of content ratings and map them into a single content rating as requested.
