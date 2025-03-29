---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "US Movie Content Rating", 
        "CODE_NAME": "content_rating_us_movie",
        "OVERLAY_LEVEL": "Movie",
        "DESCRIPTION": "an overlay based on the MPAA Age Rating on each item within your library"
    }'
    replace-tags='{"rec-sub": "Requirements: Use the [Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with either `mdb` or `omdb` to update Plex to the MPAA Age Rating."}'
    end='<!--table-before-->'
%}

| Rating | Key     |
|:-------|:--------|
| G      | `g`     |
| PG     | `pg`    |
| PG-13  | `pg-13` |
| R      | `r`     |
| NC-17  | `nc-17` |
| NR     | `nr`    |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "content_rating_us_movie", "collection_files": "overlay_files"}' 
    include-tags='all|movie' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: content_rating_us_movie
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
        include-tags="addon_image|color"
        rewrite-relative-urls=false
    %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "US Movie Content Rating Overlays"
    
        The US Movie Content Rating overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) with [filters](../../../files/filters) on a set of content ratings and map them into a single content rating as requested.
