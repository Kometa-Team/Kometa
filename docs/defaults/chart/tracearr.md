---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Tracearr Chart",
        "CODE_NAME": "tracearr",
        "LIBRARY_TYPE": "Movie, Show",
        "DESCRIPTION": "create collections based on Tracearr watch history",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": "Requirements: [Tracearr Authentication](../../config/tracearr.md)."}'
%}
| `Tracearr Popular`   | `popular`   | Collection of items watched by the most unique Tracearr users. |
| `Tracearr Watched`   | `watched`   | Collection of items with the most completed Tracearr sessions. |
| `Tracearr Trending`  | `trending`  | Collection of the most active items from the last seven days of Tracearr watch history. |
| `Tracearr Rewatched` | `rewatched` | Collection of items repeatedly played by the same Tracearr user. |
| `Tracearr Completed` | `completed` | Collection of the most recently completed items from Tracearr watch history. |
| `Tracearr Binged` | `binged` | Collection of shows with the most distinct completed episodes watched by a single Tracearr user. Show libraries only. |
| `Tracearr Most Transcoded` | `transcoded` | Collection of items with the most Tracearr sessions that required audio or video transcoding. |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "tracearr"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "tracearr"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: tracearr
            template_variables:
              use_rewatched: false #(1)!
              list_days_popular: 7 #(2)!
              list_size_popular: 10 #(3)!
              visible_library_popular: true #(4)!
              visible_home_popular: true #(5)!
              visible_shared_popular: true #(6)!
    ```

    1. Do not create the "Tracearr Rewatched" collection
    2. Change "Tracearr Popular" to look at items from the past 7 days
    3. Change "Tracearr Popular" to have a maximum of 10 items
    4. Pin the "Tracearr Popular" collection to the Recommended tab of the library
    5. Pin the "Tracearr Popular" collection to the home screen of the server owner
    6. Pin the "Tracearr Popular" collection to the home screen of other users of the server

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="tracearr|white-style|sync_mode|collection_order"
        rewrite-relative-urls=false
        replace='{"COLLECTION_ORDER": "`custom`"}'
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Tracearr Chart Collections"

        The Tracearr Chart collections use [Tracearr Builders](../../../files/builders/tracearr/overview) to create the collections.
