## Overlays

These files apply overlays and can generally be used on both Movie and Show library-types, and often works at the season and episode-level too.

It should be noted that when an overlay has &#10071; for a season or episode, it normally means that whilst the overlay can technically be applied at the level, it wasn't designed for this purpose. For example, a show's season cannot have a resolution since it is not a video file, and an episode cannot have a commonsense age-rating since only Movies and Shows are rated by CommonSense. 

In the scenario where there is missing data such as age ratings for episodes, then generally the highest-level data available will be applied at the lower level (i.e. a Show's CommonSense age rating would apply to all episodes).

These overlays are applied by calling the below paths into the `overlay_path` [section](../config/libraries.md#overlay-path) of your config.yml

### Chart Overlays

| Default                           | Path         | Example Overlays                         |  Movies  |  Shows  | Seasons  | Episodes |
|:----------------------------------|:-------------|:-----------------------------------------|:--------:|:-------:|:--------:|:--------:|
| [FlixPatrol](overlays/flixpatrol.md) | `flixpatrol` | "Streaming service logo with words "TOP" | &#9989;  | &#9989; | &#10060; | &#10060; |
| [Ribbon](overlays/ribbon.md)         | `ribbon`     | IMDb Top 250 Ribbon, RT Fresh Ribbon     | &#9989;  | &#9989; | &#10060; | &#10060; |

### Content Overlays

| Default                                 | Path           | Example Overlays                                 |  Movies  |  Shows   | Seasons  | Episodes |
|:----------------------------------------|:---------------|:-------------------------------------------------|:--------:|:--------:|:--------:|:--------:|
| [Episode Info](overlays/episode_info.md)   | `episode_info` | "S01E01", "S02E09"                               | &#10060; | &#10060; | &#10060; | &#9989;  |
| [Mediastinger](overlays/mediastinger.md)   | `mediastinger` | Mediastinger Logo for After/During Credit Scenes | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [Ratings](overlays/ratings.md)<sup>1</sup> | `ratings`      | IMDb Audience Rating, Metacritic Critic Rating   | &#9989;  | &#9989;  | &#10060; | &#9989;  |
| [Status](overlays/status.md)               | `status`       | Airing, Returning, Canceled, Ended               | &#10060; | &#9989;  | &#10060; | &#10060; |

<sup>1</sup> Requires Template Variables to function

### Media Overlays

| Default                                                  | Path             | Example Overlays                                                          | Movies  |  Shows   | Seasons  | Episodes |
|:---------------------------------------------------------|:-----------------|:--------------------------------------------------------------------------|:-------:|:--------:|:--------:|:--------:|
| [Aspect Ratio](overlays/aspect.md)<sup>1</sup>              | `aspect`         | "1.33","1.78"                                                             | &#9989; | &#9989;  | &#9989;  | &#9989;  |
| [Audio Codec](overlays/audio_codec.md)<sup>1</sup>          | `audio_codec`    | Dolby Atmos logo, DTS logo                                                | &#9989; | &#9989;  | &#9989;  | &#9989;  |
| [Audio/Subtitle Language Count](overlays/language_count.md) | `language_count` | Dual-Audio, Multi-Audio, Dual-Subtitle, Multi-Subtitle                    | &#9989; | &#9989;  | &#9989;  | &#9989;  |
| [Audio/Subtitle Language Flags](overlays/languages.md)      | `languages`      | Flags Based on the Audio/Subtitles a file has                             | &#9989; | &#9989;  | &#9989;  | &#9989;  |
| [Resolution/Editions](overlays/resolution.md)<sup>2</sup>   | `resolution`     | 4K Dolby Vision logo, 720P logo, "Director's Cut", "Criterion Collection" | &#9989; | &#9989;  | &#10060; | &#9989;  |
| [Runtimes](overlays/runtimes.md)                            | `runtimes`       | "Runtime: 1h 30m"                                                         | &#9989; | &#9989;  | &#10060; | &#9989;  |
| [Versions](overlays/versions.md)                            | `versions`       | Multiple Versions logo                                                    | &#9989; | &#9989;  | &#9989;  | &#9989;  |
| [Video Format](overlays/video_format.md)<sup>1</sup>        | `video_format`   | "REMUX", "HDTV"                                                           | &#9989; | &#10071; | &#10071; | &#9989;  |

<sup>1</sup> Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme

<sup>2</sup> Requires Plex Pass or [TRaSH Guides](https://trash-guides.info/) filename naming scheme

### Production Overlays

| Default                         | Path        | Example Overlays                                |  Movies  |  Shows  | Seasons  | Episodes |
|:--------------------------------|:------------|:------------------------------------------------|:--------:|:-------:|:--------:|:--------:|
| [Network](overlays/network.md)     | `network`   | "ABC", "CBS"                                    | &#10060; | &#9989; | &#9989;  | &#9989;  |
| [Streaming](overlays/streaming.md) | `streaming` | Netflix logo, Hulu logo                         | &#9989;  | &#9989; | &#10060; | &#10060; |
| [Studio](overlays/studio.md)       | `studio`    | "Warner Bros. Pictures", "Amblin Entertainment" | &#9989;  | &#9989; | &#9989;  | &#9989;  |

### Utility Overlays

| Default                             | Path          | Example Overlays   | Movies  |  Shows   | Seasons  | Episodes |
|:------------------------------------|:--------------|:-------------------|:-------:|:--------:|:--------:|:--------:|
| [Direct Play](overlays/direct_play.md) | `direct_play` | "Direct Play Only" | &#9989; | &#10071; | &#10071; | &#9989;  |
