---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Writer",
        "CODE_NAME": "writer",
        "DESCRIPTION": "dynamically create collections based on the most popular writers in your library",
        "LIBRARY_TYPE": "Movie",
        "SECTION_NUMBER": "170"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Writers"}' %}
| `<<writer_name>> (Writer)`<br>**Example:** `Frank Welker (Writer)` | `<<writer_name>>`<br>**Example:** `Frank Welker` | Collection of Movies by the Writer. |

{% include-markdown "./../../templates/snippets/people_style.md" replace='{"CODE_NAME": "writer"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "writer"}' include-tags='all|movie' %}
    {% include-markdown "./../../templates/snippets/people_example.md" replace='{"CODE_NAME": "writer"}' %}

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="people-data|exclude|include|limit|sort_by|style|format|tmdb_birthday|tmdb_person_offset"
        replace='{
            "DYNAMIC_NAME": "Writers", 
            "DYNAMIC_VALUE": "Writer Names",
            "NAME_FORMAT": "<<key_name>> (Writer)",
            "SUMMARY_FORMAT": "<<library_translationU>>s written by <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Writer Collections"
        
        All the Writer collections use the [dynamic collections](./../../files/dynamic.md) system based on the Writers in your library.
