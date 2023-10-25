## Example Configuration File

<details>
  <summary>Click to expand sample config.yml file:</summary>

```yaml
libraries:
  Movies:                                           # Must match a library name in your Plex
    report_path: config/missing/Movies_missing.yml
    template_variables:
      sep_style: purple                               # use the purple separators globally for this library
      collection_mode: hide                         # hide the collections within the "library" tab in Plex.
      placeholder_imdb_id: tt8579674                # 1917 (2019) placeholder id for the separators, avoids a plex bug.
    metadata_path:
    - pmm: separator_award                          # An "index card"
    - pmm: bafta                                    # BAFTA Awards
      template_variables:                           # Show collections from current_year-10 onwards.
        data:
          starting: current_year-10
          ending: current_year
    - pmm: golden                                   # Golden Globes Awards
      template_variables:                           # Show collections from current_year-10 onwards.
        data:
          starting: current_year-10
          ending: current_year
    - pmm: oscars                                   # The Oscars
      template_variables:                           # Show collections from current_year-10 onwards.
        data:
          starting: current_year-10
          ending: current_year
    - pmm: separator_chart                          # An "index card"
    - pmm: basic                                    # Some basic chart collections
    - pmm: tmdb                                     # TMDb Charts (Popular, Trending, etc.)
    - pmm: audio_language                           # English, French, Arabic, German, etc. audio language 
    - pmm: resolution                               # 4K HDR, 1080P FHD, etc. with the standards style 
      template_variables:
        style: standards
    - pmm: studio                                   # DreamWorks Studios, Lucasfilm Ltd, etc.
    - pmm: seasonal                                 # Christmas, Halloween, etc.
      template_variables:                           # Disable any US-specific seasonal collections
        schedule_independence: never
        schedule_thanksgiving: never
        schedule_memorial: never
        schedule_labor: never
    - pmm: streaming                                # Streaming on Disney+, Netflix, etc.
	  template_variables:
	    originals_only: true						# Only create collections for Original Content (i.e. Netflix Originals)
    - pmm: universe                                 # Marvel Cinematic Universe, Wizarding World, etc.
    overlay_path:
    - remove_overlays: false                        # Set to true if you want to remove overlays
    # - reapply_overlays: false                        # If you are doing a lot of testing and changes like me, keep this to true to always reapply overlays - can cause image bloat
    # - reset_overlays: tmdb                          # if you want to reset the poster to default poster from tmdb - can cause image bloat
    - pmm: audio_codec                              # FLAC, DTS-X, TrueHD, etc. style: standard/compact. compact is default
    - pmm: resolution                               # 4K HDR, 1080P FHD, etc.
    - pmm: ribbon                                   # Used for ribbon in bottom right
    - pmm: streaming                                # Streaming on Disney+, Netflix, etc.
    - pmm: video_format                             # Remux, DVD, Blu-Ray, etc. in bottom left
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
    metadata_path:
    - pmm: separator_award                          # An "index card"
    - pmm: bafta                                    # BAFTA Awards
      template_variables:                           # Show collections from current_year-10 onwards.
        data:
          starting: current_year-10
          ending: current_year
    - pmm: golden                                   # Golden Globes Awards
      template_variables:                           # Show collections from current_year-10 onwards.
        data:
          starting: current_year-10
          ending: current_year
    - pmm: oscars                                   # The Oscars
      template_variables:                           # Show collections from current_year-10 onwards.
        data:
          starting: current_year-10
          ending: current_year
    - pmm: separator_chart                          # An "index card"
    - pmm: basic                                    # Some basic chart collections
    - pmm: tmdb                                     # TMDb Charts (Popular, Trending, etc.)
    - pmm: audio_language                           # English, French, Arabic, German, etc. audio language 
    - pmm: resolution                               # 4K HDR, 1080P FHD, etc. with the standards style 
      template_variables:
        style: standards
    - pmm: network                                  # ABC, CBC, NBC, FOX, etc.
    - pmm: streaming                                # Streaming on Disney+, Netflix, etc.
	  template_variables:
	    originals_only: true						# Only create collections for Original Content (i.e. Netflix Originals)
    overlay_path:
    - remove_overlays: false                        # Set to true if you want to remove overlays
    # - reapply_overlays: false                        # If you are doing a lot of testing and changes like me, keep this to true to always reapply overlays - can cause image bloat
    # - reset_overlays: tmdb                          # if you want to reset the poster to default poster from tmdb - can cause image bloat
    - pmm: audio_codec                              # FLAC, DTS-X, TrueHD, etc. on show and episode
    - pmm: audio_codec
      template_variables:
        builder_level: episode
    - pmm: episode_info                             # S##E## information in bottom right on episode
      template_variables:
        builder_level: episode
    - pmm: resolution                               # 4K HDR, 1080P FHD, etc. on show, episode, and season
    - pmm: resolution
      template_variables:
        builder_level: episode
    - pmm: resolution
      template_variables:
        builder_level: season
    - pmm: ribbon                                   # Used for ribbon in bottom right on show
    - pmm: status                                   # Airing, Returning, Ended, Canceled on show
    - pmm: versions                                 # Will show duplicates for that media item on show and episode
    - pmm: versions                                 
      template_variables:
        builder_level: episode
    - pmm: video_format                             # Remux, DVD, Blu-Ray, etc. in bottom left on show, episode, and season
    - pmm: video_format
      template_variables:
        builder_level: episode
    settings:
      asset_directory:
      - config/assets

    operations:
      split_duplicates: false
      assets_for_all: false
playlist_files:
- pmm: playlist
  template_variables:
    libraries: Movies, TV Shows						# Must match the names of your libraries in Plex.
```

</details>
