---
search:
  boost: 2
---
# Image Asset Directory Guide

The Image Asset Directories can be used to update the posters and backgrounds of collections, movies, shows, seasons, and episodes.

## Requirements and configuration

If you want to apply artwork to movies and shows using the asset directory, the Kometa asset pipeline *requires* that your movies and shows are in folders of their own.  The name that Kometa will use to look up the asset poster for a movie is the folder that the movie file is located in *on disk*, and each movie/show needs to have a unique asset name.

In other words, this works:
```
movies/Star Wars (1977)/Star Wars (1977) Bluray-1080p.mkv
movies/Star Trek The Motion Picture (1979)/Star Trek The Motion Picture (1979) Bluray-1080p.mkv
movies/The Empire Strikes Back (1980)/The Empire Strikes Back (1980) Bluray-1080p.mkv
```
while this *WILL NOT*:
```
movies/Star Wars (1977) Bluray-1080p.mkv
movies/Star Trek The Motion Picture (1979) Bluray-1080p.mkv
movies/The Empire Strikes Back (1980) Bluray-1080p.mkv
```

If your movies and shows are not in individual folders, setting art using the asset directory will not work and you can stop here.

You can specify your asset folders under the `settings` attribute `asset_directory`:

???+ important 

    Assets can be stored anywhere on the host system that Kometa has visibility of (i.e. if using docker, the directory must be mounted/visible to the docker container).

    For the sake of this document, we will assume that your assets folders are all based within the directory mapped to `config` within your Kometa environment.

```yaml
settings:
  asset_directory: config/assets
```

To use multiple Image Asset Directories specify the directories as a YAML list:

```yaml
settings:
  asset_directory:
    - config/assets
    - config/more_assets
    - config/assets_ahoy
```

* You can specify an Image Asset Directory per Metadata/Playlist/Overlay File when calling the file. See [File Blocks](../../config/files.md) for how to define them.

* By default [if no `asset_directory` is specified], the program will look in the same folder as your `config.yml` for a folder called `assets`.

## Applying assets

Assets can be applied to collections [managed or unmanaged], playlists, and media items [movies, shows, seasons, and episodes].

Managed Collection and Playlist assets are applied whenever that collection/playlist is run.  You do not have to specifically enable assets for these items; Kometa will always search for and apply them.
  
Item [movie/show/etc] assets and Unmanaged Collections assets have to be specifically enabled before Kometa will search for and apply them.  Do this by enabling the `assets_for_all` Library Operation:

```yaml
Movies:
  operations:
    assets_for_all: true
```

* If you want to silence the `Asset Warning: No poster or background found in an assets folder for 'TITLE'` you can use the [`show_missing_assets` Setting Attribute](../../config/settings.md):
  ```yaml
  settings:
    show_missing_assets: false
  ```

## Asset interaction with overlays

If a media item has an asset associated with it, that asset image is taken as the source of truth for what artwork the item should have, and the overlay pipeline will no longer download and back up the base artwork from Plex.  Using the Asset Directory to assign custom art is the simplest and safest way to ensure that the overlay pipeline doesn't unexpectedly overwrite your custom artwork in Plex.

## Asset Naming

The table below shows the asset folder path structures that will be searched for. There are two options for how Kometa looks at the files inside your Asset Directories. Choose an option with the [`asset_folders` Setting Attribute](../../config/settings.md).  Note that `asset_folders` is a toggle; you can't put some images in folders and some not in a context where it is enabled.

Assets can be stored anywhere on the host system that Kometa has visibility of (i.e. if using docker, the directory must be mounted/visible to the docker container).

???+ important 

    The below table assumes that your assets are stored within the directory mapped to `config` in your Kometa environment.

| Image Type                       | Asset Folders Image Paths<br>`asset_folders: true`       | Flat Assets Image Paths<br>`asset_folders: false`             |
|:---------------------------------|:---------------------------------------------------------|:--------------------------------------------------------------|
| Collection/Movie/Show poster     | `<path_to_assets>/ASSET_NAME/poster.ext`                 | `<path_to_assets>/ASSET_NAME.ext`                             |
| Collection/Movie/Show background | `<path_to_assets>/ASSET_NAME/background.ext`             | `<path_to_assets>/ASSET_NAME_background.ext`                  |
| Season poster                    | `<path_to_assets>/ASSET_NAME/Season##.ext`               | `<path_to_assets>/ASSET_NAME_Season##.ext`                    |
| Season background                | `<path_to_assets>/ASSET_NAME/Season##_background.ext`    | `<path_to_assets>/ASSET_NAME_Season##_background.ext`         |
| Episode poster                   | `<path_to_assets>/ASSET_NAME/S##E##.ext`                 | `<path_to_assets>/ASSET_NAME_S##E##.ext`                      |
| Episode background               | `<path_to_assets>/ASSET_NAME/S##E##_background.ext`      | `<path_to_assets>/ASSET_NAME_S##E##_background.ext`           |

* For **Collections** replace `ASSET_NAME` with the mapping name used with the collection unless `name_mapping` is specified, which you would then use what's specified in `name_mapping`.

  For example:
  ```yaml
  collections:
    A24 Movies:
      trakt_list: https://trakt.tv/users/moonilism/lists/a24
  ```
  `ASSET_NAME` is "A24 Movies"

  ```yaml
  /// < : ** : > \\\:
     name_mapping: crazy-punctuation-collection
     trakt_list: https://trakt.tv/users/moonilism/lists/a24
  ```
  `ASSET_NAME` is "crazy-punctuation-collection"

* For **Movies** replace `ASSET_NAME` with the exact name of the folder the video file is stored in.

  That means the folder name exactly as it appears in the file system.
  ```
  /path/to/media/movies/THE NAME OF THE FOLDER HOWEVER LONG IT IS AND WHATEVER IT CONTAINS/MOVIE_NAME.mp4
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- THIS IS ASSET_NAME
  ```

  For example, given this movie:
  ```
  /path/to/media/movies/Star Wars (1977) {imdb-tt0076759} {tmdb-11}/Star Wars (1977) [1080p].mp4
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- THIS IS ASSET_NAME
  ```
  The asset names that Kometa will look for are:

  ASSET_FOLDERS=True:
  ```
  config/assets/Star Wars (1977) {imdb-tt0076759} {tmdb-11}/poster.ext
  config/assets/Star Wars (1977) {imdb-tt0076759} {tmdb-11}/background.ext
  ```
  
  ASSET_FOLDERS=False:
  ```
  config/assets/Star Wars (1977) {imdb-tt0076759} {tmdb-11}.ext
  config/assets/Star Wars (1977) {imdb-tt0076759} {tmdb-11}_background.ext
  ```

* For **Shows**, **Seasons**, and **Episodes** replace `ASSET_NAME` with the exact name of the folder for the show as a whole.

  That means the folder name exactly as it appears in the file system.
  ```
  /path/to/media/tv/THE NAME OF THE FOLDER HOWEVER LONG IT IS AND WHATEVER IT CONTAINS/Season 01/EPISODE_FILE.mkv
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- THIS IS ASSET_NAME
  ```

  For example, given this show:
  ```
  /path/to/media/tv/The Expanse (2015) {tvdb-280619}/Season 01/The Expanse (2015) - S01E01 - Dulcinea.mkv
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- THIS IS ASSET_NAME
  ```
  The asset names that Kometa will look for are:

  ASSET_FOLDERS=True:
  ```
  config/assets/The Expanse (2015) {tvdb-280619}/poster.ext
  config/assets/The Expanse (2015) {tvdb-280619}/background.ext
  ```
  
  ASSET_FOLDERS=False:
  ```
  config/assets/The Expanse (2015) {tvdb-280619}.ext
  config/assets/The Expanse (2015) {tvdb-280619}_background.ext
  ```
  
* For **Seasons** replace `##` with the zero padded season number (00 for specials)

  For example, given this show:
  ```
  /path/to/media/tv/The Expanse (2015) {tvdb-280619}/Season 01/The Expanse (2015) - S01E01 - Dulcinea.mkv
  ```

  The asset names that Kometa will look for are:

  ASSET_FOLDERS=True:
  ```
  config/assets/The Expanse (2015) {tvdb-280619}/Season01.ext
  config/assets/The Expanse (2015) {tvdb-280619}/Season01_background.ext
  ```
  
  ASSET_FOLDERS=False:
  ```
  config/assets/The Expanse (2015) {tvdb-280619}_Season01.ext
  config/assets/The Expanse (2015) {tvdb-280619}_Season01_background.ext
  ```

* For **Episodes** replacing the first `##` with the zero padded season number (00 for specials), the second `##` with the zero padded episode number

  For example, given this show:
  ```
  /path/to/media/tv/The Expanse (2015) {tvdb-280619}/Season 01/The Expanse (2015) - S01E01 - Dulcinea.mkv
  ```

  The asset names that Kometa will look for are:

  ASSET_FOLDERS=True:
  ```
  config/assets/The Expanse (2015) {tvdb-280619}/S01E01.ext
  config/assets/The Expanse (2015) {tvdb-280619}/S01E01_background.ext
  ```
  
  ASSET_FOLDERS=False:
  ```
  config/assets/The Expanse (2015) {tvdb-280619}_S01E01.ext
  config/assets/The Expanse (2015) {tvdb-280619}_S01E01_background.ext
  ```

* Replace `.ext` with the image extension

* When `asset_folders` is set to `true` movie/show folders can be nested inside other folders, but you must specify how deep you want to search because the more levels to search the longer it takes.
 
* You can specify how deep you want to scan by using the [`asset_depth` Setting Attribute](../../config/settings.md).

Here's an example config folder structure with an assets directory with `asset_folders` set to true and false.

### Asset Folders `asset_folders: true`

```
config
├── config.yml
├── Movies.yml
├── TV Shows.yml
└── assets
    ├── The Lord of the Rings
    │   ├── poster.png
    │   └── background.png
    ├── The Lord of the Rings The Fellowship of the Ring (2001)
    │   ├── poster.png
    │   └── background.png
    ├── The Lord of the Rings The Two Towers (2002)
    │   ├── poster.png
    │   └── background.png
    ├── The Lord of the Rings The Return of the King (2003)
    │   ├── poster.png
    │   └── background.png
    ├── Star Wars (Animated)
    │   ├── poster.png
    │   └── background.png
    ├── Star Wars The Clone Wars
    │   ├── poster.png
    │   ├── background.png
    │   ├── Season00.png
    │   ├── Season01.png
    │   ├── Season02.png
    │   ├── Season03.png
    │   ├── Season04.png
    │   ├── Season05.png
    │   ├── Season06.png
    │   ├── Season07.png
    │   ├── S07E01.png
    │   ├── S07E02.png
    │   ├── S07E03.png
    │   ├── S07E04.png
    │   └── S07E05.png
    └── Star Wars Rebels
        ├── poster.png
        ├── background.png
        ├── Season01.png
        ├── Season01_background.png
        ├── Season02.png
        ├── Season02_background.png
        ├── Season03.png
        ├── Season03_background.png
        ├── Season04.png
        └── Season04_background.png
```

### Flat Assets `asset_folders: false`

```
config
├── config.yml
├── Movies.yml
├── TV Shows.yml
└── assets
    ├── The Lord of the Rings.png
    ├── The Lord of the Rings_background.png
    ├── The Lord of the Rings The Fellowship of the Ring (2001).png
    ├── The Lord of the Rings The Fellowship of the Ring (2001)_background.png
    ├── The Lord of the Rings The Two Towers (2002).png
    ├── The Lord of the Rings The Two Towers (2002)_background.png
    ├── The Lord of the Rings The Return of the King (2003).png
    ├── The Lord of the Rings The Return of the King (2003)_background.png
    ├── Star Wars (Animated).png
    ├── Star Wars (Animated)_background.png
    ├── Star Wars The Clone Wars.png
    ├── Star Wars The Clone Wars_background.png
    ├── Star Wars The Clone Wars_Season00.png
    ├── Star Wars The Clone Wars_Season01.png
    ├── Star Wars The Clone Wars_Season02.png
    ├── Star Wars The Clone Wars_Season03.png
    ├── Star Wars The Clone Wars_Season04.png
    ├── Star Wars The Clone Wars_Season05.png
    ├── Star Wars The Clone Wars_Season06.png
    ├── Star Wars The Clone Wars_Season07.png
    ├── Star Wars The Clone Wars_S07E01.png
    ├── Star Wars The Clone Wars_S07E02.png
    ├── Star Wars The Clone Wars_S07E03.png
    ├── Star Wars The Clone Wars_S07E04.png
    ├── Star Wars The Clone Wars_S07E05.png
    ├── Star Wars Rebels.png
    ├── Star Wars Rebels_background.png
    ├── Star Wars Rebels_Season01.png
    ├── Star Wars Rebels_Season01_background.png
    ├── Star Wars Rebels_Season02.png
    ├── Star Wars Rebels_Season02_background.png
    ├── Star Wars Rebels_Season03.png
    ├── Star Wars Rebels_Season03_background.png
    ├── Star Wars Rebels_Season04.png
    └── Star Wars Rebels_Season04_background.png
```
