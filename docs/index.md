# <img src="_static/logo-full.png" alt="PMM">

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/meisnate12/Plex-Meta-Manager?style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/releases)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/meisnate12/plex-meta-manager?label=docker&sort=semver&style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Docker Pulls](https://img.shields.io/docker/pulls/meisnate12/plex-meta-manager?style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Develop GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop)
[![Nightly GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/nightly?label=Commits%20in%20Nightly&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/nightly)

[![Discord](https://img.shields.io/discord/822460010649878528?color=%2300bc8c&label=Discord&style=plastic)](https://discord.gg/NfH6mGFuAB)
[![Reddit](https://img.shields.io/reddit/subreddit-subscribers/PlexMetaManager?color=%2300bc8c&label=r%2FPlexMetaManager&style=plastic)](https://www.reddit.com/r/PlexMetaManager/)
[![Wiki](https://img.shields.io/readthedocs/plex-meta-manager?color=%2300bc8c&style=plastic)](https://metamanager.wiki)
[![Translations](https://img.shields.io/weblate/progress/plex-meta-manager?color=00bc8c&server=https%3A%2F%2Ftranslations.metamanager.wiki&style=plastic)](https://translations.metamanager.wiki/engage/plex-meta-manager/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/meisnate12?color=%238a2be2&style=plastic)](https://github.com/sponsors/meisnate12)
[![Sponsor or Donate](https://img.shields.io/badge/-Sponsor%2FDonate-blueviolet?style=plastic)](https://github.com/sponsors/meisnate12)
[![Feature Requests](https://img.shields.io/badge/Feature%20Requests-blueviolet?style=plastic)](https://features.metamanager.wiki/)

Plex Meta Manager is an open source Python 3 project that has been designed to ease the creation and maintenance of metadata, collections, and playlists within a Plex Media Server. The script is designed to be run continuously and be able to update information based on sources outside your plex environment. Plex Meta Manager supports Movie/TV/Music libraries and Playlists.

## What Can Plex-Meta-Manager Do?

Plex Meta Manager can

1. Create and maintain collections in Plex libraries using external lists, Plex searches, or filters.

2. Create, maintain, and share playlists on Plex servers using the same or similar criteria.

3. Manage metadata [artwork, titles, summaries, release year, etc.] for anything on your Plex server.

4. Add overlays to item artwork to display various details [ratings, resolution, edition, etc.].

5. Send missing items from external lists [for example the IMDB 250] to Radarr or Sonarr for download.

6. and more.

## Getting Started

These are the high-level steps you must take to get Plex Meta Manager up and running:

1. Install Plex Meta Manager; this process is described [here](home/installation).

2. Once installed, you have to create a [Configuration File](config/configuration), which contains URLs and credentials and the like which are used to connect to services like Plex and TMDb.

3. After that you can start updating Metadata and building automatic Collections by creating a [Metadata File](metadata/metadata) for each Library you want to interact with.

4. After that, explore the [Wiki](https://metamanager.wiki/) to see all the different Collection Builders that can be used to create collections.

## Walkthroughs

If you find steps 1-3 above daunting, there are some walkthroughs available that will take you through those three steps: getting Plex Meta Manager installed, creating a config file, and creating a couple collections to show how the process works.

   1. The [Local Walkthrough](home/guides/local) covers installing the script natively [not in docker] on your local computer or a remote server.
   2. The [Docker Walkthrough](home/guides/docker) covers the same thing, running the script via Docker.
   3. The [unRAID Walkthrough](home/guides/unraid) gets you started configuring the script in UNRaid.  It doesn't go through the same steps with regard to creating the config file and metadata file, so you may want to go through the [Docker Walkthrough](home/guides/docker) first on your computer to gain that understanding.

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

Below are some user-curated collections which have been created by Plex Meta Manager using the [PMM Defaults](defaults/guide).

### Example Movie Collection
![Movie Collection Preview](home/movie-collection-preview.png)

### Example Movie Overlays
![Movie Library Preview](home/movie-library-preview.png)

### Example Show Collection
![Show Collection Preview](home/show-collection-preview.png)

### Example Show Overlays
![Show Library Preview](home/show-library-preview.png)

## Develop & Nightly Branches

Develop and Nightly branches are deemed as "beta" branches which are updated far more frequently than the master branch. Bug fixes, new features and any other code added to Plex Meta Manager first goes to the nightly branch, followed by the develop branch, before finally being released to the master branch.

These branches (particularly the nightly branch) are only recommended for those who have a technical knowledge of Plex Meta Manager, and are happy with having to frequently update to receive the latest changes, and accept the risk that these branches may suffer breakages at any point.

<details class="details-tabs">
  <summary>Develop Branch - Click to Expand</summary>

[![Develop GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop)

The [develop](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop) branch has the most updated **documented** fixes and enhancements to Plex Meta Manager.  This version is tested and documented to some degree, but it is still an active Develop branch, so there may be rough edges.

Switching to `develop`:
````{tab} Running in Docker
Add ":develop" to the image name in your run command or configuration:
```
meisnate12/plex-meta-manager:develop
```
````
````{tab} Running on the Host
In the directory where you cloned PMM:
```bash
git checkout develop
```
To switch back:
```bash
git checkout master
```
````

If switching to the develop branch, it is recommended to also use the [develop branch of the wiki](https://metamanager.wiki/en/develop/), which documents any changes made from the Master branch.

</details>

<br>

<details class="details-tabs">
  <summary>Nightly Branch - Click to Expand</summary>

[![Nightly GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/nightly?label=Commits%20in%20Nightly&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/nightly)

**This branch will have squashed commits which can cause `git pull`/`git fetch` to error you can use `git reset origin/nightly --hard` to fix the branch.**

There is also a [nightly](https://github.com/meisnate12/Plex-Meta-Manager/tree/nightly) branch which will have the absolute latest version of the script, but it could easily break, there is no guarantee that it even works, and any new features will not be documented until they have progressed enough to reach the develop branch.

Switching to `nightly`:

````{tab} Running in Docker
Add ":nightly" to the image name in your run command or configuration:
```
meisnate12/plex-meta-manager:nightly
```
````
````{tab} Running on the Host
In the directory where you cloned PMM:
```bash
git checkout nightly
```
To switch back:
```bash
git checkout master
```
````

As this branch is subject to extreme change, there is no promise of the feature being documented in the [nightly](https://metamanager.wiki/en/nightly/) branch of the wiki and all discussions relating to changes made in the nightly branch will be held within the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB).
</details>

## Defaults and User Metadata/Overlay Files

The overlays and collection built in the images above can be easily added to any plex by using the [PMM Defaults](defaults/guide). These Files were created by the PMM team to make it easier than ever to have customized collections and overlays.

To see user submitted Metadata configuration files, and you to even add your own, go to the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs).

Plex Meta Manager can manage the metadata fields for movies, shows, seasons, episodes, artists, albums, tracks, and collections, which can allow you to have a full backup of your customizations in case of a database loss.

## Discord Support Server
Before posting on GitHub about an enhancement, error, or configuration question please visit the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB). we have a dedicated support thread system so that your query can be dealt with efficiently by our team and community.

## Feature Requests
If you have an idea for how to enhance Plex Meta Manager or just want to vote on what should be added next please visit the [Feature Request](https://features.metamanager.wiki/features) Page.

## Errors and Configuration Questions
If you are unable to use the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB), please follow this guidance:
* If you're getting an Error please update to the latest version and then open a [Bug Report](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+bug&template=bug_report.md&title=Bug%3A+) if the error persists.
* If you see a mistake/typo with the [Plex Meta Manager Wiki](https://metamanager.wiki/) or have an idea of how we can improve it please open a [Wiki Request](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+documentation&template=3.docs_request.yml&title=%5BDocs%5D%3A+)
* If you have a metadata configuration query please post in the [Discussions](https://github.com/meisnate12/Plex-Meta-Manager/discussions).

## Contributing
* Pull Requests are greatly encouraged, please submit all Pull Requests to the nightly branch.

<br>
