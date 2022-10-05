# Default Collections & Overlays

Plex Meta Manager includes a pre-created set of Metadata Files and Overlay Files which can be found in the "defaults" folder in the root of your Plex Meta Manager installation directory.

These files offer an easy-to-use and customizable set of Collections and Overlays that the user can achieve without having to worry about creating the files that makes the collections and overlays possible.

All Collections come with a matching poster to make a clean, consistent set of collections in your library. These files are stored in the [Plex Meta Manager Images](https://github.com/meisnate12/Plex-Meta-Manager-Images) Repository and each poster is downloaded straight to your Plex Collection when you run Plex Meta Manager.

It should be noted that users running the on [nightly branch](https://metamanager.wiki/en/nightly/home/kb.html#how-do-i-switch-to-the-nightly-branch) of Plex Meta Manager will receive all updates to the PMM Defaults as soon as they are published via [GitHub](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM), which may at times involve bugs or implementations that need to be further addressed. Users of the [develop](https://metamanager.wiki/en/nightly/home/kb.html#how-do-i-switch-to-the-develop-branch) and [master](https://metamanager.wiki/en/nightly/home/kb.html#how-do-i-switch-back-to-the-master-branch) branches will only receive updated Defaults files when an update to Plex Meta Manager is released - this helps to protect to keep these branches stable and prevent bugs from reaching the wider user-base.

Credits to Bullmoose20 and Yozora for helping drive this entire Default Set of Configs through the concept, design and implementation.

Special thanks to Magic815 for the overlay image inspiration and base template.

Please consider [donating](https://github.com/sponsors/meisnate12) towards the project.


## Configurations

To run a file in git you can simply add it to your `metadata_path` (For Metadata Files) or `overlay_path` (For Overlay Files) using `git` like so:

```yaml
libraries:
  Movies:
    metadata_path:
    - pmm: actor
    - pmm: genre
    overlay_path:
    - remove_overlays: false
    - pmm: ribbon
    - pmm: ratings
```

## Overlays

The default set of overlays are a combination of Positional Overlays and Text Overlays.

### Example Poster Overlays

![](images/movie-overlays1-annotated.png)
![](images/movie-overlays2-annotated.png)
<details>
  <summary>Click to expand sample config.yml Movies overlays section:</summary>

```yaml
libraries:
  Movies:
    overlay_path:
    - remove_overlays: false
    - reapply_overlay: true
    - pmm: resolution                                                    # 1
    - pmm: audio_codec                                                   # 2
    - pmm: mediastinger                                                  # 3
    - pmm: special_release                                               # 4
    - pmm: ratings                                                       # 5, 6, 7
      template_variables:
        rating1: user                                                    # 5 as this is user and mass_user_rating_update: mdb_tomatoes
        rating1_image: rt_tomato                                         # 5 as this is user and mass_user_rating_update: mdb_tomatoes
        rating1_font: config/custom_fonts/Adlib.ttf                      # 5 local font accessible to PMM
        rating1_font_size: 63                                            # 5 adjusted font size to fit rating

        rating2: critic                                                  # 6 as this is critic and mass_critic_rating_update: imdb
        rating2_image: imdb                                              # 6 as this is critic and mass_critic_rating_update: imdb
        rating2_font: config/custom_fonts/Impact.ttf                     # 6 local font accessible to PMM
        rating2_font_size: 70                                            # 6 adjusted font size to fit rating

        rating3: audience                                                # 7 as this is audience and mass_audience_rating_update: tmdb
        rating3_image: tmdb                                              # 7 as this is audience and mass_audience_rating_update: tmdb
        rating3_font: config/custom_fonts/Avenir_95_Black.ttf            # 7 local font accessible to PMM
        rating3_font_size: 70                                            # 7 adjusted font size to fit rating

        horizontal_position: right                                       # the set of ratings is on the right of the poster
    - pmm: streaming                                                     # 8
    - pmm: video_format                                                  # 9
    - pmm: audio_language                                                # 10
    - pmm: ribbon                                                        # 11, 12 Bottom right sash is used by more than one overlay so a weight for priority can be applied 
    operations:
      mass_user_rating_update: mdb_tomatoes                              # 5 This operation will update the user rating in plex with Rotten Tomatoes ratings information
      mass_critic_rating_update: imdb                                    # 6 This operation will update the critic rating in plex with IMDb ratings information
      mass_audience_rating_update: tmdb                                  # 7 This operation will update the audience rating in plex with TMDb ratings information
```
</details>

### Example TV Shows - Show Overlays

![](images/tvshow-poster-annotated.png)
<details>
  <summary>Click to expand sample config.yml TV Shows overlays section for the Show Poster:</summary>

```yaml
libraries:
  TV Shows:
    overlay_path:
    - remove_overlays: false
    - reapply_overlay: true
    - pmm: resolution                                                    # 1
    - pmm: audio_codec                                                   # 2
    - pmm: mediastinger                                                  # 3
    - pmm: ratings                                                       # 4, 5, 6
      template_variables:           
        rating1: user                                                    # 4 as this is user and mass_user_rating_update: mdb_tomatoes
        rating1_image: rt_tomato                                         # 4 as this is user and mass_user_rating_update: mdb_tomatoes
        rating1_font: config/custom_fonts/Adlib.ttf                      # 4 local font accessible to PMM
        rating1_font_size: 63                                            # 4 adjusted font size to fit rating

        rating2: critic                                                  # 5 as this is critic and mass_critic_rating_update: imdb
        rating2_image: imdb                                              # 5 as this is critic and mass_critic_rating_update: imdb
        rating2_font: config/custom_fonts/Impact.ttf                     # 5 local font accessible to PMM
        rating2_font_size: 70                                            # 5 adjusted font size to fit rating

        rating3: audience                                                # 6 as this is audience and mass_audience_rating_update: tmdb
        rating3_image: tmdb                                              # 6 as this is audience and mass_audience_rating_update: tmdb
        rating3_font: config/custom_fonts/Avenir_95_Black.ttf            # 6 local font accessible to PMM
        rating3_font_size: 70                                            # 6 adjusted font size to fit rating

        horizontal_position: right                                       # the set of ratings is on the right of the poster
    - pmm: streaming                                                     # 7
    - pmm: video_format                                                  # 8
    - pmm: ribbon                                                        # 10, 11 Bottom right sash is used by more than one overlay so a weight for priority can be applied 
    operations:
      mass_user_rating_update: mdb_tomatoes                              # 4 This operation will update the user rating in plex with Rotten Tomatoes ratings information
      mass_critic_rating_update: imdb                                    # 5 This operation will update the critic rating in plex with IMDb ratings information
      mass_audience_rating_update: tmdb                                  # 6 This operation will update the audience rating in plex with TMDb ratings information
```
</details>

### Example TV Shows - Season Overlays

![](images/tvshow-poster-season-annotated.png)
<details>
  <summary>Click to expand sample config.yml TV Shows overlays section for the Season Poster:</summary>
  
```yaml
libraries:
  TV Shows:
    overlay_path:
    - remove_overlays: false
    - reapply_overlay: true
    - pmm: resolution                                                    # 1
      template_variables:
        overlay_level: season
    - pmm: audio_codec                                                   # 2
      template_variables:
        overlay_level: season
    - pmm: video_format                                                  # 3
      template_variables:
        overlay_level: season
```
</details>

### Example TV Shows - Episode Overlays

![](images/tvshow-poster-episode-annotated.png)
<details>
  <summary>Click to expand sample config.yml TV Shows overlays section for the Episode Poster:</summary>
  
```yaml
libraries:
  TV Shows:
    overlay_path:
    - remove_overlays: false
    - reapply_overlay: true
    - pmm: resolution                                                    # 1
      template_variables:
        overlay_level: episode
    - pmm: audio_codec                                                   # 2
      template_variables:
        overlay_level: episode
    - pmm: ratings                                                       # 3, 4
      template_variables:

        rating1: critic                                                  # 3 as this is critic and mass_critic_rating_update: imdb
        rating1_image: imdb                                              # 3 as this is critic and mass_critic_rating_update: imdb
        rating1_font: config/custom_fonts/Impact.ttf                     # 3 local font accessible to PMM
        rating1_font_size: 70                                            # 3 adjusted font size to fit rating

        rating2: audience                                                # 4 as this is audience and mass_audience_rating_update: tmdb
        rating2_image: tmdb                                              # 4 as this is audience and mass_audience_rating_update: tmdb
        rating2_font: config/custom_fonts/Avenir_95_Black.ttf            # 4 local font accessible to PMM
        rating2_font_size: 70                                            # 4 adjusted font size to fit rating

        horizontal_position: right                                       # the set of ratings is on the right of the poster
        overlay_level: episode
    - pmm: video_format                                                  # 5
      template_variables:
        overlay_level: episode
    - pmm: episode_info                                                  # 6
      template_variables:
        overlay_level: episode
    - pmm: runtimes                                                      # 7
      template_variables:
        overlay_level: episode

    operations:
      mass_episode_critic_rating_update: imdb                            # 3 This operation will update the episodes critic rating in plex with IMDb ratings information
      mass_episode_audience_rating_update: tmdb                          # 4 This operation will update the episodes audience rating in plex with TMDb ratings information
```
</details>

## Separators

By default, most metadata files use separators to denote different sections of collection like actor collections vs studio collections.

<details>
  <summary>Click to expand to see an example of Separators.</summary>

   ![](images/separators.jpg)

</details>

* Can be turned off by [customizing your config](#customizing-configs)

## Collection Section Order

Almost every default metadata file has a `collection_section` attribute. These attributes determine the order of the various sections and can be set by [customizing your config](#customizing-configs).

For example: `collection_section: 01` translates to `sort_title: "!<<collection_section>><<pre>><<order_<<key>>>><<sort>>"` and so for `genre.yml` if you have a `Fantasy` collection, plex is going to show `!06_Fantasy`

This is the default PMM collection ordering:

| Collection                        | Collection Section |
|:----------------------------------|:------------------:|
| `seasonal.yml`                    |        `00`        |
| `anilist.yml`                     |        `01`        |
| `basic.yml`                       |        `01`        |
| `imdb.yml`                        |        `01`        |
| `flixpatrol.yml`                  |        `01`        |
| `myanimelist.yml`                 |        `01`        |
| `other_chart.yml`                 |        `01`        |
| `tautulli.yml`                    |        `01`        |
| `tmdb.yml`                        |        `01`        |
| `trakt.yml`                       |        `01`        |
| `universe.yml`                    |        `02`        |
| `streaming.yml`                   |        `03`        |
| `network.yml`                     |        `04`        |
| `genre.yml`                       |        `06`        |
| `studio.yml`                      |        `07`        |
| `country.yml`                     |        `09`        |
| `audio_language.yml`              |        `10`        |
| `subtitle_language.yml`           |        `11`        |
| `decade.yml`                      |        `12`        |
| `year.yml`                        |        `13`        |
| `content_rating_us.yml`           |        `14`        |
| `content_rating_uk.yml`           |        `14`        |
| `content_rating_cs.yml`           |        `14`        |
| `resolution.yml`                  |        `15`        |
| `resolution_standards.yml`        |        `15`        |
| `bafta.yml`                       |        `16`        |
| `cannes.yml`                      |        `16`        |
| `choice.yml`                      |        `16`        |
| `emmy.yml`                        |        `16`        |
| `golden.yml`                      |        `16`        |
| `oscars.yml`                      |        `16`        |
| `other_award.yml`                 |        `16`        |  
| `spirit.yml`                      |        `16`        |
| `sundance.yml`                    |        `16`        |
| `actor.yml`                       |        `17`        |
| `director.yml`                    |        `18`        |
| `producer.yml`                    |        `19`        |
| `writer.yml`                      |        `20`        |

## Rating Overlays

By default for Movies in Plex, the `Ratings Source` dropdown (`#3`) below, can come from Rotten Tomatoes (and includes Critic Ratings and Audience Ratings) or IMDb (Audience Ratings). This only changes the tiny icons displayed and where Plex will retrieve the ratings from upon initial scan and import of the media metadata.

**Plex Meta Manager can insert up to three ratings of your choice into the three spots regardless of what you choose in the `Advanced` tab of that Plex library**

![](images/ratings_source.png)

Plex has three available spots in the Plex DB to store ratings and thus Plex Meta Manager can be used to insert ratings sources of your choice into those spots. They are known as the User Rating (`#1`), Critic Rating (`#2`), and Audience Rating (`#3`). 

**Note that the little icons cannot be changed and that the numbers next to the little icons are reflected in the poster ratings overlay**

![](images/ratings_spot.png)

To be able to insert the ratings you want, Plex Meta Manager operations need to be defined. In this example below, User ratings (`#1`) are being filled with Rotten Tomatoes Critics Ratings. Critic ratings (`#2`) are filled with IMDb, and Audience ratings (`#3`) are filled with TMDb.

**mass_*_rating_update** sources can be found here: [operations](../../config/operations)

![](images/ratings_operations.png)

Finally, to show the ratings on the poster, the following was added to the `overlay_path` section in the `config.yml` file to post Rotten Tomatoes Critics Ratings in (`#1`), IMDb ratings in (`#2`), and TMDb ratings in (`#3`)

![](images/ratings_overlay_path.png)


## Customizing Configs

Configs can be customized using the `template_variables` attribute when calling the file. These `template_variables` will be given to every template call in the file which allows them to affect how that file runs.

This example changes the ratings overlay to work on episodes.

```yaml
libraries:
  TV Shows:
    overlay_path:
    - pmm: ratings
      template_variables:
        overlay_level: episode
```

Each file has a comment block at the top showing the available `template_variables` for each file. For example the [`pmm: genre`](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/PMM/genre.yml) has this:

```yaml
#############################################################
#                 Dynamic Genre Collections                 #
#         Created by Yozora, Bullmoose20, & Sohjiro         #
#############################################################
#  Call this from your config.yml (Movie or Show)           #
#  If nothing is specified these are the defaults           #
#                                                           #
#    metadata_path:                                         #
#      - pmm: genre                                     #
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
    - pmm: oscars
      template_variables:
        radarr_add_missing: true
        data:
          starting: current_year-10
          ending: current_year
```

Or maybe you want to change the number of actor collections made using pmm: actor.

```yaml
libraries:
  Movies:
    overlay_path:
    - pmm: actor
      template_variables:
        collection_mode: hide
        data:
          depth: 5
          limit: 50
```

Or maybe you want to change the collection sort order of the genre collections using pmm: genre.

```yaml
libraries:
  Movies:
    metadata_path:
    - pmm: genre
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
      - pmm: <file1>    # separator is disabled
        template_variables:
          use_separator: false
      - pmm: <file2>    # separator is enabled by default
      - pmm: <file3>    # separator is disabled
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
