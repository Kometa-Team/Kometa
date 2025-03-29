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
    replace-tags='{"title-sub": "**Please read [Kometa Ratings Explained](../../kometa/guides/ratings.md) for more understanding on how Kometa interacts with ratings.**"}'
    end='<!--rec-sub-->'
%}

Requirements: Template Variables must be configured, otherwise this file will not apply any overlays.

Recommendations: Use the [Mass * Rating Update Library Operation](../../config/operations.md#mass-rating-update) and the
[Mass Episode * Rating Update Library Operation](../../config/operations.md#mass-episode-rating-update) to update Plex to the Ratings you want on the Overlay.

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "network", "collection_files": "overlay_files"}' 
    include-tags='all|ratings|movie|show|episode' 
%}
    ```yaml
      Movies:
        overlay_files:
          - default: ratings
            template_variables:
              rating1: critic #(1)!
              rating1_image: imdb #(2)!
              rating2: audience #(3)!
              rating2_image: rt_popcorn #(4)!
              rating3: user #(5)!
              rating3_image: tmdb #(6)!
              horizontal_position: right #(7)!
        operations: #(8)!
          mass_critic_rating_update: imdb
          mass_audience_rating_update: mdb_tomatoesaudience
          mass_user_rating_update: tmdb
      TV Shows:
        overlay_files:
          - default: ratings
            template_variables:
              rating1: critic #(1)!
              rating1_image: imdb #(2)!
              rating2: audience #(3)!
              rating2_image: rt_popcorn #(4)!
              rating3: user #(5)!
              rating3_image: tmdb #(6)!
              horizontal_position: right #(7)!
          - default: ratings
            template_variables:
              builder_level: episode
              rating1: critic #(1)!
              rating1_image: imdb #(2)!
              rating2: audience #(3)!
              rating2_image: tmdb #(9)!
              horizontal_position: right #(7)!
        operations: #(8)!
          mass_critic_rating_update: imdb
          mass_audience_rating_update: mdb_tomatoesaudience
          mass_user_rating_update: tmdb
          mass_episode_critic_rating_update: imdb
          mass_episode_audience_rating_update: tmdb
    ```

    1.  In the first slot on the overlay, insert the value of the `critic` rating
    2.  In the first slot on the overlay, use the `imdb` image
    3.  In the second slot on the overlay, insert the value of the `audience` rating
    4.  In the second slot on the overlay, use the `rt_popcorn` image
    5.  In the third slot on the overlay, insert the value of the `user` rating
    6.  In the third slot on the overlay, use the `tmdb` image
    7.  Place the rating value to the right of the image
    8.  Operations are used to force ratings from third-party services into the Plex ratings slots.
    9.  In the second slot on the overlay, use the `tmdb` image

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

{% 
    include-markdown "./../../templates/defaults/base/overlays/shared.md"
    replace-tags='{
        "title-sub": "These variables can be prepended with `rating1_`, `rating2_`, or `rating3_` to change that attribute on each rating individually.",
        "notes-sub": "**IMPORTANT**: To amend `horizontal_offset` and `vertical_offset` you **must** prepend the variable with `rating1_`, `rating2_`, or `rating3_`."
    }'
%}

{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Ratings Overlays"
    
        The Ratings overlays use the [`plex_search` Builder](../../../files/builders/plex#plex-search) on ratings as set on items in Plex.
