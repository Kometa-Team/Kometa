---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Anilist Chart", 
        "CODE_NAME": "anilist",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "020", 
        "DESCRIPTION": "create collections based on Anilist charts"
    }'
%}
| `AniList Popular`   | `popular`  | Collection of the most Popular Anime on AniList.     |
| `AniList Season`    | `season`   | Collection of the Current Season's Anime on AniList. |
| `AniList Top Rated` | `top`      | Collection of the Top Rated Anime on AniList.        |
| `AniList Trending`  | `trending` | Collection of the Trending Anime on AniList.         |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "anilist"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "anilist"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: anilist
            template_variables:
              use_season: false #(1)!
              order_top: 01 #(2)!
              summary_top: "Top 10 Rated movies on AniList" #(3)!
              limit_top: 10 #(4)!
              visible_library_popular: true #(5)!
              visible_home_popular: true #(6)!
              visible_shared_popular: true #(7)!
    ```

    1. Do not create the "AniList Season" collection
    2. Change the order of "AniList Top Rated" to appear before other collections created by this file
    3. Amend the summary of the "AniList Top Rated" collection
    4. Only allow a maximum of 10 items to appear in the "AniList Top Rated" collection
    5. Pin the "AniList Popular" collection to the Recommended tab of the library
    6. Pin the "AniList Popular" collection to the home screen of the server owner
    7. Pin the "AniList Popular" collection to the home screen of other users of the server

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

    === "Anilist Chart Collections"
        
        The AniList Chart collections use [AniList Builders](../../../files/builders/anilist) to create the collections.
