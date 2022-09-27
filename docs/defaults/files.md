# List of Defaults Files

The below table outlines the available Defaults files which can be called via `metadata_path` (for Collections), `overlay_path` (for Overlays) and `playlist_files` (for Playlists).


## Collections
These files can generally be used on both Movie and Show library-types, or are part of a category of collection (such as Award Shows.)

These collections are applied by calling the below paths into the `metadata_path:` section of your config.yml

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

### Award Show Collections

| Award Show     | config.yml entry | Example Collections Created      | Works with Movies | Works with Shows |
|:---------------|:-----------------|----------------------------------|:-----------------:|:----------------:|
| BAFTA          | `award/bafta`    | BAFTA Best Films, BAFTA 2021     |      &#9989;      |     &#10060;     |
| Cannes         | `award/cannes`   | Cannes - Palme d'or, Cannes 2018 |      &#9989;      |     &#10060;     |
| Critics Choice | `award/choice`   | Critics Choice Awards 2020       |      &#9989;      |     &#9989;      |
| Emmys          | `award/emmy`     | Emmys 2021                       |      &#9989;      |     &#9989;      |
| Golden Globes  | `award/golden`   | Best Motion Pictures             |      &#9989;      |     &#9989;      |
| Oscars         | `award/oscars`   | Best Picture Winners             |      &#9989;      |     &#9989;      |
| Spirit         | `award/spirit`   | Independent Spirit Awards 2021   |      &#9989;      |     &#10060;     |
| Sundance       | `award/sundance` | Sundance Grand Jury Winners      |      &#9989;      |     &#9989;      |


### Chart Collections

| Source      | config.yml entry    | Example Collections Created                 | Works with Movies | Works with Shows |
|:------------|:--------------------|---------------------------------------------|:-----------------:|:----------------:|
| AniList     | `chart/anilist`     | AniList Popular, AniList Season             |      &#9989;      |     &#9989;      |
| Basic       | `chart/basic`       | Newly Released, New Episodes                |      &#9989;      |     &#9989;      |
| IMDb        | `chart/imdb`        | IMDb Popular, IMDb Top 250                  |      &#9989;      |     &#9989;      |
| MyAnimeList | `chart/myanimelist` | MyAnimeList Popular, MyAnimeList Top Rated  |      &#9989;      |     &#9989;      |
| Other       | `chart/other`       | AniDB Popular, Common Sense Selection       |      &#9989;      |     &#9989;      |
| Tautulli    | `chart/tautulli`    | Plex Popular, Plex Watched                  |      &#9989;      |     &#9989;      |
| TMDb        | `chart/tmdb`        | TMDb Popular, TMDb Airing Today             |      &#9989;      |     &#9989;      |
| Trakt       | `chart/trakt`       | Trakt Popular, Trakt Trending               |      &#9989;      |     &#9989;      |


## Overlays
These files apply overlays and can generally be used on both Movie and Show library-types, and often works at the season and episode-level too.

It should be noted that when an overlay has &#10060; for a season or episode, it normally means that whilst the overlay can technically be applied at the level, it wasn't designed for this purpose. For example, a show's season cannot have a resolution since it is not a video file, and an episode cannot have a commonsense age-rating since only Movies and Shows are rated by CommonSense. 

In the scenario where there is missing data such as age ratings for episodes, then generally the highest-level data available will be applied at the lower level (i.e. a Show's CommonSense age rating would apply to all episodes).

These overlays are applied by calling the below paths into the `overlay_path:` section of your config.yml

### Overlay Files

| Theme                  | path                       | Example Overlays                               |  Movies  |   Shows   |  Seasons  | Episodes |
|:-----------------------|:---------------------------|------------------------------------------------|:--------:|:---------:|:---------:|:--------:|
| Audio Codec            | `overlays/audio_codec`     | Dolby Atmos logo, DTS logo                     | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| Audio Language         | `overlays/audio_language`  | French Audio, Korean Audio                     | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| CommonSense Age Rating | `overlays/commonsense`     | "3+", "16+"                                    | &#9989;  |  &#9989;  | &#10071;  | &#10071; |
| Direct Play            | `overlays/direct_play`     | "Direct Play Only"                             | &#9989;  | &#10071;  | &#10071;  | &#9989;  |
| Editions               | `overlays/editions`        | Director's Cut logo, IMAX logo                 | &#9989;  | &#10060;  | &#10060;  | &#10060; |
| Episode Info           | `overlays/episode_info`    | "S01E01", "S02E09"                             | &#10060; | &#10060;  | &#10060;  | &#9989;  |
| Mediastinger           | `overlays/mediastinger`    | Mediastinger logo                              | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Ratings                | `overlays/ratings`         | IMDb Audience Rating, Metacritic Critic Rating | &#9989;  |  &#9989;  | &#10060;  | &#9989;  |
| Resolution             | `overlays/resolution`      | 4K Dolby Vision logo, 720P logo                | &#9989;  |  &#9989;  | &#10060;  | &#9989;  |
| Ribbon                 | `overlays/ribbon`          | IMDb Top 250 Ribbon, RT Fresh Ribbon           | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Runtimes               | `overlays/runtimes`        | "Runtime: 1h 30m"                              | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Special Releases       | `overlays/special_release` | "Director's Cut", "Criterion Collection"       | &#9989;  |  &#9989;  | &#10071;  | &#10071; |
| Streaming              | `overlays/streaming`       | Netflix logo, Hulu logo                        | &#9989;  |  &#9989;  | &#10060;  | &#10060; |
| Versions               | `overlays/versions`        | Multiple Versions logo                         | &#9989;  |  &#9989;  |  &#9989;  | &#9989;  |
| Video Format           | `overlays/video_format`    | "REMUX", "HDTV"                                | &#9989;  | &#10071;  | &#10071;  | &#9989;  |


## Playlists
These files apply playlists to the "Playlists" section of Plex and are applied by calling the below paths into the `playlist_files:` section of your config.yml

### Playlist Files

| Theme                  | path       | Example Overlays                                      |
|:-----------------------|:-----------|-------------------------------------------------------|
| Playlist               | `playlist` | Arrowverse (Timeline Order), Pokémon (Timeline Order) |

