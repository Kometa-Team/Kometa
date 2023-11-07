
# ![Logo](assets/logo-full.webp)

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/meisnate12/Plex-Meta-Manager?style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/releases)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/meisnate12/plex-meta-manager?label=docker&sort=semver&style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Docker Pulls](https://img.shields.io/docker/pulls/meisnate12/plex-meta-manager?style=plastic)](https://hub.docker.com/r/meisnate12/plex-meta-manager)
[![Develop GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop)
[![Nightly GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/nightly?label=Commits%20in%20Nightly&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/nightly)

[![Discord](https://img.shields.io/discord/822460010649878528?color=%2300bc8c&label=Discord&style=plastic)](https://discord.gg/NfH6mGFuAB)
[![Reddit](https://img.shields.io/reddit/subreddit-subscribers/PlexMetaManager?color=%2300bc8c&label=r%2FPlexMetaManager&style=plastic)](https://www.reddit.com/r/PlexMetaManager/)
[![Wiki](https://img.shields.io/readthedocs/plex-meta-manager?color=%2300bc8c&style=plastic)](https://metamanager.wiki)
[![Translations](https://img.shields.io/weblate/progress/plex-meta-manager?color=00bc8c&server=https%3A%2F%2Ftranslations.metamanager.wiki&style=plastic)](https://translations.metamanager.wiki/projects/plex-meta-manager/#languages)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/meisnate12?color=%238a2be2&style=plastic)](https://github.com/sponsors/meisnate12)
[![Sponsor or Donate](https://img.shields.io/badge/-Sponsor%2FDonate-blueviolet?style=plastic)](https://github.com/sponsors/meisnate12)
[![Feature Requests](https://img.shields.io/badge/Feature%20Requests-blueviolet?style=plastic)](https://features.metamanager.wiki/)

Plex Meta Manager is a powerful tool designed to give you complete control over your media libraries. With Plex Meta Manager, you can take your customization to the next level, with granular control over metadata, collections, overlays, and much more.

Transform your media library with Plex Meta Manager and discover its full potential! Connect to third-party services like TMDb, Trakt, and IMDb, among others, to create one-of-a-kind collections, overlays and more. Your media library will stand out and be tailored to your specific needs.

## What Can Plex Meta Manager Do?

:octicons-versions-24:{ .lg .middle } __Overhaul Your Media Libraries__

-  Elevate your library with beautifully crafted metadata - customize artwork, titles, summaries, and more to create a stunning library.

:octicons-sliders-16:{ .lg .middle } __PMM Defaults__

-  Take advantage of pre-made modular Collections & Overlays to reduce the manual effort and get to the good stuff with less effort!

:material-connection:{ .lg .middle } __Third-Party Integrations__

-  Harness the power of Trakt, TMDb, IMDb, Flixpatrol and more to create collections and overlays!
-  Integrate with Sonarr and Radarr to automate your library growth.

:material-star-face:{ .lg .middle } __And More!__

-  We're constantly working on new features to take your library management experience to the next level.
-  Consider sponsoring the project to allow us to continue building great features for you!

## Example Plex Meta Manager Libraries 

Here are some examples of the things you can achieve using Plex Meta Manager!

**Example Movie Collections using the [Plex Meta Manager Defaults](#Plex Meta Manager-defaults.md)** (click to enlarge):

![Movie Collection Preview](assets/movie-collection-preview.png){width="600"}

**Example Show Overlays using the [Plex Meta Manager Defaults](#Plex Meta Manager-defaults.md)** (click to enlarge):

![Show Library Preview](assets/show-library-preview.png){ width="600" }


## Plex Meta Manager Defaults

Want your library to look like the above images?  With the [PMM Defaults](defaults/guide.md) you can! These powerful and modular files were designed by the Plex Meta Manager team to make it simple to create a personalized, one-of-a-kind media collection without the hassle of manually defining each one.

Want to see what the community has to offer? Check out the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs) repository on GitHub to see user-submitted configuration files, or even add your own to the mix!

With Plex Meta Manager, you can also manage metadata for all your media types, from movies and shows to music and more. And since your metadata is managed outside of your libraries, you'll never have to worry about losing your customizations in the event of a media server database loss, you can simply reapply them! It is also easy to move your customizations between servers if you need to.

## Getting Started

To get started with Plex Meta Manager, follow these simple steps:

1. Install Plex Meta Manager on your device. You can find the installation instructions for a variety of platforms [here](pmm/install/installation.md).

2. Once you have installed Plex Meta Manager, create your [Configuration File](config/configuration.md). This file contains important information such as URLs and credentials needed to connect to services like Plex and TMDb

3. After creating the Configuration File, you can start updating Metadata and building automatic Collections by creating a [Metadata File](metadata/metadata.md) for each Library you want to work with. If you'd rather use some of our pre-made Metadata Files, take a look at the [Plex Meta Manager Defaults](#defaults-and-user-metadataoverlay-files)

4. Finally, check out the [Wiki](https://metamanager.wiki/), you'll find new and exciting ways to truly unlock the potential of your libraries.

## Step-by-Step Guides

If you're a beginner to the concepts of Python, Git and/or Plex Meta Manager and find the above steps challenging, don't worry. We've got some step-by-step guides that can help you get started. These guides will take you through the process of installing Plex Meta Manager, creating your Configuration File and getting some basic Collections up and running.

   1. The [Local Walkthrough](pmm/install/guides/local.md) covers installing Plex Meta Manager natively [not in docker] on your local computer or a remote server.
   2. The [Docker Walkthrough](pmm/install/guides/docker.md) covers installing Plex Meta Manager via Docker.
   3. The [unRAID Walkthrough](pmm/install/guides/unraid.md) gets you started configuring Plex Meta Manager in UNRaid.  It doesn't go through the same steps with regard to creating the config file and metadata file, so you may want to go through the [Docker Walkthrough](pmm/install/guides/docker.md) first on your computer to gain that understanding.

## Example Usage

Plex Meta Manager puts you in control of your media library by letting you create custom Collections that make discovering and organizing your content a breeze. With powerful search and filtering options, you can build Collections based on popular builders like TMDb, IMDb, Trakt, and many more.

Imagine having Collections like these at your fingertips:

  * Trending and Popular (based on TMDb, IMDb, Trakt, etc.)
  * Streaming Services (like Netflix, Disney+, and more)
  * Networks
  * Studios
  * Genres
  * Actors
  * Decades

Plex Meta Manager gives you endless possibilities to curate and organize your media library any way you want. Create custom Collections and Overlays that fit your unique preferences and make discovering your content effortless.

But if you don't want to spend time manually creating Collections and Overlays, we've got you covered. Check out the [PMM Defaults](defaults/guide.md) - a handcrafted selection of tried-and-tested Collections and Overlays made by the Plex Meta Manager team.



## Develop & Nightly Branches

The Develop and Nightly branches are "beta" versions of Plex Meta Manager that are updated more frequently than the stable version (Master branch). These branches are where bug fixes, new features, and other changes are added before being released to the Master branch.

However, these branches (especially Nightly) are recommended for more technical users who don't mind updating frequently to get the latest changes. Keep in mind that these beta branches may have bugs or other issues that could cause problems with Plex Meta Manager or your media server. So, if you're not comfortable with technical issues, it's best to stick with the Master branch.

??? "Develop Branch - Click to Expand"

    [![Develop GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop)

    The [develop](https://github.com/meisnate12/Plex-Meta-Manager/tree/develop) branch has the most updated **documented** fixes and enhancements to Plex Meta Manager.  This version is tested and documented to some degree, but it is still an active Develop branch, so there may be rough edges.

    Switching to `develop`:

    === "Running in Docker"
        Add ":develop" to the image name in your run command or configuration:
            ```
            meisnate12/plex-meta-manager:develop
            ```
    === "Running on the Host"
        In the directory where you cloned PMM:
            ```bash
            git checkout develop
            ```
        To switch back:
            ```bash
            git checkout master
            ```

    
    If switching to the develop branch, it is recommended to also use the [develop branch of the wiki](https://metamanager.wiki/en/develop/), which documents any changes made from the Master branch.

??? warning "Nightly Branch - Click to Expand"

    [![Nightly GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/meisnate12/plex-meta-manager/latest/nightly?label=Commits%20in%20Nightly&style=plastic)](https://github.com/meisnate12/Plex-Meta-Manager/tree/nightly)
    
    **This branch will have squashed commits which can cause `git pull`/`git fetch` to error you can use `git reset origin/nightly --hard` to fix the branch.**
    
    The [nightly](https://github.com/meisnate12/Plex-Meta-Manager/tree/nightly) branch has the absolute latest version of Plex Meta Manager, but it could easily break, there is no guarantee that it even works, and any new features will not be documented until they have progressed enough to reach the develop branch.

    Switching to `nightly`:

    === "Running in Docker"
        Add ":nightly" to the image name in your run command or configuration:
            ```
            meisnate12/plex-meta-manager:nightly
            ```
    === "Running on the Host"
        In the directory where you cloned PMM:
            ```bash
            git checkout nightly
            ```
        To switch back:
            ```bash
            git checkout master
            ```

    As this branch is subject to extreme change, there is no promise of the feature being documented in the [nightly](https://metamanager.wiki/en/nightly/) branch of the wiki and all discussions relating to changes made in the nightly branch will be held within the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB).

## Discord Support Server

If you're looking for support for any questions or issues you might have, or if you just want to be a part of our growing community, Join the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB).

## Feature Requests

At Plex Meta Manager, we value our community's input and actively seek feedback to drive the evolution of our product. We want to hear your ideas on how to enhance Plex Meta Manager, and we encourage you to visit our [Feature Request](https://features.metamanager.wiki/features) page to share your thoughts or vote on what features you would like to see added next. Your voice matters and helps shape the future of Plex Meta Manager, so please don't hesitate to join in the conversation and be a part of our community-driven development process.

## Errors and Configuration Questions

If you're having trouble, we recommend first joining the [Plex Meta Manager Discord Server](https://discord.gg/NfH6mGFuAB) and seeking support there. If that isn't possible for you, here's what you can do:

* If you get an error, update to the latest version and check if the issue persists. If it does, report the bug by filling out the [Bug Report](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+bug&template=bug_report.md&title=Bug%3A+) template.
* If you spot a mistake or have an idea to improve the [Plex Meta Manager Wiki](https://metamanager.wiki/), submit a request using the [Wiki Request](https://github.com/meisnate12/Plex-Meta-Manager/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+documentation&template=3.docs_request.yml&title=%5BDocs%5D%3A+) template.
* If you have a question about metadata configuration, start a discussion on the [Discussions](https://github.com/meisnate12/Plex-Meta-Manager/discussions). Remember, the community helps shape the future of Plex Meta Manager, so your input is valuable!

For support on any of the above, visit the [Discord server](https://discord.gg/ugfKXpFND8).