---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Basic Chart", 
        "CODE_NAME": "basic",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "010", 
        "DESCRIPTION": "create collections based on recently released media in your library"
    }'
%}
| `New Episodes`   | `episodes` | Collection of Episodes released in the last 7 days.            |
| `Newly Released` | `released` | Collection of Movies or TV Shows released in the last 90 days. |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "basic"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "basic"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: basic
            template_variables:
              in_the_last_episodes: 14 #(1)!
              visible_library_released: true #(2)!
              visible_home_released: true #(3)!
              visible_shared_released: true #(4)!
    ```

    1. Change the Smart Filter to look at episodes in the last 14 days.
    2. Pin the "Newly Released" collection to the Recommended tab of the library
    3. Pin the "Newly Released" collection to the home screen of the server owner
    4. Pin the "Newly Released" collection to the home screen of other users of the server

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="basic|white-style|limit|sort_by"
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Basic Chart Collections"
        
        The Basic Chart collections are based on [Smart Filters](./../../../files/builders/plex#smart-filter-builder) using the `in_the_last` attribute, not external lists.
