---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Network",
        "CODE_NAME": "network",
        "DESCRIPTION": "dynamically create collections based on the networks in your library.
???+ danger \"Important\"

    This default requires that the library be set to use the \"Plex TV Series\" scanner and the \"Plex Series\" agent.

    The error in this case will be `Plex Error: plex_search attribute: network not supported`",
        "LIBRARY_TYPE": "Show",
        "SECTION_NUMBER": "050"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Network"}' %}
| `<<network>>`<br>**Example:** `NBC` | `<<network>>`<br>**Example:** `NBC` | Collection of Shows the aired on the network. |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "network"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "network"}' include-tags='all|show' %}
    ```yaml
    libraries:
      TV Shows:
        collection_files:
          - default: network
            template_variables:
              style: white
              append_exclude:
                - BBC #(1)!
              sort_by: title.asc
              collection_mode: show_items #(2)!
              sep_style: gray #(3)!
    ```

    1. exclude "BBC" from the list of items that should be included in the Collection list
    2. Show these collections and their items within the "Library" tab
    3. Use the gray [Separator Style](../separators.md#separator-styles)

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="addons|addons-extra|exclude|include|include-extra|limit|sort_by|white-style|format"
        replace='{
            "DYNAMIC_NAME": "Networks",
            "DYNAMIC_VALUE": "Networks",
            "NAME_FORMAT": "<<key_name>>",
            "SUMMARY_FORMAT": "`<<library_translationU>>s broadcast on <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Network Collections"
    
        The Network collections use the [dynamic collections](../../../files/dynamic.md) system with a default include list and some default addons to consolidate some of the networks.

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/show/network.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/show/network.yml"
      comments=false
      start="addons:\n"
    %}
        ```
