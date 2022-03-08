# <img width="80px" src="_static/pmm.png" alt="PMM"> Plex Meta Manager

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/meisnate12/Plex-Meta-Manager?style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/releases)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/meisnate12/plex-meta-manager?label=docker&sort=semver&style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Docker Pulls](https://img.shields.io/docker/pulls/meisnate12/plex-meta-manager?style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![GitHub commits since latest release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop)

[![Discord](https://img.shields.io/discord/822460010649878528?label=Discord&style=plastic)](https://discord.gg/NfH6mGFuAB)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/meisnate12/plex-meta-manager?style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Read the Docs](https://img.shields.io/readthedocs/plex-meta-manager?style=plastic)](https://metamanager.wiki)
[![Sponsor or Donate](https://img.shields.io/badge/-Sponsor_or_Donate-blueviolet?style=plastic)](https://github.com/sponsors/meisnate12)

Plex Meta Manager is an open source Python 3 project that has been designed to ease the creation and maintenance of metadata, collections, and playlists within a Plex Media Server. The script is designed to be run continuously and be able to update information based on sources outside your plex environment. Plex Meta Manager supports Movie/TV/Music libraries and Playlists.

## Getting Started

1. Install Plex Meta Manager; this process is described [here](/home/installation).

2. Once installed, you have to create a [Configuration File](config/configuration), which contains URLs and credentials and the like which are used to connect to services like Plex and TMDB.

3. After that you can start updating Metadata and building automatic Collections by creating a [Metadata File](metadata/metadata) for each Library you want to interact with.

4. After that, explore the Wiki to see all the different Collection Builders that can be used to create collections.

## Walkthroughs

If you find steps 1-3 above daunting, there are some walkthroughs available that will take you through those three steps: getting Plex Meta Manager installed, creating a config file, and creating a couple collections to show how the process works.

   1. The [Local Walkthrough](home/guides/local) covers installing the script natively [not in docker] on your local computer or a remote server.
   2. The [Docker Walkthrough](home/guides/docker) covers the same thing, running the script via Docker.
   3. The [unRAID Walkthrough](home/guides/unraid) gets you started configuring the script in UNRaid.  It doesn't go through the same steps with regard to creating the config file and metadata file, so you may want to go through the [Docker Walkthrough](home/guides/docker) first on your computer to gain that understanding.

## Development & Nightly Builds

### Development

The [develop](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop) branch has the most updated **documented** fixes and enhancements to Plex Meta Manager.  This version is tested and documented to some degree, but it is still an active development branch, so there may be rough edges.

Switching to `develop`:

````{tab} if running in Docker
<br/>
Add ":develop" to the image name in your run command or configuration:

```
meisnate12/plex-meta-manager:develop
```
<br/>
````
````{tab} if running on the host:

In the directory where you cloned PMM:

```bash
git checkout develop
```

To switch back:

```bash
git checkout master
```
<br/>
````

If switching to the develop build, it is recommended to also use the [develop](https://metamanager.wiki/en/develop/) branch of the wiki, which documents any changes made from the Master build.

### Nightly

There is also a [nightly](https://github.com/meisnate12/Plex-Meta-Manager/tree/nightly) build which will have the absolute latest version of the script, but it could easily break, there is no guarantee that it even works, and any new features will not be documented.

Switching to `nightly`:

````{tab} if running in Docker
<br/>
Add ":nightly" to the image name in your run command or configuration:

```
meisnate12/plex-meta-manager:nightly
```
<br/>
````
````{tab} if running on the host:

In the directory where you cloned PMM:

```bash
git checkout nightly
```

To switch back:

```bash
git checkout master
```
<br/>
````


As this build is subject to extreme change, there is no promise of the feature being documented in the [nightly](https://metamanager.wiki/en/nightly/) branch of the wiki and all discussions relating to changes made in the nightly build will be held within the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB).

## Example Usage

Plex Meta Manager gives the user the power to curate a set of Collections to make discovering and organizing media easy. They can be built either using plex-based searches/filters, or by using popular builders such as TMDb, IMDb, Trakt, MDBList, MyAnimeList and many more.

Some example collections that can be created are:
  * Trending/Popular (based on TMDb, IMDb, Trakt, etc.)
  * Streaming Service (such as Netflix, Disney+, etc.)
  * Networks
  * Studios
  * Genres
  * Actors
  * Decades

Below are some user-curated collections which have been created by Plex Meta Manager.

![Movie Preview](home/movie-preview.png)

![Show Preview](home/show-preview.png)

To see user submitted Metadata configuration files, and you to even add your own, go to the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs).

Plex Meta Manager can manage the metadata fields for movies, shows, seasons, episodes, artists, albums, tracks, and collections, which can allow you to have a full backup of your customizations in case of a database loss.

## Discord Support Server
Before posting on GitHub about an enhancement, error, or configuration question please visit the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB). we have a dedicated support thread system so that your query can be dealt with efficiently by our team and community.

## Feature Requests, Errors, and Configuration Questions
If you are unable to use the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB), please follow this guidance:
* If you have an idea for how to enhance Plex Meta Manager please open a new [Feature Request](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+enhancement&template=feature_request.md&title=Feature+Request%3A+).
* If you're getting an Error please update to the latest version and then open a [Bug Report](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+bug&template=bug_report.md&title=Bug%3A+) if the error persists.
* If you see a mistake/typo with the Plex Meta Manager Wiki or have an idea of how we can improve it please open a [Wiki Request](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+documentation&template=3.docs_request.yml&title=%5BDocs%5D%3A+)
* If you have a metadata configuration query please post in the [Discussions](https://github.com/meisnate12/Plex-Meta-Manager/discussions).

## Contributing
* Pull Requests are greatly encouraged, please submit all Pull Requests to the nightly branch.
* If you wish to contribute to the Wiki please fork and send a pull request on the [Plex Meta Manager Wiki Repository](https://github.com/meisnate12/Plex-Meta-Manager-Wiki).

## IBRACORP Video Walkthrough

[IBRACORP](https://ibracorp.io/) made a video walkthough for installing Plex Meta Manager on unRAID. While you might not be using unRAID the video goes over many key aspects of Plex Meta Manager and can be a great place to start learning how to use the script.

<iframe width="560" height="315" src="https://www.youtube.com/embed/dF69MNoot3w" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
