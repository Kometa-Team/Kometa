---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Streaming Service", 
        "CODE_NAME": "streaming",
        "OVERLAY_LEVEL": "Movie, Show",
        "DESCRIPTION": "an overlay based on the streaming service the file is found on for each item within your library"
    }'
%}
| Netflix     | `netflix`     | `160` |
| Prime Video | `amazon`      | `150` |
| Disney+     | `disney`      | `140` |
| Max         | `max`         | `130` |
| Crunchyroll | `Crunchyroll` | `120` |
| YouTube     | `youtube`     | `110` |
| Hulu        | `hulu`        | `100` |
| Paramount+  | `paramount`   | `90`  |
| AppleTV     | `appletv`     | `80`  |
| Peacock     | `peacock`     | `70`  |
| discovery+  | `discovery`   | `58`  |
| Crave       | `crave`       | `55`  |
| NOW         | `now`         | `50`  |
| Channel 4   | `channel4`    | `40`  |
| ITVX        | `itvx`        | `30`  |
| BET+        | `bet`         | `20`  |
| hayu        | `hayu`        | `10`  |

## Regional Variants

Some logic is applied to allow for regional streaming service lists to be available to users depending on where they are, as detailed below:

| Region           | Key                               | Description                                                                                                                         |
|:-----------------|:----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| any besides `GB` | `channel4`, `itvx`, `hayu`, `now` | These overlays will not be used if the region is not `uk` as these streaming services are UK-focused                                |
| any besides `CA` | `crave`                           | These overlays will not be used if the region is not `ca` as these streaming services are Canada-focused                            |
| `CA`             | `max`, `showtime`                 | These overlays will not be used if the region is `ca` as these streaming services are part of the Crave streaming service in Canada |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "streaming", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show' 
%}
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: streaming
            template_variables:
              originals_only: true #(1)!
              use_disney: false #(2)!
              weight_amazon: 170 #(3)!
    ```

    1.  Applies the overlay only to items which are "original" to the streaming service, rather than anything streaming on the service.
    2.  Stops the "Disney+" overlay from applying
    3.  Increases the weight of the "Amazon" overlay, meaning it will take priority over any other streaming overlay

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all|back'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`15`",
        "HORIZONTAL_ALIGN": "`left`",
        "VERTICAL_OFFSET": "`390`",
        "VERTICAL_ALIGN": "`bottom`",
        "BACK_COLOR": "`#00000099`",
        "BACK_RADIUS": "`30`",
        "BACK_WIDTH": "`305`",
        "BACK_HEIGHT": "`105`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="streaming-overlay|weight|overlay-white-style"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Streaming Overlays"
    
        The Streaming Services overlays use two builders:

        If you are not using `originals_only`, the overlays are applied using [`tmdb_discover`](../../../files/builders/tmdb#tmdb-discover).
        
        If you are using `originals_only`, the overlays are applied using Kometa-maintained [MDBLists](../../../files/builders/mdblist#mdblist-list).
