# Overlay Files

Overlay files are used to create and maintain overlays within the Plex libraries on the server.

Overlays and templates are defined within one or more Overlay files, which are linked to libraries in the [Libraries Attribute](../config/libraries.md#overlay-path) within the [Configuration File](../config/configuration.md).

**To remove all overlays add `remove_overlays: true` to the `overlay_path` [Libraries Attribute](../config/libraries.md#remove-overlays).**

**To change a single overlay original image either replace the image in the assets folder or remove the `Overlay` shared label and then PMM will overlay the new image**

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

### Overlay Name

You can specify the Overlay Name in 3 ways.

1. If there is no `overlay` attribute PMM will look in your `config/overlays` folder for a `.png` file named the same as the mapping name of the overlay definition.
    ```yaml
    overlays:
      IMDb Top 250:
        imdb_chart: top_movies
    ```
   
2. If the `overlay` attribute is given a string PMM will look in your `config/overlays` folder for a `.png` file named the same as the string given.
    ```yaml
    overlays:
      overlay: IMDb Top 250
      IMDb Top 250:
        imdb_chart: top_movies
    ```
   
3. Using a dictionary for more overlay location options.

| Attribute      | Description                                                                                                   | Required |
|:---------------|:--------------------------------------------------------------------------------------------------------------|:--------:|
| `name`         | Name of the overlay. Each overlay name should be unique.                                                      | &#9989;  |
| `file`         | Local location of the Overlay Image.                                                                          | &#10060; |
| `url`          | URL of Overlay Image Online.                                                                                  | &#10060; |
| `git`          | Location in the [Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs) of the Overlay Image. | &#10060; |
| `repo`         | Location in the [Custom Repo](../config/settings.md#custom-repo) of the Overlay Image.                        | &#10060; |
| `group`        | Name of the Grouping for this overlay. **`weight` is required when using `group`**                            | &#10060; |
| `weight`       | Weight of this overlay in its group. **`group` is required when using `weight`**                              | &#10060; |
| `x_coordinate` | Top Left X Coordinate of this overlay. **`y_coordinate` is required when using `x_coordinate`**               | &#10060; |
| `y_coordinate` | Top Left Y Coordinate of this overlay. **`x_coordinate` is required when using `y_coordinate`**               | &#10060; |

* If `url`, `git`, and `repo` are all not defined then PMM will look in your `config/overlays` folder for a `.png` file named the same as the `name` attribute.
* Only one overlay with the highest weight per group will be applied.

```yaml
overlays:
  IMDb Top 250:
    overlay:
      name: IMDb Top 250
    imdb_chart: top_movies
```

#### Blurring Overlay

There is a special overlay named `blur` that when given as the overlay name will instead of finding the image will just blur the image instead.

You can control the level of the blur by providing a number with the attribute like so `blur(##)`.

```yaml
overlays:
  blur:
    overlay:
      name: blur(50)
    plex_search:
      all:
        resolution: 4K
```

### Suppress Overlays

You can add `suppress_overlays` to an overlay definition and give it a list or comma separated string of overlay names you want suppressed from this item if this overlay is attached to the item.

So in this example if the `4K-HDR` overlay matches an item then the `4K` and `HDR` overlays will also match. The `suppress_overlays` attribute on `4K-HDR` will stop the overlays specified (`4K` and `HDR`) from also being applied. 

```yaml
overlays:
  4K:
    plex_search:
      all:
        resolution: 4K
  HDR:
    plex_search:
      all:
        hdr: true
  4K-HDR:
    suppress_overlays:
      - 4K
      - HDR
    plex_search:
      all:
        resolution: 4K
        hdr: true
```

### Builders

Builders use third-party services to source items for overlays. Multiple builders can be used in the same overlay from a variety of sources listed below.

* [Plex Builders](builders/plex)
* [TMDb Builders](builders/tmdb)
* [TVDb Builders](builders/tvdb)
* [IMDb Builders](builders/imdb)
* [Trakt Builders](builders/trakt)
* [Tautulli Builders](builders/tautulli)
* [Radarr Builders](builders/radarr)
* [Sonarr Builders](builders/sonarr)
* [MdbList Builders](builders/mdblist)
* [Letterboxd Builders](builders/letterboxd)
* [ICheckMovies Builders](builders/icheckmovies)
* [FlixPatrol Builders](builders/flixpatrol)
* [Reciperr Builders](builders/reciperr)
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

## Example

### Example Overlay File

```yaml
overlays:
  4K:
    overlay:
      name: 4K    # This will look for a local overlays/4K.png in your config folder
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

### Example Folder Structure

```
config
├── config.yml
├── Movies.yml
├── TV Shows.yml
├── Overlays.yml
├── overlays
│   ├── 4K.png
│   ├── Dolby.png
│   ├── HDR.png
```
