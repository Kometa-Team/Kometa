---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Episode Info", 
        "CODE_NAME": "episode_info",
        "OVERLAY_LEVEL": "Episode",
        "DESCRIPTION": "an overlay on the episode title card on the episode numbering within a given series in your library"
    }'
    end='<!--rec-sub-->'
%}
{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "episode_info", "collection_files": "overlay_files"}' 
    include-tags='all|episode' 
%}
    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - default: episode_info
            template_variables:
              font_color: "#FFFFFF99" #(1)!
    ```

    1.  Sets the text to use a white color (#FFFFFF) at 99 opacity

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='file-vars'
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
    end='<!--file-header-->'
%}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Episode Info Overlays"
    
        The Episode Info overlays use the [`plex_all` Builder](../../../files/builders/plex#plex-all) to apply to every episode in the library.
