# Playlist Files Attributes

As playlists are not tied to one specific library and can combine media from multiple libraries, they require their own special [Playlist Files](../metadata/playlist) to work.

Within the [Config File](configuration), the `playlist_files` attribute specifies the [path type](paths) and path of the [Playlist Files](../metadata/playlist) that the user wants Plex Meta Manager to act on.

**The libraries used in the playlist attribute `libraries` must be defined under the `libraries` attribute of the [Config File](configuration).**

```yaml
playlist_files:
  - file: config/playlists.yml
  - pmm: playlist
```

## Example

This example is an advanced version of the playlist mappings with accompanying library mappings:

<details>
  <summary>Click to Expand</summary>
  <br />

```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
      - pmm: imdb
      - pmm: studio
      - pmm: genre
      - pmm: actor
    operations:
      mass_critic_rating_update: tmdb
      split_duplicates: true
  TV Shows:
    metadata_path:
      - file: config/TV Shows.yml
      - pmm: tmdb
      - pmm: network
    overlay_path:
      - remove_overlays: false
      - file: config/Overlays.yml
playlist_files:
  - file: config/playlists.yml
  - pmm: playlist
```
</details>
