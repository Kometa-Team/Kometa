---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Producer",
        "CODE_NAME": "producer",
        "DESCRIPTION": "dynamically create collections based on the most popular producers in your library",
        "LIBRARY_TYPE": "Movie",
        "SECTION_NUMBER": "160"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Producers"}' %}
| `<<producer_name>> (Producer)`<br>**Example:** `Frank Welker (Producer)` | `<<producer_name>>`<br>**Example:** `Frank Welker` | Collection of Movies by the Producer. |

{% include-markdown "./../../templates/snippets/people_style.md" replace='{"CODE_NAME": "producer"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "producer"}' include-tags='all|movie' %}
    {% include-markdown "./../../templates/snippets/people_example.md" replace='{"CODE_NAME": "producer"}' %}

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %} 
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="people-data|exclude|include|limit|sort_by|style|format|tmdb_birthday|tmdb_person_offset"
        replace='{
            "DYNAMIC_NAME": "Producers", 
            "DYNAMIC_VALUE": "Producer Names",
            "NAME_FORMAT": "<<key_name>> (Producer)",
            "SUMMARY_FORMAT": "<<library_translationU>>s produced by <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Producer Collections"
        
        All the Producer collections use the [dynamic collections](./../../files/dynamic.md) system based on the Producers in your library.
