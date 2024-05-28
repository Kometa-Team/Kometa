## Collections

These files can generally be used on both Movie and Show library-types, or are part of a category of collection (such as 
Award Shows.)

These collections are applied by calling the below paths into the `collection_files` section of your config.yml

### Award Collections

| Default                                                         | Path              | Example Collections                                                                        |             Works with Movies              |              Works with Shows              |
|:----------------------------------------------------------------|:------------------|:-------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|
| [Award Separator](award/separator.md)                           | `separator_award` | Award Collections                                                                          | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Academy Awards (Oscars)](award/oscars.md)                      | `oscars`          | Oscars Best Picture Winners, Oscars Best Director Winners, Oscars 2022                     | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Berlin International Film Festival Awards](award/berlinale.md) | `berlinale`       | Berlinale Golden Bears, Berlinale 2021                                                     | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [British Academy of Film Awards](award/bafta.md)                | `bafta`           | BAFTA Best Films, BAFTA 2021                                                               | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Cannes Film Festival Awards](award/cannes.md)                  | `cannes`          | Cannes Golden Palm Winners, Cannes 2018                                                    | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [César Awards](award/cesar.md)                                  | `cesar`           | César Best Film Winners, César 2018                                                        | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Critics Choice Awards](award/choice.md)                        | `choice`          | Critics Choice Best Picture Winners, Critics Choice Awards 2020                            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Emmy Awards](award/emmy.md)                                    | `emmy`            | Emmys Best in Category Winners, Emmys 2021                                                 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Golden Globe Awards](award/golden.md)                          | `golden`          | Golden Globes Best Picture Winners, Golden Globes Best Director Winners, Golden Globe 2019 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Independent Spirit Awards](award/spirit.md)                    | `spirit`          | Spirit Best Feature Winners, Independent Spirit Awards 2021                                | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [National Film Registry](award/nfr.md)                          | `nfr`             | National Film Registry All Time, National Film Registry 2021                               | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [People's Choice Awards](award/pca.md)                          | `pca`             | People's Choice Award Winners, People's Choice Awards 2022                                 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Razzie Awards](award/razzie.md)                                | `razzie`          | Razzies Golden Raspberry Winners, Razzie 2023                                              | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Screen Actors Guild Awards](award/sag.md)                      | `sag`             | Screen Actors Guild Award Winners, Screen Actors Guild 2021                                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Sundance Film Festival Awards](award/sundance.md)              | `sundance`        | Sundance Grand Jury Winners, Sundance Film Festival 2017                                   | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Toronto International Film Festival Awards](award/tiff.md)     | `tiff`            | Toronto People's Choice Award, Toronto International Film Festival 2020                    | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Venice Film Festival Awards](award/venice.md)                  | `venice`          | Venice Golden Lions, Venice 2023                                                           | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |

### Chart Collections

| Default                                          | Path              | Example Collections                        |             Works with Movies              |              Works with Shows              |
|:-------------------------------------------------|:------------------|:-------------------------------------------|:------------------------------------------:|:------------------------------------------:|
| [Chart Separator](chart/separator.md)            | `separator_chart` | Chart Collections                          | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Basic Charts](chart/basic.md)                   | `basic`           | Newly Released, New Episodes               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Tautulli Charts](chart/tautulli.md)<sup>1</sup> | `tautulli`        | Plex Popular, Plex Watched                 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [IMDb Charts](chart/imdb.md)                     | `imdb`            | IMDb Popular, IMDb Top 250                 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [TMDb Charts](chart/tmdb.md)                     | `tmdb`            | TMDb Popular, TMDb Airing Today            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Trakt Charts](chart/trakt.md)<sup>2</sup>       | `trakt`           | Trakt Popular, Trakt Trending              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [AniList Charts](chart/anilist.md)               | `anilist`         | AniList Popular, AniList Season            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [MyAnimeList Charts](chart/myanimelist.md)       | `myanimelist`     | MyAnimeList Popular, MyAnimeList Top Rated | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Letterboxd Charts](chart/letterboxd.md)         | `letterboxd`      | Letterboxd Top 250, Top 250 Most Fans      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red }   |
| [Other Charts](chart/other.md)                   | `other_chart`     | AniDB Popular, Common Sense Selection      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

<sup>1</sup> Requires [Tautulli Authentication](../config/tautulli.md)

<sup>2</sup> Requires [Trakt Authentication](../config/trakt.md)

### Content Collections

| Default                                                          | Path             | Example Collections                         |             Works with Movies              |              Works with Shows              |
|:-----------------------------------------------------------------|:-----------------|:--------------------------------------------|:------------------------------------------:|:------------------------------------------:|
| [Genres](both/genre.md)                                          | `genre`          | Action, Drama, Science Fiction              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| Franchises [Movie](movie/franchise.md)/[Show](show/franchise.md) | `franchise`      | Star Wars: Skywalker Saga, Godzilla (Anime) | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Universes](both/universe.md)                                    | `universe`       | Marvel Cinematic Universal, Wizarding World | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Based On...](both/based.md)                                     | `based`          | Based on a Book, Based on a True Story      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Collectionless](both/collectionless.md)                         | `collectionless` | Collectionless                              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

### Content Rating Collections

| Default                                                                                  | Path                 | Example Collections              |             Works with Movies              |              Works with Shows              |
|:-----------------------------------------------------------------------------------------|:---------------------|:---------------------------------|:------------------------------------------:|:------------------------------------------:|
| US Content Ratings [Movie](movie/content_rating_us.md)/[Show](show/content_rating_us.md) | `content_rating_us`  | G, PG, NC-17                     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [UK Content Ratings](both/content_rating_uk.md)                                          | `content_rating_uk`  | U, PG, 12A                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [DE Content Ratings](both/content_rating_de.md)                                          | `content_rating_de`  | Films 12, Films 16, Films 18     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [MyAnimeList Content Ratings](both/content_rating_mal.md)                                | `content_rating_mal` | G, PG, PG-13, R, R+, Rx          | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Common Sense Media Content Ratings](both/content_rating_cs.md)                          | `content_rating_cs`  | 1, 2, 3, 4, 5, 6, 15, 16, 17, 18 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

### Location Collections

| Default                                                          | Path        | Example Collections   |             Works with Movies              |              Works with Shows              |
|:-----------------------------------------------------------------|:------------|:----------------------|:------------------------------------------:|:------------------------------------------:|
| Countries [Movie](movie/country.md)/[Show](show/country.md)      | `country`   | Belgium, India        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| Regions [Movie](movie/region.md)/[Show](show/region.md)          | `region`    | Iberia, Balkans       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| Continents [Movie](movie/continent.md)/[Show](show/continent.md) | `continent` | Asia, North America   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

### Media Collections

| Default                                         | Path                | Example Collections                  |             Works with Movies              |              Works with Shows              |
|:------------------------------------------------|:--------------------|:-------------------------------------|:------------------------------------------:|:------------------------------------------:|
| [Aspect Ratios](both/aspect.md)                 | `aspect`            | 1.33, 1.65, 1.78, 1.85, 2.77         | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Resolutions](both/resolution.md)               | `resolution`        | 4K Movies, 1080p Movies, 720p Movies | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Audio Languages](both/audio_language.md)       | `audio_language`    | French Audio, Korean Audio           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Subtitle Languages](both/subtitle_language.md) | `subtitle_language` | German Subtitles, Swedish Subtitles  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

### Production Collections

| Default                        | Path        | Example Collections                      |             Works with Movies              |              Works with Shows              |
|:-------------------------------|:------------|:-----------------------------------------|:------------------------------------------:|:------------------------------------------:|
| [Networks](show/network.md)    | `network`   | Disney Channel, Lifetime                 |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| [Streaming](both/streaming.md) | `streaming` | Disney+ Movies, Max Shows                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Studios](both/studio.md)      | `studio`    | DreamWorks Studios, Walt Disney Pictures | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

### People Collections

| Default                        | Path       | Example Collections                                    |             Works with Movies              |              Works with Shows              |
|:-------------------------------|:-----------|:-------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|
| [Actors](both/actor.md)        | `actor`    | Chris Hemsworth, Margot Robbie                         | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Directors](movie/director.md) | `director` | Steven Spielberg (Director), Olivia Wilde (Director)   | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Producers](movie/producer.md) | `producer` | James Cameron (Producer), Reese Witherspoon (Producer) | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Writers](movie/writer.md)     | `writer`   | James Cameron (Writer), Lilly Wachowski (Writer)       | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |

### Time Collections

| Default                                                 | Path       | Example Collections        |             Works with Movies              |              Works with Shows              |
|:--------------------------------------------------------|:-----------|:---------------------------|:------------------------------------------:|:------------------------------------------:|
| [Seasonal](movie/seasonal.md)                           | `seasonal` | Easter, Christmas          | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Years](both/year.md)                                   | `year`     | Best of 2010, Best of 2019 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| Decades [Movie](movie/decade.md)/[Show](show/decade.md) | `decade`   | Best of 2012, Best of 2022 | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
