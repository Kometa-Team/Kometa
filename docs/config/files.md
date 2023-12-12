# Files

Files define the structure and format for creating Collections, Overlays, Playlists, and Metadata Edits within your libraries.

Files are modular and when properly leveraged, they not only facilitate the management of your library's collections and metadata but also serve as a crucial backup resource in case a restore is necessary.

There are four main File types that can be utilized against Plex servers:

| File Type                                                                                                        | Description                                                                                                                              |
|:-----------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|
| [Collection Files](data/collections.md)                                                                          | Defines the data for building collections, allowing you to group and showcase your library in unique ways                                |
| [Overlay Files](data/overlays.md)                                                                                | Defines the data for building overlays, allowing you to place information such as resolutions and ratings onto your posters.             |
| Metadata Files ([Movies](data/metadata/movie.md)/[Shows](data/metadata/show.md)/[Music](data/metadata/music.md)) | Defines the data for editing metadata, allowing you to find and manipulate the metadata on individual items within your library.         |
| [Playlist Files](data/playlists.md)                                                                              | Defines the data for building playlists, allowing you to combine media from multiple libraries and share them with users on your server  |

Collection, Overlay and Metadata Files can be linked to libraries in the [Libraries Attribute](../config/libraries.md#metadata-path) within the [Configuration File](../config/configuration.md).

## Example

This is a basic Files structure showing the use of all four File types.

???+ example "Example Files"

    Unlike the other three, Playlist Files are not defined per-library.

    Theis examples utilizes the [PMM Defaults](../defaults/files.md)

    ```yaml
    libraries:
      Movies:
        collection_files:
          - pmm: imdb
        overlay_files:
          - pmm: resolution
        metadata_files:
          - file: config/metadata.yml
    playlist_files:
      - pmm: playlists
    ```