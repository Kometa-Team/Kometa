# Plex Meta Manager

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/meisnate12/Plex-Meta-Manager?style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/releases)
[![GitHub commits since latest release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/meisnate12/plex-meta-manager?label=docker&sort=semver&style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/meisnate12/plex-meta-manager?style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Docker Pulls](https://img.shields.io/docker/pulls/meisnate12/plex-meta-manager?style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Discord](https://img.shields.io/discord/822460010649878528?label=Discord&style=plastic)](https://discord.gg/TsdpsFYqqm)
[![Sponsor or Donate](https://img.shields.io/badge/-Sponsor_or_Donate-blueviolet?style=plastic)](https://github.com/sponsors/meisnate12)

The original concept for Plex Meta Manager is [Plex Auto Collections](https://github.com/mza921/Plex-Auto-Collections), but this is rewritten from the ground up to be able to include a scheduler, metadata edits, multiple libraries, and logging. Plex Meta Manager is a Python 3 script that can be continuously run using YAML configuration files to update on a schedule the metadata of the movies, shows, and collections in your libraries as well as automatically build collections based on various methods all detailed in the wiki. Some collection examples that the script can automatically build and update daily include Plex Based Searches like actor, genre, or studio collections or Collections based on TMDb, IMDb, Trakt, TVDb, AniDB, or MyAnimeList lists and various other services.

The script can update many metadata fields for movies, shows, collections, seasons, and episodes and can act as a backup if your plex DB goes down. It can even update metadata the plex UI can't like Season Names. If the time is put into the metadata configuration file you can have a way to recreate your library and all its metadata changes with the click of a button.

The script works with most Metadata agents including the New Plex Movie Agent, New Plex TV Agent, [Hama Anime Agent](https://github.com/ZeroQI/Hama.bundle), [MyAnimeList Anime Agent](https://github.com/Fribb/MyAnimeList.bundle), and [XBMC NFO Movie and TV Agents](https://github.com/gboudreau/XBMCnfoMoviesImporter.bundle).

## Getting Started

1. Install Plex Meta Manager either by installing Python3 and following the [Local Installation Guide](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Local-Installation)
   or by installing Docker and following the [Docker Installation Guide](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Docker-Installation) or the [unRAID Installation Guide](https://github.com/meisnate12/Plex-Meta-Manager/wiki/unRAID-Installation).
2. Once installed, you have to create a [Configuration File](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Configuration-File) filled with all your values to connect to the various services. 
3. After that you can start updating Metadata and building automatic Collections by creating a [Metadata File](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Metadata-File) for each Library you want to interact with.
4. Explore the [Wiki](https://github.com/meisnate12/Plex-Meta-Manager/wiki) to see all the different Collection Builders that can be used to create collections. 

## IBRACORP Video Walkthrough

[IBRACORP](https://ibracorp.io/) made a video walkthough for installing Plex Meta Manager on Unraid. While you might not be using Unraid the video goes over many key aspects of Plex Meta Manager and can be a great place to start learning how to use the script.

[![Plex Meta Manager](https://img.youtube.com/vi/dF69MNoot3w/0.jpg)](https://www.youtube.com/watch?v=dF69MNoot3w "Plex Meta Manager")

## Support

* Before posting on GitHub about an enhancement, error, or configuration question please visit the [Plex Meta Manager Discord Server](https://discord.gg/TsdpsFYqqm).
* If you're getting an Error or have an Enhancement post in the [Issues](https://github.com/meisnate12/Plex-Meta-Manager/issues).
* If you have a configuration question post in the [Discussions](https://github.com/meisnate12/Plex-Meta-Manager/discussions).
* To see user submitted Metadata configuration files, and even add your own, go to the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs).
* Pull Requests are welcome but please submit them to the develop branch.
* If you wish to contribute to the Wiki please fork and send a pull request on the [Plex Meta Manager Wiki Repository](https://github.com/meisnate12/Plex-Meta-Manager-Wiki).
