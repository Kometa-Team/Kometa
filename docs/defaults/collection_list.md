## Collections

These files can generally be used on both Movie and Show library-types, or are part of a category of collection (such as Award Shows.)

These collections are applied by calling the below paths into the `metadata_path` section of your config.yml

### Chart Collections

| Default                            | Path              | Example Collections                        | Works with Movies | Works with Shows |
|:-----------------------------------|:------------------|:-------------------------------------------|:-----------------:|:----------------:|
| [Chart Separator](chart/separator) | `separator_chart` | Chart Collections                          |      &#9989;      |     &#9989;      |
| [AniList](chart/anilist)           | `anilist`         | AniList Popular, AniList Season            |      &#9989;      |     &#9989;      |
| [Basic](chart/basic)               | `basic`           | Newly Released, New Episodes               |      &#9989;      |     &#9989;      |
| [FlixPatrol](chart/flixpatrol)     | `flixpatrol`      | Top Disney, Top Hbo, Top Hulu, Top Netflix |      &#9989;      |     &#9989;      |
| [IMDb](chart/imdb)                 | `imdb`            | IMDb Popular, IMDb Top 250                 |      &#9989;      |     &#9989;      |
| [MyAnimeList](chart/myanimelist)   | `myanimelist`     | MyAnimeList Popular, MyAnimeList Top Rated |      &#9989;      |     &#9989;      |
| [Other](chart/other)               | `other_chart`     | AniDB Popular, Common Sense Selection      |      &#9989;      |     &#9989;      |
| [Tautulli](chart/tautulli)         | `tautulli`        | Plex Popular, Plex Watched                 |      &#9989;      |     &#9989;      |
| [TMDb](chart/tmdb)                 | `tmdb`            | TMDb Popular, TMDb Airing Today            |      &#9989;      |     &#9989;      |
| [Trakt](chart/trakt)               | `trakt`           | Trakt Popular, Trakt Trending              |      &#9989;      |     &#9989;      |

### Award Collections

| Default                                                    | Path              | Example Collections                         | Works with Movies | Works with Shows |
|:-----------------------------------------------------------|:------------------|:--------------------------------------------|:-----------------:|:----------------:|
| [Award Separator](award/separator)                         | `separator_award` | Award Collections                           |      &#9989;      |     &#9989;      |
| [British Academy of Film and Television Arts](award/bafta) | `bafta`           | BAFTA Best Films, BAFTA 2021                |      &#9989;      |     &#10060;     |
| [Cannes](award/cannes)                                     | `cannes`          | Cannes - Palme d'or, Cannes 2018            |      &#9989;      |     &#10060;     |
| [Critics Choice](award/choice)                             | `choice`          | Critics Choice Awards 2020                  |      &#9989;      |     &#9989;      |
| [Emmys](award/emmy)                                        | `emmy`            | Emmys 2021                                  |      &#9989;      |     &#9989;      |
| [Golden Globes](award/golden)                              | `golden`          | Best Motion Pictures                        |      &#9989;      |     &#9989;      |
| [Academy Awards (Oscars)](award/oscars)                    | `oscars`          | Best Picture Winners                        |      &#9989;      |     &#10060;     |
| [Independent Spirit](award/spirit)                         | `spirit`          | Independent Spirit Awards 2021              |      &#9989;      |     &#10060;     |
| [Sundance](award/sundance)                                 | `sundance`        | Sundance Grand Jury Winners                 |      &#9989;      |     &#10060;     |
| [Other](award/other)                                       | `other_award`     | Berlinale Golden Bears, Venice Golden Lions |      &#9989;      |     &#10060;     |

### General Collections

| Default                                                                             | Path                 | Example Collections                                    | Works with Movies | Works with Shows |
|:------------------------------------------------------------------------------------|:---------------------|:-------------------------------------------------------|:-----------------:|:----------------:|
| [Actor](both/actor)                                                                 | `actor`              | Chris Hemsworth, Margot Robbie                         |      &#9989;      |     &#9989;      |
| [Audio Language](both/audio_language)                                               | `audio_language`     | French Audio, Korean Audio                             |      &#9989;      |     &#9989;      |
| [Collectionless](both/collectionless)                                               | `collectionless`     | Collectionless                                         |      &#9989;      |     &#9989;      |
| [Common Sense Content Rating](both/content_rating_cs)                               | `content_rating_cs`  | 1, 2, 3, 4, 5, 6, 15, 16, 17, 18                       |      &#9989;      |     &#9989;      |
| [MyAnimeList Content Rating](both/content_rating_mal)                               | `content_rating_mal` | G, PG, PG-13, R, R+, Rx                                |      &#9989;      |     &#9989;      |
| [Content Rating (UK)](both/content_rating_uk)                                       | `content_rating_uk`  | U, PG, 12A                                             |      &#9989;      |     &#9989;      |
| Content Rating (US) [Movie](movie/content_rating_us)/[Show](show/content_rating_us) | `content_rating_us`  | G, PG, NC-17                                           |      &#9989;      |     &#9989;      |
| Country [Movie](movie/country)/[Show](show/country)                                 | `country`            | Belgium, India                                         |      &#9989;      |     &#9989;      |
| Decade [Movie](movie/decade)/[Show](show/decade)                                    | `decade`             | Best of 2012, Best of 2022                             |      &#9989;      |     &#9989;      |
| [Director](movie/director)                                                          | `director`           | Steven Spielberg (Director), Olivia Wilde (Director)   |      &#9989;      |     &#10060;     |
| Franchise [Movie](movie/franchise)/[Show](show/franchise)                           | `franchise`          | Star Wars: Skywalker Saga, Godzilla (Anime)            |      &#9989;      |     &#9989;      |
| [Genre](both/genre)                                                                 | `genre`              | Action, Drama, Science Fiction                         |      &#9989;      |     &#9989;      |
| [Network](show/network)                                                             | `network`            | Disney Channel, Lifetime                               |     &#10060;      |     &#9989;      |
| [Producer](movie/producer)                                                          | `producer`           | James Cameron (Producer), Reese Witherspoon (Producer) |      &#9989;      |     &#10060;     |
| [Resolution](both/resolution)                                                       | `resolution`         | 4K Movies, 1080p Movies, 720p Movies                   |      &#9989;      |     &#9989;      |
| [Seasonal](movie/seasonal)                                                          | `seasonal`           | Easter, Christmas                                      |      &#9989;      |     &#10060;     |
| [Streaming](both/streaming)                                                         | `streaming`          | Disney+ Movies, HBO Max Shows                          |      &#9989;      |     &#9989;      |
| [Studio](both/studio)                                                               | `studio`             | DreamWorks Studios, Walt Disney Pictures               |      &#9989;      |     &#9989;      |
| [Anime Studio](both/studio_anime)                                                   | `studio_anime`       | Bones, Studio Ghibli, Toei Animation                   |      &#9989;      |     &#9989;      |
| [Subtitle Language](both/subtitle_language)                                         | `subtitle_language`  | German Subtitles, Swedish Subtitles                    |      &#9989;      |     &#9989;      |
| [Universe](movie/universe)                                                          | `universe`           | Marvel Cinematic Universal, Wizarding World            |      &#9989;      |     &#10060;     |
| [Year](both/year)                                                                   | `year`               | Best of 2010, Best of 2019                             |      &#9989;      |     &#9989;      |
| [Writer](movie/writer)                                                              | `writer`             | James Cameron (Writer), Lilly Wachowski (Writer)       |      &#9989;      |     &#10060;     |
