---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Audio Language", 
        "CODE_NAME": "audio_language",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "090", 
        "DESCRIPTION": "dynamically create collections based on the audio languages available in your library"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Audio Language"}' %}
| `<<Audio Language>> Audio`<br>**Example:** `Japanese` | `<<ISO 639-1 Code>>`<br>**Example:** `ja` <br>`<<ISO 639-2 Code>>`<br>**Example:** `myn` | Collection of Movies/Shows that have this Audio Language. |
| `Other Audio` | `other` | Collection of Movies/Shows that are less common Languages. |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "audio_language"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: audio_language
            template_variables:
              use_other: false #(1)!
              use_separator: false #(2)!
              exclude:
                - fr #(3)!
              sort_by: title.asc
    ```

    1. Do not create an "Other Audio" collection
    2. Do not create an "Audio Language Collections" separator
    3. Exclude "French" from having an Audio Collection

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="exclude|include|include-extra|key_name_override|limit|sort_by|format"
        replace='{
            "DYNAMIC_NAME": "Audio Languages", 
            "DYNAMIC_VALUE": "[ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) or [ISO 639-2](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes) codes",
            "NAME_FORMAT": "<<key_name>> Audio",
            "SUMMARY_FORMAT": "<<library_translationU>>s filmed in the <<key_name>> Language."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Audio Language Collections"
        
        The Audio Languages collections use smart filters based on a default list of target languages.

    === "Default `include`"

        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/both/audio_language.yml" 
      comments=false
      start="include:\n"
      end="key_name_override:"
    %}
        ```

    === "Default `key_name_override`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        key_name_override: 
    {%    
      include-markdown "../../../defaults/both/audio_language.yml" 
      comments=false
      start="key_name_override:\n"
    %}
        ```
