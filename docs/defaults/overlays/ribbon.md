---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/overlays/header.md"
    replace='{
        "OVERLAY_NAME": "Ribbon", 
        "CODE_NAME": "ribbon",
        "OVERLAY_LEVEL": "Movie, Show",
        "DESCRIPTION": "a ribbon overlay based on the Top Lists of various sites on each item within your library"
    }'
%}
| Oscars Best Picture             | `oscars`          | `190`  |
| Oscars Best Director            | `oscars_director` | `180`  |
| Golden Globe Winner             | `golden`          | `170`  |
| Golden Globe Director           | `golden_director` | `160`  |
| BAFTA Winner                    | `bafta`           | `150`  |
| Cannes Winner                   | `cannes`          | `140`  |
| Berlinale Winner                | `berlinale`       | `130`  |
| Venice Winner                   | `venice`          | `120`  |
| Sundance Winner                 | `sundance`        | `110`  |
| Emmys Winner                    | `emmys`           | `100`  |
| Critic's Choice Winner          | `choice`          | `90`   |
| Independent Spirit Award Winner | `spirit`          | `80`   |
| César Winner                    | `cesar`           | `70`   |
| IMDb Top 250                    | `imdb`            | `60`   |
| Letterboxd Top 250              | `letterboxd`      | `50`   |
| Rotten Tomatoes Verified Hot    | `rottenverified`  | `45`   |
| Rotten Tomatoes Certified Fresh | `rotten`          | `40`   |
| Metacritic Must See             | `metacritic`      | `30`   |
| Common Sense Selection          | `common`          | `20`   |
| Razzies Winner                  | `razzie`          | `10`   |

{% 
    include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "ribbon", "collection_files": "overlay_files"}' 
    include-tags='all|movie|show' 
%}

    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: ribbon
            template_variables:
              style: black #(1)!
              weight_IMDB: 200 #(2)!
              use_common: false #(3)!
    ```

    1.  Changes the ribbon color to black
    2.  Gives the `imdb` key the highest weight, meaning this ribbon image will always be chosen over other ribbons.
    3.  Disables the "Common Sense Selection" overlay

{% 
    include-markdown "./../../templates/defaults/base/overlays/variables_header.md"
    include-tags='all'
    exclude-tags='text-vars'
    replace='{
        "HORIZONTAL_OFFSET": "`0`",
        "HORIZONTAL_ALIGN": "`right`",
        "VERTICAL_OFFSET": "`0`",
        "VERTICAL_ALIGN": "`bottom`"
    }'
%}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="ribbon-overlay|weight"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/overlays/shared.md" end="<!--text-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Ribbon Overlays"
    
        The Ribbon overlays use the [`imdb_award` Builder](../../../files/builders/imdb#imdb-award), [`imdb_chart` Builder](../../../files/builders/imdb#imdb-chart), 
        [`mdblist_list` Builder](../../../files/builders/mdblist#mdblist-list), 
