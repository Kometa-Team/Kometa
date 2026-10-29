---
hide:
  - toc
---
# Defaults Usage Guide

Kometa includes a pre-created set of Collection Files and Overlay Files which can be found in the "defaults" folder in the root of your Kometa installation directory.

These files offer an easy-to-use and customizable set of Collections and Overlays that the user can achieve without 
having to worry about creating the files that make the collections and overlays possible.

All Collections come with a matching poster to make a clean, consistent set of collections in your library. These files are stored in the [Kometa Images](https://github.com/Kometa-Team/Default-Images)
Repository and each poster is downloaded straight to your Plex Collection when you run Kometa.

Credits to Sohjiro, Bullmoose20, Yozora, Cpt Kuesel, and anon_fawkes for helping drive this entire Default Set of Configs through the concept, design and implementation.

Special thanks to Magic815 for the overlay image inspiration and base template.

Please consider [donating](https://github.com/sponsors/meisnate12) towards the project.

## Available defaults {#list-of-defaults-files}

Find a default by name below. Each page lists the collections or overlays it creates and the variables you can customize.

??? info "Collections"

    - [Academy Awards (Oscars)](award/oscars.md)
    - [Actors](both/actor.md)
    - [AniList Charts](chart/anilist.md)
    - [Aspect Ratio](both/aspect.md)
    - [AU Content Ratings](both/content_rating_au.md)
    - [Audio Languages](both/audio_language.md)
    - [Based On...](both/based.md)
    - [Basic Charts](chart/basic.md)
    - [Berlin Film Festival Awards](award/berlinale.md)
    - [British Academy of Film Awards](award/bafta.md)
    - [Cannes Film Festival Awards](award/cannes.md)
    - [Collectionless](both/collectionless.md)
    - [Common Sense Media Content Ratings](both/content_rating_cs.md)
    - [Continents (Movie)](movie/continent.md)
    - [Continents (Show)](show/continent.md)
    - [Countries (Movie)](movie/country.md)
    - [Countries (Show)](show/country.md)
    - [Critics Choice Awards](award/choice.md)
    - [César Awards](award/cesar.md)
    - [DE Content Ratings](both/content_rating_de.md)
    - [Decades (Movie)](movie/decade.md)
    - [Decades (Show)](show/decade.md)
    - [Directors](movie/director.md)
    - [Emmy Awards](award/emmy.md)
    - [Franchises (Movie)](movie/franchise.md)
    - [Franchises (Show)](show/franchise.md)
    - [Genres](both/genre.md)
    - [Golden Globe Awards](award/golden.md)
    - [IMDb Charts](chart/imdb.md)
    - [Independent Spirit Awards](award/spirit.md)
    - [Letterboxd Charts](chart/letterboxd.md)
    - [MyAnimeList Charts](chart/myanimelist.md)
    - [MyAnimeList Content Ratings](both/content_rating_mal.md)
    - [National Film Registry](award/nfr.md)
    - [Networks](show/network.md)
    - [NZ Content Ratings](both/content_rating_nz.md)
    - [Other Charts](chart/other.md)
    - [People's Choice Awards](award/pca.md)
    - [Producers](movie/producer.md)
    - [Razzie Awards](award/razzie.md)
    - [Regions (Movie)](movie/region.md)
    - [Regions (Show)](show/region.md)
    - [Resolutions](both/resolution.md)
    - [Screen Actors Guild Awards](award/sag.md)
    - [Seasonal](movie/seasonal.md)
    - [Separator](award/separator.md)
    - [Separator](chart/separator.md)
    - [Simkl Charts](chart/simkl.md)
    - [Streaming](both/streaming.md)
    - [Studios](both/studio.md)
    - [Subtitle Languages](both/subtitle_language.md)
    - [Sundance Film Festival Awards](award/sundance.md)
    - [Tautulli Charts](chart/tautulli.md)
    - [TMDb Charts](chart/tmdb.md)
    - [Toronto International Film Festival](award/tiff.md)
    - [Tracearr Charts](chart/tracearr.md)
    - [UK Content Ratings](both/content_rating_uk.md)
    - [Universes](both/universe.md)
    - [US Content Ratings (Movie)](movie/content_rating_us.md)
    - [US Content Ratings (Show)](show/content_rating_us.md)
    - [Venice Film Festival Awards](award/venice.md)
    - [Writers](movie/writer.md)
    - [Years](both/year.md)

??? info "Overlays"

    - [Aspect Ratio](overlays/aspect.md)
    - [AU Content Ratings](overlays/content_rating_au.md)
    - [Audio Codec](overlays/audio_codec.md)
    - [Audio/Subtitle Language Count](overlays/language_count.md)
    - [Audio/Subtitle Language Flags](overlays/languages.md)
    - [Common Sense Age Ratings](overlays/commonsense.md)
    - [DE Content Ratings](overlays/content_rating_de.md)
    - [Direct Play Only](overlays/direct_play.md)
    - [Episode Info](overlays/episode_info.md)
    - [MediaStinger](overlays/mediastinger.md)
    - [Networks](overlays/network.md)
    - [NZ Content Ratings](overlays/content_rating_nz.md)
    - [Ratings](overlays/ratings.md)
    - [Resolution/Edition](overlays/resolution.md)
    - [Ribbon](overlays/ribbon.md)
    - [Runtimes](overlays/runtimes.md)
    - [Status](overlays/status.md)
    - [Streaming](overlays/streaming.md)
    - [Studios](overlays/studio.md)
    - [UK Content Ratings](overlays/content_rating_uk.md)
    - [US Content Ratings (Movie)](overlays/content_rating_us_movie.md)
    - [US Content Ratings (Show)](overlays/content_rating_us_show.md)
    - [Versions](overlays/versions.md)
    - [Video Format](overlays/video_format.md)

??? info "Playlists"

    - [Playlists](playlist.md)

## Configurations

To run a default Kometa Collection or Overlay File you can simply add it to your `collection_files` (For Collection Files) or `overlay_files` (For Overlay Files) using `default` like so:

```yaml
libraries:
  Movies:
    collection_files:
    - default: actor
    - default: genre
    overlay_files:
    - default: ribbon
    - default: ratings
```

## Customizing these defaults

Configs can be customized using the `template_variables` attribute when calling the file.

These Template Variables can be used to customize individual collections/overlays or the set as a whole.

A given default may have variables that are specific to it, and may also leverage a common set of shared Template Variables. These lists are shown on each Defaults File's wiki page.

## Customizing individual components

Each Defaults File uses "keys" to refer to the collections and overlays that it creates, and you can use those keys to modify the behavior of individual collections or overlays created by the file.

For, example, the IMDB default creates three collections, each with their own "key":

| Collection          | Key       |
|:--------------------|:----------|
| `IMDb Popular`      | `popular` |
| `IMDb Top 250`      | `top`     |
| `IMDb Lowest Rated` | `lowest`  |

You use that key to customize the individual collection or overlay.

This example disables two keys, which will prevent those collections from being created. It also sets the visibility of one of the keys [`top`] so that it is visible on the library tab,
the server owner's home screen and shared user's home screens (assuming the server owner and/or the shared users have the library pinned to their home screen)

It also changes the resolution overlay to skip applying the overlay to 480p movies.

The Template Variables in this example happen to be all shared Template Variables.

Press the :fontawesome-solid-circle-plus: icon to learn more

```yaml title="Customizing Defaults Files via Template Variables"
libraries:
  Movies:
    collection_files:
      - default: imdb
        template_variables:
          use_popular: false #(1)!
          use_lowest: false #(2)!
          visible_library_top: true #(3)!
          visible_home_top: true
          visible_shared_top: true
    overlay_files:
      - default: resolution
        template_variables:
          use_480p: false #(4)!
```

1. Turns off the `popular` key, stopping the "IMDb Popular" collection from being processed
2. Turns off the `lowest` key, stopping the "IMDb Lowest Rated" collection from being processed
3. Sets `visible_library`, `visible_home` and `visible_shared` to `true` for the `top` key, pinning the "IMDb Top 250" collection for the server owner, shared users, and on the library's recommended tab.
4. Turns off the `480p` key, stopping the "480p" based resolution overlays from being processed

## Customizing the set as a whole

In addition to the keys, each default can be customized with other Template Variables that are not key-specific.

This example uses a file-specific variable to change the order of all the IMDB chart collections to alphabetical by title and a shared variable to schedule these IMDB collections to be run only on Wednesdays.

On the `resolution` overlay, it uses a file-specific variable to disable all the "edition" overlays and a shared variable to align the overlay on the right side of the poster.

Press the :fontawesome-solid-circle-plus: icon to learn more

```yaml
libraries:
  TV Shows:
    collection_files:
      - default: imdb
        template_variables:
          use_popular: false
          use_lowest: false
          visible_library_top: true
          visible_home_top: true
          visible_shared_top: true
          collection_order: alpha #(1)!
          schedule: weekly(wednesday) #(2)!
    overlay_files:
      - default: resolution
        template_variables:
          use_480p: false
          use_edition: false #(3)!
          horizontal_align: right #(4)!
```

1. File-Specific Template Variable that will set the sort order for all Collections created by the imdb file
2. Shared Template Variable that will schedule the imdb file to only be processed on a Wednesday
3. File-Specific Template Variable that will prevent the resolution file from processing any edition overlays (such as the "Extended Edition" dovetail)
4. Shared Template Variable that will set the alignment of overlays produced by the resolution file to be right-aligned

All of the Defaults Files are customized in this basic fashion.

**NOTE: this `template_variable` system is specific to the Defaults. If and when you start creating your own [collection](../files/collections.md) or [overlay](../files/overlays.md) files,
you cannot use this `template_variables` setup unless you specifically write your files to implement it.**

Each of these Defaults Files has a page on the wiki showing its keys, available `template_variables`, and default settings. 
For example, the Defaults Overlay File `default: resolution` has a page [here](overlays/resolution.md).

The shared Template Variables can be reviewed here for [Collections](shared.md) and [Overlays](overlay_variables.md). These are also linked from each Defaults File's wiki page. 
Keep in mind that *most*, but not all Defaults Files have access to the shared variables. This will be noted on the individual files' page.

## Collection defaults

See the [Collection Defaults](collections/usage.md) Page for more information on the specifics of the Collection Defaults.

## Overlay defaults

See the [Overlay Defaults](overlays/usage.md) Page for more information on the specifics of the Overlay Defaults.

{% include-markdown "./../templates/snippets/example_config.md" %}

## Example: customize Academy Award collections


Perhaps you want to explore the collections and overlays that Kometa provides as part of the defaults. If you want to create a variety of collections with a minimum of fuss,
these are for you. They can be enabled in your config with a single line, and support limited customization via "template_variables" in the config file.

For example, this will create 7 Academy Award collections, "Best Picture" (all years), "Best Director" (all years), and yearly collections for the past five years.

```yaml
libraries:
  Movies:
    collection_files:
      - default: oscars
```

If you wanted to create yearly collections for the past ten years, you could do that with:

```yaml
libraries:
  Movies:
    collection_files:
      - default: oscars
        template_variables:
          data:
           starting: latest-11
```

All of the defaults work this way. You can enable them with a single line, and customize them with `template_variables`.

The defaults are all documented starting [here](guide.md).
