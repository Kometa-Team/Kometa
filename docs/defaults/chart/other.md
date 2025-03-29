---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Other Chart", 
        "CODE_NAME": "other_chart",
        "LIBRARY_TYPE": "Movie, Show", 
        "DESCRIPTION": "create collections based on other charts",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": "Recommendations: The `StevenLu\'s Popular Movies` and `Top 10 Pirated Movies of the Week` Collections only work with Movie Libraries."}'
%}
| `AniDB Popular`                     | `anidb`       | Collection of the most Popular Anime on AniDB.       |
| `Common Sense Selection`            | `commonsense` | Collection of Common Sense Selection Movies/Shows.   |
| `Metacritic Must See Movies`        | `metacritic`  | Collection of Metacritic Must See Movies.            |
| `StevenLu's Popular Movies`         | `stevenlu`    | Collection of StevenLu's Popular Movies.             |
| `Top 10 Pirated Movies of the Week` | `pirated`     | Collection of the Top 10 Pirated Movies of the Week. |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "other_chart"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "other_chart"}' include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: other_chart
            template_variables:
              use_anidb: false #(1)!
              visible_library_commonsense: true #(2)!
              visible_home_commonsense: true #(3)!
              visible_shared_commonsense: true #(4)!
    ```

    1. Do not create the "AniDB Popular" collection
    2. Pin the "Common Sense Selection" collection to the Recommended tab of the library
    3. Pin the "Common Sense Selection" collection to the home screen of the server owner
    4. Pin the "Common Sense Selection" collection to the home screen of other users of the server

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="white-style|limit_anidb|sync_mode|collection_order"
        rewrite-relative-urls=false
        replace='{"COLLECTION_ORDER": "`custom`"}'
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Other Chart Collections"
        
        The collections created here use a variety of sources.
        
        | Collection                          | Source                                                                                                                                                                                                                                             |
        |:------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `AniDB Popular`                     | [`anidb_popular` Builder](../../../files/builders/anidb#anidb-popular)                                                                                                                                                                                        |
        | `Common Sense Selection`            | Sourced from mdblist:<br>[`https://mdblist.com/lists/k0meta/cssfamiliesmovies`](https://mdblist.com/lists/k0meta/cssfamiliesmovies) or<br>[`https://mdblist.com/lists/k0meta/cssfamiliesshows`](https://mdblist.com/lists/k0meta/cssfamiliesshows) |
        | `StevenLu's Popular Movies`         | [`stevenlu_popular` Builder](../../../files/builders/stevenlu)                                                                                                                                                                                  |
        | `Top 10 Pirated Movies of the Week` | Sourced from mdblist:<br>[`https://mdblist.com/lists/hdlists/top-ten-pirated-movies-of-the-week-torrent-freak-com/`](https://mdblist.com/lists/hdlists/top-ten-pirated-movies-of-the-week-torrent-freak-com/)                                      |
