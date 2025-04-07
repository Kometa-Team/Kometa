---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Network", 
        "CODE_NAME": "network",
        "OVERLAY_LEVEL": "Show, Season, Episode",
        "DESCRIPTION": "an overlay based on the show network on each item within your library"
    }'
    end='<!--rec-sub-->'
%}
{% include-markdown "./../../templates/snippets/white_style.md" replace='{"styles/CODE_NAME": "overlays/network"}' exclude-tags='logo' %}
{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "network", "collection_files": "overlay_files"}' 
    include-tags='all|show|episode|season' 
%}
    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - default: network
            template_variables:
              style: white #(1)!
              vertical_offset: 390 #(2)!
          - default: network
            template_variables:
              vertical_offset: 390 #(2)!
              builder_level: season #(3)!
          - default: network
            template_variables:
              vertical_offset: 390 #(2)!
              builder_level: episode #(4)!
    ```

    1.  Will set a white variant of the overlay images
    2.  Sets a custom offset for the overlay
    3.  Applies the overlay to episodes
    4.  Applies the overlay to seasons

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`15`",
        "HORIZONTAL_ALIGN": "`left`",
        "VERTICAL_OFFSET": "`510`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="overlay-white-style"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Network Overlays"
    
        The Network overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) on network name. 
        The list of networks is not exposed for customization using Template Variables.
