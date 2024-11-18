# Franchise Collections

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not 
show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default `addons` (click to expand) <a class="headerlink" href="#addons" title="Permanent link">¶</a>"

    <div id="addons" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    addons: {%    
      include-markdown "../../../../defaults/movie/franchise.yml" 
      comments=false
      preserve-includer-indent=false
      start="addons:"
      end="title_override:"
    %}
    ```

??? example "Default `title_override` (click to expand) <a class="headerlink" href="#title-override" title="Permanent link">¶</a>"

    <div id="title-override" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    title_override: {%    
      include-markdown "../../../../defaults/movie/franchise.yml" 
      comments=false
      preserve-includer-indent=false
      start="title_override:"
      end="template_variables:"
    %}
    ```

??? example "Default Template Variable `movie` (click to expand) <a class="headerlink" href="#movie" title="Permanent link">¶</a>"

    <div id="movie" />

    ???+ tip 

        Pass `movie_<<key>>` to the file as template variables to change this value per collection. 

        ```yaml
          - default: franchise
            template_variables:
              movie_131292:
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
      include-markdown "../../../../defaults/movie/franchise.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check1"
      end="# check2"
    %}
    ```

??? example "Default Template Variable `name_mapping` (click to expand) <a class="headerlink" href="#name-mapping" title="Permanent link">¶</a>"

    <div id="name-mapping" />
    
    ???+ tip 
    
        Pass `name_mapping_<<key>>` to the file as template variables to change this value per collection. 
    
        ```yaml
          - default: franchise
            template_variables:
              name_mapping_131292: "Iron Man Stuff"
        ```

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../../defaults/movie/franchise.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check2"
    %}
    ```
