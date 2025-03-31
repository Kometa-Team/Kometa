## Collections

These files can generally be used on both Movie and Show library-types, or are part of a category of collection (such as Award Shows.)

These collections are applied by calling the below paths into the `collection_files` section of your config.yml

=== "Awards"

    | Default                                                         | Path              | Example Collections                                                                        | Allowed Media        |
    |:----------------------------------------------------------------|:------------------|:-------------------------------------------------------------------------------------------|:----------------------|
    | [Award Separator](award/separator.md)                           | `separator_award` | Award Collections                                                                          | `Movies`<br>`Shows`     |
    | [Academy Awards (Oscars)](award/oscars.md)                      | `oscars`          | Oscars Best Picture Winners, Oscars Best Director Winners, Oscars 2022                     | `Movies`              |
    | [Berlin International Film Festival Awards](award/berlinale.md) | `berlinale`       | Berlinale Golden Bears, Berlinale 2021                                                     | `Movies`              |
    | [British Academy of Film Awards](award/bafta.md)                | `bafta`           | BAFTA Best Films, BAFTA 2021                                                               | `Movies`              |
    | [Cannes Film Festival Awards](award/cannes.md)                  | `cannes`          | Cannes Golden Palm Winners, Cannes 2018                                                    | `Movies`              |
    | [César Awards](award/cesar.md)                                  | `cesar`           | César Best Film Winners, César 2018                                                        | `Movies`              |
    | [Critics Choice Awards](award/choice.md)                        | `choice`          | Critics Choice Best Picture Winners, Critics Choice Awards 2020                            | `Movies`<br>`Shows`     |
    | [Emmy Awards](award/emmy.md)                                    | `emmy`            | Emmys Best in Category Winners, Emmys 2021                                                 | `Movies`<br>`Shows`     |
    | [Golden Globe Awards](award/golden.md)                          | `golden`          | Golden Globes Best Picture Winners, Golden Globes Best Director Winners, Golden Globe 2019 | `Movies`<br>`Shows`     |
    | [Independent Spirit Awards](award/spirit.md)                    | `spirit`          | Spirit Best Feature Winners, Independent Spirit Awards 2021                                | `Movies`              |
    | [National Film Registry](award/nfr.md)                          | `nfr`             | National Film Registry All Time, National Film Registry 2021                               | `Movies`              |
    | [People's Choice Awards](award/pca.md)                          | `pca`             | People's Choice Award Winners, People's Choice Awards 2022                                 | `Movies`<br>`Shows`     |
    | [Razzie Awards](award/razzie.md)                                | `razzie`          | Razzies Golden Raspberry Winners, Razzie 2023                                              | `Movies`              |
    | [Screen Actors Guild Awards](award/sag.md)                      | `sag`             | Screen Actors Guild Award Winners, Screen Actors Guild 2021                                | `Movies`<br>`Shows`     |
    | [Sundance Film Festival Awards](award/sundance.md)              | `sundance`        | Sundance Grand Jury Winners, Sundance Film Festival 2017                                   | `Movies`              |
    | [Toronto International Film Festival Awards](award/tiff.md)     | `tiff`            | Toronto People's Choice Award, Toronto International Film Festival 2020                    | `Movies`              |
    | [Venice Film Festival Awards](award/venice.md)                  | `venice`          | Venice Golden Lions, Venice 2023                                                           | `Movies`              |

=== "Charts"

    <div class="annotate" markdown>

    | Default                                          | Path              | Example Collections                        | Allowed Media        |
    |:-------------------------------------------------|:------------------|:-------------------------------------------|:----------------------|
    | [Chart Separator](chart/separator.md)            | `separator_chart` | Chart Collections                          | `Movies`<br>`Shows`     |
    | [Basic Charts](chart/basic.md)                   | `basic`           | Newly Released, New Episodes               | `Movies`<br>`Shows`     |
    | [AniList Charts](chart/anilist.md)               | `anilist`         | AniList Popular, AniList Season            | `Movies`<br>`Shows`     |
    | [IMDb Charts](chart/imdb.md)                     | `imdb`            | IMDb Popular, IMDb Top 250                 | `Movies`<br>`Shows`     |
    | [Letterboxd Charts](chart/letterboxd.md)         | `letterboxd`      | Letterboxd Top 250, Top 250 Most Fans      | `Movies`              |
    | [MyAnimeList Charts](chart/myanimelist.md)       | `myanimelist`     | MyAnimeList Popular, MyAnimeList Top Rated | `Movies`<br>`Shows`     |
    | [Tautulli Charts](chart/tautulli.md)(1) | `tautulli`        | Plex Popular, Plex Watched                 | `Movies`<br>`Shows`     |
    | [TMDb Charts](chart/tmdb.md)                     | `tmdb`            | TMDb Popular, TMDb Airing Today            | `Movies`<br>`Shows`     |
    | [Trakt Charts](chart/trakt.md)(2)       | `trakt`           | Trakt Popular, Trakt Trending              | `Movies`<br>`Shows`     |
    | [Other Charts](chart/other.md)                   | `other_chart`     | AniDB Popular, Common Sense Selection      | `Movies`<br>`Shows`     |

    </div>

    1.  Requires [Tautulli Authentication](../config/tautulli.md)<br>
    2.  Requires [Trakt Authentication](../config/trakt.md)

=== "Content"

    | Default                                                          | Path             | Example Collections                         | Allowed Media        |
    |:-----------------------------------------------------------------|:-----------------|:--------------------------------------------|:----------------------|
    | [Genres](both/genre.md)                                          | `genre`          | Action, Drama, Science Fiction              | `Movies`<br>`Shows`     |
    | Franchises [Movie](movie/franchise.md)/[Show](show/franchise.md) | `franchise`      | Star Wars: Skywalker Saga, Godzilla (Anime) | `Movies`<br>`Shows`     |
    | [Universes](both/universe.md)                                    | `universe`       | Marvel Cinematic Universal, Wizarding World | `Movies`<br>`Shows`     |
    | [Based On...](both/based.md)                                     | `based`          | Based on a Book, Based on a True Story      | `Movies`<br>`Shows`     |
    | [Collectionless](both/collectionless.md)                         | `collectionless` | Collectionless                              | `Movies`<br>`Shows`     |

=== "Content Ratings"

    | Default                                                                                  | Path                 | Example Collections                                   | Allowed Media        |
    |:-----------------------------------------------------------------------------------------|:---------------------|:------------------------------------------------------|:----------------------|
    | US Content Ratings [Movie](movie/content_rating_us.md)/[Show](show/content_rating_us.md) | `content_rating_us`  | G, PG, NC-17                                          | `Movies`<br>`Shows`     |
    | [UK Content Ratings](both/content_rating_uk.md)                                          | `content_rating_uk`  | U, PG, 12A                                            | `Movies`<br>`Shows`     |
    | [DE Content Ratings](both/content_rating_de.md)                                          | `content_rating_de`  | Films 12, Films 16, Films 18                          | `Movies`<br>`Shows`     |
    | [AU Content Ratings](both/content_rating_au.md)                                          | `content_rating_au`  | G, PG, M, MA15+, R18+, X18+, NR                       | `Movies`<br>`Shows`     |
    | [NZ Content Ratings](both/content_rating_nz.md)                                          | `content_rating_nz`  | G, PG, M, R13, RP13, R15, R16, RP16, R18, RP18, R, NR | `Movies`<br>`Shows`     |
    | [MyAnimeList Content Ratings](both/content_rating_mal.md)                                | `content_rating_mal` | G, PG, PG-13, R, R+, Rx                               | `Movies`<br>`Shows`     |
    | [Common Sense Media Content Ratings](both/content_rating_cs.md)                          | `content_rating_cs`  | 1, 2, 3, 4, 5, 6, 15, 16, 17, 18                      | `Movies`<br>`Shows`     |

=== "Location"

    | Default                                                          | Path        | Example Collections | Allowed Media        |
    |:-----------------------------------------------------------------|:------------|:--------------------|:----------------------|
    | Countries [Movie](movie/country.md)/[Show](show/country.md)      | `country`   | Belgium, India      | `Movies`<br>`Shows`     |
    | Regions [Movie](movie/region.md)/[Show](show/region.md)          | `region`    | Iberia, Balkans     | `Movies`<br>`Shows`     |
    | Continents [Movie](movie/continent.md)/[Show](show/continent.md) | `continent` | Asia, North America | `Movies`<br>`Shows`     |

=== "Media"

    | Default                                         | Path                | Example Collections                  | Allowed Media        |
    |:------------------------------------------------|:--------------------|:-------------------------------------|:----------------------|
    | [Aspect Ratios](both/aspect.md)                 | `aspect`            | 1.33, 1.65, 1.78, 1.85, 2.77         | `Movies`<br>`Shows`     |
    | [Resolutions](both/resolution.md)               | `resolution`        | 4K Movies, 1080p Movies, 720p Movies | `Movies`<br>`Shows`     |
    | [Audio Languages](both/audio_language.md)       | `audio_language`    | French Audio, Korean Audio           | `Movies`<br>`Shows`     |
    | [Subtitle Languages](both/subtitle_language.md) | `subtitle_language` | German Subtitles, Swedish Subtitles  | `Movies`<br>`Shows`     |

=== "People"

    | Default                        | Path       | Example Collections                                    | Allowed Media        |
    |:-------------------------------|:-----------|:-------------------------------------------------------|:----------------------|
    | [Actors](both/actor.md)        | `actor`    | Chris Hemsworth, Margot Robbie                         | `Movies`<br>`Shows`     |
    | [Directors](movie/director.md) | `director` | Steven Spielberg (Director), Olivia Wilde (Director)   | `Movies`              |
    | [Producers](movie/producer.md) | `producer` | James Cameron (Producer), Reese Witherspoon (Producer) | `Movies`              |
    | [Writers](movie/writer.md)     | `writer`   | James Cameron (Writer), Lilly Wachowski (Writer)       | `Movies`              |

=== "Production"

    | Default                        | Path        | Example Collections                      | Allowed Media        |
    |:-------------------------------|:------------|:-----------------------------------------|:----------------------|
    | [Networks](show/network.md)    | `network`   | Disney Channel, Lifetime                 | `Shows`               |
    | [Streaming](both/streaming.md) | `streaming` | Disney+ Movies, Max Shows                | `Movies`<br>`Shows`     |
    | [Studios](both/studio.md)      | `studio`    | DreamWorks Studios, Walt Disney Pictures | `Movies`<br>`Shows`     |

=== "Time"
    
    | Default                                                 | Path       | Example Collections          | Allowed Media        |
    |:--------------------------------------------------------|:-----------|:-----------------------------|:----------------------|
    | [Seasonal](movie/seasonal.md)                           | `seasonal` | Easter, Christmas            | `Movies`              |
    | [Years](both/year.md)                                   | `year`     | Best of 2010, Best of 2019   | `Movies`<br>`Shows`     |
    | Decades [Movie](movie/decade.md)/[Show](show/decade.md) | `decade`   | Best of 2012s, Best of 2022s | `Movies`<br>`Shows`     |