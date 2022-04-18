# Overlay Files

Overlay files are used to create and maintain overlays within the Plex libraries on the server.

Overlays and templates are defined within one or more Overlay files, which are linked to libraries in the [Libraries Attribute](../config/libraries.md#overlay-path) within the [Configuration File](../config/configuration.md).

**To remove all overlays use the `remove_overlays` library operation.**

**To change a single overlay original Image either replace the image in the assets folder or remove the `Overlay` shared label and then PMM will overlay the new image**

These are the attributes which can be used within the Overlay File:

| Attribute                                               | Description                                                                                                        |
|:--------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------|
| [`templates`](templates)                                | contains definitions of templates that can be leveraged by multiple overlays                                       |
| [`external_templates`](templates.md#external-templates) | contains [path types](../config/paths) that point to external templates that can be leveraged by multiple overlays |
| [`overlays`](#overlay-attributes)                       | contains definitions of overlays you wish to add                                                                   |

* `overlays` is required in order to run the Overlay File.
* Example Overlay Files can be found in the [Plex Meta Manager Configs Repository](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM)

## Overlay Attributes

Each overlay requires its own section within the `overlays` attribute.

```yaml
overlays:
  IMDb Top 250:
    # ... builders, details, and filters for this overlay
  4K:
    # ... builders, details, and filters for this overlay
  etc:
    # ... builders, details, and filters for this overlay
```

Each section must have the only required attribute, `overlay`.


| Attribute | Description                                                                                                  | Required |
|:----------|:-------------------------------------------------------------------------------------------------------------|:--------:|
| `name`    | Name of the overlay. Each overlay name should be unique.                                                     | &#9989;  |
| `url`     | URL of Overlay Image Online                                                                                  | &#10060; |
| `git`     | Location in the [Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs) of the Overlay Image | &#10060; |
| `repo`    | Location in the [Custom Repo](../config/settings.md#custom-repo) of the Overlay Image                        | &#10060; |

* If `url`, `git`, and `repo` are all not defined then PMM will look in your `config/overlays` folder for a `.png` file named the same as the `name` attribute.

```yaml
overlays:
  IMDb Top 250:
    overlay:
      name: IMDb Top 250
    imdb_chart: top_movies
```

There are three types of attributes that can be utilized within an overlay:

### Builders

Builders use third-party services to source items for overlays. Multiple builders can be used in the same overlay from a variety of sources listed below.

* [Plex Builders](builders/plex)
* [Smart Builders](builders/smart)
* [TMDb Builders](builders/tmdb)
* [TVDb Builders](builders/tvdb)
* [IMDb Builders](builders/imdb)
* [Trakt Builders](builders/trakt)
* [Tautulli Builders](builders/tautulli)
* [Letterboxd Builders](builders/letterboxd)
* [ICheckMovies Builders](builders/icheckmovies)
* [FlixPatrol Builders](builders/flixpatrol)
* [StevenLu Builders](builders/stevenlu)
* [AniDB Builders](builders/anidb)
* [AniList Builders](builders/anilist)
* [MyAnimeList Builders](builders/myanimelist)

## Details

Only a few details can be used with overlays: `limit`, `show_missing`, `save_missing`, `missing_only_released`, `minimum_items`, `cache_builders`, `tmdb_region`

* [Setting Details](details/setting)
* [Metadata Details](details/metadata)

## Filters

These filter media items added to the collection by any of the Builders.

* [Filters](filters)

## Examples

```yaml
overlays:
  4K:
    overlay:
      name: 4K    # This will look for a local overlays/4K.png in your configs folder
    plex_search:
      all:
        resolution: 4K
  HDR:
    overlay:
      name: HDR
      git: PMM/overlays/HDR
    plex_search:
      all:
        hdr: true
  Dolby:
    overlay:
      name: Dolby
      url: https://somewebsite.com/dolby_overlay.png
    plex_all: true
    filters:
      has_dolby_vision: true
```