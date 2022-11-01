## Example Configuration File

<details>
  <summary>Click to expand sample config.yml file:</summary>

```yaml
libraries:
  Movies:                                           # Must match a library name in your Plex
    report_path: config/missing/Movies_report.yml
    template_variables:
      sep_style: gray                               # use the gray separators globally for this library
      collection_mode: hide                         # hide the collections
      language: fr                                  # could be default, de, fr, pt-br or another language code that we have tranlsated
    metadata_path:
    - pmm: separator_award                          # An "index card"
    - pmm: bafta                                    # BAFTA Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 2014
          ending: current_year
    - pmm: cannes                                   # Cannes Film Fstical Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 2016
          ending: current_year
    - pmm: choice                                   # Critic's Choice Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 2014
          ending: current_year
    - pmm: golden                                   # Golden Globes Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 1943
          ending: current_year
    - pmm: oscars                                   # The Oscars
      template_variables:                           # based on when the award show started
        data:
          starting: 1927
          ending: current_year
    - pmm: other_award                              # Other award collections
    - pmm: spirit                                   # Independent Spirit Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 2014
          ending: current_year
    - pmm: sundance                                 # Sundance Film Festival Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 2010
          ending: current_year
    - pmm: separator_chart                          # An "index card"
    - pmm: anilist                                  # AniDB Charts (Popular, Trending, etc.)
    - pmm: imdb                                     # IMDb Charts (Popular, Trending, etc.)
    - pmm: myanimelist                              # MAL Charts (Popular, Trending, etc.)
    - pmm: other_chart                              # Other Charts (Popular, Trending, etc.)
    - pmm: tautulli                                 # Tautulli Charts (Popular, Trending, etc.)
    - pmm: tmdb                                     # TMDb Charts (Popular, Trending, etc.)
    - pmm: trakt                                    # Trakt Charts (Popular, Trending, etc.)
    - pmm: flixpatrol                               # Flixpatrol Charts (Popular, Trending, etc.)
    - pmm: basic                                    # Keep this as the last chart item so that collection_mode: hide works properly on library tab for CHART COLLECTION
    - pmm: collectionless                           # Collectionless movies/shows (Keep this as the last chart item so that collection_mode: hide works properly on library tab for CHART COLLECTION)
    - pmm: actor                                    # Actors
      template_variables:                           # bw, rainier, or orig style is used. depth and limit is set low but sometimes I boost to 10, 150
        style: bw
        data:
          depth: 1
          limit: 15
    - pmm: director                                 # Directors
      template_variables:                           # bw, rainier, or orig style is used. depth and limit is set low but sometimes I boost to 10, 150
        style: bw
        data:
          depth: 1
          limit: 15
    - pmm: producer                                 # Producers
      template_variables:                           # bw, rainier, or orig style is used. depth and limit is set low but sometimes I boost to 10, 150
        exclude:                                    # ever have some random person... you can exclude them if you want
        - Jeremy Kleiner
        - Thomas Hayslip
        style: bw
        data:
          depth: 1
          limit: 15
    - pmm: writer                                   # Writers
      template_variables:                           # bw, rainier, or orig style is used. depth and limit is set low but sometimes I boost to 10, 150
        style: bw
        data:
          depth: 1
          limit: 15
    - pmm: audio_language                           # English, French, Arabic, German, etc. audio language 
    - pmm: content_rating_cs                        # Choose content_rating_uk, content_rating_us, or content_rating_cs
    - pmm: genre                                    # Action, Comedy, Drama, etc.
    - pmm: resolution                               # 4K HDR, 1080P FHD, etc. with the standards style 
      template_variables:
        style: standards
    - pmm: studio                                   # DreamWorks Studios, Lucasfilm Ltd, etc.
    - pmm: studio_anime                             # Anime Studios etc.
    - pmm: subtitle_language                        # English, French, Arabic, German, etc. subtitles
    - pmm: year                                     # Year the media item was released starting from 1880 to current_year
      template_variables:
        data:
          starting: 1880
          ending: current_year
    - pmm: country                                  # Country associated to the media item
    - pmm: decade                                   # Decade the media item was released
    - pmm: seasonal                                 # Christmas, Halloween, etc.
      template_variables:                           # Canadian Thankgsgiving is a different date range. Otherwise, I want to ALWAYS see the seasonal
        schedule_independence: daily
        schedule_easter: daily
        schedule_valentine: daily
        schedule_patrick: daily
        schedule_thanksgiving: range(10/01-10/31)
        schedule_halloween: daily
        schedule_christmas: daily
        schedule_years: daily
        schedule_mother: daily
        schedule_memorial: daily
        schedule_father: daily
        schedule_labor: daily
    - pmm: streaming                                # Streaming on Disney+, Netflix, etc.
    - pmm: universe                                 # Marvel Cinematic Universe, Wizarding World, etc.
    overlay_path:
    - remove_overlays: false                        # Set to true if you want to remove overlays
    - reapply_overlay: false                        # If you are doing a lot of testing and changes like me, keep this to true to always reapply overlays
    - pmm: audio_codec                              # FLAC, DTS-X, TrueHD, etc.
    - pmm: language_count                           # blank means 1 audio language track, dual means 2, multi means > 2
    - pmm: commonsense                              # Age 2+, Age 14+, etc.
    - pmm: flixpatrol                               # Top 10 flixpatrol for 'this_year', positioned on the left
      template_variables:
        position: left
        time_window: this_year
    - pmm: mediastinger                             # Mediastinger overlay when the media item contains a stinger at the end of the movie/show or during the credits
    - pmm: ratings                                  # Ratings with custom fonts matched to the style of the rating, font_size, and on the right in 'square' format
      template_variables:
	  
        rating1: user
        rating1_image: rt_tomato
		
        rating2: critic
        rating2_image: imdb

        rating3: audience
        rating3_image: tmdb

        horizontal_position: right

    - pmm: resolution                               # 4K HDR, 1080P FHD, etc.
    - pmm: ribbon                                   # Used for ribbon in bottom right
    - pmm: streaming                                # Streaming on Disney+, Netflix, etc.
    - pmm: versions                                 # Will show duplicates for that media item in top right area
    - pmm: video_format                             # Remux, DVD, Blu-Ray, etc. in bottom left
    settings:
      asset_directory:
      - config/assets

    operations:
      split_duplicates: false
      assets_for_all: false
      delete_unmanaged_collections: true            # Any manually added collection outside of PMM will be deleted
      mass_user_rating_update: mdb_tomatoes         # Update user ratings with mdb_tomatoes
      mass_critic_rating_update: imdb               # Update critic ratings with imdb
      mass_audience_rating_update: tmdb             # Update audience ratings with tmdb
      mass_genre_update: tmdb                       # Update all genres from tmdb
      mass_content_rating_update: mdb_commonsense   # Changes Content Rating to "1", "2" etc. to specify appropriate age
      mass_originally_available_update: tmdb        # Update all original available date from tmdb
      mass_imdb_parental_labels: without_none

  TV Shows:                                         # Must match a library name in your Plex
    report_path: config/missing/TV_missing.yml
    template_variables:
      sep_style: gray                               # use the gray separators globally for this library
      collection_mode: hide                         # hide the collections
      language: fr                                  # could be default, de, fr, pt-br or another lang code that we have tranlsated
    metadata_path:
    - pmm: separator_award                          # An "index card"
    - pmm: choice                                   # Critic's Choice Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 2014
          ending: current_year
    - pmm: golden                                   # Golden Globes Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 1943
          ending: current_year
    - pmm: emmy                                     # Emmy Awards
      template_variables:                           # based on when the award show started
        data:
          starting: 1947
          ending: current_year
    - pmm: separator_chart                          # An "index card"
    - pmm: anilist                                  # AniDB Charts (Popular, Trending, etc.)
    - pmm: imdb                                     # IMDb Charts (Popular, Trending, etc.)
    - pmm: myanimelist                              # MAL Charts (Popular, Trending, etc.)
    - pmm: other_chart                              # Other Charts (Popular, Trending, etc.)
    - pmm: tautulli                                 # Tautulli Charts (Popular, Trending, etc.)
    - pmm: tmdb                                     # TMDb Charts (Popular, Trending, etc.)
    - pmm: trakt                                    # Trakt Charts (Popular, Trending, etc.)
    - pmm: flixpatrol                               # Flixpatrol Charts (Popular, Trending, etc.)
    - pmm: basic                                    # Keep this as the last chart item so that collection_mode: hide works properly on library tab for CHART COLLECTION
    - pmm: collectionless                           # Collectionless movies/shows (Keep this as the last chart item so that collection_mode: hide works properly on library tab for CHART COLLECTION)
    - pmm: actor                                    # Actors
      template_variables:                           # bw, rainier, or orig style is used. depth and limit is set low but sometimes I boost to 10, 150
        exclude:                                    # ever have some random person... you can exclude them if you want
        - Macy Nyman
        style: bw
        data:
          depth: 1
          limit: 15
    - pmm: audio_language                           # English, French, Arabic, German, etc. audio language 
    - pmm: content_rating_cs                        # Choose content_rating_uk, content_rating_us, or content_rating_cs
    - pmm: genre                                    # Action, Comedy, Drama, etc.
    - pmm: resolution                               # 4K HDR, 1080P FHD, etc. with the standards style 
      template_variables:
        style: standards
    - pmm: studio                                   # DreamWorks Studios, Lucasfilm Ltd, etc.
    - pmm: studio_anime                             # Anime Studios etc.
    - pmm: subtitle_language                        # English, French, Arabic, German, etc. subtitles
    - pmm: year                                     # Year the media item was released starting from 1880 to current_year
      template_variables:
        data:
          starting: 1880
          ending: current_year
    - pmm: country                                  # Country associated to the media item
    - pmm: decade                                   # Decade the media item was released
    - pmm: network                                  # ABC, CBC, NBC, FOX, etc.
    - pmm: streaming                                # Streaming on Disney+, Netflix, etc.
    overlay_path:
    - remove_overlays: false                        # Set to true if you want to remove overlays
    - reapply_overlay: false                        # If you are doing a lot of testing and changes like me, keep this to true to always reapply overlays
    - pmm: audio_codec                              # FLAC, DTS-X, TrueHD, etc. and works with overlay_level show, episode, and season
    - pmm: audio_codec
      template_variables:
        overlay_level: episode
    - pmm: audio_codec
      template_variables:
        overlay_level: season
    - pmm: language_count                           # blank means 1 audio language track, dual means 2, multi means > 2 and works with overlay_level show, episode, and season
    - pmm: language_count
      template_variables:
        overlay_level: episode
    - pmm: language_count
      template_variables:
        overlay_level: season
    - pmm: commonsense                              # Age 2+, Age 14+, etc. and works with overlay_level show, episode, and season
    - pmm: commonsense
      template_variables:
        overlay_level: episode
    - pmm: commonsense
      template_variables:
        overlay_level: season
    - pmm: episode_info                             # SE##E## information in bottom right and works with overlay_level episode
      template_variables:
        overlay_level: episode
    - pmm: flixpatrol                               # Top 10 flixpatrol for 'this_year', positioned on the left and works with overlay_level show
      template_variables:
        position: left
        time_window: this_year
    - pmm: mediastinger                             # Mediastinger overlay when the media item contains a stinger at the end of the movie/show or during the credits and works with overlay_level show
    - pmm: ratings                                  # Ratings with custom fonts matched to the style of the rating, font_size, and on the right in 'square' format. overlay_level: show has 3 ratings max
      template_variables:
        rating1: user
        rating1_image: rt_tomato

        rating2: critic
        rating2_image: imdb

        rating3: audience
        rating3_image: tmdb

        horizontal_position: right
    - pmm: ratings                                  # Ratings with custom fonts matched to the style of the rating, font_size, and on the right in 'square' format. overlay_level: episode has 2 ratings max
      template_variables:

        rating1: critic
        rating1_image: imdb

        rating2: audience
        rating2_image: tmdb

        horizontal_position: right
        overlay_level: episode
    - pmm: resolution                               # 4K HDR, 1080P FHD, etc. and works with overlay_level show, episode, and season
    - pmm: resolution
      template_variables:
        overlay_level: episode
    - pmm: resolution
      template_variables:
        overlay_level: season
    - pmm: ribbon                                   # Used for ribbon in bottom right and works with overlay_level show and season
    - pmm: ribbon
      template_variables:
        overlay_level: season
    - pmm: episode_info                             # Runtime information in bottom right and works with overlay_level episode
      template_variables:
        overlay_level: episode
    - pmm: status                                   # Airing, Returning, Ended, Canceled and works with overlay_level show
    - pmm: streaming                                # Streaming on Disney+, Netflix, etc. and works with overlay_level show, episode, and season
    - pmm: streaming
      template_variables:
        overlay_level: episode
    - pmm: streaming
      template_variables:
        overlay_level: season
    - pmm: versions                                 # Will show duplicates for that media item in top right area and works with overlay_level show, episode, and season
      template_variables:
        overlay_level: episode
    - pmm: versions
      template_variables:
        overlay_level: season
    - pmm: versions
      template_variables:
        overlay_level: show
    - pmm: video_format                             # Remux, DVD, Blu-Ray, etc. in bottom left and works with overlay_level show, episode, and season
    - pmm: video_format
      template_variables:
        overlay_level: episode
    - pmm: video_format
      template_variables:
        overlay_level: season
    settings:
      asset_directory:
      - config/assets

    operations:
      split_duplicates: false
      assets_for_all: false
      delete_unmanaged_collections: true            # Any manually added collection outside of PMM will be deleted
      mass_user_rating_update: mdb_tomatoes         # Update user ratings with mdb_tomatoes
      mass_critic_rating_update: imdb               # Update critic ratings with imdb
      mass_audience_rating_update: tmdb             # Update audience ratings with tmdb
      mass_genre_update: tmdb                       # Update all genres from tmdb
      mass_content_rating_update: mdb_commonsense   # Changes Content Rating to "1", "2" etc. to specify appropriate age
      mass_originally_available_update: tmdb        # Update all original available date from tmdb
      mass_episode_critic_rating_update: imdb       # Update critic ratings with imdb for episodes
      mass_episode_audience_rating_update: tmdb     # Update audience ratings with tmdb for episodes
      mass_imdb_parental_labels: without_none
playlist_files:
- pmm: playlist
  template_variables:
    libraries: Movies, TV Shows
```
</details>
