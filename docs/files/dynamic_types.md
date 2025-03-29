---
hide:
  - toc
---
# Dynamic Collection Types & Data

Every dynamic collection definition requires the `type` attribute which determines the attribute used to dynamically 
create collections.

Depending on the `type` of dynamic collection, `data` is used to specify the options that are required to fulfill the 
requirements of creating the collection.

??? blank "`tmdb_collection` - Collections based on TMDb Collections.<a class="headerlink" href="#tmdb-collection" title="Permanent link">¶</a>"

    <div id="tmdb-collection" />Creates collections based on the TMDb Collections associated with items in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `tmdb_collection`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies
    
    **Key Values:** TMDb Collection ID

    **Key Name Value:** TMDb Collection Title

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          tmdb_collection_details: <<value>>
          minimum_items: 2
        ```

    ???+ example "Example"
        
        ```yaml
        dynamic_collections:
          TMDb Collections:          # This name is the mapping name
            type: tmdb_collection
            remove_suffix: Collection
            remove_prefix: The
        ```

??? blank "`tmdb_popular_people` - Collections based on actors found on [TMDb's Popular People List](https://www.themoviedb.org/person).<a class="headerlink" href="#tmdb-popular-people" title="Permanent link">¶</a>"

    <div id="tmdb-popular-people" />Creates collections based on each actor found on 
    [TMDb's Popular People List](https://www.themoviedb.org/person).

    <hr style="margin: 0px;">
    
    **`type` Value:** `tmdb_popular_people`

    **`data` Value:** Number greater than 0

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** TMDb Person ID

    **Key Name Value:** TMDb Person Name

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          tmdb_person: <<value>>
          plex_search:
            all:
              actor: tmdb
        ```

    ???+ example "Example"

        Creates a collection for the top 10 popular people according to TMDb.
        
        ```yaml
        dynamic_collections:
          TMDb Popular People:          # This name is the mapping name
            type: tmdb_popular_people
            data: 10
        ```

??? blank "`original_language` - Collections based on TMDb original languages.<a class="headerlink" href="#original-language" title="Permanent link">¶</a>"

    <div id="original-language" />Creates collections based on the TMDb original language associated with items in the 
    library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `original_language`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** [ISO 639-1 Code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

    **Key Name Value:** ISO Language Name

    **Default `title_format`:** `<<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          plex_all: true
          filters:
            original_language: <<value>>
        ```

    ???+ example "Example"
        
        ```yaml
        dynamic_collections:
          TMDb Languages:          # This name is the mapping name
            type: original_language
        ```

??? blank "`origin_country` - Collections based on TMDb origin countries.<a class="headerlink" href="#origin-country" title="Permanent link">¶</a>"

    <div id="origin-country" />Creates collections based on the TMDb origin country associated with items in the 
    library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `origin_country`

    **`data` Value:** Not Used

    **Valid Library Types:** Shows
    
    **Key Values:** [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)

    **Key Name Value:** ISO Country Name

    **Default `title_format`:** `<<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          plex_all: true
          filters:
            origin_country: <<value>>
        ```

    ???+ example "Example"
        
        ```yaml
        dynamic_collections:
          TMDb Countries:          # This name is the mapping name
            type: origin_country
        ```

??? blank "`imdb_awards` - Collections based on IMDb Events by Year.<a class="headerlink" href="#imdb-awards" title="Permanent link">¶</a>"

    <div id="imdb-awards" />Creates collections for each of the Year's found on the IMDb event page.

    <hr style="margin: 0px;">
    
    **`type` Value:** `imdb_awards`

    **`data` Value:** [Dictionary](../kometa/yaml.md#dictionaries) of Attributes

    ??? blank "`event_id` - Determines the [IMDb Event](https://www.imdb.com/event/) used.<a class="headerlink" href="#imdb-awards-event-id" title="Permanent link">¶</a>"
        
        <div id="imdb-awards-event-id" />This determines which [IMDb Event](https://www.imdb.com/event/) is used. 

        **Allowed Values:** The ID found in the URLs linked on the [IMDb Events Page](https://www.imdb.com/event/). 
        (ex. `ev0000003`)

    ??? blank "`starting` - Determines the starting year of the event to use.<a class="headerlink" href="#imdb-awards-starting" title="Permanent link">¶</a>"
        
        <div id="imdb-awards-starting" />This determines the starting year of the event to use to create collections.

        **Allowed Values:** Number greater than 0, `first`, `latest`, relative first (`first+#`; where `#` is the number
        of events past the first event), or relative latest (`latest-#`; where `#` is the number of events back from the
        latest)

        **Default:** `first`

    ??? blank "`ending` - Determines the ending year of the event to use.<a class="headerlink" href="#imdb-awards-ending" title="Permanent link">¶</a>"
        
        <div id="imdb-awards-ending" />This determines the ending year of the event to use to create collections. 

        **Allowed Values:** Number greater than 0, `first`, `latest`, relative first (`first+#`; where `#` is the number
        of events past the first event), or relative latest (`latest-#`; where `#` is the number of events back from the
        latest)

        **Default:** `latest`

    ??? blank "`increment` - Determines amount incremented.<a class="headerlink" href="#number-increment" title="Permanent link">¶</a>"
        
        <div id="number-increment" />Determines the amount incremented from one collection to the other.

        **Allowed Values:** Number greater than 0

        **Default:** `1`

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** Award Year (sometimes this will look like `2003-2` if there are more than one award show that year) 

    **Key Name Value:** Award Year (sometimes this will look like `2003-2` if there are more than one award show that 
    year)

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          imdb_award: 
            event_id: <<event_id>>
            event_year: <<value>>
            winning: true
        ```

    ???+ example "Example"
        
        ```yaml
        dynamic_collections:
          Oscar Awards Lists:          # This name is the mapping name
            type: imdb_awards
            data:
              event_id: ev0000003
              starting: latest-15
              ending: latest
        ```

??? blank "`letterboxd_user_lists` - Collections based on the Lists of Letterboxd Users.<a class="headerlink" href="#letterboxd-user-lists" title="Permanent link">¶</a>"

    <div id="letterboxd-user-lists" />Creates collections for each of the Letterboxd lists that the user has created.

    <hr style="margin: 0px;">
    
    **`type` Value:** `letterboxd_user_lists`

    **`data` Value:** [Dictionary](../kometa/yaml.md#dictionaries) of Attributes

    ??? blank "`username` - Determines the Usernames to scan for lists.<a class="headerlink" href="#letterboxd-user-lists-username" title="Permanent link">¶</a>"
        
        <div id="letterboxd-user-lists-username" />This determines which Usernames are scanned. 

        **Allowed Values:** Username or list of Usernames

    ??? blank "`sort_by` - Determines the sort that the lists are returned.<a class="headerlink" href="#letterboxd-user-lists-sort-by" title="Permanent link">¶</a>"
        
        <div id="letterboxd-user-lists-sort-by" />Determines the sort that the lists are returned.

        **Allowed Values:** `updated`, `name`, `popularity`, `newest`, `oldest`

        **Default:** `updated`

    ??? blank "`limit` - Determines the number of lists to create collections for.<a class="headerlink" href="#letterboxd-user-lists-limit" title="Permanent link">¶</a>"
        
        <div id="letterboxd-user-lists-limit" />Determines the number of lists to create collections for. (`0` is all lists)

        **Allowed Values:** Number 0 or greater

        **Default:** `0`

    **Valid Library Types:** Movies
    
    **Key Values:** Letterboxd List URL

    **Key Name Value:** Letterboxd List Title

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          letterboxd_list_details: <<value>>
        ```

    ???+ example "Example"
        
        ```yaml
        dynamic_collections:
          Letterboxd User Lists:          # This name is the mapping name
            type: letterboxd_user_lists
            data:
              username: thebigpictures
              limit: 5
        ```

??? blank "`trakt_user_lists` - Collections based on Trakt Lists by users.<a class="headerlink" href="#trakt-user-lists" title="Permanent link">¶</a>"

    <div id="trakt-user-lists" />Creates collections for each of the Trakt lists for the specified users. Use `me` to 
    reference the authenticated user.

    ???+ warning

        Requires [Trakt Authentication](../config/trakt.md) to be configured within the Configuration File.

    <hr style="margin: 0px;">
    
    **`type` Value:** `trakt_user_lists`

    **`data` Value:** List of Trakt Users (Use `me` to reference the authenticated user)

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** Trakt List URL

    **Key Name Value:** Trakt List Title

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          trakt_list_details: <<value>>
        ```

    ???+ example "Example"
        
        ```yaml
        dynamic_collections:
          Trakt User Lists:          # This name is the mapping name
            type: trakt_user_lists
            data:
             - me
             - yozoraxcii
        ```

??? blank "`trakt_liked_lists` - Collections based on liked Trakt Lists.<a class="headerlink" href="#trakt-liked-lists" title="Permanent link">¶</a>"

    <div id="trakt-liked-lists" />Creates collections for each of the Trakt lists that the authenticated user has liked.

    ???+ warning

        Requires [Trakt Authentication](../config/trakt.md) to be configured within the Configuration File.

    <hr style="margin: 0px;">
    
    **`type` Value:** `trakt_liked_lists`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** Trakt List URL

    **Key Name Value:** Trakt List Title

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          trakt_list_details: <<value>>
        ```

    ???+ example "Example"
        
        ```yaml
        dynamic_collections:
          Trakt Liked Lists:          # This name is the mapping name
            type: trakt_liked_lists
        ```

??? blank "`trakt_people_list` - Collections based on people on Trakt Lists.<a class="headerlink" href="#trakt-people-list" title="Permanent link">¶</a>"

    <div id="trakt-people-list" />Creates collections for each of the people found within Trakt lists that the user 
    specifies.

    ???+ warning

        Requires [Trakt Authentication](../config/trakt.md) to be configured within the Configuration File.

    <hr style="margin: 0px;">
    
    **`type` Value:** `trakt_people_list`

    **`data` Value:** List of Trakt URLs

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** TMDb Person ID

    **Key Name Value:** TMDb Person Name

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          tmdb_person: <<value>>
          plex_search:
            all:
              actor: tmdb
        ```

    ???+ example "Example"
        
        ```yaml
        dynamic_collections:
          Trakt People Lists:
            type: trakt_people_list
            data:
             - https://trakt.tv/users/ash9001/lists/all-time-top-actors
        ```

??? blank "`actor` - Collections based on actor credits.<a class="headerlink" href="#actor" title="Permanent link">¶</a>"

    <div id="actor" />Creates collections for each actor found in the library based on given criteria.

    <hr style="margin: 0px;">
    
    **`type` Value:** `actor`

    **`data` Value:** [Dictionary](../kometa/yaml.md#dictionaries) of Attributes

    ??? blank "`depth` - Determines how many "top" acting credits per item.<a class="headerlink" href="#actor-depth" title="Permanent link">¶</a>"
        
        <div id="actor-depth" />This determines how many "top" acting credits there are for each item. Acting credits 
        are parsed in top billing order. 

        **Allowed Values:** Number greater than 0

        **Default:** `3`

    ??? blank "`minimum` - Determines the minimum number of "top" acting credits.<a class="headerlink" href="#actor-minimum" title="Permanent link">¶</a>"
        
        <div id="actor-minimum" />Determines the minimum number of "top" acting credits. For a collection for this actor
        to be created they must meet the minimum number of "top" acting credits.
        
        ???+ warning

            The number of "top" acting credits per item is determined by the `depth` value.

        **Allowed Values:** Number greater than 0

        **Default:** `3`

    ??? blank "`limit` - Determines the maximum number of actor collections to create.<a class="headerlink" href="#actor-limit" title="Permanent link">¶</a>"
        
        <div id="actor-limit" />Determines the maximum number of actor collections to create.

        **Allowed Values:** Number greater than 0

        **Default:** None

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** Person Name

    **Key Name Value:** Person Name

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          plex_search:
            any:
              actor: <<value>>
        ```

    ???+ example "Examples"
        
        This example creates a collection for each of the top 25 actors who appear in the "top" 5 acting credits of an 
        item in the library.
        
        ```yaml
        dynamic_collections:
          Top Actors:         # mapping name does not matter just needs to be unique
            type: actor
            data:
              depth: 5
              limit: 25
        ```

        This example creates a collection for each of the actors who appear in the "top" 5 acting credits of an item in 
        the library for at least 20 items.

        ```yaml
        dynamic_collections:
          Actors:         # mapping name does not matter just needs to be unique
            type: actor
            data:
              depth: 5
              minimum: 20
        ```

??? blank "`director` - Collections based on directors.<a class="headerlink" href="#director" title="Permanent link">¶</a>"

    <div id="director" />Creates collections for each director found in the library based on given criteria.

    <hr style="margin: 0px;">
    
    **`type` Value:** `director`

    **`data` Value:** [Dictionary](../kometa/yaml.md#dictionaries) of Attributes

    ??? blank "`depth` - Determines how many "top" directing credits per item.<a class="headerlink" href="#director-depth" title="Permanent link">¶</a>"
        
        <div id="director-depth" />This determines how many "top" directing credits there are for each item. Directing 
        credits are parsed in top billing order. 

        **Allowed Values:** Number greater than 0

        **Default:** `3`

    ??? blank "`minimum` - Determines the minimum number of "top" directing credits.<a class="headerlink" href="#director-minimum" title="Permanent link">¶</a>"
        
        <div id="director-minimum" />Determines the minimum number of "top" directing credits. For a collection for this 
        director to be created they must meet the minimum number of "top" directing credits.
        
        ???+ warning

            The number of "top" directing credits per item is determined by the `depth` value.

        **Allowed Values:** Number greater than 0

        **Default:** `3`

    ??? blank "`limit` - Determines the maximum number of director collections to create.<a class="headerlink" href="#director-limit" title="Permanent link">¶</a>"
        
        <div id="director-limit" />Determines the maximum number of director collections to create.

        **Allowed Values:** Number greater than 0

        **Default:** None

    **Valid Library Types:** Movies
    
    **Key Values:** Person Name

    **Key Name Value:** Person Name

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          plex_search:
            any:
              director: <<value>>
        ```

    ???+ example "Examples"

        This example creates a collection for the each of the top 5 directors who appear as the "top" directing credits 
        of movies.
        
        ```yaml
        dynamic_collections:
          Top Directors:         # mapping name does not matter just needs to be unique
            type: director
            data:
              depth: 1
              limit: 5
        ```

        This example creates a collection for the each of the directors who appear as the "top" directing credits of 
        movies the library for at least 10 movies.
        
        ```yaml
        dynamic_collections:
          Directors:         # mapping name does not matter just needs to be unique
            type: director
            data:
              depth: 1
              minimum: 10
        ```

??? blank "`writer` - Collections based on writers.<a class="headerlink" href="#director" title="Permanent link">¶</a>"

    <div id="director" />Creates collections for each writer found in the library based on given criteria.

    <hr style="margin: 0px;">
    
    **`type` Value:** `writer`

    **`data` Value:** [Dictionary](../kometa/yaml.md#dictionaries) of Attributes

    ??? blank "`depth` - Determines how many "top" writing credits per item.<a class="headerlink" href="#writer-depth" title="Permanent link">¶</a>"
        
        <div id="writer-depth" />This determines how many "top" writing credits there are for each item. Writing credits
        are parsed in top billing order. 

        **Allowed Values:** Number greater than 0

        **Default:** `3`

    ??? blank "`minimum` - Determines the minimum number of "top" writing credits.<a class="headerlink" href="#writer-minimum" title="Permanent link">¶</a>"
        
        <div id="writer-minimum" />Determines the minimum number of "top" writing credits. For a collection for this 
        writer to be created they must meet the minimum number of "top" writing credits.
        
        ???+ warning

            The number of "top" writing credits per item is determined by the `depth` value.

        **Allowed Values:** Number greater than 0

        **Default:** `3`

    ??? blank "`limit` - Determines the maximum number of writer collections to create.<a class="headerlink" href="#writer-limit" title="Permanent link">¶</a>"
        
        <div id="writer-limit" />Determines the maximum number of writer collections to create.

        **Allowed Values:** Number greater than 0

        **Default:** None

    **Valid Library Types:** Movies
    
    **Key Values:** Person Name

    **Key Name Value:** Person Name

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          plex_search:
            any:
              writer: <<value>>
        ```

    ???+ example "Examples"

        This example creates a collection for the each of the top 5 writers who appear as the "top" writing credits of 
        movies.
        
        ```yaml
        dynamic_collections:
          Top Writers:         # mapping name does not matter just needs to be unique
            type: writer
            data:
              depth: 1
              limit: 5
        ```

        This example creates a collection for the each of the writers who appear as the "top" writing credits of movies
        the library for at least 10 movies.
        
        ```yaml
        dynamic_collections:
          Writers:         # mapping name does not matter just needs to be unique
            type: writer
            data:
              depth: 1
              minimum: 10
        ```

??? blank "`producer` - Collections based on producers.<a class="headerlink" href="#director" title="Permanent link">¶</a>"

    <div id="director" />Creates collections for each producer found in the library based on given criteria.

    <hr style="margin: 0px;">
    
    **`type` Value:** `producer`

    **`data` Value:** [Dictionary](../kometa/yaml.md#dictionaries) of Attributes

    ??? blank "`depth` - Determines how many "top" producing credits per item.<a class="headerlink" href="#producer-depth" title="Permanent link">¶</a>"
        
        <div id="producer-depth" />This determines how many "top" producing credits there are for each item. Producing
        credits are parsed in top billing order. 

        **Allowed Values:** Number greater than 0

        **Default:** `3`

    ??? blank "`minimum` - Determines the minimum number of "top" producing credits.<a class="headerlink" href="#producer-minimum" title="Permanent link">¶</a>"
        
        <div id="producer-minimum" />Determines the minimum number of "top" producing credits. For a collection for this 
        producer to be created they must meet the minimum number of "top" producing credits.
        
        ???+ warning

            The number of "top" producing credits per item is determined by the `depth` value.

        **Allowed Values:** Number greater than 0

        **Default:** `3`

    ??? blank "`limit` - Determines the maximum number of producer collections to create.<a class="headerlink" href="#producer-limit" title="Permanent link">¶</a>"
        
        <div id="producer-limit" />Determines the maximum number of producer collections to create.

        **Allowed Values:** Number greater than 0

        **Default:** None

    **Valid Library Types:** Movies
    
    **Key Values:** Person Name

    **Key Name Value:** Person Name

    **Default `title_format`:** `<<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          plex_search:
            any:
              producer: <<value>>
        ```

    ???+ example "Examples"

        This example creates a collection for the each of the top 5 producers who appear as the "top" producing credits 
        of movies.
        
        ```yaml
        dynamic_collections:
          Top Producers:         # mapping name does not matter just needs to be unique
            type: producer
            data:
              depth: 1
              limit: 5
        ```

        This example creates a collection for the each of the producers who appear as the "top" producing credits of 
        movies the library for at least 10 movies.
        
        ```yaml
          Producers:         # mapping name does not matter just needs to be unique
            type: producers
            data:
              depth: 1
              minimum: 10
        ```

??? blank "`genre` - Collections based on genres.<a class="headerlink" href="#genre" title="Permanent link">¶</a>"

    <div id="genre" />Creates collections for each genre found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `genre`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies, Shows, Music, and Video
    
    **Key Values:** Genre

    **Key Name Value:** Genre

    **Default `title_format`:** `Top <<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.desc
            any:
              genre: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each genre found in the library. 
        
        ```yaml
        dynamic_collections:
          Genres:         # mapping name does not matter just needs to be unique
            type: genre
        ```

??? blank "`album_genre` - Collections based on album genres.<a class="headerlink" href="#album-genre" title="Permanent link">¶</a>"

    <div id="album-genre" />Creates album collections for each genre associated with albums found in the music library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `genre`

    **`data` Value:** Not Used

    **Valid Library Types:** Music
    
    **Key Values:** Genre

    **Key Name Value:** Genre

    **Default `title_format`:** `Top <<key_name>> Albums`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          builder_level: album
          smart_filter:
            limit: 50
            sort_by: plays.desc
            any:
              album_genre: <<value>>
        ```

    ???+ example "Example"

        This example creates album collections for each genre associated with albums found in the music library.
        
        ```yaml
        dynamic_collections:
          Genres:         # mapping name does not matter just needs to be unique
            type: album_genre
        ```

??? blank "`content_rating` - Collections based on content ratings.<a class="headerlink" href="#content-rating" title="Permanent link">¶</a>"

    <div id="content-rating" />Creates collections for each content rating found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `content_rating`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies, Shows, and Video
    
    **Key Values:** Content Rating

    **Key Name Value:** Content Rating

    **Default `title_format`:** `Top <<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.desc
            any:
              content_rating: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each genre found in the library. 
        
        ```yaml
        dynamic_collections:
          Content Ratings:         # mapping name does not matter just needs to be unique
            type: content_rating
        ```

??? blank "`year` - Collections based on content ratings.<a class="headerlink" href="#year" title="Permanent link">¶</a>"

    <div id="year" />Creates collections for each year found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `year`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** Year

    **Key Name Value:** Year

    **Default `title_format`:** `Best <<library_type>>s of <<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.desc
            any:
              year: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each year found in the library. 
        
        ```yaml
        dynamic_collections:
          Years:         # mapping name does not matter just needs to be unique
            type: year
        ```

??? blank "`episode_year` - Collections based on content ratings.<a class="headerlink" href="#episode-year" title="Permanent link">¶</a>"

    <div id="episode-year" />Creates collections for each year associated with episodes found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `episode_year`

    **`data` Value:** Not Used

    **Valid Library Types:** Shows
    
    **Key Values:** Year

    **Key Name Value:** Year

    **Default `title_format`:** `Best Episodes of <<key_name>>`

    ??? tip "Default Template (click to expand)"

        ```yaml
        default_template:
          builder_level: episode
          smart_filter:
            limit: 50
            sort_by: critic_rating.desc
            any:
              year: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each year found in the library. 
        
        ```yaml
        dynamic_collections:
          Years:         # mapping name does not matter just needs to be unique
            type: year
        ```

??? blank "`decade` - Collections based on decades.<a class="headerlink" href="#decade" title="Permanent link">¶</a>"

    <div id="decade" />Creates collections for each decade found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `decade`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** Decade

    **Key Name Value:** Decade with an `s` at the end

    **Default `title_format`:** `Best <<library_type>> of the <<key_name>>`

    ??? tip "Default Templates (click to expand)"
        
        === "Movie Default"

            ```yaml
            default_template:
              smart_filter:
                limit: 50
                sort_by: critic_rating.desc
                any:
                  decade: <<value>>
            ```

        === "Show Default"

            Shows don't inherently have a decade attribute so Kometa just passes all years from the decade as a list.

            ```yaml
            default_template:
              smart_filter:
                limit: 50
                sort_by: critic_rating.desc
                any:
                  year: <<value>>
            ```

    ???+ example "Example"

        This example creates collections based on each decade found in the library. 
        
        ```yaml
        dynamic_collections:
          Decades:         # mapping name does not matter just needs to be unique
            type: decade
        ```

??? blank "`country` - Collections based on countries.<a class="headerlink" href="#country" title="Permanent link">¶</a>"

    <div id="country" />Creates collections for each country found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `country`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies, Music, Video
    
    **Key Values:** Country

    **Key Name Value:** Country

    **Default `title_format`:** `Top <<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.desc
            any:
              country: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each country found in the library. 
        
        ```yaml
        dynamic_collections:
          Countries:         # mapping name does not matter just needs to be unique
            type: country
        ```

??? blank "`resolution` - Collections based on resolutions.<a class="headerlink" href="#resolution" title="Permanent link">¶</a>"

    <div id="resolution" />Creates collections for each resolution found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `resolution`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** Resolution

    **Key Name Value:** Resolution

    **Default `title_format`:** `<<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: title.asc
            any:
              resolution: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each resolution found in the library. 
        
        ```yaml
        dynamic_collections:
          Resolutions:         # mapping name does not matter just needs to be unique
            type: resolution
        ```

??? blank "`subtitle_language` - Collections based on subtitle languages.<a class="headerlink" href="#subtitle-language" title="Permanent link">¶</a>"

    <div id="subtitle-language" />Creates collections for each subtitle language found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `subtitle_language`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** [ISO 639-1 Code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

    **Key Name Value:** ISO Language Name

    **Default `title_format`:** `Top <<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.asc
            any:
              subtitle_language: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each subtitle language found in the library. 
        
        ```yaml
        dynamic_collections:
          Subtitle Languages:         # mapping name does not matter just needs to be unique
            type: subtitle_language
        ```

??? blank "`audio_language` - Collections based on audio languages.<a class="headerlink" href="#audio-language" title="Permanent link">¶</a>"

    <div id="audio-language" />Creates collections for each audio language found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `audio_language`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** [ISO 639-1 Code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

    **Key Name Value:** ISO Language Name

    **Default `title_format`:** `Top <<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.asc
            any:
              audio_language: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each audio language found in the library. 
        
        ```yaml
        dynamic_collections:
          Audio Languages:         # mapping name does not matter just needs to be unique
            type: audio_language
        ```

??? blank "`studio` - Collections based on studios.<a class="headerlink" href="#studio" title="Permanent link">¶</a>"

    <div id="studio" />Creates collections for each studio found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `studio`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies and Shows
    
    **Key Values:** Studio

    **Key Name Value:** Studio

    **Default `title_format`:** `Top <<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.asc
            any:
              studio: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each studio found in the library. 
        
        ```yaml
        dynamic_collections:
          Studios:         # mapping name does not matter just needs to be unique
            type: studio
        ```

??? blank "`edition` - Collections based on editions.<a class="headerlink" href="#edition" title="Permanent link">¶</a>"

    <div id="edition" />Creates collections for each edition found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `edition`

    **`data` Value:** Not Used

    **Valid Library Types:** Movies
    
    **Key Values:** Edition

    **Key Name Value:** Edition

    **Default `title_format`:** `Top <<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.asc
            any:
              edition: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each edition found in the library. 
        
        ```yaml
        dynamic_collections:
          Editions:         # mapping name does not matter just needs to be unique
            type: edition
        ```

??? blank "`network` - Collections based on networks.<a class="headerlink" href="#network" title="Permanent link">¶</a>"

    <div id="network" />Creates collections for each network found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `network`

    **`data` Value:** Not Used

    **Valid Library Types:** Shows
    
    **Key Values:** Network

    **Key Name Value:** Network

    **Default `title_format`:** `Top <<key_name>> <<library_type>>s`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 50
            sort_by: critic_rating.asc
            any:
              network: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each network found in the library. 
        
        ```yaml
        dynamic_collections:
          Networks:         # mapping name does not matter just needs to be unique
            type: network
        ```

??? blank "`mood` - Collections based on artist moods.<a class="headerlink" href="#mood" title="Permanent link">¶</a>"

    <div id="mood" />Creates collections for each mood associated with an artist found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `mood`

    **`data` Value:** Not Used

    **Valid Library Types:** Music
    
    **Key Values:** Mood

    **Key Name Value:** Mood

    **Default `title_format`:** `Most Played <<key_name>> Artists`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 10
            sort_by: plays.desc
            any:
              artist_mood: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each artist mood found in the library. 
        
        ```yaml
        dynamic_collections:
          Moods:         # mapping name does not matter just needs to be unique
            type: mood
        ```

??? blank "`album_mood` - Collections based on album moods.<a class="headerlink" href="#album-mood" title="Permanent link">¶</a>"

    <div id="album-mood" />Creates collections for each mood associated with an album found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `album_mood`

    **`data` Value:** Not Used

    **Valid Library Types:** Music
    
    **Key Values:** Mood

    **Key Name Value:** Mood

    **Default `title_format`:** `Most Played <<key_name>> Albums`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          builder_level: album
          smart_filter:
            limit: 10
            sort_by: plays.desc
            any:
              album_mood: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each album mood found in the library. 
        
        ```yaml
        dynamic_collections:
          Moods:         # mapping name does not matter just needs to be unique
            type: album_mood
        ```

??? blank "`track_mood` - Collections based on track moods.<a class="headerlink" href="#track-mood" title="Permanent link">¶</a>"

    <div id="track-mood" />Creates collections for each mood associated with a track found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `track_mood`

    **`data` Value:** Not Used

    **Valid Library Types:** Music
    
    **Key Values:** Mood

    **Key Name Value:** Mood

    **Default `title_format`:** `Most Played <<key_name>> Tracks`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          builder_level: track
          smart_filter:
            limit: 50
            sort_by: plays.desc
            any:
              track_mood: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each track mood found in the library. 
        
        ```yaml
        dynamic_collections:
          Moods:         # mapping name does not matter just needs to be unique
            type: track_mood
        ```

??? blank "`style` - Collections based on artist styles.<a class="headerlink" href="#style" title="Permanent link">¶</a>"

    <div id="style" />Creates collections for each style associated with an artist found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `style`

    **`data` Value:** Not Used

    **Valid Library Types:** Music
    
    **Key Values:** Style

    **Key Name Value:** Style

    **Default `title_format`:** `Most Played <<key_name>> Artists`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          smart_filter:
            limit: 10
            sort_by: plays.desc
            any:
              artist_style: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each artist style found in the library. 
        
        ```yaml
        dynamic_collections:
          Styles:         # mapping name does not matter just needs to be unique
            type: style
        ```

??? blank "`album_style` - Collections based on album styles.<a class="headerlink" href="#album-style" title="Permanent link">¶</a>"

    <div id="album-style" />Creates collections for each style associated with an album found in the library.

    <hr style="margin: 0px;">
    
    **`type` Value:** `album_style`

    **`data` Value:** Not Used

    **Valid Library Types:** Music
    
    **Key Values:** Style

    **Key Name Value:** Style

    **Default `title_format`:** `Most Played <<key_name>> Artists`

    ??? tip "Default Template (click to expand)"
       
        ```yaml
        default_template:
          builder_level: album
          smart_filter:
            limit: 10
            sort_by: plays.desc
            any:
              album_style: <<value>>
        ```

    ???+ example "Example"

        This example creates collections based on each album style found in the library. 
        
        ```yaml
        dynamic_collections:
          Styles:         # mapping name does not matter just needs to be unique
            type: album_style
        ```

??? blank "`number` - Collections based on defined numbers.<a class="headerlink" href="#number" title="Permanent link">¶</a>"

    <div id="number" />Creates collections for each number based on given criteria.

    <hr style="margin: 0px;">
    
    **`type` Value:** `number`

    **`data` Value:** [Dictionary](../kometa/yaml.md#dictionaries) of Attributes

    ??? blank "`starting` - Determines the starting number.<a class="headerlink" href="#number-starting" title="Permanent link">¶</a>"
        
        <div id="number-starting" />This determines the starting number of collections to create.

        **Allowed Values:** Number greater than 0, `current_year`, or relative year `current_year-#` (`#` is the number 
        of years back from the current year)

        **Default:** `0`

    ??? blank "`ending` - Determines the ending number.<a class="headerlink" href="#number-ending" title="Permanent link">¶</a>"
        
        <div id="number-ending" />This determines the ending number of collections to create. 
        
        **Allowed Values:** Number greater than 1, `current_year`, or relative year `current_year-#` (`#` is the number 
        of years back from the current year)

        **Default:** `1`

    ??? blank "`increment` - Determines amount incremented.<a class="headerlink" href="#number-increment" title="Permanent link">¶</a>"
        
        <div id="number-increment" />Determines the amount incremented from one collection to the other.

        **Allowed Values:** Number greater than 0

        **Default:** `1`

    **Valid Library Types:** Movies, Shows, Music, and Video
    
    **Key Values:** Number

    **Key Name Value:** Number

    **Default `title_format`:** `<<key_name>>`

    ???+ warning

        There's no default template for this type one has to be specified.

    ???+ example "Example"

        This example create a collection for the Oscar Winner by Year for the last 5 years and names the collection 
        "Oscars Winners [Number]".
        
        ```yaml
        templates:
          Oscars:
            summary: Academy Awards (Oscars) Winners for <<key>>
            imdb_search:
              release.after: <<key>>-01-01
              release.before: <<key>>-12-31
              event.winning: oscar_picture, oscar_director
              sort_by: popularity.asc
            sync_mode: sync
            collection_order: custom
        dynamic_collections:
          Oscars Winners Awards:
            type: number
            sync: true
            data:
              starting: current_year-5
              ending: current_year
            title_format: Oscars Winners <<key_name>>
            template:
              - Oscars
        ```

??? blank "`custom` - Collections based on given values.<a class="headerlink" href="#custom" title="Permanent link">¶</a>"

    <div id="custom" />Creates collections for each custom `dynamic key: key_name` pair defined.

    <hr style="margin: 0px;">
    
    **`type` Value:** `custom`

    **`data` Value:** [Dictionary](../kometa/yaml.md#dictionaries) with the keys being the `dynamic key` and the values 
    being the `key name`

    **Valid Library Types:** Movies, Shows, Music, and Video
    
    **Key Values:** `dynamic key`

    **Key Name Value:** `key_name`

    **Default `title_format`:** `<<key_name>>`

    ???+ warning

        There's no default template for this type one has to be specified.

    ???+ example "Example"

        This example creates a collection for the various Streaming Services and names them "[Key Name] Movies".
        
        ```yaml
        templates:
          streaming:
            cache_builders: 1
            smart_label: release.desc
            sync_mode: sync
            mdblist_list: https://mdblist.com/lists/k0meta/<<key>>-movies
            url_poster: https://raw.githubusercontent.com/Kometa-Team/Default-Images/master/streaming/<<key_name_encoded>>.jpg
        
        dynamic_collections:
          Streaming:
            type: custom
            data:
              all-4: All 4
              appletv: Apple TV+
              bet: BET+
              itvx: ITVX
              disney: Disney+
              max: Max
              hulu: Hulu
              netflix: Netflix
              now: NOW
              paramount: Paramount+
              peacock: Peacock
              amazon-prime-video: Prime Video
            title_format: <<key_name>> Movies
            template:
              - streaming
              - shared
        ```

{% include-markdown "./../templates/snippets/dynamic_examples.md" %}