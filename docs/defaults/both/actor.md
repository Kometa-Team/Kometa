---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Actor",
        "CODE_NAME": "actor",
        "DESCRIPTION": "dynamically create collections based on the most popular actors/actresses in your library",
        "LIBRARY_TYPE": "Movie, Show",
        "SECTION_NUMBER": "140"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Actors"}' %}
| `<<actor_name>>`<br>**Example:** `Frank Welker` | `<<actor_name>>`<br>**Example:** `Frank Welker` | Collection of Movies/Shows the actor is top billing in. |

{% include-markdown "./../../templates/snippets/people_style.md" replace='{"CODE_NAME": "actor"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "actor"}' include-tags='all|movie|show' %}
    {% include-markdown "./../../templates/snippets/people_example.md" replace='{"CODE_NAME": "actor"}' rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="people-data|exclude|include|limit|sort_by|style|format|tmdb_birthday|tmdb_person_offset"
        replace='{
            "DYNAMIC_NAME": "Actors", 
            "DYNAMIC_VALUE": "Actor Names",
            "NAME_FORMAT": "<<key_name>>",
            "SUMMARY_FORMAT": "<<library_translationU>>s with <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Actor Collections"
        
        All the Actor collections use the [dynamic collections](./../../files/dynamic.md) system based on the Actors in your library.
