## Collections

These files can generally be used on both Movie and Show library-types, or are part of a category of collection (such as Award Shows.)

These collections are applied by calling the below paths into the `collection_files` section of your config.yml

=== "Awards"

    | Default                                                            | Path              | Example Collections                                                                        | Allowed Media       |
    |:-------------------------------------------------------------------|:------------------|:-------------------------------------------------------------------------------------------|:--------------------|
    | [Award Separator](../../award/separator)                           | `separator_award` | Award Collections                                                                          | `Movies`<br>`Shows` |
    | [Academy Awards (Oscars)](../../award/oscars)                      | `oscars`          | Oscars Best Picture Winners, Oscars Best Director Winners, Oscars 2022                     | `Movies`            |
    | [Berlin International Film Festival Awards](../../award/berlinale) | `berlinale`       | Berlinale Golden Bears, Berlinale 2021                                                     | `Movies`            |
    | [British Academy of Film Awards](../../award/bafta)                | `bafta`           | BAFTA Best Films, BAFTA 2021                                                               | `Movies`            |
    | [Cannes Film Festival Awards](../../award/cannes)                  | `cannes`          | Cannes Golden Palm Winners, Cannes 2018                                                    | `Movies`            |
    | [César Awards](../../award/cesar)                                  | `cesar`           | César Best Film Winners, César 2018                                                        | `Movies`            |
    | [Critics Choice Awards](../../award/choice)                        | `choice`          | Critics Choice Best Picture Winners, Critics Choice Awards 2020                            | `Movies`<br>`Shows` |
    | [Emmy Awards](../../award/emmy)                                    | `emmy`            | Emmys Best in Category Winners, Emmys 2021                                                 | `Movies`<br>`Shows` |
    | [Golden Globe Awards](../../award/golden)                          | `golden`          | Golden Globes Best Picture Winners, Golden Globes Best Director Winners, Golden Globe 2019 | `Movies`<br>`Shows` |
    | [Independent Spirit Awards](../../award/spirit)                    | `spirit`          | Spirit Best Feature Winners, Independent Spirit Awards 2021                                | `Movies`            |
    | [National Film Registry](../../award/nfr)                          | `nfr`             | National Film Registry All Time, National Film Registry 2021                               | `Movies`            |
    | [People's Choice Awards](../../award/pca)                          | `pca`             | People's Choice Award Winners, People's Choice Awards 2022                                 | `Movies`<br>`Shows` |
    | [Razzie Awards](../../award/razzie)                                | `razzie`          | Razzies Golden Raspberry Winners, Razzie 2023                                              | `Movies`            |
    | [Screen Actors Guild Awards](../../award/sag)                      | `sag`             | Screen Actors Guild Award Winners, Screen Actors Guild 2021                                | `Movies`<br>`Shows` |
    | [Sundance Film Festival Awards](../../award/sundance)              | `sundance`        | Sundance Grand Jury Winners, Sundance Film Festival 2017                                   | `Movies`            |
    | [Toronto International Film Festival Awards](../../award/tiff)     | `tiff`            | Toronto People's Choice Award, Toronto International Film Festival 2020                    | `Movies`            |
    | [Venice Film Festival Awards](../../award/venice)                  | `venice`          | Venice Golden Lions, Venice 2023                                                           | `Movies`            |

=== "Charts"

    <div class="annotate" markdown>

    | Default                                       | Path              | Example Collections                        | Allowed Media       |
    |:----------------------------------------------|:------------------|:-------------------------------------------|:--------------------|
    | [Chart Separator](../../chart/separator)      | `separator_chart` | Chart Collections                          | `Movies`<br>`Shows` |
    | [Basic Charts](../../chart/basic)             | `basic`           | Newly Released, New Episodes               | `Movies`<br>`Shows` |
    | [AniList Charts](../../chart/anilist)         | `anilist`         | AniList Popular, AniList Season            | `Movies`<br>`Shows` |
    | [IMDb Charts](../../chart/imdb)               | `imdb`            | IMDb Popular, IMDb Top 250                 | `Movies`<br>`Shows` |
    | [Letterboxd Charts](../../chart/letterboxd)   | `letterboxd`      | Letterboxd Top 250, Top 250 Most Fans      | `Movies`            |
    | [MyAnimeList Charts](../../chart/myanimelist) | `myanimelist`     | MyAnimeList Popular, MyAnimeList Top Rated | `Movies`<br>`Shows` |
    | [Tautulli Charts](../../chart/tautulli)(1)    | `tautulli`        | Plex Popular, Plex Watched                 | `Movies`<br>`Shows` |
    | [TMDb Charts](../../chart/tmdb)               | `tmdb`            | TMDb Popular, TMDb Airing Today            | `Movies`<br>`Shows` |
    | [Trakt Charts](../../chart/trakt)(2)          | `trakt`           | Trakt Popular, Trakt Trending              | `Movies`<br>`Shows` |
    | [Other Charts](../../chart/other)             | `other_chart`     | AniDB Popular, Common Sense Selection      | `Movies`<br>`Shows` |

    </div>

    1.  Requires [Tautulli Authentication](../../../config/tautulli)<br>
    2.  Requires [Trakt Authentication](../../../config/trakt)

=== "Content"

    | Default                                                                | Path             | Example Collections                         | Allowed Media       |
    |:-----------------------------------------------------------------------|:-----------------|:--------------------------------------------|:--------------------|
    | [Genres](../../both/genre)                                             | `genre`          | Action, Drama, Science Fiction              | `Movies`<br>`Shows` |
    | Franchises [Movie](../../movie/franchise)/[Show](../../show/franchise) | `franchise`      | Star Wars: Skywalker Saga, Godzilla (Anime) | `Movies`<br>`Shows` |
    | [Universes](../../both/universe)                                       | `universe`       | Marvel Cinematic Universal, Wizarding World | `Movies`<br>`Shows` |
    | [Based On...](../../both/based)                                        | `based`          | Based on a Book, Based on a True Story      | `Movies`<br>`Shows` |
    | [Collectionless](../../both/collectionless)                            | `collectionless` | Collectionless                              | `Movies`<br>`Shows` |

=== "Content Ratings"

    | Default                                                                                        | Path                 | Example Collections                                   | Allowed Media       |
    |:-----------------------------------------------------------------------------------------------|:---------------------|:------------------------------------------------------|:--------------------|
    | US Content Ratings [Movie](../../movie/content_rating_us)/[Show](../../show/content_rating_us) | `content_rating_us`  | G, PG, NC-17                                          | `Movies`<br>`Shows` |
    | [UK Content Ratings](../../both/content_rating_uk)                                             | `content_rating_uk`  | U, PG, 12A                                            | `Movies`<br>`Shows` |
    | [DE Content Ratings](../../both/content_rating_de)                                             | `content_rating_de`  | Films 12, Films 16, Films 18                          | `Movies`<br>`Shows` |
    | [AU Content Ratings](../../both/content_rating_au)                                             | `content_rating_au`  | G, PG, M, MA15+, R18+, X18+, NR                       | `Movies`<br>`Shows` |
    | [NZ Content Ratings](../../both/content_rating_nz)                                             | `content_rating_nz`  | G, PG, M, R13, RP13, R15, R16, RP16, R18, RP18, R, NR | `Movies`<br>`Shows` |
    | [MyAnimeList Content Ratings](../../both/content_rating_mal)                                   | `content_rating_mal` | G, PG, PG-13, R, R+, Rx                               | `Movies`<br>`Shows` |
    | [Common Sense Media Content Ratings](../../both/content_rating_cs)                             | `content_rating_cs`  | 1, 2, 3, 4, 5, 6, 15, 16, 17, 18                      | `Movies`<br>`Shows` |

=== "Location"

    | Default                                                                | Path        | Example Collections | Allowed Media       |
    |:-----------------------------------------------------------------------|:------------|:--------------------|:--------------------|
    | Countries [Movie](../../movie/country)/[Show](../../show/country)      | `country`   | Belgium, India      | `Movies`<br>`Shows` |
    | Regions [Movie](../../movie/region)/[Show](../../show/region)          | `region`    | Iberia, Balkans     | `Movies`<br>`Shows` |
    | Continents [Movie](../../movie/continent)/[Show](../../show/continent) | `continent` | Asia, North America | `Movies`<br>`Shows` |

=== "Media"

    | Default                                            | Path                | Example Collections                  | Allowed Media       |
    |:---------------------------------------------------|:--------------------|:-------------------------------------|:--------------------|
    | [Aspect Ratios](../../both/aspect)                 | `aspect`            | 1.33, 1.65, 1.78, 1.85, 2.77         | `Movies`<br>`Shows` |
    | [Resolutions](../../both/resolution)               | `resolution`        | 4K Movies, 1080p Movies, 720p Movies | `Movies`<br>`Shows` |
    | [Audio Languages](../../both/audio_language)       | `audio_language`    | French Audio, Korean Audio           | `Movies`<br>`Shows` |
    | [Subtitle Languages](../../both/subtitle_language) | `subtitle_language` | German Subtitles, Swedish Subtitles  | `Movies`<br>`Shows` |

=== "People"

    | Default                           | Path       | Example Collections                                    | Allowed Media       |
    |:----------------------------------|:-----------|:-------------------------------------------------------|:--------------------|
    | [Actors](../../both/actor)        | `actor`    | Chris Hemsworth, Margot Robbie                         | `Movies`<br>`Shows` |
    | [Directors](../../movie/director) | `director` | Steven Spielberg (Director), Olivia Wilde (Director)   | `Movies`            |
    | [Producers](../../movie/producer) | `producer` | James Cameron (Producer), Reese Witherspoon (Producer) | `Movies`            |
    | [Writers](../../movie/writer)     | `writer`   | James Cameron (Writer), Lilly Wachowski (Writer)       | `Movies`            |

=== "Production"

    | Default                           | Path        | Example Collections                      | Allowed Media       |
    |:----------------------------------|:------------|:-----------------------------------------|:--------------------|
    | [Networks](../../show/network)    | `network`   | Disney Channel, Lifetime                 | `Shows`             |
    | [Streaming](../../both/streaming) | `streaming` | Disney+ Movies, Max Shows                | `Movies`<br>`Shows` |
    | [Studios](../../both/studio)      | `studio`    | DreamWorks Studios, Walt Disney Pictures | `Movies`<br>`Shows` |

=== "Time"
    
    | Default                                                       | Path       | Example Collections          | Allowed Media       |
    |:--------------------------------------------------------------|:-----------|:-----------------------------|:--------------------|
    | [Seasonal](../../movie/seasonal)                              | `seasonal` | Easter, Christmas            | `Movies`            |
    | [Years](../../both/year)                                      | `year`     | Best of 2010, Best of 2019   | `Movies`<br>`Shows` |
    | Decades [Movie](../../movie/decade)/[Show](../../show/decade) | `decade`   | Best of 2012s, Best of 2022s | `Movies`<br>`Shows` |