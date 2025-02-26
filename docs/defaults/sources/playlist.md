# Playlists

These are lists provided for reference to show what values will be in use if you do no customization. **These do not 
show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default Template Variable `imdb_list` (click to expand) <a class="headerlink" href="#imdb-list" title="Permanent link">¶</a>"

    <div id="imdb-list" />

    ???+ tip 
    
        Pass `imdb_list_<<key>>` to the file as template variables to change this value per playlist.

        ```yaml
          - default: playlists
            template_variables:
              imdb_list_startrek: https://www.imdb.com/list/ls547463722/
        ```

    ```yaml
    {%
      include-markdown "../../../defaults/playlist.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check1"
      end="# check2"
    %}
    ```

??? example "Default Template Variable `mdblist_list` (click to expand) <a class="headerlink" href="#mdblist-list" title="Permanent link">¶</a>"

    <div id="mdblist-list" />

    ```yaml
    {%
      include-markdown "../../../defaults/playlist.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check3"
      end="# check4"
    %}
    ```