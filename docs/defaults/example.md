## Example Configuration File

<details>
  <summary>Click to expand sample config.yml file:</summary>

```yaml
libraries:
  Movies:
    metadata_path:
    - pmm: bafta
    - pmm: cannes
    - pmm: choice
    - pmm: golden
    - pmm: oscars
    - pmm: other_award
    - pmm: spirit
    - pmm: sundance
    - pmm: anilist
    - pmm: basic
    - pmm: imdb
    - pmm: myanimelist
    - pmm: other_chart
    - pmm: tautulli
    - pmm: tmdb
    - pmm: trakt
    - pmm: actor
    - pmm: audio_language
    - pmm: content_rating_us           # Choose content_rating_uk or content_rating_us
    - pmm: genre
    - pmm: resolution_standards              # Choose resolution_standards or resolution
    - pmm: streaming
    - pmm: studio
    - pmm: subtitle_language
    - pmm: year
    - pmm: country
    - pmm: decade
    - pmm: director
    - pmm: franchise
    - pmm: universe
    - pmm: producer
    - pmm: seasonal
    - pmm: writer
    overlay_path:
    - remove_overlays: false
    - pmm: audio_codec
    - pmm: audio_language
    - pmm: commonsense
    - pmm: direct_play
    - pmm: edition
    - pmm: episode_info
    - pmm: flixpatrol
    - pmm: mediastinger
    - pmm: ratings
      template_variables:
        rating1: critic
        rating1_image: rt_tomato
    - pmm: resolution
    - pmm: ribbon
    - pmm: runtimes
    - pmm: special_release
    - pmm: streaming
    - pmm: versions
    - pmm: video_format
  TV Shows:
    metadata_path:
    - pmm: choice
    - pmm: golden
    - pmm: emmy
    - pmm: anilist
    - pmm: basic
    - pmm: imdb
    - pmm: myanimelist
    - pmm: other_chart
    - pmm: tautulli
    - pmm: tmdb
    - pmm: trakt
    - pmm: actor
    - pmm: audio_language
    - pmm: content_rating_us            # Choose content_rating_uk or content_rating_us
    - pmm: genre
    - pmm: resolution_standards              # Choose resolution_standards or resolution
    - pmm: streaming
    - pmm: studio
    - pmm: subtitle_language
    - pmm: year
    - pmm: country
    - pmm: decade
    - pmm: network
    overlay_path:
    - remove_overlays: false
    - pmm: audio_codec
    - pmm: audio_codec
      template_variables:
        overlay_level: episode
    - pmm: audio_codec
      template_variables:
        overlay_level: season
    - pmm: audio_language
    - pmm: audio_language
      template_variables:
        overlay_level: episode
    - pmm: audio_language
      template_variables:
        overlay_level: season
    - pmm: commonsense
    - pmm: commonsense
      template_variables:
        overlay_level: episode
    - pmm: commonsense
      template_variables:
        overlay_level: season
    - pmm: direct_play
    - pmm: direct_play
      template_variables:
        overlay_level: episode
    - pmm: direct_play
      template_variables:
        overlay_level: season
    - pmm: edition
    - pmm: edition
      template_variables:
        overlay_level: episode
    - pmm: episode_info
      template_variables:
        overlay_level: episode
    - pmm: flixpatrol
    - pmm: flixpatrol
      template_variables:
        overlay_level: episode
    - pmm: flixpatrol
      template_variables:
        overlay_level: season
    - pmm: mediastinger
    - pmm: mediastinger
      template_variables:
        overlay_level: episode
    - pmm: mediastinger
      template_variables:
        overlay_level: season
    - pmm: ratings
      template_variables:
        rating2: audience
        rating2_image: imdb
    - pmm: ratings
      template_variables:
        rating2: audience
        rating2_image: imdb
        overlay_level: episode
    - pmm: resolution
    - pmm: resolution
      template_variables:
        overlay_level: episode
    - pmm: resolution
      template_variables:
        overlay_level: season
    - pmm: ribbon
    - pmm: ribbon
      template_variables:
        overlay_level: episode
    - pmm: ribbon
      template_variables:
        overlay_level: season
    - pmm: runtimes
      template_variables:
        overlay_level: episode
    - pmm: special_release
    - pmm: special_release
      template_variables:
        overlay_level: episode
    - pmm: special_release
      template_variables:
        overlay_level: season
    - pmm: streaming
    - pmm: versions
    - pmm: versions
      template_variables:
        overlay_level: episode
    - pmm: versions
      template_variables:
        overlay_level: season
    - pmm: versions
      template_variables:
        overlay_level: show
    - pmm: video_format
    - pmm: video_format
      template_variables:
        overlay_level: episode
    - pmm: video_format
      template_variables:
        overlay_level: season
playlist_files:
- pmm: playlist
```
</details>
