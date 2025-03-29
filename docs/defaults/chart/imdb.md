---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "IMDb Charts", 
        "CODE_NAME": "imdb",
        "LIBRARY_TYPE": "Movie, Show", 
        "DESCRIPTION": "create collections based on IMDb charts",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": "Recommendations: The `IMDb Lowest Rated` Collection only works with Movie Libraries."}'
%}
| `IMDb Lowest Rated` | `lowest`  | Collection of the lowest Rated Movies on IMDb.       |
| `IMDb Popular`      | `popular` | Collection of the most Popular Movies/Shows on IMDb. |
| `IMDb Top 250`      | `top`     | Collection of Top 250 Movies/Shows on IMDb.          |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "imdb"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "imdb"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: imdb
            template_variables:
              use_lowest: false #(1)!
              visible_library_top: true #(2)!
              visible_home_top: true #(3)!
              visible_shared_top: true #(4)!
    ```

    1. Do not create the "IMDb Lowest Rated" collection
    2. Pin the "IMDB Top 250" collection to the Recommended tab of the library
    3. Pin the "IMDB Top 250" collection to the home screen of the server owner
    4. Pin the "IMDB Top 250" collection to the home screen of other users of the server

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="white-style|sync_mode|collection_order"
        rewrite-relative-urls=false
        replace='{"COLLECTION_ORDER": "`custom`"}'
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "IMDb Chart Collections"
        
        The IMDb Chart collections use the [`imdb_chart` IMDb Builder](../../../files/builders/imdb#imdb-chart) to create the collections.
