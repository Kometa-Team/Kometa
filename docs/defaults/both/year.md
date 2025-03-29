---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Year", 
        "CODE_NAME": "year",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "105", 
        "DESCRIPTION": "dynamically create collections based on the years available in your library, sorted by critic rating to create \"best of YEAR\" collections"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Year"}' %}
| `Best of <<Year>>`<br>**Example:** `Best of 2022` | `<<Year>>`<br>**Example:** `2022` | Collection of Movies/Shows that have this Year. |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "year"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: year
            template_variables:
              sep_style: purple #(1)!
              sort_by: title.asc 
              sort_by_2022: release.desc #(2)!
    ```

    1. Use the purple [Separator Style](../separators.md#separator-styles)
    2. Set the sort order for "Best of 2022" to release date descending

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="year-data|exclude|limit|sort_by|format"
        replace='{
            "DYNAMIC_NAME": "Years", 
            "DYNAMIC_VALUE": "Years",
            "NAME_FORMAT": "Best of <<key_name>>",
            "SUMMARY_FORMAT": "<<library_translationU>>s released in <<key_name>>.",
            "release.desc": "critic_rating.desc"
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Year Collections"
        
        The Year collections use the [dynamic collections](./../../files/dynamic.md) system based on the release dates of the items in your libraries.
