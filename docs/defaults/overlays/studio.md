---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Studio", 
        "CODE_NAME": "studio",
        "OVERLAY_LEVEL": "Movie, Show",
        "DESCRIPTION": "an overlay based on the show studio on each item within your library"
    }'
    end='<!--rec-sub-->'
%}

### Bigger Style

Below is a screenshot of the alternative Bigger (`bigger`) style which can be set via the `style` Template Variable.

![studio_bigger](../../assets/images/defaults/overlays/studio_bigger.jpg)

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "studio", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: studio
            template_variables:
              vertical_offset: 390 #(1)!
      TV Shows:
        overlay_files:
          - default: studio
          - default: studio
            template_variables:
              builder_level: season #(2)!
              vertical_align: bottom  #(3)!
              vertical_offset: 15  #(1)!
              horizontal_align: left  #(4)!
              horizontal_offset: 15  #(1)!
              style: bigger  #(5)!
          - default: studio
            template_variables:
              builder_level: episode  #(6)!
              vertical_align: top  #(7)!
              vertical_offset: 15 #(1)!
    ```

    1.  Changes the offset of the overlay
    2.  Applies the overlay to seasons
    3.  Moves the overlay position to the bottom
    4.  Moves the overlay position to the left
    5.  Uses the bigger style overlay images
    6.  Applies the overlay to episodes
    7.  Moves the overlay position to the top

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`15`",
        "HORIZONTAL_ALIGN": "`left`",
        "VERTICAL_OFFSET": "`150`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="studio-overlay|builder_level"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Studio Overlays"
    
        The Studio overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) on studio names. 
        The list of studio is not exposed for customization using Template Variables.
