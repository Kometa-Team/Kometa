# Playlists

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not 
show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default Template Variable `trakt_list` (click to expand) <a class="headerlink" href="#trakt-list" title="Permanent link">¶</a>"

    <div id="trakt-list" />

    ???+ tip 
    
        Pass `trakt_list_<<key>>` to the file as template variables to change this value per playlist.

        ```yaml
          - default: playlists
            template_variables:
              trakt_list_startrek: https://trakt.tv/users/username/lists/startrek
        ```

    ```yaml
    {%
      include-markdown "../../../defaults/playlist.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="conditions:"
      end="default:"
    %}
    ```
