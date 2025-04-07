{%
    include-markdown "./base/collection/header.md"
    replace='{
        "COLLECTION": "Decade", 
        "CODE_NAME": "decade",
        "DESCRIPTION": "dynamically create collections based on the decades available in your library, sorted by critic rating to create \"Best of <decade>s Collections\"",
        "SECTION_NUMBER": "100"
    }'
%}
{% include-markdown "./../snippets/separator_line.md" replace='{"SEPARATOR": "Decade"}' %}
| `Best of <<Decade>>`<br>**Example:** `Best of 2020s` | `<<Year>>`<br>**Example:** `2020` | Collection of FULL_TYPE released in this Decade. |

{% include-markdown "./base/mid.md" replace='{"CODE_NAME": "decade"}' include-tags='all|SHORT_TYPE' %}
    ```yaml
    libraries:
      FULL_TYPE:
        collection_files:
          - default: decade
            template_variables:
              sep_style: purple #(1)!
              sort_by: title.asc 
              sort_by_2020: release.desc #(2)!
    ```

    1. Use the purple [Separator Style](../separators.md#separator-styles)
    2. Set the sort order for "Best of 2020s" to release date descending

{% include-markdown "./base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../variable_list.md"
        include-tags="exclude|limit|sort_by|format"
        replace='{
            "DYNAMIC_NAME": "Decades",
            "DYNAMIC_VALUE": "Decades",
            "NAME_FORMAT": "Best of <<key_name>>",
            "SUMMARY_FORMAT": "`Top <<limit>> <<library_translation>>s of the <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./base/values.md" rewrite-relative-urls=false %}

    === "Decade Collections"

        The Decade collections use the [dynamic collections](../../../files/dynamic) system based on the release dates of the items in your libraries.