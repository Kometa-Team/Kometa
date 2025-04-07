---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Trakt Chart", 
        "CODE_NAME": "trakt",
        "LIBRARY_TYPE": "Movie, Show", 
        "DESCRIPTION": "create collections based on Trakt charts",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": "Requirements: [Trakt Authentication](../../../../../config/trakt)."}'
%}
| `Trakt Collected`   | `collected`   | Collection of the Most Collected Movies/Shows on Trakt. |
| `Trakt Popular`     | `popular`     | Collection of the Most Popular Movies/Shows on Trakt.   |
| `Trakt Recommended` | `recommended` | Collection of Recommended Movies/Shows on Trakt.        |
| `Trakt Trending`    | `trending`    | Collection of Trending Movies/Shows on Trakt.           |
| `Trakt Watched`     | `watched`     | Collection of the Most Watched Movies/Shows on Trakt.   |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "trakt"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "trakt"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: trakt
            template_variables:
              use_collected: false #(1)!
              use_recommended: false #(2)!
              limit: 20 #(3)!
              visible_library_popular: true #(4)!
              visible_home_popular: true #(5)!
              visible_shared_popular: true #(6)!
    ```

    1. Do not create the "Trakt Collected" collection
    2. Do not create the "Trakt Recommended" collection
    3. Change all collections built by this file to have a maximum of 20 items
    4. Pin the "Trakt Popular" collection to the Recommended tab of the library
    5. Pin the "Trakt Popular" collection to the home screen of the server owner
    6. Pin the "Trakt Popular" collection to the home screen of other users of the server

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

    === "Trakt Chart Collections"
        
        The Trakt Chart collections use [Trakt Builders](../../../files/builders/trakt) to create the collections.
