---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Aspect Ratio", 
        "CODE_NAME": "aspect",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "125", 
        "DESCRIPTION": "create collections with items that are based on their aspect ratio"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Aspect Ratio"}' %}
| `1.33 - Academy Aperture`      | `1.33` | Collection of Movies/Shows with a 1.33 aspect ratio. |
| `1.65 - Early Widescreen`      | `1.65` | Collection of Movies/Shows with a 1.65 aspect ratio. |
| `1.66 - European Widescreen`   | `1.66` | Collection of Movies/Shows with a 1.66 aspect ratio. |
| `1.78 - Widescreen TV`         | `1.78` | Collection of Movies/Shows with a 1.78 aspect ratio. |
| `1.85 - American Widescreen`   | `1.85` | Collection of Movies/Shows with a 1.85 aspect ratio. |
| `2.2 - 70mm Frame`             | `2.2`  | Collection of Movies/Shows with a 2.2 aspect ratio.  |
| `2.35 - Anamorphic Projection` | `2.35` | Collection of Movies/Shows with a 2.35 aspect ratio. |
| `2.77 - Cinerama`              | `2.77` | Collection of Movies/Shows with a 2.77 aspect ratio. |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "aspect"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: aspect
            template_variables:
              use_1.65: false #(1)!
              sep_style: plum #(2)!
    ```

    1. Do not create a "1.65 - Early Widescreen" collection
    2. Use the plum [Separator Style](../separators.md#separator-styles)

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="exclude|limit|sort_by|sync_mode|format"
        replace='{
            "DYNAMIC_NAME": "Media Outlets", 
            "DYNAMIC_VALUE": "Media Outlet Keys",
            "NAME_FORMAT": "<<key_name>>",
            "SUMMARY_FORMAT": "A collection of <<library_translationU>>s with the aspect ratio of <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Aspect Ratio Collections"
        
        The Aspect Ratio collections use Plex searches and filters based on a fixed list of aspect ratios.
