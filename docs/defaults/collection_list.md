## Collections

These files can generally be used on both Movie and Show library-types, or are part of a category of collection (such as Award Shows.)

These collections are applied by calling the below paths into the `metadata_path` section of your config.yml

### Award Collections

| Default                                         | Path              | Example Collections                         |  Works with Movies   |  Works with Shows   |
|:------------------------------------------------|:------------------|:--------------------------------------------|:--------------------:|:-------------------:|
| [Award Separator](award/separator)              | `separator_award` | Award Collections                           |       &#9989;        |       &#9989;       |
| [Academy Awards (Oscars)](award/oscars)         | `oscars`          | Best Picture Winners                        |       &#9989;        |      &#10060;       |
| [British Academy of Film Awards](award/bafta)   | `bafta`           | BAFTA Best Films, BAFTA 2021                | &#9989;<sup>1</sup>  |      &#10060;       |
| [Cannes Film Festival Awards](award/cannes)     | `cannes`          | Cannes - Palme d'or, Cannes 2018            | &#9989;<sup>1</sup>  |      &#10060;       |
| [Critics Choice Awards](award/choice)           | `choice`          | Critics Choice Awards 2020                  | &#9989;<sup>1</sup>  | &#9989;<sup>1</sup> |
| [Emmy Awards](award/emmy)                       | `emmy`            | Emmys 2021                                  |       &#9989;        |       &#9989;       |
| [Golden Globe Awards](award/golden)             | `golden`          | Best Motion Pictures                        |       &#9989;        |       &#9989;       |
| [Independent Spirit Awards](award/spirit)       | `spirit`          | Independent Spirit Awards 2021              | &#9989;<sup>1</sup>  |      &#10060;       |
| [Sundance Film Festival Awards](award/sundance) | `sundance`        | Sundance Grand Jury Winners                 | &#9989;<sup>1</sup>  |      &#10060;       |
| [Other Awards](award/other)                     | `other_award`     | Berlinale Golden Bears, Venice Golden Lions | &#9989;<sup>1</sup>  |      &#10060;       |

<sup>1</sup> Requires [Trakt Authentication](../config/trakt)

### Chart Collections

| Default                                 | Path              | Example Collections                        |  Works with Movies  |  Works with Shows   |
|:----------------------------------------|:------------------|:-------------------------------------------|:-------------------:|:-------------------:|
| [Chart Separator](chart/separator)      | `separator_chart` | Chart Collections                          |       &#9989;       |       &#9989;       |
| [Basic Charts](chart/basic)             | `basic`           | Newly Released, New Episodes               |       &#9989;       |       &#9989;       |
| [Tautulli Charts](chart/tautulli)       | `tautulli`        | Plex Popular, Plex Watched                 | &#9989;<sup>2</sup> | &#9989;<sup>2</sup> |
| [IMDb Charts](chart/imdb)               | `imdb`            | IMDb Popular, IMDb Top 250                 |       &#9989;       |       &#9989;       |
| [TMDb Charts](chart/tmdb)               | `tmdb`            | TMDb Popular, TMDb Airing Today            |       &#9989;       |       &#9989;       |
| [Trakt Charts](chart/trakt)             | `trakt`           | Trakt Popular, Trakt Trending              | &#9989;<sup>1</sup> | &#9989;<sup>1</sup> |
| [AniList Charts](chart/anilist)         | `anilist`         | AniList Popular, AniList Season            |       &#9989;       |       &#9989;       |
| [MyAnimeList Charts](chart/myanimelist) | `myanimelist`     | MyAnimeList Popular, MyAnimeList Top Rated |       &#9989;       |       &#9989;       |
| [Other Charts](chart/other)             | `other_chart`     | AniDB Popular, Common Sense Selection      |       &#9989;       |       &#9989;       |

<sup>1</sup> Requires [Trakt Authentication](../config/trakt)
<sup>2</sup> Requires [Tautulli Authentication](../config/tautulli)

### Content Collections

| Default                                                    | Path        | Example Collections                         | Works with Movies | Works with Shows |
|:-----------------------------------------------------------|:------------|:--------------------------------------------|:-----------------:|:----------------:|
| [Genres](both/genre)                                       | `genre`     | Action, Drama, Science Fiction              |      &#9989;      |     &#9989;      |
| Franchises [Movie](movie/franchise)/[Show](show/franchise) | `franchise` | Star Wars: Skywalker Saga, Godzilla (Anime) |      &#9989;      |     &#9989;      |
| [Universes](both/universe)                                 | `universe`  | Marvel Cinematic Universal, Wizarding World |      &#9989;      |     &#9989;      |
| [Based On...](both/based)                                  | `based`     | Based on a Book, Based on a True Story      |      &#9989;      |     &#9989;      |

### Content Rating Collections

| Default                                                                            | Path                 | Example Collections              | Works with Movies | Works with Shows |
|:-----------------------------------------------------------------------------------|:---------------------|:---------------------------------|:-----------------:|:----------------:|
| US Content Ratings [Movie](movie/content_rating_us)/[Show](show/content_rating_us) | `content_rating_us`  | G, PG, NC-17                     |      &#9989;      |     &#9989;      |
| [UK Content Ratings](both/content_rating_uk)                                       | `content_rating_uk`  | U, PG, 12A                       |      &#9989;      |     &#9989;      |
| [MyAnimeList Content Ratings](both/content_rating_mal)                             | `content_rating_mal` | G, PG, PG-13, R, R+, Rx          |      &#9989;      |     &#9989;      |
| [Common Sense Media Content Ratings](both/content_rating_cs)                       | `content_rating_cs`  | 1, 2, 3, 4, 5, 6, 15, 16, 17, 18 |      &#9989;      |     &#9989;      |

### Location Collections

| Default                                                    | Path        | Example Collections    | Works with Movies | Works with Shows |
|:-----------------------------------------------------------|:------------|:-----------------------|:-----------------:|:----------------:|
| Countries [Movie](movie/country)/[Show](show/country)      | `country`   | Belgium, India         |      &#9989;      |     &#9989;      |
| Regions [Movie](movie/region)/[Show](show/region)          | `region`    | Iberia, Balkans        |      &#9989;      |     &#9989;      |
| Continents [Movie](movie/continent)/[Show](show/continent) | `continent` | Asia, North America    |      &#9989;      |     &#9989;      |

### Media Collections

| Default                                      | Path                | Example Collections                  | Works with Movies | Works with Shows |
|:---------------------------------------------|:--------------------|:-------------------------------------|:-----------------:|:----------------:|
| [Aspect Ratios](both/aspect)                 | `aspect`            | 1.33, 1.65, 1.78, 1.85, 2.77         |      &#9989;      |     &#9989;      |
| [Resolutions](both/resolution)               | `resolution`        | 4K Movies, 1080p Movies, 720p Movies |      &#9989;      |     &#9989;      |
| [Audio Languages](both/audio_language)       | `audio_language`    | French Audio, Korean Audio           |      &#9989;      |     &#9989;      |
| [Subtitle Languages](both/subtitle_language) | `subtitle_language` | German Subtitles, Swedish Subtitles  |      &#9989;      |     &#9989;      |

### Production Collections

| Default                     | Path        | Example Collections                      | Works with Movies | Works with Shows |
|:----------------------------|:------------|:-----------------------------------------|:-----------------:|:----------------:|
| [Networks](show/network)    | `network`   | Disney Channel, Lifetime                 |     &#10060;      |     &#9989;      |
| [Streaming](both/streaming) | `streaming` | Disney+ Movies, Max Shows                |      &#9989;      |     &#9989;      |
| [Studios](both/studio)      | `studio`    | DreamWorks Studios, Walt Disney Pictures |      &#9989;      |     &#9989;      |

### People Collections

| Default                     | Path       | Example Collections                                    | Works with Movies | Works with Shows |
|:----------------------------|:-----------|:-------------------------------------------------------|:-----------------:|:----------------:|
| [Actors](both/actor)        | `actor`    | Chris Hemsworth, Margot Robbie                         |      &#9989;      |     &#9989;      |
| [Directors](movie/director) | `director` | Steven Spielberg (Director), Olivia Wilde (Director)   |      &#9989;      |     &#10060;     |
| [Producers](movie/producer) | `producer` | James Cameron (Producer), Reese Witherspoon (Producer) |      &#9989;      |     &#10060;     |
| [Writers](movie/writer)     | `writer`   | James Cameron (Writer), Lilly Wachowski (Writer)       |      &#9989;      |     &#10060;     |

### Time Collections

| Default                                           | Path       | Example Collections        | Works with Movies | Works with Shows |
|:--------------------------------------------------|:-----------|:---------------------------|:-----------------:|:----------------:|
| [Seasonal](movie/seasonal)                        | `seasonal` | Easter, Christmas          |      &#9989;      |     &#10060;     |
| [Years](both/year)                                | `year`     | Best of 2010, Best of 2019 |      &#9989;      |     &#9989;      |
| Decades [Movie](movie/decade)/[Show](show/decade) | `decade`   | Best of 2012, Best of 2022 |      &#9989;      |     &#9989;      |

### Utility Collections

| Default                               | Path             | Example Collections      | Works with Movies | Works with Shows |
|:--------------------------------------|:-----------------|:-------------------------|:-----------------:|:----------------:|
| [Collectionless](both/collectionless) | `collectionless` | Collectionless           |      &#9989;      |     &#9989;      |
