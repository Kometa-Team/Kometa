# List of Defaults Files

The below table outlines the available Defaults files which can be called via `metadata_path` (for Collections), `overlay_path` (for Overlays) and `playlist_files` (for Playlists).

## Collections

These files can generally be used on both Movie and Show library-types, or are part of a category of collection (such as Award Shows.)

These collections are applied by calling the below paths into the `metadata_path:` section of your config.yml

### Chart Collections

| Source      | config.yml entry    | Example Collections Created                  | Works with Movies | Works with Shows |
|:------------|:--------------------|----------------------------------------------|:-----------------:|:----------------:|
| AniList     | `anilist`           | AniList Popular, AniList Season              |      &#9989;      |     &#9989;      |
| Basic       | `basic`             | Newly Released, New Episodes                 |      &#9989;      |     &#9989;      |
| FlixPatrol  | `flixpatrol`        | Top Disney, Top Hbo, Top Hulu, Top Netflix   |      &#9989;      |     &#9989;      |
| IMDb        | `imdb`              | IMDb Popular, IMDb Top 250                   |      &#9989;      |     &#9989;      |
| MyAnimeList | `myanimelist`       | MyAnimeList Popular, MyAnimeList Top Rated   |      &#9989;      |     &#9989;      |
| Other       | `other`             | AniDB Popular, Common Sense Selection        |      &#9989;      |     &#9989;      |
| Tautulli    | `tautulli`          | Plex Popular, Plex Watched                   |      &#9989;      |     &#9989;      |
| TMDb        | `tmdb`              | TMDb Popular, TMDb Airing Today              |      &#9989;      |     &#9989;      |
| Trakt       | `trakt`             | Trakt Popular, Trakt Trending                |      &#9989;      |     &#9989;      |

### Award Collections

| Award Show     | config.yml entry | Example Collections Created      | Works with Movies | Works with Shows |
|:---------------|:-----------------|----------------------------------|:-----------------:|:----------------:|
| BAFTA          | `bafta`          | BAFTA Best Films, BAFTA 2021     |      &#9989;      |     &#10060;     |
| Cannes         | `cannes`         | Cannes - Palme d'or, Cannes 2018 |      &#9989;      |     &#10060;     |
| Critics Choice | `choice`         | Critics Choice Awards 2020       |      &#9989;      |     &#9989;      |
| Emmys          | `emmy`           | Emmys 2021                       |      &#9989;      |     &#9989;      |
| Golden Globes  | `golden`         | Best Motion Pictures             |      &#9989;      |     &#9989;      |
| Oscars         | `oscars`         | Best Picture Winners             |      &#9989;      |     &#9989;      |
| Spirit         | `spirit`         | Independent Spirit Awards 2021   |      &#9989;      |     &#10060;     |
| Sundance       | `sundance`       | Sundance Grand Jury Winners      |      &#9989;      |     &#9989;      |

### General Collections

| Theme               | config.yml entry                       | Example Collections Created                            | Works with Movies | Works with Shows |
|:--------------------|:---------------------------------------|:-------------------------------------------------------|:-----------------:|:----------------:|
| Actor               | `actor`                                | Chris Hemsworth, Margot Robbie                         |      &#9989;      |     &#9989;      |
| Audio Language      | `audio_language`                       | French Audio, Korean Audio                             |      &#9989;      |     &#9989;      |
| Content Rating (UK) | `content_rating_uk`                    | U, PG, 12A                                             |      &#9989;      |     &#9989;      |
| Content Rating (US) | `content_rating_us`                    | G, PG, NC-17                                           |      &#9989;      |     &#9989;      |
| Country             | `country`                              | Belgium, India                                         |      &#9989;      |     &#9989;      |
| Decade              | `decade`                               | Best of 2012, Best of 2022                             |      &#9989;      |     &#9989;      |
| Director            | `director`                             | Steven Spielberg (Director), Olivia Wilde (Director)   |      &#9989;      |     &#10060;     |
| Franchise           | `franchise`                            | Star Wars: Skywalker Saga, Godzilla (Anime)            |      &#9989;      |     &#9989;      |
| Genre               | `genre`                                | Action, Drama, Science Fiction                         |      &#9989;      |     &#9989;      |
| Network             | `network`                              | Disney Channel, Lifetime                               |     &#10060;      |     &#9989;      |
| Producer            | `producer`                             | James Cameron (Producer), Reese Witherspoon (Producer) |      &#9989;      |     &#10060;     |
| Resolution          | `resolution` OR `resolution_standards` | 4K, 1080 OR Ultra HD, Full HD                          |      &#9989;      |     &#9989;      |
| Seasonal            | `seasonal`                             | Easter, Christmas                                      |      &#9989;      |     &#10060;     |
| Streaming           | `streaming`                            | Disney+ Movies, HBO Max Shows                          |      &#9989;      |     &#9989;      |
| Studio              | `studio`                               | DreamWorks Studios, Walt Disney Pictures               |      &#9989;      |     &#9989;      |
| Subtitle Language   | `subtitle_language`                    | German Subtitles, Swedish Subtitles                    |      &#9989;      |     &#9989;      |
| Universe            | `universe`                             | Marvel Cinematic Universal, Wizarding World            |      &#9989;      |     &#10060;     |
| Year                | `year`                                 | Best of 2010, Best of 2019                             |      &#9989;      |     &#9989;      |
| Writer              | `writer`                               | James Cameron (Writer), Lilly Wachowski (Writer)       |      &#9989;      |     &#10060;     |

## Overlays

These files apply overlays and can generally be used on both Movie and Show library-types, and often works at the season and episode-level too.

It should be noted that when an overlay has &#10071; for a season or episode, it normally means that whilst the overlay can technically be applied at the level, it wasn't designed for this purpose. For example, a show's season cannot have a resolution since it is not a video file, and an episode cannot have a commonsense age-rating since only Movies and Shows are rated by CommonSense. 

In the scenario where there is missing data such as age ratings for episodes, then generally the highest-level data available will be applied at the lower level (i.e. a Show's CommonSense age rating would apply to all episodes).

These overlays are applied by calling the below paths into the `overlay_path:` [section](https://metamanager.wiki/en/nightly/config/libraries.html#overlay-path) of your config.yml

### Overlay Files

| Theme                  | path                       | Example Overlays                               |  Movies  |   Shows   |  Seasons  | Episodes |
|:-----------------------|:---------------------------|------------------------------------------------|:--------:|:---------:|:---------:|:--------:|
| Audio Codec            | `audio_codec`              | Dolby Atmos logo, DTS logo                     | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| Audio Language         | `audio_language`           | French Audio, Korean Audio                     | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| CommonSense Age Rating | `commonsense`              | "3+", "16+"                                    | &#9989;  |  &#9989;  | &#10071;  | &#10071; |
| Direct Play            | `direct_play`              | "Direct Play Only"                             | &#9989;  | &#10071;  | &#10071;  | &#9989;  |
| Editions               | `editions`                 | Director's Cut logo, IMAX logo                 | &#9989;  | &#10060;  | &#10060;  | &#10060; |
| Episode Info           | `episode_info`             | "S01E01", "S02E09"                             | &#10060; | &#10060;  | &#10060;  | &#9989;  |
| FlixPatrol             | `flixpatrol`               | "Streaming service logo with words "TOP"       | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Mediastinger           | `mediastinger`             | Mediastinger logo                              | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Ratings                | `ratings`                  | IMDb Audience Rating, Metacritic Critic Rating | &#9989;  |  &#9989;  | &#10060;  | &#9989;  |
| Resolution             | `resolution`               | 4K Dolby Vision logo, 720P logo                | &#9989;  |  &#9989;  | &#10060;  | &#9989;  |
| Ribbon                 | `ribbon`                   | IMDb Top 250 Ribbon, RT Fresh Ribbon           | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Runtimes               | `runtimes`                 | "Runtime: 1h 30m"                              | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Special Releases       | `special_release`          | "Director's Cut", "Criterion Collection"       | &#9989;  |  &#9989;  | &#10071;  | &#10071; |
| Streaming              | `streaming`                | Netflix logo, Hulu logo                        | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Versions               | `versions`                 | Multiple Versions logo                         | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| Video Format           | `video_format`             | "REMUX", "HDTV"                                | &#9989;  | &#10071;  | &#10071;  | &#9989;  |

## Playlists

These files apply playlists to the "Playlists" section of Plex and are applied by calling the below paths into the `playlist_files:` section of your config.yml

### Playlist Files

| Theme                  | path       | Example Overlays                                      |
|:-----------------------|:-----------|-------------------------------------------------------|
| Playlist               | `playlist` | Arrowverse (Timeline Order), Pokémon (Timeline Order) |

