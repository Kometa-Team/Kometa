---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Tautulli Chart", 
        "CODE_NAME": "tautulli",
        "LIBRARY_TYPE": "Movie, Show", 
        "DESCRIPTION": "create collections based on Tautulli/Plex charts",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": "Requirements: [Tautulli Authentication](../../config/tautulli.md)."}'
%}
| `Plex Popular` | `popular` | Collection of the most Popular Movies/Shows on Plex. |
| `Plex Watched` | `watched` | Collection of the most Watched Movies/Shows on Plex. |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "tautulli"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "tautulli"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: tautulli
            template_variables:
              use_watched: false #(1)!
              list_days_popular: 7 #(2)!
              list_size_popular: 10 #(3)!
              visible_library_popular: true #(4)!
              visible_home_popular: true #(5)!
              visible_shared_popular: true #(6)!
    ```

    1. Do not create the "Plex Watched" collection
    2. Change "Plex Popular" to look at items from the past 7 days
    3. Change "Plex Popular" to have a maximum of 10 items
    4. Pin the "Plex Popular" collection to the Recommended tab of the library
    5. Pin the "Plex Popular" collection to the home screen of the server owner
    6. Pin the "Plex Popular" collection to the home screen of other users of the server

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="tautulli|white-style|sync_mode|collection_order"
        rewrite-relative-urls=false
        replace='{"COLLECTION_ORDER": "`custom`"}'
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Tautulli Chart Collections"
        
        The Tautulli Chart collections use [Tautulli Builders](../../../files/builders/tautulli) to create the collections.
