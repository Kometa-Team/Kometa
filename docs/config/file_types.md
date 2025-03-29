Files define the structure and format for creating Collections, Overlays, Playlists, and Metadata Edits within your libraries.

Files are modular and when properly leveraged, they not only facilitate the management of your library's collections and 
metadata but also serve as a crucial backup resource in case a restore is necessary.

These are the File types that can be utilized against Plex servers:

| File Type                                   | Description                                                                                                                              |   Parent Attribute   |
|:--------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|:--------------------:|
| [Collection Files](../files/collections.md) | Defines the data for building collections, allowing you to group and showcase your library in unique ways.                               |  `collection_files`  |
| [Overlay Files](../files/overlays.md)       | Defines the data for building overlays, allowing you to place information such as resolutions and ratings onto your posters.             |   `overlay_files`    |
| [Metadata Files](../files/metadata.md)      | Defines the data for editing metadata, allowing you to find and manipulate the metadata on individual items within your library.         |   `metadata_files`   |
| [Playlist Files](../files/playlists.md)     | Defines the data for building playlists, allowing you to combine media from multiple libraries and share them with users on your server. |   `playlist_files`   |
| [Template Files](../files/templates.md)     | Defines templates in external files, allowing you to use the same templates across multiple other files.                                 | `external_templates` |

??? example "Example File Blocks (click to expand)"
    
    In this example, multiple file blocks are defined for the `"TV Shows"` library:
    
    ```yaml
    libraries:
      TV Shows:
        collection_files:
          - file: config/TVShows.yml
          - folder: config/TV Shows/
        overlay_files:
          - default: imdb
          - repo: overlays
    playlist_files:
      - url: https://somewhere.com/Playlists.yml
    ```
    
    **Unlike the others, Playlist Files are not defined per-library.**

    Within the above example, Kometa will:

    * First, look within the root of the Kometa directory (also known as `config/`) for a Collection File named `TVShows.yml`. If this file does not exist, 
    Kometa will skip the entry and move to the next one in the list.

    * Then, look within the root of the Kometa directory (also known as `config/`) for a directory called `TV Shows`, and then load any collection files within that directory.

    * Then, look in the [Defaults folder](https://github.com/Kometa-Team/Kometa/tree/master/defaults) within the local Kometa folder
      [or docker container] for a file called `imdb.yml`.

    * Then, look within the Custom Defined Repo for a file called `overlays.yml`.

    * Finally, load the playlist file located at `https://somewhere.com/Playlists.yml`.
