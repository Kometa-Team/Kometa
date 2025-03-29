{%
    include-markdown "./base/collection/header.md"
    replace='{
        "COLLECTION": "Country", 
        "CODE_NAME": "country",
        "DESCRIPTION": "dynamically create collections based on the countries within your library",
        "SECTION_NUMBER": "080"
    }'
%}
{% include-markdown "./../snippets/separator_line.md" replace='{"SEPARATOR": "Country"}' %}
| `<<Country>>`<br>**Example:** `Germany` | `<<Country>>`<br>**Example:** `Germany` | Collection of FULL_TYPE that have this Country.               |
| `Other Countries`                       | `other`                                 | Collection of FULL_TYPE that are in other uncommon Countries. |

{% include-markdown "./../snippets/color_style.md" replace='{"CODE_NAME": "country"}' %}
{% include-markdown "./base/mid.md" replace='{"CODE_NAME": "country"}' include-tags='all|SHORT_TYPE' %}
    ```yaml
    libraries:
      FULL_TYPE:
        collection_files:
          - default: country
            template_variables:
              use_other: false #(1)!
              use_separator: false #(2)!
              style: color #(3)!
              exclude:
                - France #(4)!
              sort_by: title.asc
    ```

    1. Do not create the "Other Countries" collection
    2. Do not create a "Country Collections" separator
    3. Set the [Color Style](#color-style)
    4. Exclude "France" from the list of collections that are created

{% include-markdown "./base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../variable_list.md"
        include-tags="addons|addons-extra|exclude|include|include-extra|key_name_override|limit|sort_by|color-style|format"
        replace='{
            "DYNAMIC_NAME": "Countries",
            "NAME_FORMAT": "<<key_name>>",
            "SUMMARY_FORMAT": "`<<library_translationU>>s filmed in <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./base/values.md" rewrite-relative-urls=false %}

    === "Country Collections"

        The Country collections use the [dynamic collections](../../../files/dynamic) system with a default include list and some default addons to consolidate some of the countries.
