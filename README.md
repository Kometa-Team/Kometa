# <img src="https://kometa.wiki/en/nightly/assets/images/icons/logo-full.png" alt="Kometa">

<!--shield-start-->
<a href="https://github.com/Kometa-Team/Kometa/releases"><img src="https://img.shields.io/github/v/release/Kometa-Team/Kometa?style=plastic" alt="GitHub release (latest by date)"></a>
<a href="https://hub.docker.com/r/kometateam/kometa"><img src="https://img.shields.io/docker/v/kometateam/kometa?label=docker&sort=semver&style=plastic" alt="Docker Image Version"></a>
<a href="https://hub.docker.com/r/kometateam/kometa"><img src="https://img.shields.io/docker/pulls/kometateam/kometa?style=plastic" alt="Docker Pulls"></a>
<a href="https://github.com/Kometa-Team/Kometa/tree/develop"><img src="https://img.shields.io/github/commits-since/Kometa-Team/Kometa/latest/develop?label=Commits%20in%20Develop&style=plastic" alt="Commits in Develop"></a>
<a href="https://github.com/Kometa-Team/Kometa/tree/nightly"><img src="https://img.shields.io/github/commits-since/Kometa-Team/Kometa/latest/nightly?label=Commits%20in%20Nightly&style=plastic" alt="Commits in Nightly"></a>

<br>

<a href="https://kometa.wiki/en/latest/discord/"><img src="https://img.shields.io/discord/822460010649878528?color=%2300bc8c&label=Discord&style=plastic" alt="Discord"></a>
<a href="https://www.reddit.com/r/kometa/"><img src="https://img.shields.io/badge/%2Fr%2Fkometa-e05d44?style=plastic&logo=Reddit&logoColor=white&labelColor=0e8a6a&color=00bc8c" alt="Reddit"></a>
<a href="https://kometa.wiki"><img src="https://img.shields.io/readthedocs/kometa?color=%2300bc8c&style=plastic" alt="Wiki"></a>
<a href="https://translations.kometa.wiki/projects/kometa/#languages"><img src="https://img.shields.io/weblate/progress/kometa?color=00bc8c&server=https%3A%2F%2Ftranslations.kometa.wiki&style=plastic" alt="Translations"></a>
<a href="https://github.com/sponsors/meisnate12"><img src="https://img.shields.io/github/sponsors/meisnate12?color=%238a2be2&style=plastic" alt="GitHub Sponsors"></a>
<a href="https://github.com/sponsors/meisnate12"><img src="https://img.shields.io/badge/-Sponsor%2FDonate-blueviolet?style=plastic" alt="Sponsor or Donate"></a>
<a href="https://features.kometa.wiki/"><img src="https://img.shields.io/badge/Feature%20Requests-blueviolet?style=plastic" alt="Feature Requests"></a>
<!--shield-end-->
<!--intro-start-->
Kometa is a powerful tool designed to give you complete control over your media libraries. With Kometa, you can take your customization to the next level, 
with granular control over metadata, collections, overlays, and much more.

Transform your media library with Kometa and discover its full potential! Connect to third-party services like TMDb, Trakt, and IMDb, among others, 
to create one-of-a-kind collections, overlays and more. Your media library will stand out and be tailored to your specific needs.

## What Can Kometa Do?
<!--intro-end-->
<!--whatcanitdo-start-->
Elevate your library with beautifully crafted metadata - customize artwork, titles, summaries, and more to create a stunning library.

Harness the power of Trakt, TMDb, IMDb and more to create collections and overlays. Take advantage of pre-made modular Collections & Overlays to reduce the manual effort and get to the good stuff with less effort! You can see some example Collection images above and some example Overlay images below.

Integrate with Sonarr and Radarr to automate your library growth.
<!--whatcanitdo-end-->

## Example Kometa Libraries 

Here are some examples of the things you can achieve using Kometa!

**Example Movie Collections using the [Kometa Defaults](https://kometa.wiki/en/latest/defaults/collections/)** (click to enlarge):

<img src="https://kometa.wiki/en/nightly/assets/images/movie-collections.png" width="600" alt="Movie Collection Preview">

**Example Show Overlays using the [Kometa Defaults](https://kometa.wiki/en/latest/defaults/overlays/)** (click to enlarge):

<img src="https://kometa.wiki/en/nightly/assets/images/show-overlays.png" width="600" alt="Show Collection Preview">

<!--collecionsoverlays-start-->
## Collections & Overlays

The [Kometa Defaults](https://kometa.wiki/en/latest/defaults/guide/) are modular files designed by the Kometa team to make it simple to create a personalized, one-of-a-kind media collection without the hassle of manually defining each one.

Want to see what the community has to offer? Check out the [Kometa Community Configs](https://github.com/Kometa-Team/Community-Configs) repository on GitHub to see user-submitted configuration files, or even add your own to the mix!

With Kometa, you can also manage metadata for all your media types, from movies and shows to music and more and since your metadata is managed outside your libraries, 
you'll never have to worry about losing your customizations in the event of a media server database loss, you can simply reapply them! 
It is also easy to move your customizations between servers if you need to.
<!--collecionsoverlays-end-->

<!--started-start-->
## Getting Started

To get started with Kometa, follow these simple steps:

1.  Install Kometa on your device. You can find the installation instructions for a variety of platforms [here](https://kometa.wiki/en/latest/kometa/install/overview/).

2.  Once you have installed Kometa, create your [Configuration File](https://kometa.wiki/en/latest/config/overview/). 
     file contains important information such as URLs and credentials needed to connect to services like Plex and TMDb.

3.  After creating the Configuration File, you can start updating Metadata and building automatic Collections by creating a 
    [Collection File](https://kometa.wiki/en/latest/files/collections/) for each Library you want to work with. 
    If you'd rather use some of our pre-made Collection Files, take a look at the [Kometa Defaults](https://kometa.wiki/en/latest/defaults/guide/).

4.  Finally, check out the [Wiki](https://kometa.wiki), you'll find new and exciting ways to truly unlock the potential of your libraries.

## Step-by-Step Guides

If you're a beginner to the concepts of Python, Git and/or Kometa and find the above steps challenging, don't worry. We've got some step-by-step guides that can help you get 
started. These guides will take you through the process of installing Kometa, creating your Configuration File and getting some basic Collections up and running.

For those who need full installation walkthroughs, please refer to the following walkthrough guides:

  * [Local Walkthrough](https://kometa.wiki/en/latest/kometa/install/walkthroughs/local/) - follow this if you are running the script directly on Windows, OS X, or Linux.
  * [Docker Walkthrough](https://kometa.wiki/en/latest/kometa/install/walkthroughs/docker/) - this discusses using Docker at the command line.

If you are using unRAID, Kubernetes, QNAP, or Synology refer to the following basic guide to Docker container setup for each system:

**This doesn't cover the Kometa setup specifics found in the guides above with regard to creating the config file and collection file, so you may want to go through the 
[Docker Walkthrough](https://kometa.wiki/en/latest/kometa/install/walkthroughs/docker/) first on your computer to gain that understanding.**

  * [unRAID Walkthrough](https://kometa.wiki/en/latest/kometa/install/walkthroughs/unraid/)
  * [Kubernetes Walkthrough](https://kometa.wiki/en/latest/kometa/install/walkthroughs/kubernetes/)
  * [QNAP Walkthrough](https://kometa.wiki/en/latest/kometa/install/walkthroughs/qnap/)
  * [Synology Walkthrough](https://kometa.wiki/en/latest/kometa/install/walkthroughs/synology/)


## Example Usage

Kometa puts you in control of your media library by letting you create custom Collections that make discovering and organizing your content a breeze. 
With powerful search and filtering options, you can build Collections based on popular builders like TMDb, IMDb, Trakt, and many more.

Imagine having Collections like these at your fingertips:

  * Trending and Popular (based on TMDb, IMDb, Trakt, etc.)
  * Streaming Services (like Netflix, Disney+, and more)
  * Networks
  * Studios
  * Genres
  * Actors
  * Decades

Kometa gives you endless possibilities to curate and organize your media library any way you want. Create custom 
Collections and Overlays that fit your unique preferences and make discovering your content effortless.

But if you don't want to spend time manually creating Collections and Overlays, we've got you covered. Check out the 
[Kometa Defaults](https://kometa.wiki/en/latest/defaults/guide/) - a handcrafted selection of tried-and-tested Collections and Overlays made by the Kometa team.
<!--started-end-->
## Alternate Branches

The Develop and Nightly branches are "beta" versions of Kometa that are updated more frequently than the stable version (Master branch). 
These branches are where bug fixes, new features, and other changes are added before being released to the Master branch.

However, these branches (especially Nightly) are recommended for more technical users who don't mind updating frequently to get the latest changes. 
Keep in mind that these beta branches may have bugs or other issues that could cause problems with Kometa or your media server. 
So, if you're not comfortable with technical issues, it's best to stick with the Master branch.

### Develop Branch

<!--develop-start-->
[![Develop GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/Kometa-Team/Kometa/latest/develop?label=Commits%20in%20Develop&style=plastic)](https://github.com/Kometa-Team/Kometa/tree/develop)

The [develop](https://github.com/Kometa-Team/Kometa/tree/develop) branch has the most updated **documented** fixes and enhancements to Kometa. 
This version is tested and documented to some degree, but it is still an active Develop branch, so there may be rough edges.

Switching to `develop`:
<!--develop-end-->

<details>
  <summary>Running in Docker (click to expand)</summary>

<!--develop-docker-start-->
Add ":develop" to the image name in your run command or configuration:
```
kometateam/kometa:develop
```
<!--develop-docker-end-->

</details>

<details>
  <summary>Running on the Host (click to expand)</summary>

<!--develop-host-start-->
In the directory where you cloned Kometa:
```bash
git checkout develop
```
To switch back:
```bash
git checkout master
```
<!--develop-host-end-->

</details>

<!--develop2-start-->
If switching to the develop branch, it is recommended to also use the [develop branch of the wiki](https://kometa.wiki/en/develop/), 
which documents any changes made from the Master branch.
<!--develop2-end-->

### Nightly Branch

<!--nightly-start-->
[![Nightly GitHub commits since latest stable release (by SemVer)](https://img.shields.io/github/commits-since/Kometa-Team/Kometa/latest/nightly?label=Commits%20in%20Nightly&style=plastic)](https://github.com/Kometa-Team/Kometa/tree/nightly)

**This branch will have squashed commits which can cause `git pull`/`git fetch` to error you can use `git reset origin/nightly --hard` to fix the branch.**

There is also a [nightly](https://github.com/Kometa-Team/Kometa/tree/nightly) branch which will have the absolute latest version of the script, but it could easily break, 
there is no guarantee that it even works, and any new features will not be documented until they have progressed enough to reach the develop branch.

Switching to `nightly`:
<!--nightly-end-->


<details>
  <summary>Running in Docker (click to expand)</summary>

<!--nightly-docker-start-->
Add ":nightly" to the image name in your run command or configuration:
```
kometateam/kometa:nightly
```
<!--nightly-docker-end-->

</details>

<details>
  <summary>Running on the Host (click to expand)</summary>

<!--nightly-host-start-->
In the directory where you cloned Kometa:
```bash
git checkout nightly
```
To switch back:
```bash
git checkout master
```
<!--nightly-host-end-->

</details>

<!--nightly2-start-->
As this branch is subject to extreme change, there is no promise of the feature being documented in the [nightly](https://kometa.wiki/en/nightly/) branch of the wiki and all 
discussions relating to changes made in the nightly branch will be held within the [Kometa Discord Server](https://kometa.wiki/en/latest/discord/).
<!--nightly2-end-->
<!--discord-start-->
## Discord Support Server

If you're looking for support for any questions or issues you might have, or if you just want to be a part of our 
growing community, Join the [Kometa Discord Server](https://kometa.wiki/en/latest/discord/).
<!--discord-end-->
## Feature Requests

At Kometa, we value our community's input and actively seek feedback to drive the evolution of our product. We want to hear your ideas on how to enhance Kometa, 
and we encourage you to visit our [Feature Request](https://features.kometa.wiki/features) page to share your thoughts or vote on what features you would like to see added next. 
Your voice matters and helps shape the future of Kometa, so please don't hesitate to join in the conversation and be a part of our community-driven development process.

<!--outro-start-->
## Errors and Configuration Questions

If you're having trouble, we recommend first joining the [Kometa Discord Server](https://kometa.wiki/en/latest/discord/) 
and seeking support there. If that isn't possible for you, here's what you can do:

* If you get an error, update to the latest version and check if the issue persists. If it does, report the bug by filling out the 
  [Bug Report](https://github.com/Kometa-Team/Kometa/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+bug&template=bug_report.md&title=Bug%3A+) template.
* If you spot a mistake or have an idea to improve the [Kometa Wiki](https://kometa.wiki/), submit a request using the 
  [Wiki Request](https://github.com/Kometa-Team/Kometa/issues/new?assignees=meisnate12&labels=status%3Anot-yet-viewed%2C+documentation&template=3.docs_request.yml&title=%5BDocs%5D%3A+)
  template.
* If you have a question about metadata configuration, start a discussion on the [Discussions](https://github.com/Kometa-Team/Kometa/discussions). 
  Remember, the community helps shape the future of Kometa, so your input is valuable!

For support on any of the above, visit the [Discord server](https://kometa.wiki/en/latest/discord/).
<!--outro-end-->
## Contributing
* Pull Requests are greatly encouraged, please submit all Pull Requests to the nightly branch.

<!--sponsor-start-->
## GitHub Sponsors

Maintenance of this project is made possible by all the <a href="https://github.com/Kometa-Team/Kometa/graphs/contributors">contributors</a> and <a href="https://github.com/sponsors/meisnate12">sponsors</a>. If you'd like to sponsor this project and have your avatar or company logo appear below <a href="https://github.com/sponsors/meisnate12">click here</a>. 💖

<h2 align="center">Gold Sponsors</h2>

<p align="center">
<!--gold-sponsors--><a href="https://github.com/merci45k"><img src="https://github.com/merci45k.png" width="120px" alt="User avatar: merci45k" /></a>&nbsp;&nbsp;<a href="https://github.com/strcrzy"><img src="https://github.com/strcrzy.png" width="120px" alt="User avatar: strcrzy" /></a>&nbsp;&nbsp;<a href="https://github.com/ndkid1986"><img src="https://github.com/ndkid1986.png" width="120px" alt="User avatar: ndkid1986" /></a>&nbsp;&nbsp;<a href="https://github.com/genomez"><img src="https://github.com/genomez.png" width="120px" alt="User avatar: genomez" /></a>&nbsp;&nbsp;<a href="https://github.com/Injuku"><img src="https://github.com/Injuku.png" width="120px" alt="User avatar: Injuku" /></a>&nbsp;&nbsp;<a href="https://github.com/Anarchy27"><img src="https://github.com/Anarchy27.png" width="120px" alt="User avatar: Anarchy27" /></a>&nbsp;&nbsp;<a href="https://github.com/axsuul"><img src="https://github.com/axsuul.png" width="120px" alt="User avatar: axsuul" /></a>&nbsp;&nbsp;<a href="https://github.com/RayBishopTN"><img src="https://github.com/RayBishopTN.png" width="120px" alt="User avatar: RayBishopTN" /></a>&nbsp;&nbsp;<a href="https://github.com/Steezy33"><img src="https://github.com/Steezy33.png" width="120px" alt="User avatar: Steezy33" /></a>
</p>

<h2 align="center">Silver Sponsors</h2>

<p align="center">
<!--silver-sponsors--><a href="https://github.com/chazlarson"><img src="https://github.com/chazlarson.png" width="80px" alt="User avatar: chazlarson" /></a>&nbsp;&nbsp;<a href="https://github.com/Ramshackles"><img src="https://github.com/Ramshackles.png" width="80px" alt="User avatar: Ramshackles" /></a>&nbsp;&nbsp;<a href="https://github.com/Ackthbpt"><img src="https://github.com/Ackthbpt.png" width="80px" alt="User avatar: Ackthbpt" /></a>&nbsp;&nbsp;<a href="https://github.com/Quick104"><img src="https://github.com/Quick104.png" width="80px" alt="User avatar: Quick104" /></a>&nbsp;&nbsp;<a href="https://github.com/aschillingchi"><img src="https://github.com/aschillingchi.png" width="80px" alt="User avatar: aschillingchi" /></a>&nbsp;&nbsp;<a href="https://github.com/tecnobrat"><img src="https://github.com/tecnobrat.png" width="80px" alt="User avatar: tecnobrat" /></a>&nbsp;&nbsp;<a href="https://github.com/darthShadow"><img src="https://github.com/darthShadow.png" width="80px" alt="User avatar: darthShadow" /></a>&nbsp;&nbsp;<a href="https://github.com/TheWatcherOfPlex"><img src="https://github.com/TheWatcherOfPlex.png" width="80px" alt="User avatar: TheWatcherOfPlex" /></a>&nbsp;&nbsp;<a href="https://github.com/jarodaustin"><img src="https://github.com/jarodaustin.png" width="80px" alt="User avatar: jarodaustin" /></a>&nbsp;&nbsp;<a href="https://github.com/wellingssimon"><img src="https://github.com/wellingssimon.png" width="80px" alt="User avatar: wellingssimon" /></a>&nbsp;&nbsp;<a href="https://github.com/Eagle1337"><img src="https://github.com/Eagle1337.png" width="80px" alt="User avatar: Eagle1337" /></a>&nbsp;&nbsp;<a href="https://github.com/kevbentz"><img src="https://github.com/kevbentz.png" width="80px" alt="User avatar: kevbentz" /></a>&nbsp;&nbsp;<a href="https://github.com/sw4rl3y79"><img src="https://github.com/sw4rl3y79.png" width="80px" alt="User avatar: sw4rl3y79" /></a>&nbsp;&nbsp;<a href="https://github.com/mrbuckwheet"><img src="https://github.com/mrbuckwheet.png" width="80px" alt="User avatar: mrbuckwheet" /></a>&nbsp;&nbsp;<a href="https://github.com/htlcalbbs"><img src="https://github.com/htlcalbbs.png" width="80px" alt="User avatar: htlcalbbs" /></a>&nbsp;&nbsp;<a href="https://github.com/industrial64"><img src="https://github.com/industrial64.png" width="80px" alt="User avatar: industrial64" /></a>&nbsp;&nbsp;<a href="https://github.com/timothystewart6"><img src="https://github.com/timothystewart6.png" width="80px" alt="User avatar: timothystewart6" /></a>
</p>

<h2 align="center">Bronze Sponsors</h2>

<p align="center">
<!--bronze-sponsors--><a href="https://github.com/TheSpoon98"><img src="https://github.com/TheSpoon98.png" width="50px" alt="User avatar: TheSpoon98" /></a>&nbsp;&nbsp;<a href="https://github.com/nichols89ben"><img src="https://github.com/nichols89ben.png" width="50px" alt="User avatar: nichols89ben" /></a>&nbsp;&nbsp;<a href="https://github.com/Kha-kis"><img src="https://github.com/Kha-kis.png" width="50px" alt="User avatar: Kha-kis" /></a>&nbsp;&nbsp;<a href="https://github.com/RobertDoc"><img src="https://github.com/RobertDoc.png" width="50px" alt="User avatar: RobertDoc" /></a>&nbsp;&nbsp;<a href="https://github.com/VulgarBoatman"><img src="https://github.com/VulgarBoatman.png" width="50px" alt="User avatar: VulgarBoatman" /></a>&nbsp;&nbsp;<a href="https://github.com/DaddyDarkan"><img src="https://github.com/DaddyDarkan.png" width="50px" alt="User avatar: DaddyDarkan" /></a>&nbsp;&nbsp;<a href="https://github.com/Arial-Z"><img src="https://github.com/Arial-Z.png" width="50px" alt="User avatar: Arial-Z" /></a>&nbsp;&nbsp;<a href="https://github.com/kokuragari"><img src="https://github.com/kokuragari.png" width="50px" alt="User avatar: kokuragari" /></a>&nbsp;&nbsp;<a href="https://github.com/owine"><img src="https://github.com/owine.png" width="50px" alt="User avatar: owine" /></a>&nbsp;&nbsp;<a href="https://github.com/paterson37"><img src="https://github.com/paterson37.png" width="50px" alt="User avatar: paterson37" /></a>&nbsp;&nbsp;<a href="https://github.com/erwintwr2"><img src="https://github.com/erwintwr2.png" width="50px" alt="User avatar: erwintwr2" /></a>&nbsp;&nbsp;<a href="https://github.com/TR3JACK"><img src="https://github.com/TR3JACK.png" width="50px" alt="User avatar: TR3JACK" /></a>&nbsp;&nbsp;<a href="https://github.com/qazero"><img src="https://github.com/qazero.png" width="50px" alt="User avatar: qazero" /></a>&nbsp;&nbsp;<a href="https://github.com/andrewmcd7"><img src="https://github.com/andrewmcd7.png" width="50px" alt="User avatar: andrewmcd7" /></a>&nbsp;&nbsp;<a href="https://github.com/michaelkahn"><img src="https://github.com/michaelkahn.png" width="50px" alt="User avatar: michaelkahn" /></a>&nbsp;&nbsp;<a href="https://github.com/rg9400"><img src="https://github.com/rg9400.png" width="50px" alt="User avatar: rg9400" /></a>&nbsp;&nbsp;<a href="https://github.com/Alaksin"><img src="https://github.com/Alaksin.png" width="50px" alt="User avatar: Alaksin" /></a>&nbsp;&nbsp;<a href="https://github.com/AwesomeAustn"><img src="https://github.com/AwesomeAustn.png" width="50px" alt="User avatar: AwesomeAustn" /></a>&nbsp;&nbsp;<a href="https://github.com/wcbutler"><img src="https://github.com/wcbutler.png" width="50px" alt="User avatar: wcbutler" /></a>&nbsp;&nbsp;<a href="https://github.com/TownyMontana"><img src="https://github.com/TownyMontana.png" width="50px" alt="User avatar: TownyMontana" /></a>&nbsp;&nbsp;<a href="https://github.com/bullmoose20"><img src="https://github.com/bullmoose20.png" width="50px" alt="User avatar: bullmoose20" /></a>&nbsp;&nbsp;<a href="https://github.com/CountofNotreDame"><img src="https://github.com/CountofNotreDame.png" width="50px" alt="User avatar: CountofNotreDame" /></a>&nbsp;&nbsp;<a href="https://github.com/alexandercraen"><img src="https://github.com/alexandercraen.png" width="50px" alt="User avatar: alexandercraen" /></a>&nbsp;&nbsp;<a href="https://github.com/Iyagovos"><img src="https://github.com/Iyagovos.png" width="50px" alt="User avatar: Iyagovos" /></a>&nbsp;&nbsp;<a href="https://github.com/theimmortal68"><img src="https://github.com/theimmortal68.png" width="50px" alt="User avatar: theimmortal68" /></a>
</p>

Thank you so much for everyone's past and continued support!
<!--sponsor-end-->