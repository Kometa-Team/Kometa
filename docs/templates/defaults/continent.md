{%
    include-markdown "./base/collection/header.md"
    replace='{
        "COLLECTION": "Continent", 
        "CODE_NAME": "continent",
        "DESCRIPTION": "dynamically create collections based on the countries within your library. The collection aims to be inclusive, with all 230 countries incorporated into continents",
        "SECTION_NUMBER": "082"
    }'
%}
{% include-markdown "./../snippets/separator_line.md" replace='{"SEPARATOR": "Continent"}' %}
| `Africa`           | `Africa`     | Collection of FULL_TYPE filmed in Africa.                      |
| `Americas`         | `Americas`   | Collection of FULL_TYPE filmed in Americas.                    |
| `Antarctica`       | `Antarctica` | Collection of FULL_TYPE filmed in Antarctica.                  |
| `Asia`             | `Asia`       | Collection of FULL_TYPE filmed in Asia.                        |
| `Europe`           | `Europe`     | Collection of FULL_TYPE filmed in Europe.                      |
| `Oceania`          | `Oceania`    | Collection of FULL_TYPE filmed in Oceania.                     |
| `Other Continents` | `other`      | Collection of FULL_TYPE that are in other uncommon Continents. |

{% include-markdown "./../snippets/color_style.md" replace='{"CODE_NAME": "continent"}' %}
{% include-markdown "./base/mid.md" replace='{"CODE_NAME": "continent"}' include-tags='all|SHORT_TYPE' %}
    ```yaml
    libraries:
      FULL_TYPE:
        collection_files:
          - default: continent
            template_variables:
              use_other: false #(1)!
              use_separator: false #(2)!
              style: color #(3)!
              exclude:
                - Europe #(4)!
              sort_by: title.asc
    ```

    1. Do not create the "Other Continents" collection
    2. Do not create a "Continent Collections" separator
    3. Set the [Color Style](#color-style)
    4. Exclude "Europe" from the list of collections that are created

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

    === "Continent Collections"

        The Continents collections use the [dynamic collections](../../../files/dynamic) system with some default addons to consolidate the countries into continents.
