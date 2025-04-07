{%
    include-markdown "./base/collection/header.md"
    replace='{
        "DESCRIPTION": "dynamically create collections based on the content ratings available in your library.\n\n If you do not use the SHORT_NAME-based rating system within Plex, this file will attempt to match the ratings in your library to the respective rating system",
        "SECTION_NUMBER": "110"
    }'
    replace-tags='{"rec-sub": "Recommendation: Set the Certification Country within your library\'s advanced settings to \"PLEX_NAME\"."}'
%}
{% include-markdown "./../snippets/separator_line.md" replace='{"SEPARATOR": "Ratings"}' %}
| `<<Content Rating>> Movies/Shows`<br>**Example:** `EXAMPLE_NAME` | `<<Content Rating>>`<br>**Example:** `EXAMPLE1` | Collection of Movies/Shows that have this Content Rating.                             |
| `Not Rated Movies/Shows`                                         | `other`                                         | Collection of Movies/Shows that are Unrated, Not Rated or any other uncommon Ratings. |

{% include-markdown "./base/mid.md" include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: CODE_NAME
            template_variables:
              sep_style: stb #(1)!
              use_other: false #(2)!
              append_addons:
                EXAMPLE1: #(3)!
                  - EXAMPLE2 #(4)!
              sort_by: title.asc
    ```

    1. Use the stb [Separator Style](../../defaults/separators.md#separator-styles)
    2. Do not create a "Not Rated Movies/Shows" collection
    3. Defines a collection which will be called "EXAMPLE1", this does not need to already exist in your library
    4. Adds the "EXAMPLE2" content rating to the "EXAMPLE1" addon list, "EXAMPLE2" must exist in your library if the "EXAMPLE1" content rating does not

{% include-markdown "./base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../variable_list.md"
        include-tags="addons|addons-extra|exclude|include|include-extra|limit|sort_by|format"
        replace='{
            "DYNAMIC_NAME": "Content Ratings", 
            "DYNAMIC_VALUE": "Content Ratings",
            "NAME_FORMAT": "<<key_name>> <<library_translationU>>s",
            "SUMMARY_FORMAT": "<<library_translationU>>s that are rated <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./base/values.md" rewrite-relative-urls=false %}

    === "COLLECTION Collections"
        
        The COLLECTION collections use the [dynamic collections](../../../files/dynamic) system based on the content ratings of the items in your libraries. 
        They each have a addons which combine all the ratings in your library into collections reflecting the desired system.
