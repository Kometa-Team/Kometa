---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Universe", 
        "CODE_NAME": "universe",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "040", 
        "DESCRIPTION": "create collections based on popular Movie universes (such as the Marvel Cinematic Universe or Wizarding World)"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Universe"}' %}
| `Alien / Predator`           | `avp`       | Collection of Movies in the Alien / Predator Universe             |
| `Arrowverse`                 | `arrow`     | Collection of Movies in the The Arrow Universe                    |
| `DC Animated Universe`       | `dca`       | Collection of Movies in the DC Animated Universe                  |
| `DC Extended Universe`       | `dcu`       | Collection of Movies in the DC Extended Universe                  |
| `Fast & Furious`             | `fast`      | Collection of Movies in the Fast & Furious Universe               |
| `In Association with Marvel` | `marvel`    | Collection of Movies in the Marvel Universe (but not part of MCU) |
| `Marvel Cinematic Universe`  | `mcu`       | Collection of Movies in the Marvel Cinematic Universe             |
| `Middle Earth`               | `middle`    | Collection of Movies in the Middle Earth Universe                 |
| `Rocky / Creed`              | `rocky`     | Collection of Movies in the Rocky / Creed Universe                |
| `Star Trek`                  | `trek`      | Collection of Movies in the Star Trek Universe                    |
| `Star Wars Universe`         | `star`      | Collection of Movies in the Star Wars Universe                    |
| `The Mummy Universe`         | `mummy`     | Collection of Movies in the The Mummy Universe                    |
| `View Askewverse`            | `askew`     | Collection of Movies in the The View Askew Universe               |
| `Wizarding World`            | `wizard`    | Collection of Movies in the Wizarding World Universe              |
| `X-Men Universe`             | `xmen`      | Collection of Movies in the X-Men Universe                        |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "universe"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: universe
            template_variables:
              sep_style: salmon #(1)!
              collection_order: release #(2)!
              radarr_add_missing: true #(3)!
              append_data:
                monster: MonsterVerse #(4)!
              trakt_list_monster: https://trakt.tv/users/rzepkowski/lists/monsterverse-movies #(5)!
    ```

    1. Use the salmon [Separator Style](../separators.md#separator-styles)
    2. Sort the Universe collections by release date
    3. Send missing items in your library from the source lists to Radarr
    4. Create a new universe called "MonsterVerse", the key for this universe will be "monster"
    5. Add a trakt list to the "monster" key

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="universe|data|exclude|collection_order|sync_mode"
        replace='{
            "DYNAMIC_NAME": "Universes", 
            "DYNAMIC_VALUE": "Universes",
            "COLLECTION_ORDER": "`custom`"
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Universe Collections"
        
        The Universe collections are based on either Trakt lists or MDB lists.

    === "Default `data`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        data: 
    {%    
      include-markdown "../../../defaults/both/universe.yml" 
      comments=false
      start="data:\n"
      end="template:"
    %}
        ```

    === "Default `imdb_url`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        imdb_url: 
  {%    
    include-markdown "../../../defaults/both/universe.yml" 
    comments=false
    start="imdb_url:\n"
    end="mdblist_url:"
  %}
        ```

    === "Default `mdblist_url`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        mdblist_url: 
  {%    
    include-markdown "../../../defaults/both/universe.yml" 
    comments=false
    start="mdblist_url:\n"
    end="image:"
  %}
        ```
