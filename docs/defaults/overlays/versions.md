---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Versions", 
        "CODE_NAME": "versions",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay based on if there\'s multiple versions on each item within your library"
    }'
    end='<!--rec-sub-->'
%}

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "versions", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode|season' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: versions
            template_variables:
              back_color: "#FFFFFF99" #(1)!
    ```

    1.  Sets the text to use a white color (#FFFFFF) at 99 opacity

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`15`/`235`",
        "HORIZONTAL_ALIGN": "`right`/`center`",
        "VERTICAL_OFFSET": "`1050`/`15`",
        "VERTICAL_ALIGN": "`top`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`105`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="builder_level"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Versions Overlays"
    
        The Versions overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) for duplicate items or episodes.
