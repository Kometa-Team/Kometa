---
search:
  boost: 5 
hide:
  - toc
---
# Library Attributes

Within the [Configuration File](overview.md), the `libraries` attribute specifies the Plex libraries that the user wants Kometa to act on.

Attributes are used to instruct Kometa what actions to take, such as "load the following libraries" or "execute the following Collection Definition files". 
These attributes can be specified individually per library, or can be inherited from the global value if it has been set. 
If an attribute is specified at both the library and global level, then the library level attribute will take priority.

## Attributes

The available attributes for each library are as follows:

??? blank "`library_name` - Used to specify the Library's name.<a class="headerlink" href="#library-name" title="Permanent link">¶</a>"

    <div id="library-name" />*Required only when trying to use multiple servers with the same name.*

    Each library that the user wants Kometa to interact with must be documented with a library attribute. 

    A library attribute is represented by the mapping name (i.e. `Movies` or `TV Shows`), this must have a unique name that correlates with a 
    library of the same name within the Plex Media Server.
    
    In the situation that two servers are being connected to which both have libraries of the same name, the `library_name` attribute can be utilized to specify the real 
    Library Name, whilst the library attribute's mapping name can be made into a placeholder. This is showcased below:

    <hr style="margin: 0px;">
    
    **Attribute:** `library_name`
    
    **Accepted Values:** Library Name.

    **Default Value:** Base Attribute Name

    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies01:
            library_name: Movies
          Movies02:
            library_name: Movies
            plex:
              url: http://192.168.1.35:32400
              token: ####################
          TV Shows:
          Anime:
        plex:
          url: http://192.168.1.12:32400
          token: ####################
        ```
        
        * In this example, `"Movies01"`, `"TV Shows"`, and `"Anime"` will all use the global plex server (**http://192.168.1.12:32400**) which is defined using the global 
          `plex` mapping. `"Movies02"` will use the plex server **http://192.168.1.35:32400** which is defined under its `plex` mapping over the global mapping.

??? blank "`collection_files` - Used to define [Collection Files](../files/collections.md).<a class="headerlink" href="#collection-files" title="Permanent link">¶</a>"

    <div id="collection-files" />The `collection_files` attribute is used to define [Collection Files](../files/collections.md) by specifying 
    the path type and path of the files that will be executed against the parent library. See [File Blocks](files.md) for how to define them.

    <hr style="margin: 0px;">
    
    **Attribute:** `collection_files`
    
    **Accepted Values:** Location of Collection YAML files.

    **Default Value:** `/config/<<MAPPING_NAME>>.yml`

    ???+ example "Example"
        
        ```yaml
        libraries:
          TV Shows:
            collection_files:
              - file: config/TV Shows.yml
              - default: tmdb
              - default: network
        ```

        By default, when `collection_files` is missing Kometa will look within the root Kometa directory for a Collection File called 
        `<MAPPING_NAME>.yml`. In the example below, Kometa will look for a file named `TV Shows.yml`.
        
        ```yaml
        libraries:
          TV Shows:
        ```


??? blank "`metadata_files` - Used to define [Metadata Files](../files/metadata.md).<a class="headerlink" href="#metadata-files" title="Permanent link">¶</a>"

    <div id="metadata-files" />The `metadata_files` attribute is used to define Metadata Files by specifying the path of
    the files that will be executed against the parent library. See [File Blocks](files.md) for how to define them.

    ???+ tip
    
        As of Kometa 1.20.0 "Metadata Files" refers to YAML files which refers to managing the metadata of items [movies, shows, music] 
        within your library, and "Collection Files" refers to YAML files which define Collections.
    
        In previous version of Kometa, "Metadata Files" could mean either of the above.

    <hr style="margin: 0px;">
    
    **Attribute:** `metadata_files`
    
    **Accepted Values:** Location of [Metadata Files](../files/metadata.md).

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        libraries:
          TV Shows:
            metadata_files:
              - file: config/metadata.yml
        ```

??? blank "`overlay_files` - Used to define [Overlay Files](../files/overlays.md).<a class="headerlink" href="#overlay-files" title="Permanent link">¶</a>"

    <div id="overlay-files" />The `overlay_files` attribute is used to define [Overlay Files](../files/overlays.md) by specifying the path 
    type and path of the files that will be executed against the parent library. See [File Blocks](files.md) for how to define them.

    <hr style="margin: 0px;">
    
    **Attribute:** `overlay_files`
    
    **Accepted Values:** Location of [Overlay Files](../files/overlays.md).

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        libraries:
          TV Shows:
            collection_files:
              - file: config/TV Shows.yml
            overlay_files:
              - file: config/Overlays.yml
        ```

??? blank "`report_path` - Location to save the YAML Report file for a library.<a class="headerlink" href="#report-path" title="Permanent link">¶</a>"

    <div id="report-path" />The `report_path` attribute is used to define where to save the YAML Report file. This file is used to store information about what media is added, 
    removed, filtered, and missing from the Plex library compared to what is expected from the Collection, Metadata, Overlay or Playlist file.
    
    If your Collection File creates a collection with `Movie 1`, `Movie 2` and `Movie 3` but your Plex library only has `Movie 1` and `Movie 3`, 
    then the missing YAML file will be updated to inform the user that `Movie 2` was missing from the library.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `report_path`
    
    **Accepted Values:** Location to save the YAML Report file.

    **Default Value:** `/config/<<MAPPING_NAME>>_report.yml` (Where `<<MAPPING_NAME>>` is the name of the library attribute.)

    ???+ example "Example"
        
        If you want to call your Report YAML something different you can like so:

        ```yaml
        libraries:
          Movies:
            report_path: /config/My Movie Report.yml
        ```
        
        Alternatively, Report YAML files can be placed in their own directory, as below:
        
        ```yaml
        libraries:
          Movies:
            report_path: /config/reports/Movies.yml
            collection_files:
              - file: config/Movies.yml
            overlay_files:
              - file: config/Overlays.yml
        ```

??? blank "`template_variables` - Used to define [Custom Template Variables](../files/templates.md#template-variables) for every file in a library.<a class="headerlink" href="#template-variables" title="Permanent link">¶</a>"

    <div id="template-variables" />Passes all given [Template Variables](../files/templates.md#template-variables) 
    to every template in every Collection, Metadata, and Overlay File run.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `template_variables`
    
    **Accepted Values:** [Dictionary](../kometa/yaml.md#dictionaries) of values specified by each particular file.

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            template_variables:
              collection_mode: hide_items
            collection_files:
              - file: config/Movies.yml
            overlay_files:
              - file: config/Overlays.yml
        ```

??? blank "`schedule` - Used to schedule when a library is run.<a class="headerlink" href="#schedule" title="Permanent link">¶</a>"

    <div id="schedule" />Used to schedule when a library is run using the [schedule options](schedule.md).
    
    <hr style="margin: 0px;">
    
    **Attribute:** `schedule`
    
    **Accepted Values:** Any [schedule option](schedule.md).

    **Default Value:** `daily`

    ???+ example "Example"
        
        ```yaml
        libraries:
          TV Shows:
            schedule: weekly(sunday)
            collection_files:
              - file: config/TV Shows.yml
            overlay_files:
              - file: config/Overlays.yml
        ```

??? blank "`operations` - Used to specify [Library Operations](operations.md) to run.<a class="headerlink" href="#operations" title="Permanent link">¶</a>"

    <div id="operations" />Used to specify [Library Operations](operations.md) to run.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `operations`
    
    **Accepted Values:** Any [Library Operation](operations.md).

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - default: imdb
            operations:
              mass_critic_rating_update: tmdb
              split_duplicates: true
        ```

??? blank "`remove_overlays` - Used to remove overlays.<a class="headerlink" href="#remove-overlays" title="Permanent link">¶</a>"

    <div id="remove-overlays" />Used to remove overlays from this library only. 

    Kometa will aim to use the Original Posters backup that it created in the "overlays" folder to restore from, and will be unable to remove the overlays if this backup no longer exists. 
    Kometa will also remove the `Overlay` label from the items in Plex.

    The result of setting `remove_overlays` is your Plex library should no longer have any Overlays applied by Kometa.

    ???+ warning "Proceed with Caution"

        When set to `true`, this will remove all overlays from your library every run, but will not delete 
        the overlaid images from your system, resulting in [image bloat](../kometa/scripts/imagemaid.md).

    <hr style="margin: 0px;">
    
    **Attribute:** `remove_overlays`
    
    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
            libraries:
              Movies:
                remove_overlays: true
                collection_files:
                  - file: config/Movies.yml
                overlay_files:
                  - file: config/Overlays.yml
        ```

??? blank "`reapply_overlays` - Used to reapply overlays.<a class="headerlink" href="#reapply-overlays" title="Permanent link">¶</a>"

    <div id="reapply-overlays" />Used to reapply overlays from this library only. This will reapply overlays to every item in your library.

    Note that this is typically NEVER required. Kometa will automatically update overlays as needed as part of a regular overlay run.

    ???+ warning "Proceed with Caution"

        When set to `true`, this will reapply all overlays on each run even if there is no need to do so, which will result in [image bloat](../kometa/scripts/imagemaid.md).

        If you think you need to use this setting, please think hard about why you have that impression, as you are almost certainly mistaken.

        In general use, this setting will only extend runtimes and cause image bloat in the Plex metadata for no good reason.

    <hr style="margin: 0px;">
    
    **Attribute:** `reapply_overlays`
    
    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
            libraries:
              Movies:
                reapply_overlays: true
                collection_files:
                  - file: config/Movies.yml
                overlay_files:
                  - file: config/Overlays.yml
        ```

??? blank "`reset_overlays` - Used to reset overlays.<a class="headerlink" href="#reset-overlays" title="Permanent link">¶</a>"

    <div id="reset-overlays" />Used to reset the base image used for overlays from this library only.

    Kometa will fetch a new "base" image from the desired source, and will use that as the new Original Poster upon which to apply overlays as part of the run. 

    The result of setting `reset_overlays` is that your Plex library will have Overlays applied based upon the new images taken from the source specified.
    
    ???+ warning "Proceed with Caution"

        This will reset all posters to the desired source on each run and will reapply all overlays on each run, which will result in [image bloat](../kometa/scripts/imagemaid.md).

        Additionally, any image obtained from this setting will take priority over any image you set using an Asset Directory. If you use Asset Directories, 
        you shouldn't really be using this setting as the Asset Directory should be the single source of truth for what the "base" image is.

    <hr style="margin: 0px;">
    
    **Attribute:** `reset_overlays`
    
    **Accepted Values:** `plex` or `tmdb`.

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
            libraries:
              Movies:
                reset_overlays: tmdb
                collection_files:
                  - file: config/Movies.yml
                overlay_files:
                  - file: config/Overlays.yml
        ```

??? blank "`schedule_overlays` - Used to schedule overlays.<a class="headerlink" href="#schedule-overlays" title="Permanent link">¶</a>"

    <div id="schedule-overlays" />Used to schedule overlays to run when desired. Overlays are applied all at once in a batch therefore you
    cannot schedule individual Overlay Files, as any unscheduled Overlay File will be removed each time Kometa is run.

    <hr style="margin: 0px;">
    
    **Attribute:** `schedule_overlays`
    
    **Accepted Values:** [Any Schedule Option](schedule.md).

    **Default Value:** `daily`

    ???+ example "Example"
    
        ```yaml
        libraries:
          TV Shows:
            schedule_overlays: weekly(sunday)
            collection_files:
              - file: config/TV Shows.yml
            overlay_files:
              - file: config/Overlays.yml
        ```

??? blank "`settings` - Used to override global [`setting` attributes](settings.md) for this library only.<a class="headerlink" href="#settings" title="Permanent link">¶</a>"

    <div id="settings" />Used to override global [`setting` attributes](settings.md) for this library only.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `settings`
    
    **Accepted Values:** Any [`setting`](settings.md) attribute that overrides a global value.

    **Default Value:** Global Value

    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - default: imdb
            settings:
              asset_directory: config/assets/Movies
        ```

??? blank "`plex` - Used to override global [`plex` attributes](plex.md) for this library only.<a class="headerlink" href="#plex" title="Permanent link">¶</a>"

    <div id="plex" />Used to override global [`plex` attributes](plex.md) for this library only. 

    **`plex` Attribute is required either here or globally**
    
    <hr style="margin: 0px;">
    
    **Attribute:** `plex`
    
    **Accepted Values:** Any [`plex`](plex.md) attribute that overrides a global value.

    **Default Value:** Global Value

    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - file: config/Movies.yml
          Movies_on_Second_Plex:
            library_name: Movies
            collection_files:
              - file: config/Movies.yml
            plex:
              url: http://plex.boing.bong
              token: SOME_TOKEN
              timeout: 360
              db_cache: 8192
        ...
        plex:
          url: http://plex.bing.bang
          token: SOME_TOKEN
          timeout: 60
          db_cache: 4096
          clean_bundles: false
          empty_trash: false
          optimize: false
        ...
        ```

??? blank "`radarr` - Used to override global [`radarr` attributes](radarr.md) for this library only.<a class="headerlink" href="#radarr" title="Permanent link">¶</a>"

    <div id="radarr" />Used to override global [`radarr` attributes](radarr.md) for this library only.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `radarr`
    
    **Accepted Values:** Any [`radarr`](radarr.md) attribute that overrides a global value.

    **Default Value:** Global Value

    ???+ example "Example"
        
        ```yaml
        libraries:
          Library01:     # this library uses the default radarr config
            collection_files:
              - file: config/Movies.yml
        
          Library02:     # this library overrides radarr root path and profile
            collection_files:
              - file: config/Movies.yml
            radarr:
              root_folder_path: /data/media/movies/tony
              quality_profile: Better
        
          Library03:      # this library overrides radarr quality profile
            collection_files:
              - file: config/Movies.yml
            radarr:
              quality_profile: Best
        
          Library04:      # this library uses the 4K radarr instance
            collection_files:
              - file: config/Movies.yml
            radarr:
              url: https://radarr-4k.bing.bang
              token: SOME_OTHER_TOKEN
              root_folder_path: /data/media/movies/geezer
              quality_profile: Bestest
        
          Library05:      # movies get added by a custom script so they should get added to radarr-4k
            collection_files:
              - file: config/Movies.yml
            radarr:
              url: https://radarr-4k.bing.bang
              token: SOME_OTHER_TOKEN
              root_folder_path: /data/media/movies/bill
              quality_profile: Bestest
              add_existing: true
              sonarr_path: /data/media/movies/bill
              plex_path: /mnt/unionfs/movies/bill
        ...
        radarr:
          url: https://radarr.bing.bang
          token: SOME_TOKEN
          quality_profile: Good
          add_missing: true
          add_existing: false
          upgrade_existing: false
          monitor_existing: false
          root_folder_path: /movies
          monitor: false
          availability: released
          tag:
          search: false
          radarr_path:
          plex_path:
        ...
        ```

??? blank "`sonarr` - Used to override global [`sonarr` attributes](sonarr.md) for this library only.<a class="headerlink" href="#sonarr" title="Permanent link">¶</a>"

    <div id="sonarr" />Used to override global [`sonarr` attributes](sonarr.md) for this library only.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `sonarr`
    
    **Accepted Values:** Any [`sonarr`](sonarr.md) attribute that overrides a global value.

    **Default Value:** Global Value

    ???+ example "Example"
        
        ```yaml
        libraries:
          Library01:     # this library uses the default sonarr config
            collection_files:
              - file: config/TV.yml
        
          Library02:     # this library overrides sonarr root path and profile
            collection_files:
              - file: config/TV.yml
            sonarr:
              root_folder_path: /data/media/shows/tony
              quality_profile: Better
        
          Library03:      # this library overrides sonarr quality profile
            collection_files:
              - file: config/TV.yml
            sonarr:
              quality_profile: Best
        
          Library04:      # this library uses the 4K sonarr instance
            collection_files:
              - file: config/TV.yml
            sonarr:
              url: https://sonarr-4k.bing.bang
              token: SOME_OTHER_TOKEN
              root_folder_path: /data/media/shows/geezer
              quality_profile: Bestest
        
          Library05:      # shows get added by a custom script so they should get added to sonarr-4k
            collection_files:
              - file: config/TV.yml
            sonarr:
              url: https://sonarr-4k.bing.bang
              token: SOME_OTHER_TOKEN
              root_folder_path: /data/media/shows/bill
              quality_profile: Bestest
              add_existing: true
              sonarr_path: /data/media/shows/bill
              plex_path: /mnt/unionfs/shows/bill
        
        ...
        sonarr:
          url: https://sonarr.bing.bang
          token: SOME_TOKEN
          add_missing: false
          add_existing: false
          upgrade_existing: false
          monitor_existing: false
          root_folder_path: /data/media/shows/ozzy
          monitor: all
          quality_profile: Good
          language_profile: English
          series_type: standard
          season_folder: true
          tag:
          search: false
          cutoff_search: false
          sonarr_path:
          plex_path:
        ...
        ```

??? blank "`tautulli` - Used to override global [`tautulli` attributes](tautulli.md) for this library only.<a class="headerlink" href="#tautulli" title="Permanent link">¶</a>"

    <div id="tautulli" />Used to override global [`tautulli` attributes](tautulli.md) for this library only.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `tautulli`
    
    **Accepted Values:** Any [`tautulli`](tautulli.md) attribute that overrides a global value.

    **Default Value:** Global Value

    ???+ example "Example"
        
        ```yaml
            libraries:
              Movies:
                collection_files:
                  - file: config/Movies.yml
              TV Shows:
                collection_files:
                  - file: config/TV.yml
                tautulli:
                  url: http://192.168.1.14:8659
                  apikey: SOME_KEY
            ...
            tautulli:
              url: http://192.168.1.12:8659
              apikey: SOME_KEY
            ...
        ```

### Example

This example is an advanced version of the library mappings which highlights some attributes being set at the global level, and some being set at the library level:

???+ example "Example Library Mappings"

    In this example, the `"TV Shows On Second Plex"` library has a library-level `plex` configuration, which takes priority over the `plex` configuration set at the global level.
    
    The `"Anime"` library also has a library-level `radarr` configuration, which takes priority over the `radarr` configuration set at the global level.

    ```yaml
    libraries:
      Movies:
        collection_files:
          - file: config/Movies.yml
          - default: imdb
          - default: studio
          - default: genre
          - default: actor
        operations:
          mass_critic_rating_update: tmdb
          split_duplicates: true
      TV Shows:
        collection_files:
          - file: config/TV Shows.yml
          - default: tmdb
          - default: network
        remove_overlays: false
        overlay_files:
          - file: config/Overlays.yml
      TV Shows On Second Plex:
        library_name: TV Shows
        plex:
          url: http://192.168.1.98:32400
          token: ####################
        collection_files:
          - file: config/TV Shows.yml
          - default: tmdb
          - default: network
      Anime:
        collection_files:
          - file: config/Anime.yml
          - default: myanimelist
        radarr:
          url: http://192.168.1.45:7878
          token: ################################
          root_folder_path: S:/Anime
        settings:
          asset_directory: config/assets/anime
    plex:
      url: http://192.168.1.12:32400
      token: ####################
    radarr:
      url: http://192.168.1.12:7878
      token: ################################
      add: true
      root_folder_path: S:/Movies
      monitor: true
      availability: announced
      quality_profile: HD-1080p
      tag: kometa
      search: false
    ```
