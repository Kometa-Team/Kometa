---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Runtimes", 
        "CODE_NAME": "runtimes",
        "OVERLAY_LEVEL": "Movie, Show, Episode",
        "DESCRIPTION": "an overlay of the movie runtime, episode runtime, or average episode runtime for all items in your library"
    }'
    end='<!--rec-sub-->'
%}

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "runtimes", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show|episode' 
%}
    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - default: runtimes
            template_variables:
              builder_level: episode #(1)!
              vertical_align: top #(2)!
    ```

    1.  Applies the overlay to episodes
    2.  Moves the overlay to the top of the image

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    replace='{
        "HORIZONTAL_OFFSET": "`15`",
        "HORIZONTAL_ALIGN": "`right`",
        "VERTICAL_OFFSET": "`30`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`600`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="runtimes-overlay"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md"
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Runtimes Overlays"
    
        The Runtimes overlays use the [`plex_all` Builder](../../../files/builders/plex#plex-all) to apply to all items in the library.
