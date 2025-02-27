---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "MyAnimeList Chart", 
        "CODE_NAME": "myanimelist",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "020", 
        "DESCRIPTION": "create collections based on MyAnimeList charts"
    }'
%}
| `MyAnimeList Favorited`  | `favorited` | Collection of most Favorited Anime on MyAnimeList.      |
| `MyAnimeList Popular`    | `popular`   | Collection of the most Popular Anime on MyAnimeList.    |
| `MyAnimeList Season`     | `season`    | Collection of the Current Seasons Anime on MyAnimeList. |
| `MyAnimeList Top Airing` | `airing`    | Collection of the Top Rated Airing on MyAnimeList.      |
| `MyAnimeList Top Rated`  | `top`       | Collection of the Top Rated Anime on MyAnimeList.       |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "myanimelist"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: myanimelist
            template_variables:
              use_season: false #(1)!
              order_popular: 01 #(2)!
              limit_popular: 20 #(3)!
              visible_library_popular: true #(4)!
              visible_home_popular: true #(5)!
              visible_shared_popular: true #(6)!
    ```

    1. Do not create the "MyAnimeList Season" collection
    2. Change the order of "MyAnimeList Popular" to appear before all other collections created by this file
    3. Limit the "MyAnimeList Popular" collection to 20 items.
    4. Pin the "MyAnimeList Popular" collection to the Recommended tab of the library
    5. Pin the "MyAnimeList Popular" collection to the home screen of the server owner
    6. Pin the "MyAnimeList Popular" collection to the home screen of other users of the server

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="myanimelist|limit|sync_mode|collection_order"
        rewrite-relative-urls=false
        replace='{"<!--limit-extra-->": "<br>**Default:** `100`", "COLLECTION_ORDER": "`custom`"}'
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "MyAnimeList Chart Collections"
        
        The MyAnimeList Chart collections use [MyAnimeList Builders](../../../files/builders/myanimelist) to create the collections.
