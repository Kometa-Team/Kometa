## Example Configuration File

??? example "Sample `config.yml` file (click to expand)"

    ```yaml
    libraries:
      Movies:                                           # Must match a library name in your Plex
        report_path: config/missing/Movies_missing.yml
        template_variables:
          sep_style: purple                               # use the purple separators globally for this library
          collection_mode: hide                         # hide the collections within the "library" tab in Plex.
          placeholder_imdb_id: tt8579674                # 1917 (2019) placeholder id for the separators, avoids a plex bug.
        collection_files:
          - default: separator_award                          # An "index card"
          - default: bafta                                    # BAFTA Awards
            template_variables:                           # Show collections from latest-10 onwards.
              data:
                starting: latest-10
                ending: latest
          - default: golden                                   # Golden Globes Awards
            template_variables:                           # Show collections from latest-10 onwards.
              data:
                starting: latest-10
                ending: latest
          - default: oscars                                   # The Oscars
            template_variables:                           # Show collections from latest-10 onwards.
              data:
                starting: latest-10
                ending: latest
          - default: separator_chart                          # An "index card"
          - default: basic                                    # Some basic chart collections
          - default: tmdb                                     # TMDb Charts (Popular, Trending, etc.)
          - default: audio_language                           # English, French, Arabic, German, etc. audio language 
          - default: resolution                               # 4K HDR, 1080P FHD, etc. with the standards style 
            template_variables:
              style: standards
          - default: studio                                   # DreamWorks Studios, Lucasfilm Ltd, etc.
          - default: seasonal                                 # Christmas, Halloween, etc.
            template_variables:                           # Disable any US-specific seasonal collections
              schedule_independence: never
              schedule_thanksgiving: never
              schedule_memorial: never
              schedule_labor: never
          - default: streaming                                # Streaming on Disney+, Netflix, etc.
            template_variables:
              originals_only: true						# Only create collections for Original Content (i.e. Netflix Originals)
          - default: universe                                 # Marvel Cinematic Universe, Wizarding World, etc.
          
        remove_overlays: false                          # Set to true if you want to remove overlays
        reapply_overlays: false                         # If you are doing a lot of testing and changes like me, keep this to true to always reapply overlays - can cause image bloat
        #reset_overlays: tmdb                           # if you want to reset the poster to default poster from tmdb - can cause image bloat
        
        overlay_files:
          - default: audio_codec                              # FLAC, DTS-X, TrueHD, etc. style: standard/compact. compact is default
          - default: resolution                               # 4K HDR, 1080P FHD, etc.
          - default: ribbon                                   # Used for ribbon in bottom right
          - default: streaming                                # Streaming on Disney+, Netflix, etc.
          - default: video_format                             # Remux, DVD, Blu-Ray, etc. in bottom left
        settings:
          asset_directory:
            - config/assets
    
        operations:
          split_duplicates: false
          assets_for_all: false
    
      TV Shows:                                         # Must match a library name in your Plex
        report_path: config/missing/TV_missing.yml
        template_variables:
          sep_style: plum                               # use the plum separators globally for this library
          collection_mode: hide                         # hide the collections within the "library" tab in Plex.
          placeholder_imdb_id: tt1190634                # The Boys (2019) placeholder id for the separators, avoids a plex bug.
        collection_files:
          - default: separator_award                          # An "index card"
          - default: bafta                                    # BAFTA Awards
            template_variables:                           # Show collections from latest-10 onwards.
              data:
                starting: latest-10
                ending: latest
          - default: golden                                   # Golden Globes Awards
            template_variables:                           # Show collections from latest-10 onwards.
              data:
                starting: latest-10
                ending: latest
          - default: oscars                                   # The Oscars
            template_variables:                           # Show collections from latest-10 onwards.
              data:
                starting: latest-10
                ending: latest
          - default: separator_chart                          # An "index card"
          - default: basic                                    # Some basic chart collections
          - default: tmdb                                     # TMDb Charts (Popular, Trending, etc.)
          - default: audio_language                           # English, French, Arabic, German, etc. audio language 
          - default: resolution                               # 4K HDR, 1080P FHD, etc. with the standards style 
            template_variables:
              style: standards
          - default: network                                  # ABC, CBC, NBC, FOX, etc.
          - default: streaming                                # Streaming on Disney+, Netflix, etc.
            template_variables:
              originals_only: true						# Only create collections for Original Content (i.e. Netflix Originals)
        remove_overlays: false                          # Set to true if you want to remove overlays
        reapply_overlays: false                         # If you are doing a lot of testing and changes like me, keep this to true to always reapply overlays - can cause image bloat
        #reset_overlays: tmdb                           # if you want to reset the poster to default poster from tmdb - can cause image bloat
        overlay_files:
          - default: audio_codec                              # FLAC, DTS-X, TrueHD, etc. on show and episode
          - default: audio_codec
            template_variables:
              builder_level: episode
          - default: episode_info                             # S##E## information in bottom right on episode
            template_variables:
              builder_level: episode
          - default: resolution                               # 4K HDR, 1080P FHD, etc. on show, episode, and season
          - default: resolution
            template_variables:
              builder_level: episode
          - default: resolution
            template_variables:
              builder_level: season
          - default: ribbon                                   # Used for ribbon in bottom right on show
          - default: status                                   # Airing, Returning, Ended, Canceled on show
          - default: versions                                 # Will show duplicates for that media item on show and episode
          - default: versions                                 
            template_variables:
              builder_level: episode
          - default: video_format                             # Remux, DVD, Blu-Ray, etc. in bottom left on show, episode, and season
          - default: video_format
            template_variables:
              builder_level: episode
        settings:
          asset_directory:
            - config/assets
    
        operations:
          split_duplicates: false
          assets_for_all: false
    playlist_files:
      - default: playlist
        template_variables:
          libraries: Movies, TV Shows						# Must match the names of your libraries in Plex.
    ```
