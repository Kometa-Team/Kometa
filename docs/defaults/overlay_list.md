## Overlays

These files apply overlays and can generally be used on both Movie and Show library-types, and often works at the season and episode-level too.

It should be noted that when an overlay has &#10071; for a season or episode, it normally means that whilst the overlay can technically be applied at the level, it wasn't designed for this purpose. For example, a show's season cannot have a resolution since it is not a video file, and an episode cannot have a commonsense age-rating since only Movies and Shows are rated by CommonSense. 

In the scenario where there is missing data such as age ratings for episodes, then generally the highest-level data available will be applied at the lower level (i.e. a Show's CommonSense age rating would apply to all episodes).

These overlays are applied by calling the below paths into the `overlay_path` [section](../config/libraries.md#overlay-path) of your config.yml

### Overlay Files

| Default                                        | path             | Example Overlays                                                          |        Movies        |        Shows         |       Seasons       |       Episodes       |
|:-----------------------------------------------|:-----------------|:--------------------------------------------------------------------------|:--------------------:|:--------------------:|:-------------------:|:--------------------:|
| [Audio Codec](overlays/audio_codec)            | `audio_codec`    | Dolby Atmos logo, DTS logo                                                | &#9989;<sup>1</sup>  | &#9989;<sup>1</sup>  | &#9989;<sup>1</sup> | &#9989;<sup>1</sup>  |
| [CommonSense Age Rating](overlays/commonsense) | `commonsense`    | "3+", "16+"                                                               |       &#9989;        |       &#9989;        |      &#10071;       |       &#10071;       |
| [Direct Play](overlays/direct_play)            | `direct_play`    | "Direct Play Only"                                                        |       &#9989;        |       &#10071;       |      &#10071;       |       &#9989;        |
| [Episode Info](overlays/episode_info)          | `episode_info`   | "S01E01", "S02E09"                                                        |       &#10060;       |       &#10060;       |      &#10060;       |       &#9989;        |
| [FlixPatrol](overlays/flixpatrol)              | `flixpatrol`     | "Streaming service logo with words "TOP"                                  |       &#9989;        |       &#9989;        |      &#10060;       |       &#10060;       |
| [Language Count](overlays/language_count)      | `language_count` | Dual-Audio, Multi-Audio, Dual-Subtitle, Multi-Subtitle                    |       &#9989;        |       &#9989;        |       &#9989;       |       &#9989;        |
| [Languages](overlays/languages)                | `languages`      | Flags Based on the Audio/Subtitles a file has                             |       &#9989;        |       &#9989;        |       &#9989;       |       &#9989;        |
| [Mediastinger](overlays/mediastinger)          | `mediastinger`   | Mediastinger Logo for After/During Credit Scenes                          |       &#9989;        |       &#9989;        |      &#10060;       |       &#10060;       |
| [Ratings](overlays/ratings)                    | `ratings`        | IMDb Audience Rating, Metacritic Critic Rating                            | &#9989;<sup>3</sup>  | &#9989;<sup>3</sup>  |      &#10060;       | &#9989;<sup>3</sup>  |
| [Resolution/Editions](overlays/resolution)     | `resolution`     | 4K Dolby Vision logo, 720P logo, "Director's Cut", "Criterion Collection" | &#9989;<sup>2</sup>  | &#9989;<sup>2</sup>  |      &#10060;       | &#9989;<sup>2</sup>  |
| [Ribbon](overlays/ribbon)                      | `ribbon`         | IMDb Top 250 Ribbon, RT Fresh Ribbon                                      |       &#9989;        |       &#9989;        |      &#10060;       |       &#10060;       |
| [Runtimes](overlays/runtimes)                  | `runtimes`       | "Runtime: 1h 30m"                                                         |       &#9989;        |       &#9989;        |      &#10060;       |       &#9989;        |
| [Status](overlays/status)                      | `status`         | Airing, Returning, Canceled, Ended                                        |       &#10060;       |       &#9989;        |      &#10060;       |       &#10060;       |
| [Streaming](overlays/streaming)                | `streaming`      | Netflix logo, Hulu logo                                                   |       &#9989;        |       &#9989;        |      &#10060;       |       &#10060;       |
| [Versions](overlays/versions)                  | `versions`       | Multiple Versions logo                                                    |       &#9989;        |       &#9989;        |       &#9989;       |       &#9989;        |
| [Video Format](overlays/video_format)          | `video_format`   | "REMUX", "HDTV"                                                           | &#9989;<sup>1</sup>  |       &#10071;       |      &#10071        | &#9989;<sup>1</sup>  |
<sup>1</sup> Designed for [TRaSH Guides](https://trash-guides.info/) filename naming scheme
<sup>2</sup> Requires Plex Pass or [TRaSH Guides](https://trash-guides.info/) filename naming scheme
<sup>3</sup> Requires Template Variables to function