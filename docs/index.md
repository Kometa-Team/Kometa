---
glightbox: false
hide:
  - toc
---

<style>
.md-content h1, .md-content__button { display: none; }
.kometa-home-brand { text-align: center; }
.kometa-home-brand img { max-width: min(100%, 32rem); margin-bottom: 1rem; }
.md-typeset .kometa-home-start {
    grid-template-columns: minmax(0, 1fr);
}
.md-typeset .kometa-home-start.cards > ul > li {
    width: 100%;
}
@media screen and (min-width: 40em) {
    .md-typeset .kometa-home-start {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
@media screen and (min-width: 76.25em) {
    .md-typeset .kometa-home-start {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }
}
</style>

# Kometa

<div class="kometa-home-brand">
  <img src="assets/images/icons/logo-full.png" alt="Kometa">
</div>

Organize and personalize your Plex libraries with automatic collections, poster overlays, playlists, and metadata updates. Use ready-made Defaults or write your own YAML definitions, drawing on services such as TMDb and IMDb.

## Where to start

<div class="grid cards kometa-home-start" markdown>

-   :lucide-download: **Install Kometa**

    Set up Kometa and make your first run, with walkthroughs for local and Docker installations.

    [Get started](kometa/install/index.md)

-   :lucide-sparkles: **Use ready-made Defaults**

    Browse collections, overlays, and playlists you can add to your configuration.

    [Browse Defaults](defaults/guide.md#list-of-defaults-files)

-   :lucide-settings: **Create your own**

    Choose builders, filter their results, and define collections for your libraries.

    [Write collection files](files/collections.md)

-   :lucide-life-buoy: **Get help**

    Understand your logs and find the information needed to troubleshoot a run.

    [Read the logs guide](kometa/help.md) or [ask on Discord](https://kometa.wiki/en/latest/discord/).

</div>

## Your first setup

1. **[Install Kometa](kometa/install/index.md)** using the guide for your platform.
2. **[Configure your connections](config/overview.md)** with the URLs and credentials Kometa needs for Plex, TMDb, and your other services.
3. **[Add Defaults](defaults/guide.md)** or your own collection files, then **[run Kometa](kometa/environmental.md#run)** to apply them.

!!! tip "Using a NAS or Kubernetes?"

    The installation guide includes unRAID, Kubernetes, QNAP, and Synology paths. If you are new to Kometa, follow the [Docker walkthrough](kometa/install/index.md#path-docker) first to understand the configuration and collection files used by those setups.

## See what you can create

### Collections

Group movies and shows by streaming service, genre, actor, decade, awards, or popularity. For example, create an IMDb Top 250 collection or keep a recently released collection up to date.

<div class="randomized half-height very-slow padded rounded stylized scroller">
  <div class="scroller__inner">
    <figure>
      <img src="assets/images/scrollers/collections/Max.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Metacritic%20Must%20See.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Shrek.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Animation.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Common%20Sense%20Selection.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Newly%20Released%20Episodes.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/UK.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Oscar%20Best%20Picture%20Winners.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/2000.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Plex%20Popular.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/IMDb%20Top%20250.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Food%20Network.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/best_director_winner.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Netflix.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Book.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/mcu.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/PG.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Hallmark.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/bafta_best_picture_winner.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/IMDb%20Popular.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/best_picture_winner.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Hulu.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/dcu.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/Disney%2B_originals.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/marvel.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/collections/RT%20Certified%20Fresh.jpg" loading="lazy">
    </figure>
  </div>
</div>
<figcaption style="text-align: center; max-width: 100%; margin-top: 0.1rem;" >
  Collections created using the <a href="defaults/guide.md">Kometa Defaults</a>
</figcaption>

### Overlays

Add information such as ratings or resolution to your posters. Start with [Default overlays](defaults/overlays/usage.md) or use overlay files shared by the community.

<div class="reversed randomized half-height very-slow padded rounded stylized scroller">
  <div class="scroller__inner">
    <figure>
      <img src="assets/images/scrollers/overlays/1.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/2.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/3.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/4.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/5.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/6.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/7.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/8.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/9.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/10.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/11.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/12.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/13.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/14.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/15.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/16.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/17.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/18.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/19.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/20.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/21.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/22.jpg" loading="lazy">
    </figure>
    <figure>
      <img src="assets/images/scrollers/overlays/23.jpg" loading="lazy">
    </figure>
  </div>
</div>
<figcaption style="text-align: center; max-width: 100%; margin-top: 0.1rem;" >
  Overlays created using the <a href="defaults/guide.md">Kometa Defaults</a> or by community created Overlay Files
</figcaption>

### Metadata and automation

[Update titles, summaries, artwork, and more](files/updates.md) from files you can reapply or move between servers. Connect [Radarr](config/radarr.md) and [Sonarr](config/sonarr.md) to manage missing movies and shows, and explore [Community Configs](https://github.com/Kometa-Team/Community-Configs) for examples you can adapt.

## Help shape Kometa

Join the [Discord community](https://kometa.wiki/en/latest/discord/) for support and ideas, [request a feature](https://features.kometa.wiki/), or [contribute to Kometa](https://github.com/Kometa-Team/Kometa). Found a documentation issue? [Report it in the wiki repository](https://github.com/Kometa-Team/Kometa-Wiki/issues).

Find [releases](https://github.com/Kometa-Team/Kometa/releases) and [Docker images](https://hub.docker.com/r/kometateam/kometa), join the [subreddit](https://www.reddit.com/r/kometa/), or [help with translations](https://translations.kometa.wiki/projects/kometa/#languages).

{%
    include-markdown "templates/project.md"
    start="<!--sponsor-start-->"
    end="<!--sponsor-end-->"
%}
