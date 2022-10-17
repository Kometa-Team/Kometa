# List of Defaults Files

The below table outlines the available Defaults files which can be called via `metadata_path` (for Collections), `overlay_path` (for Overlays) and `playlist_files` (for Playlists).

## Collections

These files can generally be used on both Movie and Show library-types, or are part of a category of collection (such as Award Shows.)

These collections are applied by calling the below paths into the `metadata_path:` section of your config.yml

### Chart Collections

| Default                            |       Path        | Example Collections                        | Works with Movies | Works with Shows |
|:-----------------------------------|:-----------------:|:-------------------------------------------|:-----------------:|:----------------:|
| [Chart Separator](chart/separator) | `separator_chart` | Chart Collections                          |      &#9989;      |     &#9989;      |
| [AniList](chart/anilist)           |     `anilist`     | AniList Popular, AniList Season            |      &#9989;      |     &#9989;      |
| [Basic](chart/basic)               |      `basic`      | Newly Released, New Episodes               |      &#9989;      |     &#9989;      |
| [FlixPatrol](chart/flixpatrol)     |   `flixpatrol`    | Top Disney, Top Hbo, Top Hulu, Top Netflix |      &#9989;      |     &#9989;      |
| [IMDb](chart/imdb)                 |      `imdb`       | IMDb Popular, IMDb Top 250                 |      &#9989;      |     &#9989;      |
| [MyAnimeList](chart/myanimelist)   |   `myanimelist`   | MyAnimeList Popular, MyAnimeList Top Rated |      &#9989;      |     &#9989;      |
| [Other](chart/other)               |   `other_chart`   | AniDB Popular, Common Sense Selection      |      &#9989;      |     &#9989;      |
| [Tautulli](chart/tautulli)         |    `tautulli`     | Plex Popular, Plex Watched                 |      &#9989;      |     &#9989;      |
| [TMDb](chart/tmdb)                 |      `tmdb`       | TMDb Popular, TMDb Airing Today            |      &#9989;      |     &#9989;      |
| [Trakt](chart/trakt)               |      `trakt`      | Trakt Popular, Trakt Trending              |      &#9989;      |     &#9989;      |

### Award Collections

| Default                                                    |       Path        | Example Collections                         | Works with Movies | Works with Shows |
|:-----------------------------------------------------------|:-----------------:|:--------------------------------------------|:-----------------:|:----------------:|
| [Award Separator](award/separator)                         | `separator_award` | Award Collections                           |      &#9989;      |     &#9989;      |
| [British Academy of Film and Television Arts](award/bafta) |      `bafta`      | BAFTA Best Films, BAFTA 2021                |      &#9989;      |     &#10060;     |
| [Cannes](award/cannes)                                     |     `cannes`      | Cannes - Palme d'or, Cannes 2018            |      &#9989;      |     &#10060;     |
| [Critics Choice](award/choice)                             |     `choice`      | Critics Choice Awards 2020                  |      &#9989;      |     &#9989;      |
| [Emmys](award/emmy)                                        |      `emmy`       | Emmys 2021                                  |      &#9989;      |     &#9989;      |
| [Golden Globes](award/golden)                              |     `golden`      | Best Motion Pictures                        |      &#9989;      |     &#9989;      |
| [Academy Awards (Oscars)](award/oscars)                    |     `oscars`      | Best Picture Winners                        |      &#9989;      |     &#9989;      |
| [Independent Spirit](award/spirit)                         |     `spirit`      | Independent Spirit Awards 2021              |      &#9989;      |     &#10060;     |
| [Sundance](award/sundance)                                 |    `sundance`     | Sundance Grand Jury Winners                 |      &#9989;      |     &#9989;      |
| [Other](award/other)                                       |   `other_award`   | Berlinale Golden Bears, Venice Golden Lions |      &#9989;      |     &#10060;     |

### General Collections

| Default                                                                             |          Path          | Example Collections                                    | Works with Movies | Works with Shows |
|:------------------------------------------------------------------------------------|:----------------------:|:-------------------------------------------------------|:-----------------:|:----------------:|
| [Actor](both/actor)                                                                 |        `actor`         | Chris Hemsworth, Margot Robbie                         |      &#9989;      |     &#9989;      |
| [Audio Language](both/audio_language)                                               |    `audio_language`    | French Audio, Korean Audio                             |      &#9989;      |     &#9989;      |
| [Common Sense Content Rating](both/content_rating_cs)                               |  `content_rating_cs`   | 1, 2, 3, 4, 5, 6, 15, 16, 17, 18                       |      &#9989;      |     &#9989;      |
| [Content Rating (UK)](both/content_rating_uk)                                       |  `content_rating_uk`   | U, PG, 12A                                             |      &#9989;      |     &#9989;      |
| Content Rating (US) [Movie](movie/content_rating_us)/[Show](show/content_rating_us) |  `content_rating_us`   | G, PG, NC-17                                           |      &#9989;      |     &#9989;      |
| Country [Movie](movie/country)/[Show](show/country)                                 |       `country`        | Belgium, India                                         |      &#9989;      |     &#9989;      |
| Decade [Movie](movie/decade)/[Show](show/decade)                                    |        `decade`        | Best of 2012, Best of 2022                             |      &#9989;      |     &#9989;      |
| [Director](movie/director)                                                          |       `director`       | Steven Spielberg (Director), Olivia Wilde (Director)   |      &#9989;      |     &#10060;     |
| Franchise [Movie](movie/franchise)/[Show](show/franchise)                           |      `franchise`       | Star Wars: Skywalker Saga, Godzilla (Anime)            |      &#9989;      |     &#9989;      |
| [Genre](both/genre)                                                                 |        `genre`         | Action, Drama, Science Fiction                         |      &#9989;      |     &#9989;      |
| [Network](show/network)                                                             |       `network`        | Disney Channel, Lifetime                               |     &#10060;      |     &#9989;      |
| [Producer](movie/producer)                                                          |       `producer`       | James Cameron (Producer), Reese Witherspoon (Producer) |      &#9989;      |     &#10060;     |
| [Resolution](both/resolution)                                                       |      `resolution`      | 4K Movies, 1080p Movies, 720p Movies                   |      &#9989;      |     &#9989;      |
| [Resolution Standards](both/resolution_standards)                                   | `resolution_standards` | 4K, 1080 OR Ultra HD, Full HD                          |      &#9989;      |     &#9989;      |
| [Seasonal](movie/seasonal)                                                          |       `seasonal`       | Easter, Christmas                                      |      &#9989;      |     &#10060;     |
| [Streaming](both/streaming)                                                         |      `streaming`       | Disney+ Movies, HBO Max Shows                          |      &#9989;      |     &#9989;      |
| [Studio](both/studio)                                                               |        `studio`        | DreamWorks Studios, Walt Disney Pictures               |      &#9989;      |     &#9989;      |
| [Subtitle Language](both/subtitle_language)                                         |  `subtitle_language`   | German Subtitles, Swedish Subtitles                    |      &#9989;      |     &#9989;      |
| [Universe](movie/universe)                                                          |       `universe`       | Marvel Cinematic Universal, Wizarding World            |      &#9989;      |     &#10060;     |
| [Year](both/year)                                                                   |         `year`         | Best of 2010, Best of 2019                             |      &#9989;      |     &#9989;      |
| [Writer](movie/writer)                                                              |        `writer`        | James Cameron (Writer), Lilly Wachowski (Writer)       |      &#9989;      |     &#10060;     |

## Overlays

These files apply overlays and can generally be used on both Movie and Show library-types, and often works at the season and episode-level too.

It should be noted that when an overlay has &#10071; for a season or episode, it normally means that whilst the overlay can technically be applied at the level, it wasn't designed for this purpose. For example, a show's season cannot have a resolution since it is not a video file, and an episode cannot have a commonsense age-rating since only Movies and Shows are rated by CommonSense. 

In the scenario where there is missing data such as age ratings for episodes, then generally the highest-level data available will be applied at the lower level (i.e. a Show's CommonSense age rating would apply to all episodes).

These overlays are applied by calling the below paths into the `overlay_path:` [section](../config/libraries.md#overlay-path) of your config.yml

### Overlay Files

| Default                                        |       path        | Example Overlays                                                          |  Movies  |   Shows   |  Seasons  | Episodes |
|:-----------------------------------------------|:-----------------:|:--------------------------------------------------------------------------|:--------:|:---------:|:---------:|:--------:|
| [Audio Codec](overlays/audio_codec)            |   `audio_codec`   | Dolby Atmos logo, DTS logo                                                | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| [Audio Language](overlays/audio_language)      | `audio_language`  | French Audio, Korean Audio                                                | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| [CommonSense Age Rating](overlays/commonsense) |   `commonsense`   | "3+", "16+"                                                               | &#9989;  |  &#9989;  | &#10071;  | &#10071; |
| [Direct Play](overlays/direct_play)            |   `direct_play`   | "Direct Play Only"                                                        | &#9989;  | &#10071;  | &#10071;  | &#9989;  |
| [Episode Info](overlays/episode_info)          |  `episode_info`   | "S01E01", "S02E09"                                                        | &#10060; | &#10060;  | &#10060;  | &#9989;  |
| [FlixPatrol](overlays/flixpatrol)              |   `flixpatrol`    | "Streaming service logo with words "TOP"                                  | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| [Mediastinger](overlays/mediastinger)          |  `mediastinger`   | Mediastinger Logo for After/During Credit Scenes                          | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| [Ratings](overlays/ratings)                    |     `ratings`     | IMDb Audience Rating, Metacritic Critic Rating                            | &#9989;  |  &#9989;  | &#10060;  | &#9989;  |
| [Resolution/Editions](overlays/resolution)     |   `resolution`    | 4K Dolby Vision logo, 720P logo, "Director's Cut", "Criterion Collection" | &#9989;  |  &#9989;  | &#10060;  | &#9989;  |
| [Ribbon](overlays/ribbon)                      |     `ribbon`      | IMDb Top 250 Ribbon, RT Fresh Ribbon                                      | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| [Runtimes](overlays/runtimes)                  |    `runtimes`     | "Runtime: 1h 30m"                                                         | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| [Status](overlays/status)                      |     `status`      | Airing, Returning, Canceled, Ended                                        | &#10060; |  &#9989;  | &#10060;  | &#10060; |
| [Streaming](overlays/streaming)                |    `streaming`    | Netflix logo, Hulu logo                                                   | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| [Versions](overlays/versions)                  |    `versions`     | Multiple Versions logo                                                    | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| [Video Format](overlays/video_format)          |  `video_format`   | "REMUX", "HDTV"                                                           | &#9989;  | &#10071;  | &#10071;  | &#9989;  |

## Playlists

These files apply playlists to the "Playlists" section of Plex and are applied by calling the below paths into the `playlist_files:` section of your config.yml

### Playlist Files

| Default              |    path    | Example Overlays                                       |
|:---------------------|:----------:|:-------------------------------------------------------|
| [Playlist](playlist) | `playlist` | Arrowverse (Timeline Order), Pokémon (Timeline Order)  |
