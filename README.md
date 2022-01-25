# Plex Meta Manager

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/meisnate12/Plex-Meta-Manager?style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/releases)
[![GitHub commits since latest release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/meisnate12/plex-meta-manager?label=docker&sort=semver&style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/meisnate12/plex-meta-manager?style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Docker Pulls](https://img.shields.io/docker/pulls/meisnate12/plex-meta-manager?style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Discord](https://img.shields.io/discord/822460010649878528?label=Discord&style=plastic)](https://discord.gg/NfH6mGFuAB)
[![Sponsor or Donate](https://img.shields.io/badge/-Sponsor_or_Donate-blueviolet?style=plastic)](https://github.com/sponsors/meisnate12)

The original concept for Plex Meta Manager is [Plex Auto Collections](https://github.com/mza921/Plex-Auto-Collections), but this is rewritten from the ground up to be able to include a scheduler, metadata edits, multiple libraries, and logging. Plex Meta Manager is a Python 3 script that can be continuously run using YAML configuration files to update on a schedule the metadata of the movies, shows, and collections in your libraries as well as automatically build collections based on various methods all detailed in the wiki. Some collection examples that the script can automatically build and update daily include Plex Based Searches like actor, genre, or studio collections or Collections based on TMDb, IMDb, Trakt, TVDb, AniDB, or MyAnimeList lists and various other services.

The script can update many metadata fields for movies, shows, collections, seasons, and episodes and can act as a backup if your plex DB goes down. If the time is put into the metadata configuration file you can have a way to recreate your library and all its metadata changes with the click of a button.

The script works with most Metadata agents including the New Plex Movie Agent, New Plex TV Agent, [Hama Anime Agent](https://github.com/ZeroQI/Hama.bundle), [MyAnimeList Anime Agent](https://github.com/Fribb/MyAnimeList.bundle), and [XBMC NFO Movie and TV Agents](https://github.com/gboudreau/XBMCnfoMoviesImporter.bundle).

![Colletions1](https://raw.githubusercontent.com/wiki/meisnate12/Plex-Meta-Manager/collections1.png)

![Colletions2](https://raw.githubusercontent.com/wiki/meisnate12/Plex-Meta-Manager/collections2.png)

## Getting Started

1. Install Plex Meta Manager either by installing Python3 and following the [Local Walkthrough](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Local-Walkthrough)
   or by installing Docker and following the [Docker Walkthrough](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Docker-Walkthrough) or the [unRAID Walkthrough](https://github.com/meisnate12/Plex-Meta-Manager/wiki/unRAID-Walkthrough).
2. Once installed, you have to create a [Configuration File](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Configuration-File) filled with all your values to connect to the various services.
3. After that you can start updating Metadata and building automatic Collections by creating a [Metadata File](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Metadata-and-Playlist-File) for each Library you want to interact with.
4. Explore the [Wiki](https://github.com/meisnate12/Plex-Meta-Manager/wiki) to see all the different Collection Builders that can be used to create collections.

## Wiki
The [Wiki](https://github.com/meisnate12/Plex-Meta-Manager/wiki) details evey available option you have with Plex Meta Manager its Table of Contents is below. 

## Example Community Metadata Files
To see user submitted Metadata configuration files, and you to even add your own, go to the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs).

## Support Discord
Before posting on GitHub about an enhancement, error, or configuration question please visit the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB) **it is without a doubt the best place to get support**.

## Feature Requests, Errors, and Configuration Questions
* If you have an idea for how to enhance Plex Meta Manager please open a new [Feature Request](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+enhancement&template=feature_request.md&title=Feature+Request%3A+).
* If you're getting an Error please update to the latest develop branch and then open a [Bug Report](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+bug&template=bug_report.md&title=Bug%3A+) if it's still happening.
* If you have a metadata configuration question post in the [Discussions](https://github.com/meisnate12/Plex-Meta-Manager/discussions).

## Development Build
* There is a [develop](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop) branch which will have the most updated fixes and enhancements to the script.
* to access the Docker Image for the develop branch use the `develop` tag by adding `:develop` to the image name. i.e. `meisnate12/plex-meta-manager:develop`

## Contributing
* Pull Request are welcome but please submit them to the develop branch.
* If you wish to contribute to the Wiki please fork and send a pull request on the [Plex Meta Manager Wiki Repository](https://github.com/meisnate12/Plex-Meta-Manager-Wiki).

## IBRACORP Video Walkthrough

[IBRACORP](https://ibracorp.io/) made a video walkthough for installing Plex Meta Manager on unRAID. While you might not be using unRAID the video goes over many key accepts of Plex Meta Manager and can be a great place to start learning how to use the script.

[![Plex Meta Manager](https://img.youtube.com/vi/dF69MNoot3w/0.jpg)](https://www.youtube.com/watch?v=dF69MNoot3w "Plex Meta Manager")

## Wiki Table of Contents
- [Home](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Home)
- [Installation](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Installation)
- [Run Commands & Environmental Variables](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Run-Commands-&-Environmental-Variables)
  - [Local Walkthrough](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Local-Walkthrough)
  - [Docker Walkthrough](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Docker-Walkthrough)
  - [unRAID Walkthrough](https://github.com/meisnate12/Plex-Meta-Manager/wiki/unRAID-Walkthrough)
- [Configuration File](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Configuration-File)
  - [Libraries Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Libraries-Attributes)
    - [Operations Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Operations-Attributes)
  - [Playlist Files Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Playlist-Files-Attributes)
  - [Settings Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Settings-Attributes)
    - [Image Asset Directory](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Image-Asset-Directory)
  - [Webhooks Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Webhooks-Attributes)
  - [Plex Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Plex-Attributes)
  - [TMDb Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/TMDb-Attributes)
  - [Tautulli Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Tautulli-Attributes)
  - [OMDb Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/OMDb-Attributes)
  - [Notifiarr Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Notifiarr-Attributes)
  - [AniDB Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/AniDB-Attributes)
  - [Radarr Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Radarr-Attributes)
  - [Sonarr Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Sonarr-Attributes)
  - [Trakt Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Trakt-Attributes)
  - [MyAnimeList Attributes](https://github.com/meisnate12/Plex-Meta-Manager/wiki/MyAnimeList-Attributes)
- [Metadata and Playlist Files](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Metadata-and-Playlist-Files)
  - Metadata
    - [Movie Library Metadata](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Movie-Library-Metadata)
    - [TV Show Library Metadata](https://github.com/meisnate12/Plex-Meta-Manager/wiki/TV-Show-Library-Metadata)
    - [Music Library Metadata](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Music-Library-Metadata)
  - [Templates](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Templates)
  - [Filters](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Filters)
  - Builders
    - [Plex Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Plex-Builders)
    - [Smart Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Smart-Builders)
    - [TMDb Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/TMDb-Builders)
    - [TVDb Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/TVDb-Builders)
    - [IMDb Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/IMDb-Builders)
    - [Trakt Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Trakt-Builders)
    - [Tautulli Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Tautulli-Builders)
    - [MdbList Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/MdbList-Builders)
    - [Letterboxd Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Letterboxd-Builders)
    - [ICheckMovies Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/ICheckMovies-Builders)
    - [FlixPatrol Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/FlixPatrol-Builders)
    - [StevenLu Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/StevenLu-Builders)
    - [AniDB Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/AniDB-Builders)
    - [AniList Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/AniList-Builders)
    - [MyAnimeList Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/MyAnimeList-Builders)
  - Details
    - [Setting Details](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Setting-Details)
    - [Schedule Detail](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Schedule-Detail)
    - [Image Overlay Detail](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Image-Overlay-Detail)
    - [Metadata Details](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Metadata-Details)
    - [Arr Details](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Arr-Details)
- [Acknowledgements](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Acknowledgements)