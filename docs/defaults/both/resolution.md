---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Resolution", 
        "CODE_NAME": "resolution",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "120", 
        "DESCRIPTION": "dynamically create collections based on the resolutions available in your library"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Resolution"}' %}
| `<<Resolution>> Movies/Shows`<br>**Example:** `1080p Movies` | `<<Number>>`<br>**Example:** `1080` | Collection of Movies/Shows that have this Resolution. |

## Standards Style

Below is a screenshot of the alternative Standards (`standards`) style which can be set via the `style` template variable.

Standards Style takes the base resolutions ("4K" and "720p") and turns them into the commonly-known standards name ("Ultra HD" and "HD Ready").

![](../../assets/images/defaults/styles/resolution_standards.png)

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "resolution"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: resolution
            template_variables:
              sep_style: green #(1)!
              exclude:
                - sd #(2)!
              sort_by: title.asc
    ```

    1. Use the green [Separator Style](../separators.md#separator-styles)
    2. Do not use the "sd" resolution as part of the "480p Movies/Shows" Collections

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="addons|addons-extra|exclude|include|include-extra|limit|sort_by|resolution-style|sync_mode|format"
        replace='{
            "DYNAMIC_NAME": "Resolutions", 
            "DYNAMIC_VALUE": "Resolutions",
            "NAME_FORMAT": "<<key_name>> <<library_translationU>>s",
            "SUMMARY_FORMAT": "<<library_translationU>>s that have the resolution <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Resolution Collections"

        The Resolution collections use the [dynamic collections](../../../files/dynamic) system based on the resolution of the items in your libraries.
        
        They use a default list of resolutions to create the collections, and some default addons to group resolutions together.


    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/both/resolution.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/both/resolution.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
