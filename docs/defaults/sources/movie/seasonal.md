# Seasonal Collections

??? example "Default `data` (click to expand) <a class="headerlink" href="#data" title="Permanent link">¶</a>"

    <div id="data" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    data: {%    
      include-markdown "../../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=false
      start="data:"
      end="title_format:"
    %}
    ```

??? example "Default Template Variable `emoji` (click to expand) <a class="headerlink" href="#emoji" title="Permanent link">¶</a>"

    <div id="emoji" />
    
    ???+ tip 
    
        Pass `emoji_<<key>>` to the file as template variables to change this value per collection.

        ```yaml
          - default: seasonal
            template_variables:
              emoji_easter: "🥚 "
        ```

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check1"
      end="# check2"
    %}
    ```

??? example "Default Template Variable `schedule` (click to expand) <a class="headerlink" href="#schedule" title="Permanent link">¶</a>"

    <div id="schedule" />
    
    ???+ tip 
    
        Pass `schedule_<<key>>` to the file as template variables to change this value per collection.

        ```yaml
          - default: seasonal
            template_variables:
              schedule_valentine: range(02/10-02/15)
        ```

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check2"
      end="# check4"
    %}
    ```

??? example "Default Template Variable `imdb_search` (click to expand) <a class="headerlink" href="#imdb-search" title="Permanent link">¶</a>"

    <div id="imdb-search" />
    
    ???+ tip 
    
        Pass `imdb_search_<<key>>` to the file as template variables to change this value per collection.

        ```yaml
          - default: seasonal
            template_variables:
              imdb_search_easter: 
                list.any:
                  - ls075298827
                  - ls000099714
        ```

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check4"
      end="# check5"
    %}
    ```

??? example "Default Template Variable `tmdb_collection` (click to expand) <a class="headerlink" href="#tmdb-collection" title="Permanent link">¶</a>"

    <div id="tmdb-collection" />
    
    ???+ tip 
    
        Pass `tmdb_collection_<<key>>` to the file as template variables to change this value per collection.

        ```yaml
          - default: seasonal
            template_variables:
              tmdb_collection_years: 
                - 1234
                - 5678
        ```

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check5"
      end="# check6"
    %}
    ```

??? example "Default Template Variable `tmdb_movie` (click to expand) <a class="headerlink" href="#tmdb-movie" title="Permanent link">¶</a>"

    <div id="tmdb-movie" />
    
    ???+ tip 
    
        Pass `tmdb_movie_<<key>>` to the file as template variables to change this value per collection.

        ```yaml
          - default: seasonal
            template_variables:
              tmdb_movie_valentine: 
                - 4321
                - 8765
        ```

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check6"
      end="# check7"
    %}
    ```

??? example "Default Template Variable `mdblist_list` (click to expand) <a class="headerlink" href="#mdblist-list" title="Permanent link">¶</a>"

    <div id="mdblist-list" />
    
    ???+ tip 
    
        Pass `mdblist_list_<<key>>` to the file as template variables to change this value per collection.

        ```yaml
          - default: seasonal
            template_variables:
              mdblist_list_memorial: https://mdblist.com/lists/rizreflects/world-war-related-movies 
        ```

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check7"
      end="# check8"
    %}
    ```

??? example "Default Template Variable `trakt_list` (click to expand) <a class="headerlink" href="#trakt-list" title="Permanent link">¶</a>"

    <div id="trakt-list" />
    
    ???+ tip 
    
        Pass `trakt_list_<<key>>` to the file as template variables to change this value per collection.

        ```yaml
          - default: seasonal
            template_variables:
              trakt_list_mother:  
                - https://trakt.tv/users/robertsnorlax/lists/arizona-westerns
                - https://trakt.tv/users/pullsa/lists/the-96th-academy-awards-oscars-2024
        ```

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../../defaults/movie/seasonal.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check8"
      end="# check9"
    %}
    ```
