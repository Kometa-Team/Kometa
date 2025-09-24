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

<p align="center">
<!-- real-premium --><a href="https://github.com/Alaksin"><img src="https:&#x2F;&#x2F;github.com&#x2F;Alaksin.png" width="80px" alt="User avatar: Alaksin" /></a>&nbsp;&nbsp;<a href="https://github.com/rg9400"><img src="https:&#x2F;&#x2F;github.com&#x2F;rg9400.png" width="80px" alt="User avatar: rg9400" /></a>&nbsp;&nbsp;<a href="https://github.com/michaelkahn"><img src="https:&#x2F;&#x2F;github.com&#x2F;michaelkahn.png" width="80px" alt="User avatar: michaelkahn" /></a>&nbsp;&nbsp;<a href="https://github.com/Injuku"><img src="https:&#x2F;&#x2F;github.com&#x2F;Injuku.png" width="80px" alt="User avatar: Injuku" /></a>&nbsp;&nbsp;<a href="https://github.com/bullmoose20"><img src="https:&#x2F;&#x2F;github.com&#x2F;bullmoose20.png" width="80px" alt="User avatar: bullmoose20" /></a>&nbsp;&nbsp;<a href="https://github.com/Ramshackles"><img src="https:&#x2F;&#x2F;github.com&#x2F;Ramshackles.png" width="80px" alt="User avatar: Ramshackles" /></a>&nbsp;&nbsp;<a href="https://github.com/andrewmcd7"><img src="https:&#x2F;&#x2F;github.com&#x2F;andrewmcd7.png" width="80px" alt="User avatar: andrewmcd7" /></a>&nbsp;&nbsp;<a href="https://github.com/industrial64"><img src="https:&#x2F;&#x2F;github.com&#x2F;industrial64.png" width="80px" alt="User avatar: industrial64" /></a>&nbsp;&nbsp;<a href="https://github.com/Davo1624"><img src="https:&#x2F;&#x2F;github.com&#x2F;Davo1624.png" width="80px" alt="User avatar: Davo1624" /></a>&nbsp;&nbsp;<a href="https://github.com/merci45k"><img src="https:&#x2F;&#x2F;github.com&#x2F;merci45k.png" width="80px" alt="User avatar: merci45k" /></a>&nbsp;&nbsp;<a href="https://github.com/ndkid1986"><img src="https:&#x2F;&#x2F;github.com&#x2F;ndkid1986.png" width="80px" alt="User avatar: ndkid1986" /></a>&nbsp;&nbsp;<!-- real-premium -->
</p>

<p align="center">
<!-- real-sponsors --><a href="https://github.com/darthShadow"><img src="https:&#x2F;&#x2F;github.com&#x2F;darthShadow.png" width="50px" alt="User avatar: darthShadow" /></a>&nbsp;&nbsp;<a href="https://github.com/djnield"><img src="https:&#x2F;&#x2F;github.com&#x2F;djnield.png" width="50px" alt="User avatar: djnield" /></a>&nbsp;&nbsp;<a href="https://github.com/Juansit0"><img src="https:&#x2F;&#x2F;github.com&#x2F;Juansit0.png" width="50px" alt="User avatar: Juansit0" /></a>&nbsp;&nbsp;<a href="https://github.com/tshirtnjeans"><img src="https:&#x2F;&#x2F;github.com&#x2F;tshirtnjeans.png" width="50px" alt="User avatar: tshirtnjeans" /></a>&nbsp;&nbsp;<a href="https://github.com/littlebirdiegr"><img src="https:&#x2F;&#x2F;github.com&#x2F;littlebirdiegr.png" width="50px" alt="User avatar: littlebirdiegr" /></a>&nbsp;&nbsp;<a href="https://github.com/boff999"><img src="https:&#x2F;&#x2F;github.com&#x2F;boff999.png" width="50px" alt="User avatar: boff999" /></a>&nbsp;&nbsp;<a href="https://github.com/magefesa"><img src="https:&#x2F;&#x2F;github.com&#x2F;magefesa.png" width="50px" alt="User avatar: magefesa" /></a>&nbsp;&nbsp;<a href="https://github.com/axsuul"><img src="https:&#x2F;&#x2F;github.com&#x2F;axsuul.png" width="50px" alt="User avatar: axsuul" /></a>&nbsp;&nbsp;<a href="https://github.com/tylernguyen"><img src="https:&#x2F;&#x2F;github.com&#x2F;tylernguyen.png" width="50px" alt="User avatar: tylernguyen" /></a>&nbsp;&nbsp;<a href="https://github.com/owine"><img src="https:&#x2F;&#x2F;github.com&#x2F;owine.png" width="50px" alt="User avatar: owine" /></a>&nbsp;&nbsp;<a href="https://github.com/rjay0890"><img src="https:&#x2F;&#x2F;github.com&#x2F;rjay0890.png" width="50px" alt="User avatar: rjay0890" /></a>&nbsp;&nbsp;<a href="https://github.com/RobertDoc"><img src="https:&#x2F;&#x2F;github.com&#x2F;RobertDoc.png" width="50px" alt="User avatar: RobertDoc" /></a>&nbsp;&nbsp;<a href="https://github.com/Quick104"><img src="https:&#x2F;&#x2F;github.com&#x2F;Quick104.png" width="50px" alt="User avatar: Quick104" /></a>&nbsp;&nbsp;<a href="https://github.com/chazlarson"><img src="https:&#x2F;&#x2F;github.com&#x2F;chazlarson.png" width="50px" alt="User avatar: chazlarson" /></a>&nbsp;&nbsp;<a href="https://github.com/DrLeoSpaceman"><img src="https:&#x2F;&#x2F;github.com&#x2F;DrLeoSpaceman.png" width="50px" alt="User avatar: DrLeoSpaceman" /></a>&nbsp;&nbsp;<a href="https://github.com/sw4rl3y79"><img src="https:&#x2F;&#x2F;github.com&#x2F;sw4rl3y79.png" width="50px" alt="User avatar: sw4rl3y79" /></a>&nbsp;&nbsp;<a href="https://github.com/digitalgp"><img src="https:&#x2F;&#x2F;github.com&#x2F;digitalgp.png" width="50px" alt="User avatar: digitalgp" /></a>&nbsp;&nbsp;<a href="https://github.com/iamwoz"><img src="https:&#x2F;&#x2F;github.com&#x2F;iamwoz.png" width="50px" alt="User avatar: iamwoz" /></a>&nbsp;&nbsp;<a href="https://github.com/evilgod93"><img src="https:&#x2F;&#x2F;github.com&#x2F;evilgod93.png" width="50px" alt="User avatar: evilgod93" /></a>&nbsp;&nbsp;<a href="https://github.com/phatkroger10"><img src="https:&#x2F;&#x2F;github.com&#x2F;phatkroger10.png" width="50px" alt="User avatar: phatkroger10" /></a>&nbsp;&nbsp;<a href="https://github.com/cpt-kuesel"><img src="https:&#x2F;&#x2F;github.com&#x2F;cpt-kuesel.png" width="50px" alt="User avatar: cpt-kuesel" /></a>&nbsp;&nbsp;<a href="https://github.com/lozman"><img src="https:&#x2F;&#x2F;github.com&#x2F;lozman.png" width="50px" alt="User avatar: lozman" /></a>&nbsp;&nbsp;<a href="https://github.com/DanielGothenborg"><img src="https:&#x2F;&#x2F;github.com&#x2F;DanielGothenborg.png" width="50px" alt="User avatar: DanielGothenborg" /></a>&nbsp;&nbsp;<a href="https://github.com/lkjfdsaofmc"><img src="https:&#x2F;&#x2F;github.com&#x2F;lkjfdsaofmc.png" width="50px" alt="User avatar: lkjfdsaofmc" /></a>&nbsp;&nbsp;<a href="https://github.com/jjjonesjr33"><img src="https:&#x2F;&#x2F;github.com&#x2F;jjjonesjr33.png" width="50px" alt="User avatar: jjjonesjr33" /></a>&nbsp;&nbsp;<a href="https://github.com/TR3JACK"><img src="https:&#x2F;&#x2F;github.com&#x2F;TR3JACK.png" width="50px" alt="User avatar: TR3JACK" /></a>&nbsp;&nbsp;<a href="https://github.com/overlord-The-II"><img src="https:&#x2F;&#x2F;github.com&#x2F;overlord-The-II.png" width="50px" alt="User avatar: overlord-The-II" /></a>&nbsp;&nbsp;<a href="https://github.com/Drazzilb08"><img src="https:&#x2F;&#x2F;github.com&#x2F;Drazzilb08.png" width="50px" alt="User avatar: Drazzilb08" /></a>&nbsp;&nbsp;<a href="https://github.com/JesseWebDotCom"><img src="https:&#x2F;&#x2F;github.com&#x2F;JesseWebDotCom.png" width="50px" alt="User avatar: JesseWebDotCom" /></a>&nbsp;&nbsp;<a href="https://github.com/aljohn92"><img src="https:&#x2F;&#x2F;github.com&#x2F;aljohn92.png" width="50px" alt="User avatar: aljohn92" /></a>&nbsp;&nbsp;<a href="https://github.com/Deathproof76"><img src="https:&#x2F;&#x2F;github.com&#x2F;Deathproof76.png" width="50px" alt="User avatar: Deathproof76" /></a>&nbsp;&nbsp;<a href="https://github.com/manosioa"><img src="https:&#x2F;&#x2F;github.com&#x2F;manosioa.png" width="50px" alt="User avatar: manosioa" /></a>&nbsp;&nbsp;<a href="https://github.com/Mushin"><img src="https:&#x2F;&#x2F;github.com&#x2F;Mushin.png" width="50px" alt="User avatar: Mushin" /></a>&nbsp;&nbsp;<a href="https://github.com/hexfield"><img src="https:&#x2F;&#x2F;github.com&#x2F;hexfield.png" width="50px" alt="User avatar: hexfield" /></a>&nbsp;&nbsp;<a href="https://github.com/SiskoUrso"><img src="https:&#x2F;&#x2F;github.com&#x2F;SiskoUrso.png" width="50px" alt="User avatar: SiskoUrso" /></a>&nbsp;&nbsp;<a href="https://github.com/LunarVigilante"><img src="https:&#x2F;&#x2F;github.com&#x2F;LunarVigilante.png" width="50px" alt="User avatar: LunarVigilante" /></a>&nbsp;&nbsp;<a href="https://github.com/qazero"><img src="https:&#x2F;&#x2F;github.com&#x2F;qazero.png" width="50px" alt="User avatar: qazero" /></a>&nbsp;&nbsp;<a href="https://github.com/TheSpoon98"><img src="https:&#x2F;&#x2F;github.com&#x2F;TheSpoon98.png" width="50px" alt="User avatar: TheSpoon98" /></a>&nbsp;&nbsp;<a href="https://github.com/styggiti"><img src="https:&#x2F;&#x2F;github.com&#x2F;styggiti.png" width="50px" alt="User avatar: styggiti" /></a>&nbsp;&nbsp;<a href="https://github.com/annihilatethee"><img src="https:&#x2F;&#x2F;github.com&#x2F;annihilatethee.png" width="50px" alt="User avatar: annihilatethee" /></a>&nbsp;&nbsp;<a href="https://github.com/msorelle"><img src="https:&#x2F;&#x2F;github.com&#x2F;msorelle.png" width="50px" alt="User avatar: msorelle" /></a>&nbsp;&nbsp;<a href="https://github.com/AwesomeAustn"><img src="https:&#x2F;&#x2F;github.com&#x2F;AwesomeAustn.png" width="50px" alt="User avatar: AwesomeAustn" /></a>&nbsp;&nbsp;<a href="https://github.com/chris6611"><img src="https:&#x2F;&#x2F;github.com&#x2F;chris6611.png" width="50px" alt="User avatar: chris6611" /></a>&nbsp;&nbsp;<a href="https://github.com/elmakus"><img src="https:&#x2F;&#x2F;github.com&#x2F;elmakus.png" width="50px" alt="User avatar: elmakus" /></a>&nbsp;&nbsp;<a href="https://github.com/spike9172"><img src="https:&#x2F;&#x2F;github.com&#x2F;spike9172.png" width="50px" alt="User avatar: spike9172" /></a>&nbsp;&nbsp;<a href="https://github.com/netplexflix"><img src="https:&#x2F;&#x2F;github.com&#x2F;netplexflix.png" width="50px" alt="User avatar: netplexflix" /></a>&nbsp;&nbsp;<a href="https://github.com/Kha-kis"><img src="https:&#x2F;&#x2F;github.com&#x2F;Kha-kis.png" width="50px" alt="User avatar: Kha-kis" /></a>&nbsp;&nbsp;<a href="https://github.com/ICHlMOKU"><img src="https:&#x2F;&#x2F;github.com&#x2F;ICHlMOKU.png" width="50px" alt="User avatar: ICHlMOKU" /></a>&nbsp;&nbsp;<a href="https://github.com/zippydude"><img src="https:&#x2F;&#x2F;github.com&#x2F;zippydude.png" width="50px" alt="User avatar: zippydude" /></a>&nbsp;&nbsp;<a href="https://github.com/Sunnyr48"><img src="https:&#x2F;&#x2F;github.com&#x2F;Sunnyr48.png" width="50px" alt="User avatar: Sunnyr48" /></a>&nbsp;&nbsp;<a href="https://github.com/maikash2747"><img src="https:&#x2F;&#x2F;github.com&#x2F;maikash2747.png" width="50px" alt="User avatar: maikash2747" /></a>&nbsp;&nbsp;<a href="https://github.com/kristianfreeman"><img src="https:&#x2F;&#x2F;github.com&#x2F;kristianfreeman.png" width="50px" alt="User avatar: kristianfreeman" /></a>&nbsp;&nbsp;<a href="https://github.com/krizzo"><img src="https:&#x2F;&#x2F;github.com&#x2F;krizzo.png" width="50px" alt="User avatar: krizzo" /></a>&nbsp;&nbsp;<a href="https://github.com/pterisaur"><img src="https:&#x2F;&#x2F;github.com&#x2F;pterisaur.png" width="50px" alt="User avatar: pterisaur" /></a>&nbsp;&nbsp;<a href="https://github.com/rzilla75"><img src="https:&#x2F;&#x2F;github.com&#x2F;rzilla75.png" width="50px" alt="User avatar: rzilla75" /></a>&nbsp;&nbsp;<a href="https://github.com/minermartijn"><img src="https:&#x2F;&#x2F;github.com&#x2F;minermartijn.png" width="50px" alt="User avatar: minermartijn" /></a>&nbsp;&nbsp;<a href="https://github.com/elit3ge"><img src="https:&#x2F;&#x2F;github.com&#x2F;elit3ge.png" width="50px" alt="User avatar: elit3ge" /></a>&nbsp;&nbsp;<a href="https://github.com/mguffin68"><img src="https:&#x2F;&#x2F;github.com&#x2F;mguffin68.png" width="50px" alt="User avatar: mguffin68" /></a>&nbsp;&nbsp;<a href="https://github.com/Goden57"><img src="https:&#x2F;&#x2F;github.com&#x2F;Goden57.png" width="50px" alt="User avatar: Goden57" /></a>&nbsp;&nbsp;<a href="https://github.com/antwanchild"><img src="https:&#x2F;&#x2F;github.com&#x2F;antwanchild.png" width="50px" alt="User avatar: antwanchild" /></a>&nbsp;&nbsp;<a href="https://github.com/htlcalbbs"><img src="https:&#x2F;&#x2F;github.com&#x2F;htlcalbbs.png" width="50px" alt="User avatar: htlcalbbs" /></a>&nbsp;&nbsp;<a href="https://github.com/jpotrz"><img src="https:&#x2F;&#x2F;github.com&#x2F;jpotrz.png" width="50px" alt="User avatar: jpotrz" /></a>&nbsp;&nbsp;<a href="https://github.com/GHB-B"><img src="https:&#x2F;&#x2F;github.com&#x2F;GHB-B.png" width="50px" alt="User avatar: GHB-B" /></a>&nbsp;&nbsp;<a href="https://github.com/mariosemes"><img src="https:&#x2F;&#x2F;github.com&#x2F;mariosemes.png" width="50px" alt="User avatar: mariosemes" /></a>&nbsp;&nbsp;<a href="https://github.com/pete2583"><img src="https:&#x2F;&#x2F;github.com&#x2F;pete2583.png" width="50px" alt="User avatar: pete2583" /></a>&nbsp;&nbsp;<a href="https://github.com/shrikeh"><img src="https:&#x2F;&#x2F;github.com&#x2F;shrikeh.png" width="50px" alt="User avatar: shrikeh" /></a>&nbsp;&nbsp;<a href="https://github.com/Shootin89"><img src="https:&#x2F;&#x2F;github.com&#x2F;Shootin89.png" width="50px" alt="User avatar: Shootin89" /></a>&nbsp;&nbsp;<a href="https://github.com/genomez"><img src="https:&#x2F;&#x2F;github.com&#x2F;genomez.png" width="50px" alt="User avatar: genomez" /></a>&nbsp;&nbsp;<a href="https://github.com/helangen"><img src="https:&#x2F;&#x2F;github.com&#x2F;helangen.png" width="50px" alt="User avatar: helangen" /></a>&nbsp;&nbsp;<a href="https://github.com/RandomNinjaAtk"><img src="https:&#x2F;&#x2F;github.com&#x2F;RandomNinjaAtk.png" width="50px" alt="User avatar: RandomNinjaAtk" /></a>&nbsp;&nbsp;<a href="https://github.com/havpac2"><img src="https:&#x2F;&#x2F;github.com&#x2F;havpac2.png" width="50px" alt="User avatar: havpac2" /></a>&nbsp;&nbsp;<a href="https://github.com/Eagle1337"><img src="https:&#x2F;&#x2F;github.com&#x2F;Eagle1337.png" width="50px" alt="User avatar: Eagle1337" /></a>&nbsp;&nbsp;<a href="https://github.com/Celeggur"><img src="https:&#x2F;&#x2F;github.com&#x2F;Celeggur.png" width="50px" alt="User avatar: Celeggur" /></a>&nbsp;&nbsp;<a href="https://github.com/WanderAndExplore"><img src="https:&#x2F;&#x2F;github.com&#x2F;WanderAndExplore.png" width="50px" alt="User avatar: WanderAndExplore" /></a>&nbsp;&nbsp;<a href="https://github.com/rumoxx"><img src="https:&#x2F;&#x2F;github.com&#x2F;rumoxx.png" width="50px" alt="User avatar: rumoxx" /></a>&nbsp;&nbsp;<a href="https://github.com/jaketame"><img src="https:&#x2F;&#x2F;github.com&#x2F;jaketame.png" width="50px" alt="User avatar: jaketame" /></a>&nbsp;&nbsp;<a href="https://github.com/LegendaryLass"><img src="https:&#x2F;&#x2F;github.com&#x2F;LegendaryLass.png" width="50px" alt="User avatar: LegendaryLass" /></a>&nbsp;&nbsp;<a href="https://github.com/makkish"><img src="https:&#x2F;&#x2F;github.com&#x2F;makkish.png" width="50px" alt="User avatar: makkish" /></a>&nbsp;&nbsp;<a href="https://github.com/Anon0511"><img src="https:&#x2F;&#x2F;github.com&#x2F;Anon0511.png" width="50px" alt="User avatar: Anon0511" /></a>&nbsp;&nbsp;<a href="https://github.com/Arial-Z"><img src="https:&#x2F;&#x2F;github.com&#x2F;Arial-Z.png" width="50px" alt="User avatar: Arial-Z" /></a>&nbsp;&nbsp;<a href="https://github.com/AndrewCloss"><img src="https:&#x2F;&#x2F;github.com&#x2F;AndrewCloss.png" width="50px" alt="User avatar: AndrewCloss" /></a>&nbsp;&nbsp;<a href="https://github.com/MYanello"><img src="https:&#x2F;&#x2F;github.com&#x2F;MYanello.png" width="50px" alt="User avatar: MYanello" /></a>&nbsp;&nbsp;<a href="https://github.com/killuagit"><img src="https:&#x2F;&#x2F;github.com&#x2F;killuagit.png" width="50px" alt="User avatar: killuagit" /></a>&nbsp;&nbsp;<a href="https://github.com/TheLidlMan"><img src="https:&#x2F;&#x2F;github.com&#x2F;TheLidlMan.png" width="50px" alt="User avatar: TheLidlMan" /></a>&nbsp;&nbsp;<a href="https://github.com/LT3Dave"><img src="https:&#x2F;&#x2F;github.com&#x2F;LT3Dave.png" width="50px" alt="User avatar: LT3Dave" /></a>&nbsp;&nbsp;<a href="https://github.com/0marLittle"><img src="https:&#x2F;&#x2F;github.com&#x2F;0marLittle.png" width="50px" alt="User avatar: 0marLittle" /></a>&nbsp;&nbsp;<a href="https://github.com/Spazholio"><img src="https:&#x2F;&#x2F;github.com&#x2F;Spazholio.png" width="50px" alt="User avatar: Spazholio" /></a>&nbsp;&nbsp;<a href="https://github.com/thedinz"><img src="https:&#x2F;&#x2F;github.com&#x2F;thedinz.png" width="50px" alt="User avatar: thedinz" /></a>&nbsp;&nbsp;<a href="https://github.com/ravensorb"><img src="https:&#x2F;&#x2F;github.com&#x2F;ravensorb.png" width="50px" alt="User avatar: ravensorb" /></a>&nbsp;&nbsp;<!-- real-sponsors -->
</p>

Thank you so much for your continued support!
<!--sponsor-end-->