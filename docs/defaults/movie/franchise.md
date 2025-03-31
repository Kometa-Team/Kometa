---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Franchise", 
        "CODE_NAME": "franchise",
        "DESCRIPTION": "dynamically create collections based on popular Movie franchises, and can be used as a replacement to the TMDb Collections that Plex creates out-of-the-box",
        "LIBRARY_TYPE": "Movie", 
        "Section SECTION_NUMBER": ""
    }'
    replace-tags='{
        "title-sub": "Unlike most Default Collection Files, Franchise works by placing collections inline with the main library items if your library allows it. 
For example, the \"Iron Man\" franchise collection will appear next to the \"Iron Man\" movies within your library.

**[This file has a Show Library Counterpart.](./../../../../show/franchise)**",
        "image": "![](./../../../../assets/images/defaults/posters/franchise_movie.png)",
        "rec-sub": "It is important to disable Plex\'s in-built Automatic Collections if you are using this Default file. Please see the below video showing how to do this.

<video controls><source src=\"./../../../../../assets/images/defaults/automatic_collections.mp4\" type=\"video/mp4\"></video>

You\'ll also need to delete any Collections created automatically by Plex prior to Kometa running this file. 
You can use the [`delete_collections` operation](./../../../../config/operations.md#delete-collections) to do this, or any other method."
    }'
%}
| `<<Collection Name>>`<br>**Example:** `Iron Man` | `<<TMDb Collection ID>>`<br>**Example:** `131292` | Collection of Movies found in this Collection on TMDb. |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "franchise"}' include-tags='all|movie' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: franchise
            template_variables:
              build_collection: false #(1)!
              movie_105995: 336560 #(2)!
              radarr_add_missing: true #(3)!
    ```

    1. Do not create any physical collections in Plex (normally used when you want to perform an "operation" instead, see the third tooltip for the example)
    2. Add [TMDb Movie 336560](https://www.themoviedb.org/movie/336560-lake-placid-vs-anaconda) to [TMDb Collection 105995](https://www.themoviedb.org/collection/105995-anaconda-collection) 
    3. Add items missing from your library in Plex to Radarr. When used in this particular file, hundreds if not thousands of items may be sent to Radarr - proceed with caution!

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" end="<!--file-->" %}
{% include-markdown "./../../templates/snippets/no_shared_variables.md" %}
{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" start="<!--file-header-->" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="franchise|arr|addons|addons-extra|exclude|sync_mode|collection_mode|collection_order"
        replace='{
            "DYNAMIC_NAME": "TMDb Collections", 
            "DYNAMIC_VALUE": "TMDb Collection IDs",
            "COLLECTION_ORDER": "`release`",
            "ARR_CODE": "radarr",
            "ARR_NAME": "Radarr",
            "ARR_TYPE": "movie"
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Franchise Collections"
        
        The Continents collections use the [dynamic collections](../../../files/dynamic) system with a default list of target franchises and some default addons to group shows and movies into those franchises.

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/movie/franchise.yml" 
      comments=false
      start="addons:\n"
      end="title_override:"
    %}
        ```

    === "Default `title_override`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        title_override: 
    {%    
      include-markdown "../../../defaults/movie/franchise.yml" 
      comments=false
      start="title_override:\n"
      end="template_variables:"
    %}
        ```

    === "Default `movie`"
    
        ???+ tip 
    
            Pass `movie_<<key>>` to the file as Template Variables to change this value per collection. 
    
            ```yaml
              - default: franchise
                template_variables:
                  movie_131292:
                    - 1234
                    - 5678
            ```

        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        movie: 
  {%    
    include-markdown "../../../defaults/movie/franchise.yml" 
    comments=false
    start="movie:\n"
    end="name_mapping:"
  %}
        ```

    === "Default `name_mapping`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        name_mapping: 
  {%    
    include-markdown "../../../defaults/movie/franchise.yml" 
    comments=false
    start="name_mapping:\n"
  %}
        ```
