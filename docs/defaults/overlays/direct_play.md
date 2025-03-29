---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Direct Play", 
        "CODE_NAME": "direct_play",
        "OVERLAY_LEVEL": "Movie, Show, Season, Episode",
        "DESCRIPTION": "an overlay to indicate items that cannot be transcoded and instead only support Direct Play (i.e. if you use Tautulli to kill 4K transcoding)"
    }'
    end='<!--rec-sub-->'
%}
{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "direct_play", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode' 
%}
    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - default: direct_play
            template_variables:
              builder_level: episode #(1)!
    ```

    1.  Applies the overlay to episodes

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    replace='{
        "HORIZONTAL_OFFSET": "`0`",
        "HORIZONTAL_ALIGN": "`center`",
        "VERTICAL_OFFSET": "`150`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`170`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="builder_level"
        rewrite-relative-urls=false
    %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Direct Play Overlays"
    
        The Direct Play overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) for 4K items.
