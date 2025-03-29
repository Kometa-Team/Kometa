---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "MediaStinger", 
        "CODE_NAME": "mediastinger",
        "OVERLAY_LEVEL": "Movie",
        "DESCRIPTION": "an overlay based on if there\'s an after/during credit scene on each movie within your library"
    }'
    end='<!--rec-sub-->'
%}
{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "mediastinger", "collection_files": "overlay_files"}' 
    include-tags='all|movie' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: mediastinger
            template_variables:
              font_color: "#FFFFFF99" #(1)!
    ```

    1.  Sets the text to use a white color (#FFFFFF) at 99 opacity

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='file-vars|text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`200`",
        "HORIZONTAL_ALIGN": "`right`",
        "VERTICAL_OFFSET": "`215`",
        "VERTICAL_ALIGN": "`top`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`105`",
        "BACK_HEIGHT": "`105`"
    }'
    end='<!--file-header-->'
%}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "MediaStinger Overlays"
    
        The MediaStinger overlays use the [`plex_all` Builder](../../../files/builders/plex#plex-all) with [filters](../../../files/filters) on `tmdb_keyword: aftercreditsstinger, duringcreditsstinger`.
