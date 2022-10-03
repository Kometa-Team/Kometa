# Default Metadata & Overlays Files

There is a default set of Metadata and Overlay Files located in the [PMM Folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM) in the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs) Repository.

The intention of this directory is to offer easy to use and slightly customizable (using [`template_variables`](../../config/paths.md#template-variables)) Metadata and Overlay Files for a general user who wants nice collections but doesn't want to learn all of Plex Meta Manager.

All posters defined in the Metadata Files are stored in the [Plex Meta Manager Images](https://github.com/meisnate12/Plex-Meta-Manager-Images) Repository and all Overlay images are in the [Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs) Repository at [PMM/overlays/images](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM/overlays/images), which allows for changes to be made in one central location that will deploy to all users of this setup when they next run PMM.


## Configurations

To run a file in git you can simply add it to your `metadata_path` (For Metadata Files) or `overlay_path` (For Overlay Files) using `git` like so:

```yaml
libraries:
  Movies:
    metadata_path:
    - git: PMM/actor
    - git: PMM/genre
    overlay_path:
    - remove_overlays: false
    - git: PMM/overlays/imdb_top_250
    - git: PMM/overlays/ratings
```

## Overlays

The default set of overlays are a combination of Positional Overlays and Text Overlays.

### Example Poster Overlays

![](movie-overlays1-annotated.png)
![](movie-overlays2-annotated.png)
<details>
  <summary>Click to expand sample config.yml Movies overlays section:</summary>

```yaml
libraries:
  Movies:
    overlay_path:
    - remove_overlays: false
    - reapply_overlay: true
    - git: PMM/overlays/resolution                                       # 1
    - git: PMM/overlays/audio_codec                                      # 2
    - git: PMM/overlays/mediastinger                                     # 3
    - git: PMM/overlays/special_release                                  # 4
    - git: PMM/overlays/ratings                                          # 5,6,7
      template_variables:
        rating1: user                                                    # 5 as this is user and mass_user_rating_update: mdb_tomatoes
        rating1_image: rt_tomato                                         # 5 as this is user and mass_user_rating_update: mdb_tomatoes
        rating1_font: config/metadata/overlays/fonts/Adlib.ttf           # 5 local font accessible to PMM
        rating1_font_size: 63                                            # 5 adjusted font size to fit rating

        rating2: critic                                                  # 6 as this is critic and mass_critic_rating_update: imdb
        rating2_image: imdb                                              # 6 as this is critic and mass_critic_rating_update: imdb
        rating2_font: config/metadata/overlays/fonts/Impact.ttf          # 6 local font accessible to PMM
        rating2_font_size: 70                                            # 6 adjusted font size to fit rating

        rating3: audience                                                # 7 as this is audience and mass_audience_rating_update: tmdb
        rating3_image: tmdb                                              # 7 as this is audience and mass_audience_rating_update: tmdb
        rating3_font: config/metadata/overlays/fonts/Avenir_95_Black.ttf # 7 local font accessible to PMM
        rating3_font_size: 70                                            # 7 adjusted font size to fit rating

        horizontal_position: right                                       # the set of ratings is on the right of the poster
    - git: PMM/overlays/streaming                                        # 8
    - git: PMM/overlays/video_format                                     # 9
    - git: PMM/overlays/audio_language                                   # 10
    - git: PMM/overlays/oscars                                           # 11
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 40                                                       # Weight of 40 applies if more than 1 sash is applied in bottom right
    - git: PMM/overlays/imdb_top_250                                     # 12
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 30                                                       # Weight of 30 applies if more than 1 sash is applied in bottom right
    - git: PMM/overlays/rt_cert_fresh                                    # 13
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 20                                                       # Weight of 20 applies if more than 1 sash is applied in bottom right
    - git: PMM/overlays/mc_must_see                                      # NOT SHOWN, however would apply the "MetaCritic Must See" sash in the bottom right
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 10                                                       # Weight of 10 applies if more than 1 sash is applied in bottom right
    - git: PMM/overlays/commonsense_selection                                     # NOT SHOWN, however would apply the "Commonsense Selected Families" sash in the bottom right
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 5                                                        # Weight of 5 applies if more than 1 sash is applied in bottom right

    operations:
      mass_user_rating_update: mdb_tomatoes                              # 5 This operation will update the user rating in plex with Rotten Tomatoes ratings information
      mass_critic_rating_update: imdb                                    # 6 This operation will update the critic rating in plex with IMDb ratings information
      mass_audience_rating_update: tmdb                                  # 7 This operation will update the audience rating in plex with TMDb ratings information
```
</details>

### Example TV Shows - Show Overlays

![](tvshow-poster-annotated.png)
<details>
  <summary>Click to expand sample config.yml TV Shows overlays section for the Show Poster:</summary>

```yaml
libraries:
  TV Shows:
    overlay_path:
    - remove_overlays: false
    - reapply_overlay: true
    - git: PMM/overlays/resolution                                       # 1
    - git: PMM/overlays/audio_codec                                      # 2
    - git: PMM/overlays/mediastinger                                     # 3
    - git: PMM/overlays/ratings                                          # 4,5,6
      template_variables:           
        rating1: user                                                    # 4 as this is user and mass_user_rating_update: mdb_tomatoes
        rating1_image: rt_tomato                                         # 4 as this is user and mass_user_rating_update: mdb_tomatoes
        rating1_font: config/metadata/overlays/fonts/Adlib.ttf           # 4 local font accessible to PMM
        rating1_font_size: 63                                            # 4 adjusted font size to fit rating

        rating2: critic                                                  # 5 as this is critic and mass_critic_rating_update: imdb
        rating2_image: imdb                                              # 5 as this is critic and mass_critic_rating_update: imdb
        rating2_font: config/metadata/overlays/fonts/Impact.ttf          # 5 local font accessible to PMM
        rating2_font_size: 70                                            # 5 adjusted font size to fit rating

        rating3: audience                                                # 6 as this is audience and mass_audience_rating_update: tmdb
        rating3_image: tmdb                                              # 6 as this is audience and mass_audience_rating_update: tmdb
        rating3_font: config/metadata/overlays/fonts/Avenir_95_Black.ttf # 6 local font accessible to PMM
        rating3_font_size: 70                                            # 6 adjusted font size to fit rating

        horizontal_position: right                                       # the set of ratings is on the right of the poster
    - git: PMM/overlays/streaming                                        # 7
    - git: PMM/overlays/video_format                                     # 8
    - git: PMM/overlays/imdb_top_250                                     # 9
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 30                                                       # Weight of 30 applies if more than 1 sash is applied in bottom right
    - git: PMM/overlays/rt_cert_fresh                                    # 10
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 20                                                       # Weight of 20 applies if more than 1 sash is applied in bottom right
    - git: PMM/overlays/mc_must_see                                      # NOT SHOWN, however would apply the "MetaCritic Must See" sash in the bottom right
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 10                                                       # Weight of 10 applies if more than 1 sash is applied in bottom right
    - git: PMM/overlays/commonsense_selection                                     # NOT SHOWN, however would apply the "Commonsense Selected Families" sash in the bottom right
      template_variables:                                                # Bottom right sash is used by more than one overlay so a weight for priority is applied
        weight: 5                                                        # Weight of 5 applies if more than 1 sash is applied in bottom right

    operations:
      mass_user_rating_update: mdb_tomatoes                              # 4 This operation will update the user rating in plex with Rotten Tomatoes ratings information
      mass_critic_rating_update: imdb                                    # 5 This operation will update the critic rating in plex with IMDb ratings information
      mass_audience_rating_update: tmdb                                  # 6 This operation will update the audience rating in plex with TMDb ratings information
```
</details>

### Example TV Shows - Season Overlays

![](tvshow-poster-season-annotated.png)
<details>
  <summary>Click to expand sample config.yml TV Shows overlays section for the Season Poster:</summary>
  
```yaml
libraries:
  TV Shows:
    overlay_path:
    - remove_overlays: false
    - reapply_overlay: true
    - git: PMM/overlays/resolution                                       # 1
      template_variables:
        overlay_level: season
    - git: PMM/overlays/audio_codec                                      # 2
      template_variables:
        overlay_level: season
    - git: PMM/overlays/video_format                                     # 3
      template_variables:
        overlay_level: season
```
</details>

### Example TV Shows - Episode Overlays

![](tvshow-poster-episode-annotated.png)
<details>
  <summary>Click to expand sample config.yml TV Shows overlays section for the Episode Poster:</summary>
  
```yaml
libraries:
  TV Shows:
    overlay_path:
    - remove_overlays: false
    - reapply_overlay: true
    - git: PMM/overlays/resolution                                       # 1
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/audio_codec                                      # 2
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/ratings                                          # 3,4
      template_variables:

        rating1: critic                                                  # 3 as this is critic and mass_critic_rating_update: imdb
        rating1_image: imdb                                              # 3 as this is critic and mass_critic_rating_update: imdb
        rating1_font: config/metadata/overlays/fonts/Impact.ttf          # 3 local font accessible to PMM
        rating1_font_size: 70                                            # 3 adjusted font size to fit rating

        rating2: audience                                                # 4 as this is audience and mass_audience_rating_update: tmdb
        rating2_image: tmdb                                              # 4 as this is audience and mass_audience_rating_update: tmdb
        rating2_font: config/metadata/overlays/fonts/Avenir_95_Black.ttf # 4 local font accessible to PMM
        rating2_font_size: 70                                            # 4 adjusted font size to fit rating

        horizontal_position: right                                       # the set of ratings is on the right of the poster
        overlay_level: episode
    - git: PMM/overlays/video_format                                     # 5
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/episode_info                                     # 6
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/runtimes                                         # 7
      template_variables:
        overlay_level: episode

    operations:
      mass_episode_critic_rating_update: imdb                            # 3 This operation will update the episodes critic rating in plex with IMDb ratings information
      mass_episode_audience_rating_update: tmdb                          # 4 This operation will update the episodes audience rating in plex with TMDb ratings information
```
</details>

## Collection Section Order

Almost every default metadata file has a `collection_section` attribute. These attributes determine the order of the various sections and can be set by [customizing your config](#customizing-configs).

For example: `collection_section:01` translates to `sort_title: "!<<collection_section>><<pre>><<order_<<key>>>><<sort>>"` and so for `genre.yml` if you have a `Fantasy` collection, plex is going to show `!06_Fantasy`

This is the default PMM collection ordering:


| Collection	                       | Order                  |
|:-------------------------------------|------------------------|
| `PMM/movie/seasonal.yml`             | collection_section: 00 |
| `PMM/chart/anilist.yml`              | collection_section: 01 |
| `PMM/chart/basic.yml`                | collection_section: 01 |
| `PMM/chart/imdb.yml`                 | collection_section: 01 |
| `PMM/chart/myanimelist.yml`          | collection_section: 01 |
| `PMM/chart/other.yml`                | collection_section: 01 |
| `PMM/chart/tautulli.yml`             | collection_section: 01 |
| `PMM/chart/tmdb.yml`                 | collection_section: 01 |
| `PMM/chart/trakt.yml`                | collection_section: 01 |
| `PMM/movie/universe.yml`             | collection_section: 02 |
| `PMM/streaming.yml`                  | collection_section: 03 |
| `PMM/show/network.yml`               | collection_section: 04 |
| `PMM/genre.yml`                      | collection_section: 06 |
| `PMM/studio.yml`                     | collection_section: 07 |
| `PMM/movie/country.yml`              | collection_section: 09 |
| `PMM/show/country.yml`               | collection_section: 09 |
| `PMM/audio_language.yml`             | collection_section: 10 |
| `PMM/subtitle_language.yml`          | collection_section: 11 |
| `PMM/movie/decade.yml`               | collection_section: 12 |
| `PMM/show/decade.yml`                | collection_section: 12 |
| `PMM/year.yml`                       | collection_section: 13 |
| `PMM/content_rating_uk.yml`          | collection_section: 14 |
| `PMM/movie/content_rating_us.yml`    | collection_section: 14 |
| `PMM/show/content_rating_us.yml`     | collection_section: 14 |
| `PMM/resolution.yml`                 | collection_section: 15 |
| `PMM/resolution_standards.yml`       | collection_section: 15 |
| `PMM/award/bafta.yml`                | collection_section: 16 |
| `PMM/award/cannes.yml`               | collection_section: 16 |
| `PMM/award/choice.yml`               | collection_section: 16 |
| `PMM/award/emmy.yml`                 | collection_section: 16 |
| `PMM/award/golden.yml`               | collection_section: 16 |
| `PMM/award/oscars.yml`               | collection_section: 16 |
| `PMM/award/other.yml`                | collection_section: 16 |
| `PMM/award/separator.yml`            | collection_section: 16 |
| `PMM/award/spirit.yml`               | collection_section: 16 |
| `PMM/award/sundance.yml`             | collection_section: 16 |
| `PMM/actor.yml`                      | collection_section: 17 |
| `PMM/movie/director.yml`             | collection_section: 18 |
| `PMM/movie/producer.yml`             | collection_section: 19 |
| `PMM/movie/writer.yml`               | collection_section: 20 |

## Ratings Overlays

By default for Movies in Plex, the `Ratings Source` dropdown (`#3`) below, can come from Rotten Tomatoes (and includes Critic Ratings and Audience Ratings) or IMDb (Audience Ratings). This only changes the tiny icons displayed and where Plex will retrieve the ratings from upon initial scan and import of the media metadata.

**Plex Meta Manager can insert up to three ratings of your choice into the three spots regardless of what you choose in the `Advanced` tab of that Plex library**

![](ratings_source.png)

Plex has three available spots in the Plex DB to store ratings and thus Plex Meta Manager can be used to insert ratings sources of your choice into those spots. They are known as the User Rating (`#1`), Critic Rating (`#2`), and Audience Rating (`#3`). 

**Note that the little icons cannot be changed and that the numbers next to the little icons are reflected in the poster ratings overlay**

![](ratings_spot.png)

To be able to insert the ratings you want, Plex Meta Manager operations need to be defined. In this example below, User ratings (`#1`) are being filled with Rotten Tomatoes Critics Ratings. Critic ratings (`#2`) are filled with IMDb, and Audience ratings (`#3`) are filled with TMDb.

**mass_*_rating_update** sources can be found here: [operations](../../config/operations)

![](ratings_operations.png)

Finally, to show the ratings on the poster, the following was added to the `overlay_path` section in the `config.yml` file to post Rotten Tomatoes Critics Ratings in (`#1`), IMDb ratings in (`#2`), and TMDb ratings in (`#3`)

![](ratings_overlay_path.png)





## Customizing Configs

Configs can be customized using the `template_variables` attribute when calling the file. These `template_variables` will be given to every template call in the file which allows them to affect how that file runs.

This example changes the ratings overlay to work on episodes.

```yaml
libraries:
  TV Shows:
    overlay_path:
    - git: PMM/overlays/ratings
      template_variables:
        overlay_level: episode
```

Each file has a comment block at the top showing the available `template_variables` for each file. For example the [`PMM/genre`](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/PMM/genre.yml) has this:

```yaml
#############################################################
#                 Dynamic Genre Collections                 #
#         Created by Yozora, Bullmoose20, & Sohjiro         #
#############################################################
#  Call this from your config.yml (Movie or Show)           #
#  If nothing is specified these are the defaults           #
#                                                           #
#    metadata_path:                                         #
#      - git: PMM/genre                                     #
#        template_variables:                                #
#          # Turn the separator collection on/off           #
#          use_separator: true                              #
#          # Sets how the collection is sorted              #
#          sort_by: release.desc                            #
#          # Sets the collection mode of the collection     #
#          collection_mode:                                 #
#          # Sets the value at the start of the sort title  #
#          collection_section: "06"                         #
#############################################################
```
 
Each of these when passed will change how the collection runs slightly. 
* `use_separator` Turn the separator collection on/off
* `sort_by` Sets how the collection is sorted
* `collection_mode` Sets the collection mode of the collection 
* `collection_section` Sets the value at the start of the sort title

**In addition to the defined `template_variables` each file in the PMM Folder has access to the `radarr_add_missing` and `sonarr_add_missing` template variables and for dynamic collections most attributes can be passed as template variables**

For example if you want yearly oscar collections that go back 10 years instead of 5 all of which gets sent to radarr use the `data` and `radarr_add_missing` template variables.

```yaml
libraries:
  Movies:
    metadata_path:
    - git: PMM/award/oscars
      template_variables:
        radarr_add_missing: true
        data:
          starting: current_year-10
          ending: current_year
```

Or maybe you want to change the number of actor collections made using PMM/actor.

```yaml
libraries:
  Movies:
    overlay_path:
    - git: PMM/actor
      template_variables:
        collection_mode: hide
        data:
          depth: 5
          limit: 50
```

Or maybe you want to change the collection sort order of the genre collections using PMM/genre.

```yaml
libraries:
  Movies:
    metadata_path:
    - git: PMM/genre
      template_variables:
        collection_section: 11
```

Or maybe you want to disable separators globally per library.

```yaml
libraries:
  LIBRARYNAME:
    template_variables:
      use_separator: false
    metadata_path:
```

Alternatively it can be turned off individually per git file:

```yaml
libraries:
  LIBRARYNAME:
    metadata_path:
      - git: PMM/<file1>    # separator is disabled
        template_variables:
          use_separator: false
      - git: PMM/<file2>    # separator is enabled by default
      - git: PMM/<file3>    # separator is disabled
        template_variables:
          use_separator: false
```

## Errors

If there are collections being made that have configuration errors or missing posters please either bring it up in our Discord or raise an Issue on the [Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs/issues/new/choose). 

## Example Configuration File

<details>
  <summary>Click to expand sample config.yml file:</summary>

```yaml
libraries:
  Movies:
    metadata_path:
    - git: PMM/award/bafta
    - git: PMM/award/cannes
    - git: PMM/award/choice
    - git: PMM/award/golden
    - git: PMM/award/oscars
    - git: PMM/award/other
    - git: PMM/award/spirit
    - git: PMM/award/sundance
    - git: PMM/chart/anilist
    - git: PMM/chart/basic
    - git: PMM/chart/imdb
    - git: PMM/chart/myanimelist
    - git: PMM/chart/other
    - git: PMM/chart/tautulli
    - git: PMM/chart/tmdb
    - git: PMM/chart/trakt
    - git: PMM/actor
    - git: PMM/audio_language
    - git: PMM/movie/content_rating_us           # Choose content_rating_uk or content_rating_us
    - git: PMM/genre
    - git: PMM/resolution_standards              # Choose resolution_standards or resolution
    - git: PMM/streaming
    - git: PMM/studio
    - git: PMM/subtitle_language
    - git: PMM/year
    - git: PMM/movie/country
    - git: PMM/movie/decade
    - git: PMM/movie/director
    - git: PMM/movie/franchise
    - git: PMM/movie/universe
    - git: PMM/movie/producer
    - git: PMM/movie/seasonal
    - git: PMM/movie/writer
    overlay_path:
    - remove_overlays: false
    - git: PMM/overlays/audio_codec
    - git: PMM/overlays/audio_language
    - git: PMM/overlays/commonsense
    - git: PMM/overlays/direct_play
    - git: PMM/overlays/mediastinger
    - git: PMM/overlays/imdb_top_250
    - git: PMM/overlays/mc_must_see
    - git: PMM/overlays/rt_cert_fresh
    - git: PMM/overlays/commonsense_selection
    - git: PMM/overlays/ratings
      template_variables:
        rating1: critic
        rating1_image: rt_tomato
    - git: PMM/overlays/resolution
    - git: PMM/overlays/special_release
    - git: PMM/overlays/streaming
    - git: PMM/overlays/versions
    - git: PMM/overlays/video_format
  TV Shows:
    metadata_path:
    - git: PMM/award/choice
    - git: PMM/award/golden
    - git: PMM/award/emmy
    - git: PMM/chart/anilist
    - git: PMM/chart/basic
    - git: PMM/chart/imdb
    - git: PMM/chart/myanimelist
    - git: PMM/chart/other
    - git: PMM/chart/tautulli
    - git: PMM/chart/tmdb
    - git: PMM/chart/trakt
    - git: PMM/actor
    - git: PMM/audio_language
    - git: PMM/show/content_rating_us            # Choose content_rating_uk or content_rating_us
    - git: PMM/genre
    - git: PMM/resolution_standards              # Choose resolution_standards or resolution
    - git: PMM/streaming
    - git: PMM/studio
    - git: PMM/subtitle_language
    - git: PMM/year
    - git: PMM/show/country
    - git: PMM/show/decade
    - git: PMM/show/network
    overlay_path:
    - remove_overlays: false
    - git: PMM/overlays/audio_codec
    - git: PMM/overlays/audio_codec
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/audio_codec
      template_variables:
        overlay_level: season
    - git: PMM/overlays/audio_language
    - git: PMM/overlays/audio_language
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/audio_language
      template_variables:
        overlay_level: season
    - git: PMM/overlays/commonsense
    - git: PMM/overlays/commonsense
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/commonsense
      template_variables:
        overlay_level: season
    - git: PMM/overlays/direct_play
    - git: PMM/overlays/direct_play
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/direct_play
      template_variables:
        overlay_level: season
    - git: PMM/overlays/episode_info
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/mediastinger
    - git: PMM/overlays/mediastinger
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/mediastinger
      template_variables:
        overlay_level: season
    - git: PMM/overlays/imdb_top_250
    - git: PMM/overlays/imdb_top_250
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/imdb_top_250
      template_variables:
        overlay_level: season
    - git: PMM/overlays/mc_must_see
    - git: PMM/overlays/mc_must_see
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/mc_must_see
      template_variables:
        overlay_level: season
    - git: PMM/overlays/rt_cert_fresh
    - git: PMM/overlays/rt_cert_fresh
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/rt_cert_fresh
      template_variables:
        overlay_level: season
    - git: PMM/overlays/commonsense_selection
    - git: PMM/overlays/commonsense_selection
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/commonsense_selection
      template_variables:
        overlay_level: season
    - git: PMM/overlays/ratings
      template_variables:
        rating2: audience
        rating2_image: imdb
    - git: PMM/overlays/ratings
      template_variables:
        rating2: audience
        rating2_image: imdb
        overlay_level: episode
    - git: PMM/overlays/resolution
    - git: PMM/overlays/resolution
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/resolution
      template_variables:
        overlay_level: season
    - git: PMM/overlays/runtimes
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/special_release
    - git: PMM/overlays/special_release
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/special_release
      template_variables:
        overlay_level: season
    - git: PMM/overlays/streaming
    - git: PMM/overlays/versions
    - git: PMM/overlays/versions
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/versions
      template_variables:
        overlay_level: season
    - git: PMM/overlays/versions
      template_variables:
        overlay_level: show
    - git: PMM/overlays/video_format
    - git: PMM/overlays/video_format
      template_variables:
        overlay_level: episode
    - git: PMM/overlays/video_format
      template_variables:
        overlay_level: season
playlist_files:
- git: PMM/playlist
```
</details>
