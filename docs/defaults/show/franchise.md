---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Franchise", 
        "CODE_NAME": "franchise",
        "DESCRIPTION": "dynamically create collections based on popular TV Show franchises",
        "LIBRARY_TYPE": "Movie", 
        "Section SECTION_NUMBER": ""
    }'
    replace-tags='{
        "title-sub": "Unlike most Default Collection Files, Franchise works by placing collections inline with the main library items if your library allows it. 
For example, the \"Pretty Little Liars\" franchise collection will appear next to the \"Pretty Little Liars\" show in your library.

**[This file has a Movie Library Counterpart.](./../../../../movie/franchise)**",
        "image": "![](./../../../../assets/images/defaults/posters/franchise_show.png)"
    }'
%}
| `<<Collection Name>>`<br>**Example:** `Pretty Little Liars` | `<<Starting TMDb Show ID>>`<br>**Example:** `31917` | Collection of Shows specified for this Collection. |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "franchise"}' include-tags='all|show' %}
    ```yaml
    libraries:
      TV Shows:
        collection_files:
          - default: franchise
            template_variables:
              append_data:
                "31917": Pretty Little Liars #(1)!
              append_addons:
                31917: [46958, 79863, 110531] #(2)!
              sonarr_add_missing: true #(3)!
    ```

    1. Add [TMDb Show 31917](https://www.themoviedb.org/tv/31917-pretty-little-liars) to the data dictionary
    2. Add TMDb Shows [46958](https://www.themoviedb.org/tv/46958), [79863](https://www.themoviedb.org/tv/79863) and [110531](https://www.themoviedb.org/tv/110531) as 
        addons of [TMDb Show 31917](https://www.themoviedb.org/tv/31917-pretty-little-liars) so that they appear in the same collection
    3. Add items missing from your library in Plex to Sonarr

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" end="<!--file-->" %}
{% include-markdown "./../../templates/snippets/no_shared_variables.md" %}
{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" start="<!--file-header-->" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="show-franchise|arr|sync_mode|collection_mode|collection_order"
        replace='{
            "DYNAMIC_NAME": "TMDb Collections", 
            "DYNAMIC_VALUE": "TMDb Show IDs",
            "COLLECTION_ORDER": "`release`",
            "ARR_CODE": "sonarr",
            "ARR_NAME": "Sonarr",
            "ARR_TYPE": "show"
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Franchise Collections"
        
        The Continents collections use the [dynamic collections](../../../files/dynamic) system with a default list of target franchises and some default addons to group shows and movies into those franchises.

    === "Default `data`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        data: 
    {%    
      include-markdown "../../../defaults/show/franchise.yml" 
      comments=false
      start="data:\n"
      end="template:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/show/franchise.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
