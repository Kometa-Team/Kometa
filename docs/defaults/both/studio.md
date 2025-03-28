---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Studio", 
        "CODE_NAME": "studio",
        "DESCRIPTION": "dynamically create collections based on the studios available in your library",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "070"
    }'
    replace-tags='{"title-sub": "This file also merges similarly named studios (such as \"20th Century Fox\" and \"20th Century Animation\") into one (\"20th Century Studios\")."}'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Studio"}' %}
| `<<Studio>>`<br>**Example:** `Blumhouse Productions` | `<<Studio>>`<br>**Example:** `Blumhouse Productions` | Collection of Movies/Shows that have this Studio. |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "studio"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: studio
            template_variables:
              append_include:
                - Big Bull Productions #(1)!
              sort_by: title.asc
              collection_mode: show_items #(2)!
              sep_style: gray #(3)!
    ```

    1. add "Big Bull Productions" to the list of items that should be included in the Collection list
    2. Show these collections and their items within the "Library" tab
    3. Use the gray [Separator Style](../separators.md#separator-styles)

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="addons|addons-extra|exclude|include|include-extra|limit|sort_by|format"
        replace='{
            "DYNAMIC_NAME": "Studios", 
            "DYNAMIC_VALUE": "Studios",
            "NAME_FORMAT": "<<key_name>>",
            "SUMMARY_FORMAT": "<<library_translationU>>s produced by <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Studio Collections"

        The Studio collections use the [dynamic collections](../../../files/dynamic) system with a default include list and some default addons to consolidate some of the studios.

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/both/studio.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/both/studio.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
