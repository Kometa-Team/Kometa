---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Simkl Chart", 
        "CODE_NAME": "simkl",
        "LIBRARY_TYPE": "Movie, Show", 
        "DESCRIPTION": "create collections based on Simkl charts",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": ""}'
%}
| `Simkl Trending Today`      | `trending_today`  | Collection of Movies/Shows Trending Today on Simkl.      |
| `Simkl Trending This Week`  | `trending_week`   | Collection of Movies/Shows Trending This Week on Simkl.  |
| `Simkl Trending This Month` | `trending_month`  | Collection of Movies/Shows Trending This Month on Simkl. |
| `Simkl DVD`                 | `dvd`             | Collection of Movies/Shows from Simkl's DVD Release list. |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "simkl"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "simkl"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: simkl
            template_variables:
              use_dvd: false #(1)!
              limit: 20 #(2)!
              visible_library_trending_today: true #(3)!
              visible_home_trending_today: true #(4)!
              visible_shared_trending_today: true #(5)!
    ```

    1. Do not create the "Simkl DVD" collection
    2. Change all collections built by this file to have a maximum of 20 items
    3. Pin the "Simkl Trending Today" collection to the Recommended tab of the library
    4. Pin the "Simkl Trending Today" collection to the home screen of the server owner
    5. Pin the "Simkl Trending Today" collection to the home screen of other users of the server

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

    === "Simkl Chart Collections"
        
        The Simkl Chart collections use [Simkl Builders](../../../files/builders/simkl/overview) to create the collections.
