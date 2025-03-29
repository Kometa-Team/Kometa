<!--all-->
{%
    include-markdown "./base/collection/header.md"
    replace='{
        "SECTION_NUMBER": "130",
        "COLLECTION": "FULL_NAME Awards",
        "DESCRIPTION": "create collections based on the FULL_NAME Awards"
    }'
%}
<!--all-->
<!--bafta-->
| `BAFTA Best Films` | `best` | Collection of British Academy of Film and Television Arts Best Film Award Winners. |
<!--bafta-->
<!--berlinale-->
| `Berlinale Golden Bears` | `golden` | Collection of Berlin International Film Festival Golden Bear Award Winners. |
<!--berlinale-->
<!--cannes-->
| `Cannes Golden Palm Winners` | `palm` | Collection of Cannes Golden Palm Award Winners. |
<!--cannes-->
<!--cesar-->
| `César Best Film Winners` | `best` | Collection of César Award Winners. |
<!--cesar-->
<!--choice-->
| `Critics Choice Best Picture Winners` | `best` | Collection of Critics Choice Best Feature Award Winners |
<!--choice-->
<!--emmy-->
| `Emmys Best in Category Winners` | `best` | Collection of Emmys Best in Category Award Winners. |
<!--emmy-->
<!--golden-->
| `Golden Globes Best Picture Winners`  | `best_picture`  | Collection of Golden Globe Best Picture Award Winners.  |
| `Golden Globes Best Director Winners` | `best_director` | Collection of Golden Globe Best Director Award Winners. |
<!--golden-->
<!--nfr-->
| `National Film Registry All Time` | `all_time` | Collection of Films added to the National Film Registry. |
<!--nfr-->
<!--oscars-->
| `Oscars Best Picture Winners`  | `best_picture`  | Collection of Oscars Best Picture Award Winners.  |
| `Oscars Best Director Winners` | `best_director` | Collection of Oscars Best Director Award Winners. |
<!--oscars-->
<!--pca-->
| `People's Choice Award Winners` | `pca` | Collection of People's Choice Award Winners. |
<!--pca-->
<!--razzie-->
| `Razzies Golden Raspberry Winners` | `golden` | Collection of Razzie Golden Raspberry Award Winners. |
<!--razzie-->
<!--sag-->
| `Screen Actors Guild Award Winners` | `golden` | Collection of Screen Actors Guild Award Winners. |
<!--sag-->
<!--spirit-->
| `Independent Spirit Best Feature Winners` | `best` | Collection of Independent Spirit Best Feature Award Winners. |
<!--spirit-->
<!--sundance-->
| `Sundance Grand Jury Winners` | `grand` | Collection of Sundance Film Festival Grand Jury Award Winners. |
<!--sundance-->
<!--tiff-->
| `Toronto People's Choice Award Winners` | `best` | Collection of Toronto International Film Festival People's Choice Award Winners. |
<!--tiff-->
<!--venice-->
| `Venice Golden Lions` | `golden` | Collection of Venice Film Festival Golden Lions Award Winners. |
<!--venice-->
<!--all-->
| `SHORT_NAME <<year>>`<br>**Example:** `SHORT_NAME 2022` | `<<year>>`<br>**Example:** `2022` | Collection of FULL_NAME Award Winners for the given year. |

{% include-markdown "./base/mid.md" include-tags='all|TYPES' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: CODE_NAME
            template_variables:
              collection_mode: show_items #(1)!
              collection_order: alpha #(2)!
              radarr_add_missing: true #(3)!
              name_format: SHORT_NAME <<key_name>> Winners #(4)!
              data: #(5)!
                starting: latest-10
                ending: latest
    ```

    1. Shows the collection and all of its items within the Library tab in Plex.
    2. Sorts the collection items alphabetically.
    3. Adds items from the source list which are not in Plex to Radarr.
    4. Change the name of the collections to "SHORT_NAME yearhere Winners".
    5. Creates collections from 10 award shows back to the latest award show.

{% include-markdown "./base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../variable_list.md"
        include-tags="award|award-data|exclude|collection_mode|sync_mode|format"
        replace='{
            "DYNAMIC_NAME": "Years", 
            "DYNAMIC_VALUE": "Years",
            "NAME_FORMAT": "SHORT_NAME <<key_name>>",
            "SUMMARY_FORMAT": "<<key_name>> SHORT_NAME Award Winners."
        }'
        rewrite-relative-urls=false
    %}
    
    {% include-markdown "./../variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./base/values.md" rewrite-relative-urls=false %}

    === "FULL_NAME Awards Collections"
        
        All the FULL_NAME Awards Collections use the [IMDb Awards Builder](../../../files/builders/imdb) to create the collections.

<!--all-->