---
search:
  boost: 2
hide:
  - toc
---
# Image Asset Directory Guide

The Image Asset Directories can be used to update the posters and backgrounds of collections, movies, shows, seasons, and episodes.

Please read thorough this entire guide.  Everything in it assumes understanding of what came before.

## What is an Asset?

Kometa can apply a variety of images to a variety of items in Plex from a variety of sources.

An "Asset" is one of those sources; it's a set of directories full of images with specific names that can be applied to items by Kometa.  Kometa can apply asset images to:

    | Item Type    | poster | background | logo | square_art |
    |:-------------|:----------------------------------------|
    | Collection   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
    | Playlist     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
    | Movie        | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
    | Show         | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
    | Season       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .red }   | :fontawesome-solid-circle-check:{ .red }   |
    | Episode      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .red }   | :fontawesome-solid-circle-check:{ .red }   |

Without additional specific configuration, Kometa will apply assets **only** to collections/playlists which Kometa has created itself ("managed" collections/playlists).  This refers to the **collection itself**, not the items **in** the collection.

Kometa **will not** apply assets to *items within collections*, and that functionality is not available in Kometa since a movie/show/episode has a single poster across the entire library.  Assets can already be applied to individual items, so a duplicate method to apply such assets is not needed.

    | Item Type            | when assets are applied          |
    |:---------------------|:---------------------------------|
    | Managed Collection   | happens automatically            |
    | Managed Playlist     | happens automatically            |
    | Unmanaged Collection | assets_for_all_collections: true |
    | Unmanaged Playlist   | NOT SUPPORTED                    |
    | Movie                | assets_for_all: true             |
    | Show                 | assets_for_all: true             |
    | Season               | assets_for_all: true             |
    | Episode              | assets_for_all: true             |

Relevant operations:
[`assets_for_all`](../../config/operations/#assets-for-all)
[`assets_for_all_collections`](../../config/operations/#assets-for-all-collections)

Image **assets** are stored in and retrieved by Kometa from "asset directories".

## What is an Asset Directory?

It is a folder containing artwork (posters and/or backgrounds) that is *typically* entirely separate to your media directories.

The only connection an asset directory has with your media directories is that **the name of the folder containing your movie or series' video files** is the "asset name".
Kometa uses that "asset name" as the **key** to find the artwork in the asset directory.

Media directory:

```txt
/this/part/does/not/matter/Star Wars (1977)/neither_does_this_part.mkv
                           ^^^^^^^^^^^^^^^^ "asset name"
```
Asset Directory:

with asset folders:

```txt
/this/part/does/not/matter/Star Wars (1977)/background.jpg
/this/part/does/not/matter/Star Wars (1977)/poster.jpg
                           ^^^^^^^^^^^^^^^^ "asset name" used as lookup key
```

OR without asset folders

```txt
/this/part/does/not/matter/Star Wars (1977)_background.jpg
/this/part/does/not/matter/Star Wars (1977).jpg
                           ^^^^^^^^^^^^^^^^ "asset name" used as lookup key
```

You **can** use your media directories as the asset directories (if for example you like to keep your artwork next to your media files), but this is not typical, nor is it required.

Kometa does not require direct access to your media directories in normal use, and it is typically run remote from the Plex server, which is why the asset directory is *typically* entirely separate.

Relevant settings:
[`asset-directory`](../../config/settings/#asset-directory)

## Requirements and configuration

If you want to apply artwork to movies and shows using the asset directory, the Kometa asset pipeline *requires* that your movies and shows are in folders of their own.
The name that Kometa will use to look up the asset poster for a movie is the folder that the movie file is located in *on disk*, and each movie/show needs to have a unique asset name.

In other words, this works:

```txt
movies/Star Wars (1977)/Star Wars (1977) Bluray-1080p.mkv
movies/Star Trek The Motion Picture (1979)/Star Trek The Motion Picture (1979) Bluray-1080p.mkv
movies/The Empire Strikes Back (1980)/The Empire Strikes Back (1980) Bluray-1080p.mkv
```

while this *WILL NOT*:

```txt
movies/Star Wars (1977) Bluray-1080p.mkv
movies/Star Trek The Motion Picture (1979) Bluray-1080p.mkv
movies/The Empire Strikes Back (1980) Bluray-1080p.mkv
```

If your movies and shows are not in individual folders, setting art using the asset directory will not work and you can stop here.

You can specify your asset folders under the `settings` attribute `asset_directory`:

???+ important

    Assets can be stored anywhere on the host system that Kometa has visibility of (i.e. if using docker, the directory must be mounted/visible to the docker container).

    For the sake of this document, we will assume that your assets folders are all based within the directory mapped to `config` within your Kometa environment.

    Asset directories can be scoped to type/library/collection; those specifics are not discussed here.  See the [`asset-directory`](../../config/settings/#asset-directory) docs.

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

* Kometa will not create the asset directories themselves; it will create folder *within* asset directories [if configured to do so with `create_asset_folders: true`], but not the asset directories themselves.

* You can specify an Image Asset Directory per Metadata/Playlist/Overlay File when calling the file. See [File Blocks](../../config/files.md) for how to define them.

* By default [if no `asset_directory` is specified], the program will look in the same folder as your `config.yml` for a folder called `assets`.

## Applying assets

Assets can be applied to collections [managed or unmanaged], playlists, and media items [movies, shows, seasons, and episodes].

Managed Collection and Playlist assets are applied whenever that collection/playlist is run.

You do not have to specifically enable assets for these items; Kometa will always search for and apply them.

Item [movie/show/etc] assets and Unmanaged Collections assets have to be specifically enabled before Kometa will search for and apply them. Do this by enabling the `assets_for_all` and/or `assets_for_all_collections` Library Operations:

```yaml
Movies:
  operations:
    assets_for_all: true             # apply assets to individual moives/shows/season/episodes
    assets_for_all_collections: true # apply assets to UNMANAGED collections
```
Applying an asset to a collection affects **ONLY** the collection.  The items within the collection are **not affected** unless you enable `assets_for_all` and even then you need to individually configure assets for those items.  There is no built-in functionality for "apply assets to this collection and all the things within it".  Also, if you apply assets to items within a collection, those assets show up everytwhere in the Plex UI.  A movie, for example, has one poster.  If you set an asset on "Star Wars", then that poster shows up on the movie when you view your "Star Wars" collection along with everywhere else the movie appears [other collections, the library].

Relevant operations:
[`assets_for_all`](../../config/operations/#assets-for-all)
[`assets_for_all_collections`](../../config/operations/#assets-for-all-collections)

If you want to silence the `Asset Warning: No poster or background found in an assets folder for 'TITLE'` you can use the [`show_missing_assets` Setting Attribute](../../config/settings.md):

```yaml
settings:
  show_missing_assets: false
```
[`asset-show_missing_assets`](../../config/settings/#show_missing_assets)

## Asset interaction with overlays

If a media item has an asset associated with it, that asset image is taken as the source of truth for what artwork the item should have,
and the overlay pipeline will no longer download and back up the base artwork from Plex. Using the Asset Directory to assign custom art is
the simplest and safest way to ensure that the overlay pipeline doesn't unexpectedly overwrite your custom artwork in Plex.

## Asset Naming

The table below shows the asset folder path structures that will be searched for. There are two options for how Kometa looks at the files inside your Asset Directories. Choose an option with

the [`asset_folders` Setting Attribute](../../config/settings/#asset_folders). Note that `asset_folders` is a toggle; you can't put some images in folders and some not in a context where it is enabled.

Assets can be stored anywhere on the host system that Kometa has visibility of (i.e. if using docker, the directory must be mounted/visible to the docker container).

Replace `.ext` with a supported image extension: `.jpg`, `.jpeg`, `.png`, `.webp`, or `.tbn`.

Numbered variants such as `poster-2.png` or `fanart-2.tbn` are accepted for the same base asset names listed below. When both an exact asset name and a numbered variant exist, the exact asset name takes priority. For example, `poster.jpg` is used before `poster-2.png`.

???+ important

    In this table, `<path_to_assets>` is an asset directory OR some directory below an asset directory, depending on your setting for `asset_depth`.

    For example, if your `asset_directory` is `/config/assets` and your `asset_depth` is 2, then `<path_to_assets>` might be:

    ```
    /config/assets
    /config/assets/this
    /config/assets/this/that
    ```
    WHATEVER `this` and `that` are.

    The important detail in this table is what `ASSET_NAME` is and how enabling asset folders affects the thing that Kometa is looking for, not *where* it's looking aside from "in an asset directory".

=== "ASSET_FOLDERS=True"

    | Image Type                       | Asset Folders Image Paths<br>`asset_folders: true`         |
    |:---------------------------------|:-----------------------------------------------------------|
    | Collection/Movie/Show poster     | `<path_to_assets>/ASSET_NAME/poster.ext`, `cover.ext`, `default.ext`, `folder.ext`, or `movie.ext` |
    | Collection/Movie/Show background | `<path_to_assets>/ASSET_NAME/background.ext`, `art.ext`, `backdrop.ext`, or `fanart.ext` |
    | Collection/Playlist/Movie/Show logo       | `<path_to_assets>/ASSET_NAME/logo.ext` or `clearlogo.ext` |
    | Collection/Playlist/Movie/Show square art | `<path_to_assets>/ASSET_NAME/square.ext`, `square_art.ext`, `squareArt.ext`, or `backgroundSquare.ext` |
    | Season poster                    | `<path_to_assets>/ASSET_NAME/Season##.ext`                 |
    | Season background                | `<path_to_assets>/ASSET_NAME/Season##_background.ext`      |
    | Episode poster                   | `<path_to_assets>/ASSET_NAME/S##E##.ext`                   |
    | Episode background               | `<path_to_assets>/ASSET_NAME/S##E##_background.ext`        |

=== "ASSET_FOLDERS=False"

    | Image Type                       | Flat Assets Image Paths<br>`asset_folders: false`          |
    |:---------------------------------|:-----------------------------------------------------------|
    | Collection/Movie/Show poster     | `<path_to_assets>/ASSET_NAME.ext`                         |
    | Collection/Movie/Show background | `<path_to_assets>/ASSET_NAME_background.ext`, `ASSET_NAME-art.ext`, `ASSET_NAME-backdrop.ext`, `ASSET_NAME-background.ext`, or `ASSET_NAME-fanart.ext` |
    | Collection/Playlist/Movie/Show logo       | `<path_to_assets>/ASSET_NAME_logo.ext`, `ASSET_NAME-clearlogo.ext`, or `ASSET_NAME-logo.ext` |
    | Collection/Playlist/Movie/Show square art | `<path_to_assets>/ASSET_NAME_square.ext`, `ASSET_NAME_square_art.ext`, `ASSET_NAME-square.ext`, `ASSET_NAME-squareArt.ext`, or `ASSET_NAME-backgroundSquare.ext` |
    | Season poster                    | `<path_to_assets>/ASSET_NAME_Season##.ext`                 |
    | Season background                | `<path_to_assets>/ASSET_NAME_Season##_background.ext`      |
    | Episode poster                   | `<path_to_assets>/ASSET_NAME_S##E##.ext`                   |
    | Episode background               | `<path_to_assets>/ASSET_NAME_S##E##_background.ext`        |

For example, if the asset name is `Toy Story (1995)`, Kometa accepts the following item-level filenames:

=== "ASSET_FOLDERS=True"

    ```txt
    config/assets/Toy Story (1995)/poster.jpg
    config/assets/Toy Story (1995)/poster-2.png
    config/assets/Toy Story (1995)/cover.jpg
    config/assets/Toy Story (1995)/default.png
    config/assets/Toy Story (1995)/folder.tbn
    config/assets/Toy Story (1995)/movie.jpg

    config/assets/Toy Story (1995)/background.jpg
    config/assets/Toy Story (1995)/fanart.png
    config/assets/Toy Story (1995)/backdrop.tbn
    config/assets/Toy Story (1995)/art.jpg

    config/assets/Toy Story (1995)/logo.png
    config/assets/Toy Story (1995)/clearlogo.png

    config/assets/Toy Story (1995)/square.jpg
    config/assets/Toy Story (1995)/square_art.png
    config/assets/Toy Story (1995)/squareArt.jpg
    config/assets/Toy Story (1995)/backgroundSquare.png
    ```

=== "ASSET_FOLDERS=False"

    ```txt
    config/assets/Toy Story (1995).jpg
    config/assets/Toy Story (1995)-2.png

    config/assets/Toy Story (1995)_background.jpg
    config/assets/Toy Story (1995)-background.jpg
    config/assets/Toy Story (1995)-fanart.png
    config/assets/Toy Story (1995)-backdrop.tbn
    config/assets/Toy Story (1995)-art.jpg

    config/assets/Toy Story (1995)_logo.png
    config/assets/Toy Story (1995)-logo.png
    config/assets/Toy Story (1995)-clearlogo.png

    config/assets/Toy Story (1995)_square.jpg
    config/assets/Toy Story (1995)_square_art.png
    config/assets/Toy Story (1995)-square.jpg
    config/assets/Toy Story (1995)-squareArt.png
    config/assets/Toy Story (1995)-backgroundSquare.png
    ```

## Determining the "Asset Name"

=== "Collections"

    `ASSET_NAME` is the mapping name used with the collection unless `name_mapping` is specified, in which case you would use what's specified in `name_mapping`.

    For example:
    ```yaml
    collections:
      A24 Movies:
        mdblist_list: https://mdblist.com/lists/inshanemagic/a24-films
    ```
    `ASSET_NAME` is "A24 Movies"

    ```yaml
    collections:
      /// < : ** : > \\\:
        name_mapping: crazy-punctuation-collection
        mdblist_list: https://mdblist.com/lists/inshanemagic/a24-films
    ```
    `ASSET_NAME` is "crazy-punctuation-collection"

=== "Movies"

    `ASSET_NAME` is the exact name of the folder the video file is stored in.

    That means the folder name exactly as it appears in the file system.
    ```
    /path/to/media/movies/NAME OF THE FOLDER HOWEVER LONG AND WHATEVER IT CONTAINS/MOVIE_NAME.mp4
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- THIS IS ASSET_NAME
    ```

    For example, given this movie:
    ```
    /path/to/media/movies/Star Wars (1977) {imdb-tt0076759} {tmdb-11}/Star Wars (1977) [1080p].mp4
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- THIS IS ASSET_NAME
    ```
    The asset names that Kometa will look for are:

    === "ASSET_FOLDERS=True"
        ```
        config/assets/Star Wars (1977) {imdb-tt0076759} {tmdb-11}/poster.ext
        config/assets/Star Wars (1977) {imdb-tt0076759} {tmdb-11}/background.ext
        ```
    === "ASSET_FOLDERS=False"
        ```
        config/assets/Star Wars (1977) {imdb-tt0076759} {tmdb-11}.ext
        config/assets/Star Wars (1977) {imdb-tt0076759} {tmdb-11}_background.ext
        ```

=== "Shows, Seasons, and Episodes"

    `ASSET_NAME` is the exact name of the folder for the show as a whole.

    That means the folder name exactly as it appears in the file system.
    ```
    /path/to/media/tv/NAME OF THE FOLDER HOWEVER LONG AND WHATEVER IT CONTAINS/Season 01/EPISODE_FILE.mkv
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- THIS IS ASSET_NAME
    ```

    For example, given this show:
    ```
    /path/to/media/tv/The Expanse (2015) {tvdb-280619}/Season 01/The Expanse (2015) - S01E01 - Dulcinea.mkv
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- THIS IS ASSET_NAME
    ```
    The asset names that Kometa will look for are:

    === "ASSET_FOLDERS=True"

        ```
        config/assets/The Expanse (2015) {tvdb-280619}/poster.ext
        config/assets/The Expanse (2015) {tvdb-280619}/background.ext
        ```

    === "ASSET_FOLDERS=False"

        ```
        config/assets/The Expanse (2015) {tvdb-280619}.ext
        config/assets/The Expanse (2015) {tvdb-280619}_background.ext
        ```

## Season and Episode numbers

=== "Seasons"

    Replace `##` with the zero padded season number (00 for specials)

    For example, given this show:
    ```
    /path/to/media/tv/The Expanse (2015) {tvdb-280619}/Season 01/The Expanse (2015) - S01E01 - Dulcinea.mkv
    ```

    The asset names that Kometa will look for are:

    === "ASSET_FOLDERS=True"

        ```
        config/assets/The Expanse (2015) {tvdb-280619}/Season01.ext
        config/assets/The Expanse (2015) {tvdb-280619}/Season01_background.ext
        ```

    === "ASSET_FOLDERS=False"

        ```
        config/assets/The Expanse (2015) {tvdb-280619}_Season01.ext
        config/assets/The Expanse (2015) {tvdb-280619}_Season01_background.ext
        ```

=== "Episodes"

    Replace the first `##` with the zero padded season number (00 for specials), the second `##` with the zero padded episode number

    For example, given this show:
    ```
    /path/to/media/tv/The Expanse (2015) {tvdb-280619}/Season 01/The Expanse (2015) - S01E01 - Dulcinea.mkv
    ```

    The asset names that Kometa will look for are:

    === "ASSET_FOLDERS=True"

        ```
        config/assets/The Expanse (2015) {tvdb-280619}/S01E01.ext
        config/assets/The Expanse (2015) {tvdb-280619}/S01E01_background.ext
        ```

    === "ASSET_FOLDERS=False"

        ```
        config/assets/The Expanse (2015) {tvdb-280619}_S01E01.ext
        config/assets/The Expanse (2015) {tvdb-280619}_S01E01_background.ext
        ```

* Replace `.ext` with a supported image extension: `.jpg`, `.jpeg`, `.png`, `.webp`, or `.tbn`.

* When `asset_folders` is set to `true` movie/show folders can be nested inside other folders, but you must specify how deep you want to search because the more levels to search the longer it takes.

* You can specify how deep you want to scan by using the [`asset_depth` Setting Attribute](../../config/settings.md).

Here's an example config folder structure with an assets directory with `asset_folders` set to true and false.

### Asset Folders vs Flat Assets

=== "ASSET_FOLDERS=True"

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

=== "ASSET_FOLDERS=False"

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

### Other settings

There are other asset-related settings described starting [here](../../config/settings/#asset-depth)

### Step-by-Step

The Cookbook has a step-by-step [walkthrough](https://github.com/Kometa-Team/Cookbook/blob/main/cookbook/asset_pipeline_walkthrough.md).