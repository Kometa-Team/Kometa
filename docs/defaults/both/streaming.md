---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Streaming", 
        "CODE_NAME": "streaming",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "030", 
        "DESCRIPTION": "dynamically create collections based on the streaming Services that your media is available on"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Streaming"}' %}
| `Apple TV+ Movies/Shows`   | `appletv`     | Collection of Movies/Shows Streaming on Apple TV+.   |
| `BET+ Movies/Shows`        | `bet`         | Collection of Movies/Shows Streaming on BET+.        |
| `Channel 4 Movies/Shows`   | `channel4`    | Collection of Movies/Shows Streaming on Channel 4.   |
| `Crave Movies/Shows`       | `crave`       | Collection of Movies/Shows Streaming on Crave.       |
| `Crunchyroll Shows`        | `crunchyroll` | Collection of Shows Streaming on Crunchyroll.        |
| `discovery+ Shows`         | `discovery`   | Collection of Shows Streaming on discovery+.         |
| `Disney+ Movies/Shows`     | `disney`      | Collection of Movies/Shows Streaming on Disney+.     |
| `Hayu Shows`               | `hayu`        | Collection of Shows Streaming on Hulu.               |
| `Hulu Movies/Shows`        | `hulu`        | Collection of Movies/Shows Streaming on Hulu.        |
| `ITVX Movies/Shows`        | `itvx`        | Collection of Movies/Shows Streaming on ITVX.        |
| `Max Movies/Shows`         | `max`         | Collection of Movies/Shows Streaming on Max.         |
| `Netflix Movies/Shows`     | `netflix`     | Collection of Movies/Shows Streaming on Netflix.     |
| `NOW Movies/Shows`         | `now`         | Collection of Movies/Shows Streaming on NOW.         |
| `Paramount+ Movies/Shows`  | `paramount`   | Collection of Movies/Shows Streaming on Paramount+.  |
| `Peacock Movies/Shows`     | `peacock`     | Collection of Movies/Shows Streaming on Peacock.     |
| `Prime Video Movies/Shows` | `amazon`      | Collection of Movies/Shows Streaming on Prime Video. |
| `YouTube Movies/Shows`     | `youtube`     | Collection of Movies/Shows Streaming on YouTube.     |

## Regional Variants

Some logic is applied for specific regions to prevent collections appearing which do not exist in said region.

| Region           | Key                               | Description                                                                                                                                |
|:-----------------|:----------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------|
| `CA`             | `max`, `showtime`                 | These collections will not be created if the region is `CA` as these streaming services are part of the Crave streaming service in Canada. |
| any besides `CA` | `crave`                           | These collections will not be created if the region is not `CA` as these streaming services are Canada-focused.                            |
| any besides `GB` | `all4`, `channel4`, `hayu`, `now` | These collections will not be created if the region is not `GB` as these streaming services are UK-focused.                                |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "streaming"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "streaming"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: streaming
            template_variables:
              region: FR #(1)!
              sep_style: amethyst #(2)!
              visible_library_disney: true #(3)!
              visible_home_disney: true #(4)!
              visible_shared_disney: true #(5)!
              sonarr_add_missing_hulu: true #(6)!
              radarr_add_missing_amazon: true #(7)!
              sort_by: random #(8)!
    ```

    1. Use French region to determine streaming data from JustWatch/TMDb.
    2. Use the amethyst [Separator Style](../separators.md#separator-styles)
    3. Pin the "Disney+ Movies/Shows" collection to the Recommended tab of the library
    4. Pin the "Disney+ Movies/Shows" collection to the home screen of the server owner
    5. Pin the "Disney+ Movies/Shows" collection to the home screen of other users of the server
    6. Add missing shows in your library from the "Hulu Shows" list to your Sonarr
    7. Add missing movies in your library from the "Prime Video Movies" list to your Radarr
    8. Sort all the collections created by this file randomly

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="streaming|limit|sort_by|white-style|sync_mode|format|exclude"
        replace='{
            "DYNAMIC_NAME": "Streaming Services", 
            "DYNAMIC_VALUE": "Streaming Service Keys",
            "NAME_FORMAT": "<<key_name>> <<library_translationU>>s",
            "SUMMARY_FORMAT": "<<library_translationU>>s streaming on <<key_name>>."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Streaming Collections"
        
        The Streaming collections use two builders to create the collections:
        
        If you are not using `originals_only`, the collections are created using [`tmdb_discover`](../../../files/builders/tmdb#discover).
        
        If you are using `originals_only`, the collections are created using Kometa-maintained MDBLists.
