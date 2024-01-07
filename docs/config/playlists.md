# Playlist Files Attribute

As playlists are not tied to one specific library and can combine media from multiple libraries, they require their own 
special [Playlist Files](../files/playlists.md) to work.

Within the [Configuration File](overview.md), the `playlist_files` attribute specifies the 
[File Blocks](../config/files.md#blocks) of the [Playlist Files](../files/playlists.md) that the user wants Plex Meta 
Manager to act on.

**The libraries used in the playlist attribute `libraries` must be defined under the `libraries` attribute of the 
[Configuration File](overview.md).**

```yaml
playlist_files:
  - file: config/playlists.yml
  - pmm: playlist
```

???+ example "Example"

    This example is an advanced version of the playlist mappings with accompanying library mappings:

    ```yaml
    libraries:
      Movies:
        collection_files:
          - file: config/Movies.yml
          - pmm: imdb
          - pmm: studio
          - pmm: genre
          - pmm: actor
        operations:
          mass_critic_rating_update: tmdb
          split_duplicates: true
      TV Shows:
        collection_files:
          - file: config/TV Shows.yml
          - pmm: tmdb
          - pmm: network
        remove_overlays: false
        overlay_files:
          - file: config/Overlays.yml
    playlist_files:
      - file: config/playlists.yml
      - pmm: playlist
    ```