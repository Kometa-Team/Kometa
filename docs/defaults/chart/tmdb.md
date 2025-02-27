---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "TMDb Chart", 
        "CODE_NAME": "tmdb",
        "LIBRARY_TYPE": "Movie, Show", 
        "DESCRIPTION": "create collections based on TMDb charts",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": "Recommendations: The `TMDb Airing Today` and `TMDb On The Air` Collections only work with Show Libraries."}'
%}
| `TMDb Airing Today` | `airing`   | Collection of Shows Airing Today on TMDb.            |
| `TMDb On The Air`   | `air`      | Collection of Shows currently On The Air on TMDb.    |
| `TMDb Popular`      | `popular`  | Collection of the Most Popular Movies/Shows on TMDb. |
| `TMDb Top Rated`    | `top`      | Collection of the Top Rated Movies/Shows on TMDb.    |
| `TMDb Trending`     | `trending` | Collection of Trending Movies/Shows on TMDb.         |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "tmdb"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "tmdb"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: tmdb
            template_variables:
              use_trending: false #(1)!
              limit_popular: 20 #(2)!
              visible_library_popular: true #(3)!
              visible_home_popular: true #(4)!
              visible_shared_popular: true #(5)!
    ```

    1. Do not create the "TMDb Trending" collection
    2. Change "TMDb Popular" to have a maximum of 20 items
    3. Pin the "TMDb Popular" collection to the Recommended tab of the library
    4. Pin the "TMDb Popular" collection to the home screen of the server owner
    5. Pin the "TMDb Popular" collection to the home screen of other users of the server

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="white-style|limit|sync_mode|collection_order"
        rewrite-relative-urls=false
        replace='{"<!--limit-extra-->": "<br>**Default:** `100`", "COLLECTION_ORDER": "`custom`"}'
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "TMDb Chart Collections"
        
        The TMDb Chart collections use [TMDb Builders](../../../files/builders/tmdb) to create the collections.
