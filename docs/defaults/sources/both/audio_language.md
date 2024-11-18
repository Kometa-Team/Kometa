# Audio Language Collections

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not 
show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default `include` (click to expand) <a class="headerlink" href="#include" title="Permanent link">¶</a>"

    <div id="include" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    include: {%    
      include-markdown "../../../../defaults/both/audio_language.yml" 
      comments=false
      preserve-includer-indent=false
      start="include:"
      end="key_name_override:"
    %}
    ```

??? example "Default `key_name_override` (click to expand) <a class="headerlink" href="#key-name-override" title="Permanent link">¶</a>"

    <div id="key-name-override" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    key_name_override: {%    
      include-markdown "../../../../defaults/both/audio_language.yml" 
      comments=false
      preserve-includer-indent=false
      start="key_name_override:"
    %}
    ```
