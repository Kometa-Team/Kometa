{%
    include-markdown "./base/collection/header.md"
    replace='{
        "COLLECTION": "Region", 
        "CODE_NAME": "region",
        "DESCRIPTION": "dynamically create collections based on the countries within your 
library. The collection aims to be inclusive, with all 230 countries incorporated into 39 countries or collections of 
countries. Some care has been taken to ensure all countries are included, and the groupings won\'t fit well with 
everyone\'s collections. Western and Southern Europe, Oceania, and North America could be useful groupings for those 
libraries with more of an Asian focus, for instance. Please see the comments in the yml below where a decision point 
might be seen as controversial. You are welcome to edit this to fit your own audience\'s needs",
        "SECTION_NUMBER": "081"
    }'
%}
{% include-markdown "./../snippets/separator_line.md" replace='{"SEPARATOR": "Region"}' %}
| `Northern Africa`           | `Northern Africa`           | Collection of FULL_TYPE that have been filmed in Northern Africa.           | 
| `Eastern Africa`            | `Eastern Africa`            | Collection of FULL_TYPE that have been filmed in Eastern Africa.            | 
| `Central Africa`            | `Central Africa`            | Collection of FULL_TYPE that have been filmed in Central Africa.            | 
| `Southern Africa`           | `Southern Africa`           | Collection of FULL_TYPE that have been filmed in Southern Africa.           | 
| `Western Africa`            | `Western Africa`            | Collection of FULL_TYPE that have been filmed in Western Africa.            | 
| `Caribbean`                 | `Caribbean`                 | Collection of FULL_TYPE that have been filmed in the Caribbean.             | 
| `Central America`           | `Central America`           | Collection of FULL_TYPE that have been filmed in Central America.           | 
| `South America`             | `South America`             | Collection of FULL_TYPE that have been filmed in South America.             | 
| `North America`             | `North America`             | Collection of FULL_TYPE that have been filmed in North America.             | 
| `Antarctica`                | `Antarctica`                | Collection of FULL_TYPE that have been filmed in Antarctica.                | 
| `Central Asia`              | `Central Asia`              | Collection of FULL_TYPE that have been filmed in Central Asia.              | 
| `Eastern Asia`              | `Eastern Asia`              | Collection of FULL_TYPE that have been filmed in Eastern Asia.              | 
| `South-Eastern Asia`        | `South-Eastern Asia`        | Collection of FULL_TYPE that have been filmed in South-Eastern Asia.        | 
| `Southern Asia`             | `Southern Asia`             | Collection of FULL_TYPE that have been filmed in Southern Asia.             | 
| `Western Asia`              | `Western Asia`              | Collection of FULL_TYPE that have been filmed in Western Asia.              | 
| `Eastern Europe`            | `Eastern Europe`            | Collection of FULL_TYPE that have been filmed in Eastern Europe.            | 
| `Northern Europe`           | `Northern Europe`           | Collection of FULL_TYPE that have been filmed in Northern Europe.           | 
| `Southern Europe`           | `Southern Europe`           | Collection of FULL_TYPE that have been filmed in Southern Europe.           | 
| `Western Europe`            | `Western Europe`            | Collection of FULL_TYPE that have been filmed in Western Europe.            | 
| `Australia and New Zealand` | `Australia and New Zealand` | Collection of FULL_TYPE that have been filmed in Australia and New Zealand. | 
| `Melanesia`                 | `Melanesia`                 | Collection of FULL_TYPE that have been filmed in Melanesia.                 | 
| `Micronesia`                | `Micronesia`                | Collection of FULL_TYPE that have been filmed in Micronesia.                | 
| `Polynesia`                 | `Polynesia`                 | Collection of FULL_TYPE that have been filmed in Polynesia.                 | 
| `Other Regions`             | `other`                     | Collection of FULL_TYPE that are in other uncommon Regions.                 |

{% include-markdown "./../snippets/color_style.md" replace='{"CODE_NAME": "region"}' %}
{% include-markdown "./base/mid.md" replace='{"CODE_NAME": "region"}' include-tags='all|SHORT_TYPE' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: region
            template_variables:
              use_other: false #(1)!
              use_separator: false #(2)!
              style: color #(3)!
              exclude:
                - Melanesia #(4)!
              sort_by: title.asc
    ```

    1. Do not create the "Other Regions" collection
    2. Do not create a "Region Collections" separator
    3. Set the [Color Style](#color-style)
    4. Exclude "Melanesia" from the list of collections that are created

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

    === "Region Collections"

        The Region collections use the [dynamic collections](../../../files/dynamic) system with a default include list and some default addons to consolidate some of the regions.