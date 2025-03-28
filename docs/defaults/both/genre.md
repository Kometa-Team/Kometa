---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Genre", 
        "CODE_NAME": "genre",
        "DESCRIPTION": "dynamically create collections based on the genres available in your library",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "060"
    }'
    replace-tags='{"title-sub": "This file also merges similarly named genres (such as \"Sci-Fi\", \"SciFi\" and \"Sci-Fi & Fantasy\") into one (\"Science Fiction\")."}'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Genre"}' %}
| `<<Genre>> Movies/Shows`<br>**Example:** `Action Movies` | `<<Genre>>`<br>**Example:** `Action` | Collection of Movies/Shows that have this Genre. |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "genre"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: genre
            template_variables:
              sep_style: red #(1)!
              exclude:
                - Politics #(2)!
                - News #(3)!
              append_addons:
                Horror: #(4)!
                  - Thriller #(5)! # Adds all thriller items to the Horror collection
    ```

    1. Use the red [Separator Style](../separators.md#separator-styles)
    2. Do not create a "Politics" collection, and do not include it in any other collections that it may be in as part of an "include"
    3. Do not create a "News" collection, and do not include it in any other collections that it may be in as part of an "include"
    4. Create a "Horror" collection, this genre does not need to exist in your library
    5. Include the "Thriller" genre in the "Horror" collection, the "Thriller" genre must exist in your library if the "Horror" genre does not

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="addons|addons-extra|exclude|limit|sort_by|format"
        replace='{
            "DYNAMIC_NAME": "Genres", 
            "DYNAMIC_VALUE": "Genres",
            "NAME_FORMAT": "<<key_name>> <<library_translationU>>s",
            "SUMMARY_FORMAT": "<<library_translationU>>s that have the genre <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Genre Collections"

        The Genre collections use the [dynamic collections](../../../files/dynamic) system based on the genres found in your library
        and some default addons to consolidate some of the genres.

        i.e. `SciFi` and `Sci-Fi` are both addons of `Science Fiction` so that they all end up in the same `Science Fiction` collection despite technically having different genres.

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/both/genre.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
