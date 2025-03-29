---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Director",
        "CODE_NAME": "director",
        "DESCRIPTION": "dynamically create collections based on the most popular directors in your library",
        "LIBRARY_TYPE": "Movie",
        "SECTION_NUMBER": "150"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Directors"}' %}
| `<<director_name>> (Director)`<br>**Example:** `Frank Welker (Director)` | `<<director_name>>`<br>**Example:** `Frank Welker` | Collection of Movies by the Director. |

{% include-markdown "./../../templates/snippets/people_style.md" replace='{"CODE_NAME": "director"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "director"}' include-tags='all|movie' %}
    {% include-markdown "./../../templates/snippets/people_example.md" replace='{"CODE_NAME": "director"}' %}

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="people-data|exclude|include|limit|sort_by|style|format|tmdb_birthday|tmdb_person_offset"
        replace='{
            "DYNAMIC_NAME": "Directors", 
            "DYNAMIC_VALUE": "Director Names",
            "NAME_FORMAT": "<<key_name>> (Director)",
            "SUMMARY_FORMAT": "<<library_translationU>>s directed by <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Director Collections"
        
        All the Director collections use the [dynamic collections](./../../files/dynamic.md) system based on the Directors in your library.
