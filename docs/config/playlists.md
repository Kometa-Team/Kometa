---
hide:
  - toc
---
# Playlist Files Attribute

As playlists are not tied to one specific library and can combine media from multiple libraries, they require their own special [Playlist Files](../files/playlists.md) to work.

Within the [Configuration File](overview.md), the `playlist_files` attribute specifies the [File Blocks](../config/files.md#blocks) 
of the [Playlist Files](../files/playlists.md) that the user wants Kometa to act on.

**The libraries used in the playlist attribute `libraries` must be defined under the `libraries` attribute of the [Configuration File](overview.md).**

```yaml title="config.yml Playlists sample"
playlist_files:
  - file: config/playlists.yml
  - default: playlist
```

???+ example "Example"

    This example is an advanced version of the playlist mappings with accompanying library mappings:

    ```yaml
    libraries:
      Movies:
        collection_files:
          - file: config/Movies.yml
          - default: imdb
          - default: studio
          - default: genre
          - default: actor
        operations:
          mass_critic_rating_update: tmdb
          split_duplicates: true
      TV Shows:
        collection_files:
          - file: config/TV Shows.yml
          - default: tmdb
          - default: network
        remove_overlays: false
        overlay_files:
          - file: config/Overlays.yml
    playlist_files:
      - file: config/playlists.yml
      - default: playlist
    ```