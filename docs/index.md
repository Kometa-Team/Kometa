---
title: Home
---
#

<style>
  .md-typeset h1,
  .md-content__button {
    display: none;
  }
</style>

<center>
![Logo](assets/logo-full.png)

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/Kometa-Team/Kometa?style=plastic)](https://github.com/Kometa-Team/Kometa/releases)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/kometateam/kometa?label=docker&sort=semver&style=plastic)](https://hub.docker.com/r/kometateam/kometa)
[![Docker Pulls](https://img.shields.io/docker/pulls/kometateam/kometa?style=plastic)](https://hub.docker.com/r/kometateam/kometa)
[![Develop GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/Kometa-Team/Kometa/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/Kometa-Team/Kometa/tree/develop)
[![Nightly GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/Kometa-Team/Kometa/latest/nightly?label=Commits%20in%20Nightly&style=plastic)](https://github.com/Kometa-Team/Kometa/tree/nightly)

[![Discord](https://img.shields.io/discord/822460010649878528?color=%2300bc8c&label=Discord&style=plastic)](https://kometa.wiki/en/latest/discord/)
[![Reddit](https://img.shields.io/badge/%2Fr%2Fkometa-e05d44?style=plastic&logo=Reddit&logoColor=white&labelColor=5d5d5d&color=00bc8c)](https://www.reddit.com/r/Kometa/)
[![Wiki](https://img.shields.io/readthedocs/kometa?color=%2300bc8c&style=plastic)](https://kometa.wiki)
[![Translations](https://img.shields.io/weblate/progress/kometa?color=00bc8c&server=https%3A%2F%2Ftranslations.kometa.wiki&style=plastic)](https://translations.kometa.wiki/projects/kometa/#languages)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/meisnate12?color=00bc8c&style=plastic)](https://github.com/sponsors/meisnate12)
[![Sponsor or Donate](https://img.shields.io/badge/-Sponsor%2FDonate-00bc8c?style=plastic)](https://github.com/sponsors/meisnate12)
[![Feature Requests](https://img.shields.io/badge/Feature%20Requests-00bc8c?style=plastic)](https://features.kometa.wiki/)
</center>

!!! info "What Happened to Plex Meta Manager?"

    On April 25th 2024, the Plex Meta Manager name was officially retired and replaced with Kometa. This change was essential to avoid a trademark issue with Plex.

    **If you are still using Plex Meta Manager and are unsure how to upgrade to Kometa, [click here to follow our guide](kometa/guides/rebrand.md)**

Kometa (formerly known as Plex Meta Manager) is a powerful tool designed to give you complete control over your media libraries. With Kometa, you can take your customization to the next level, with granular control over metadata, collections, overlays, and much more.

Transform your media library with Kometa and discover its full potential! Connect to third-party services like TMDb, Trakt, and IMDb, among others, to create one-of-a-kind collections, overlays and more. Your media library will stand out and be tailored to your specific needs.

## What Can Kometa Do?


<div class="grid cards" markdown>

-   :octicons-versions-24:{ .lg .middle } __Overhaul Your Media Libraries__

    ---

    Elevate your library with beautifully crafted metadata - customize artwork, titles, summaries, and more to create a stunning library.

-   :octicons-sliders-16:{ .lg .middle } __Kometa Defaults__

    ---

    Take advantage of pre-made modular Collections & Overlays to reduce the manual effort and get to the good stuff with less effort!

-   :material-connection:{ .lg .middle } __Third-Party Integrations__

    ---

    Harness the power of Trakt, TMDb, IMDb and more to create collections and overlays!

    Integrate with Sonarr and Radarr to automate your library growth.

-   :material-tools:{ .lg .middle } __Library Operations__

    ---

    Use operations to overhaul aspects of your library

    Replace ratings with your preferred source, fetch new posters from TMDb, backup your metadata to a file and more!


-   :material-star-face:{ .lg .middle } __And More!__

    ---

    We're constantly working on new features to take your library management experience to the next level.

    Consider sponsoring the project to allow us to continue building great features for you!

</div>

## Example Kometa Libraries 

Here are some examples of the things you can achieve using Kometa!

**Example Movie Collections using the [Kometa Defaults](defaults/collections.md)** (click to enlarge):

![Movie Collection Preview](images/movie-collection-preview.png){width="600"}

**Example Show Overlays using the [Kometa Defaults](defaults/overlays.md)** (click to enlarge):

![Show Library Preview](images/show-library-preview.png){ width="600" }

## Kometa Defaults

Want your library to look like the above images?  With the [Kometa Defaults](defaults/guide.md) you can! These powerful and modular files were designed by the Kometa team to make it simple to create a personalized, one-of-a-kind media collection without the hassle of manually defining each one.

Want to see what the community has to offer? Check out the [Kometa Community Configs](https://github.com/Kometa-Team/Community-Configs) repository on GitHub to see user-submitted configuration files, or even add your own to the mix!

With Kometa, you can also manage metadata for all your media types, from movies and shows to music and more. And since your metadata is managed outside your libraries, you'll never have to worry about losing your customizations in the event of a media server database loss, you can simply reapply them! It is also easy to move your customizations between servers if you need to.

## Getting Started

To get started with Kometa, follow these simple steps:

1. Install Kometa on your device. You can find the installation instructions for a variety of platforms [here](kometa/install/overview.md).

2. Once you have installed Kometa, create your [Configuration File](config/overview.md). This file contains important information such as URLs and credentials needed to connect to services like Plex and TMDb

3. After creating the Configuration File, you can start updating Metadata and building automatic Collections by creating a [Collection File](files/collections.md) for each Library you want to work with. If you'd rather use some of our pre-made Collection Files, take a look at the [Kometa Defaults](defaults/guide.md)

4. Finally, check out the [Wiki](https://kometa.wiki/), you'll find new and exciting ways to truly unlock the potential of your libraries.

## Step-by-Step Guides

If you're a beginner to the concepts of Python, Git and/or Kometa and find the above steps challenging, don't worry. We've got some step-by-step guides that can help you get started. These guides will take you through the process of installing Kometa, creating your Configuration File and getting some basic Collections up and running.

For those who need full installation walkthroughs, please refer to the following walkthrough guides:

  * [Local Walkthrough](kometa/install/local.md) - follow this if you are running the script directly on Windows, OS X, or Linux
  * [Docker Walkthrough](kometa/install/docker.md) - this discusses using Docker at the command line

If you are using unRAID, Kubernetes, QNAP, or Synology refer to the following basic guide to Docker container setup for each system:

**this doesn't cover the Kometa setup specifics found in the guides above with regard to creating the config file and collection file, so you may want to go through the [Docker Walkthrough](kometa/install/docker.md) first on your computer to gain that understanding.**

  * [unRAID Walkthrough](kometa/install/unraid.md)
  * [Kubernetes Walkthrough](kometa/install/kubernetes.md)
  * [QNAP Walkthrough](kometa/install/qnap.md)
  * [Synology Walkthrough](kometa/install/synology.md)

## Example Usage

Kometa puts you in control of your media library by letting you create custom Collections that make discovering and organizing your content a breeze. With powerful search and filtering options, you can build Collections based on popular builders like TMDb, IMDb, Trakt, and many more.

Imagine having Collections like these at your fingertips:

  * Trending and Popular (based on TMDb, IMDb, Trakt, etc.)
  * Streaming Services (like Netflix, Disney+, and more)
  * Networks
  * Studios
  * Genres
  * Actors
  * Decades

Kometa gives you endless possibilities to curate and organize your media library any way you want. Create custom Collections and Overlays that fit your unique preferences and make discovering your content effortless.

But if you don't want to spend time manually creating Collections and Overlays, we've got you covered. Check out the [Kometa Defaults](defaults/guide.md) - a handcrafted selection of tried-and-tested Collections and Overlays made by the Kometa team.

## Alternate Branches

The Develop and Nightly branches are "beta" versions of Kometa that are updated more frequently than the stable version (Master branch). These branches are where bug fixes, new features, and other changes are added before being released to the Master branch.

However, these branches (especially Nightly) are recommended for more technical users who don't mind updating frequently to get the latest changes. Keep in mind that these beta branches may have bugs or other issues that could cause problems with Kometa or your media server. So, if you're not comfortable with technical issues, it's best to stick with the Master branch.

??? "Develop Branch (click to expand)"

    [![Develop GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/Kometa-Team/Kometa/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/Kometa-Team/Kometa/tree/develop)

    The [develop](https://github.com/Kometa-Team/Kometa/tree/develop) branch has the most updated **documented** fixes and enhancements to Kometa.  This version is tested and documented to some degree, but it is still an active Develop branch, so there may be rough edges.

    Switching to `develop`:

    === "Running in Docker"
        Add ":develop" to the image name in your run command or configuration:
            ```
            kometateam/kometa:develop
            ```
    === "Running on the Host"
        In the directory where you cloned Kometa:
            ```bash
            git checkout develop
            ```
        To switch back:
            ```bash
            git checkout master
            ```
    
    If switching to the develop branch, it is recommended to also use the [develop branch of the wiki](https://kometa.wiki/en/develop/), which documents any changes made from the Master branch.

??? warning "Nightly Branch (click to expand)"

    [![Nightly GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/Kometa-Team/Kometa/latest/nightly?label=Commits%20in%20Nightly&style=plastic)](https://github.com/Kometa-Team/Kometa/tree/nightly)
    
    **This branch will have squashed commits which can cause `git pull`/`git fetch` to error you can use `git reset origin/nightly --hard` to fix the branch.**
    
    The [nightly](https://github.com/Kometa-Team/Kometa/tree/nightly) branch has the absolute latest version of Kometa, but it could easily break, there is no guarantee that it even works, and any new features will not be documented until they have progressed enough to reach the develop branch.

    Switching to `nightly`:

    === "Running in Docker"
        Add ":nightly" to the image name in your run command or configuration:
            ```
            kometateam/kometa:nightly
            ```
    === "Running on the Host"
        In the directory where you cloned Kometa:
            ```bash
            git checkout nightly
            ```
        To switch back:
            ```bash
            git checkout master
            ```

    As this branch is subject to extreme change, there is no promise of the feature being documented in the [nightly](https://kometa.wiki/en/nightly/) branch of the wiki and all discussions relating to changes made in the nightly branch will be held within the [Kometa Discord Server](https://kometa.wiki/en/latest/discord/).

???+ tip "`lmxl` Variants for Unsupported Hardware"

    In March 2024, lxml, a prerequisite for operating Kometa, ceased support for older CPUs. This impedes users from running Kometa on unsupported hardware.

    To address this issue, we have implemented 'lxml' variants for each Kometa branch (master, develop, and nightly). These variants resume compatibility with older hardware by freezing lxml on a previous version which has wider hardware support.

    To transition to the lxml branch, simply prepend 'lxml-' to the branch name you are currently utilizing. For instance, `Kometa-Team/Kometa:lxml-master`, `Kometa-Team/Kometa:lxml-develop` and `Kometa-Team/Kometa:lxml-nightly`.

## Discord Support Server

If you're looking for support for any questions or issues you might have, or if you just want to be a part of our growing community, Join the [Kometa Discord Server](https://kometa.wiki/en/latest/discord/).

## Feature Requests

At Kometa, we value our community's input and actively seek feedback to drive the evolution of our product. We want to hear your ideas on how to enhance Kometa, and we encourage you to visit our [Feature Request](https://features.kometa.wiki/features) page to share your thoughts or vote on what features you would like to see added next. Your voice matters and helps shape the future of Kometa, so please don't hesitate to join in the conversation and be a part of our community-driven development process.

## Errors and Configuration Questions

If you're having trouble, we recommend first joining the [Kometa Discord Server](https://kometa.wiki/en/latest/discord/) and seeking support there. If that isn't possible for you, here's what you can do:

* If you get an error, update to the latest version and check if the issue persists. If it does, report the bug by filling out the [Bug Report](https://github.com/Kometa-Team/Kometa/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+bug&template=bug_report.md&title=Bug%3A+) template.
* If you spot a mistake or have an idea to improve the [Kometa Wiki](https://kometa.wiki/), submit a request using the [Wiki Request](https://github.com/Kometa-Team/Kometa/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+documentation&template=3.docs_request.yml&title=%5BDocs%5D%3A+) template.
* If you have a question about metadata configuration, start a discussion on the [Discussions](https://github.com/Kometa-Team/Kometa/discussions). Remember, the community helps shape the future of Kometa, so your input is valuable!

For support on any of the above, visit the [Discord server](https://kometa.wiki/en/latest/discord/).

## Contributing
* Pull Requests are greatly encouraged, please submit all Pull Requests to the nightly branch.