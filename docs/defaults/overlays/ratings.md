---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Ratings", 
        "CODE_NAME": "ratings",
        "OVERLAY_LEVEL": "Movie, Show, Episode",
        "DESCRIPTION": "an overlay based on the Critic Rating, Audience Rating, and User Rating in Plex for each item within your library.

This file only updates the overlays based on the data in Plex, it will not pull the ratings directly from any third-party website, see recommendations below for more info"
    }'
%}

!!! warning "IMPORTANT CHANGES TO RATINGS IN KOMETA 2.2.3"

    A new way to apply Ratings overlays has been released as part of Kometa 2.2.3,

    This new system allows the rating to be applied to posters without having to first run Operations to override Plex's in-built ratings slots.

    This is an opt-in feature, any existing configs will continue to work.


{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "ratings", "collection_files": "overlay_files", "collections:": "overlays:"}' 
    include-tags='all|ratings|movie|show|episode' 
%}
    ```yaml
      Movies:
        overlay_files:
          - default: ratings
            template_variables:
              rating1: critic
              rating2: audience
              rating3: user
      TV Shows:
        overlay_files:
          - default: ratings
            template_variables:
              builder_level: episode
              rating1: critic
              rating2: audience
    ```

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back|back_padding|back_radius'
    replace='{
        "HORIZONTAL_OFFSET": "`30`",
        "HORIZONTAL_ALIGN": "`left`",
        "VERTICAL_OFFSET": "`0`",
        "VERTICAL_ALIGN": "`center`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`160`",
        "BACK_HEIGHT": "`160`",
        "BACK_PADDING": "`15`",
        "BACK_RADIUS": "`30`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="ratings-overlay|addon_image|builder_level"
        rewrite-relative-urls=false
        replace='{
            "`left`<br>": "`top`<br>",
            "`season` or ": ""
        }'
    %}

    {% include-markdown "./../../templates/variable_list.md"
       include-tags="sup1"
       rewrite-relative-urls=false
    %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" replace='{"CODE_NAME": "ratings"}'
    replace-tags='{
        "title-sub": "These variables can be prepended with `rating1_`, `rating2_`, or `rating3_` to change that attribute on each rating individually.",
        "notes-sub": "**IMPORTANT**: To amend `horizontal_offset` and `vertical_offset` you **must** prepend the variable with `rating1_`, `rating2_`, or `rating3_`."
    }'
%}

{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Ratings Overlays"
    
        The Ratings overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) on ratings as set on items in Plex.
