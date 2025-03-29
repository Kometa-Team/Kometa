---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Letterboxd Chart", 
        "CODE_NAME": "letterboxd",
        "LIBRARY_TYPE": "Movie", 
        "DESCRIPTION": "create collections based on lists from Letterboxd",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": "
Recommendations: Users might consider increasing the value set for the Template Variable 
`cache_builders:` as several lists are in excess of 1,000 items and are not updated daily.

The collections `IMDb Top 250 (Letterboxd)`, `Oscar Best Picture Winners`, and `Cannes Palme d\'Or Winners` are turned 
off by default as these collections already exist within other defaults. Refer to the examples below for turning the 
collections on within the Letterboxd defaults using Template Variables.
"}'
    
%}
| `1,001 To See Before You Die`    | `1001_movies`       | Collection of 1,001 Movies You Must See Before You Die.                       |
| `AFI 100 Years 100 Movies`       | `afi_100`           | Collection of AFI's 100 Years...100 Movies.                                   |
| `Box Office Mojo All Time 100`   | `boxofficemojo_100` | Collection of Box Office Mojo's all-time top 100 films.                       |
| `Cannes Palme d'Or Winners`      | `cannes`            | Collection of films that have won the Palme d'Or at the Cannes Film Festival. |
| `Edgar Wright's 1,000 Favorites` | `edgarwright`       | Collection of Edgar Wright's 1,000 Favorite Movies.                           |
| `IMDb Top 250 (Letterboxd)`      | `imdb_top_250`      | Collection of the Top 250 Movies on IMDb, from Letterboxd.                    |
| `Letterboxd Top 250`             | `top_250`           | Collection of the Top 250 films on Letterboxd.                                |
| `Oscar Best Picture Winners`     | `oscars`            | Collection of films that have won the Academy Award for Best Picture.         |
| `Roger Ebert's Great Movies`     | `rogerebert`        | Collection of films from Roger Ebert's "Great Movies" essays.                 |
| `Sight & Sound Greatest Films`   | `sight_sound`       | Collection of Sight and Sound's Greatest Films of All Time.                   |
| `Top 100 Animation`              | `animation`         | Collection of the Top 100 animated films on Letterboxd.                       |
| `Top 100 Black-Directed`         | `black_directors`   | Collection of the Top 100 Black-Directed films on Letterboxd.                 |
| `Top 250 Documentaries`          | `documentaries`     | Collection of the Top 250 documentary films on Letterboxd.                    |
| `Top 250 Horror`                 | `horror`            | Collection of the Top 250 horror films on Letterboxd.                         |
| `Top 250 Most Fans`              | `most_fans`         | Collection of the Top 250 films with the most fans on Letterboxd.             |
| `Top 250 Women-Directed`         | `women_directors`   | Collection of the Top 250 Women-Directed films on Letterboxd.                 |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "letterboxd"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "letterboxd"}' include-tags='all|movie' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: letterboxd
            template_variables:
              use_imdb_top_250: true #(1)!
              use_oscars: true #(2)!
              use_cannes: true #(3)!
              visible_library_top_250: true #(4)!
              visible_home_top_250: true #(5)!
              visible_shared_top_250: true #(6)!
              cache_builders: 7 #(7)!
              cache_builders_1001_movies: 30 #(8)!
              cache_builders_edgarwright: 30 #(9)!
    ```

    1. Create the "IMDb Top 250 (Letterboxd)" collection
    2. Create the "Oscar Best Picture Winners" collection
    3. Create the "Cannes Palme d'Or Winners" collection
    4. Pin the "Letterboxd Top 250" collection to the Recommended tab of the library
    5. Pin the "Letterboxd Top 250" collection to the home screen of the server owner
    6. Pin the "Letterboxd Top 250" collection to the home screen of other users of the server
    7. Set the value for `cache_builders` for all collections (except those explicity defined with `cache_builders_<<key>>`) to 7 days
    8. Set the value for `cache_builders` for the "1,001 To See Before You Die" collection to 30 days
    9. Set the value for `cache_builders` for the "Edgar Wright's 1,000 Favorites" collection to 30 days

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="cache_builders|white-style|limit|sync_mode|collection_order"
        rewrite-relative-urls=false
        replace='{"COLLECTION_ORDER": "`custom`"}'
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Letterboxd Chart Collections"
        
        The Letterboxd Chart collections use [Letterboxd Builders](../../../files/builders/letterboxd) to create the collections.
