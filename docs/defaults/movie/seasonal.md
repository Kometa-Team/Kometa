---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Seasonal", 
        "CODE_NAME": "seasonal",
        "LIBRARY_TYPE": "Movie, Show", 
        "SECTION_NUMBER": "090", 
        "DESCRIPTION": "dynamically create seasonal collections based on holidays"
    }'
%}
{% include-markdown "./../../templates/snippets/separator_line.md" replace='{"SEPARATOR": "Seasonal"}' %}
| `Asian American Pacific Islander Movies` | `aapi`          | Collection of Movies related to Asian American Pacific Islander Month |
| `Black History Month Movies`             | `black_history` | Collection of Movies related to Black History Month                   |
| `Christmas Movies`                       | `christmas`     | Collection of Movies related to Christmas.                            |
| `Disability Month Movies`                | `disabilities`  | Collection of Movies related to Disability Month                      |
| `Easter Movies`                          | `easter`        | Collection of Movies related to Easter.                               |
| `Father's Day Movies`                    | `father`        | Collection of Movies related to Father's Day.                         |
| `Halloween Movies`                       | `halloween`     | Collection of Movies related to Halloween.                            |
| `Independence Day Movies`                | `independence`  | Collection of Movies related to Independence Day.                     |
| `Labor Day Movies`                       | `labor`         | Collection of Movies related to Labor Day.                            |
| `LGBTQ Month Movies`                     | `lgbtq`         | Collection of Movies related to LGBTQ Month                           |
| `Memorial Day Movies`                    | `memorial`      | Collection of Movies related to Memorial Day.                         |
| `Mother's Day Movies`                    | `mother`        | Collection of Movies related to Mother's Day.                         |
| `National Hispanic Heritage Movies`      | `latinx`        | Collection of Movies related to National Hispanic Heritage Month      |
| `New Year's Day Movies`                  | `years`         | Collection of Movies related to New Year's Day.                       |
| `St. Patrick's Day Movies`               | `patrick`       | Collection of Movies related to St. Patrick's Day.                    |
| `Thanksgiving Movies`                    | `thanksgiving`  | Collection of Movies related to Thanksgiving.                         |
| `Valentine's Day Movies`                 | `valentine`     | Collection of Movies related to Valentine's Day.                      |
| `Veteran's Day Movies`                   | `veteran`       | Collection of Movies related to Veteran's Day.                        |
| `Women's History Month Movies`           | `women`         | Collection of Movies related to Women's History Month                 |

{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "seasonal"}' include-tags='all|movie' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: seasonal
            template_variables:
              use_independence: false #(1)!
              schedule_thanksgiving: range(10/01-10/30) #(2)!
              sort_by: random #(3)!
              tmdb_collection_years: #(4)!
                - 1234
                - 5678
              tmdb_movie_valentine: #(5)!
                - 4321
                - 8765
              imdb_list_patrick: https://www.imdb.com/list/ls089196478/ #(6)!
              imdb_search_easter: #(7)!
                list.any:
                  - ls075298827
                  - ls000099714
              trakt_list_mother: #(8)!
                - https://trakt.tv/users/robertsnorlax/lists/arizona-westerns
                - https://trakt.tv/users/pullsa/lists/the-96th-academy-awards-oscars-2024
              mdblist_list_memorial: https://mdblist.com/lists/rizreflects/world-war-related-movies #(9)!
              letterboxd_list_father: https://letterboxd.com/patrickb15/list/fathers-day/ #(10)!
              append_data:
                apes: Planet of the Apes Day #(11)!
              schedule_apes: range(11/24-11/26) #(12)!
              imdb_list_apes: https://www.imdb.com/list/ls005126084/ #(13)!
              emoji_apes: "🐵 " #(14)!
    ```

    1. Do not create the "Independence Day" collection
    2. Set a custom schedule for the Thanksgiving Day collection
    3. Sort the collections created by this file in random order
    4. Add two TMDB collections to the "New Year's Day" collection
    5. Add two movies to the "Valentine's Day" collection
    6. Replace the IMDb List for the "St. Patrick's Day" collection
    7. Add the contents of two IMDB lists to the "Easter" collection
    8. Replace the lists for the "Mother's Day" collection with two Trakt lists
    9. Replace the source list for the "Memorial Day" collection with a MDBList
    10. Replace the source list for the "Father's Day" collection with a Letterboxd list
    11. Create a new Seasonal collection called "Planet of the Apes Day", and set the key for this collection to `apes`
    12. Set a scheduled range for the "Planet of the Apes Day" collection. Planet Of The Apes Day is 11/25.
    13.  Add an IMDb List to be used for the "Planet of the Apes Day" collection
    14.  Add the 🐵 emoji to the "Planet of the Apes Day" collection so that the title in Plex is "🐵 Planet of the Apes Day Movies"

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" rewrite-relative-urls=false %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="seasonal|data|exclude|limit|sort_by|sync_mode|format"
        replace='{
            "DYNAMIC_NAME": "Seasons", 
            "DYNAMIC_VALUE": "Seasons Keys",
            "NAME_FORMAT": "<<key_name>> <<library_translationU>>s",
            "SUMMARY_FORMAT": "A collection of <<key_name>> <<library_translation>>s that may relate to the season."
        }'
        rewrite-relative-urls=false
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" rewrite-relative-urls=false %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}