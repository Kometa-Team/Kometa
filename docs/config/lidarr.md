---
search:
  boost: 3
hide:
  - toc
---
# Lidarr Attributes

Lidarr integration is optional. It manages **artists** from a Plex music library; it does not add individual tracks. Kometa reads a Plex artist's `mbid://` GUID and adds the artist only when it contains one valid MusicBrainz artist ID. Artists without that GUID are reported and skipped. See the [Lidarr builders](../files/builders/lidarr/overview.md) for artist collections sourced from Lidarr.

```yaml title="config.yml Lidarr sample"
lidarr:
  url: http://localhost:8686
  token: LIDARR_API_KEY
  add_missing: false
  add_existing: false
  upgrade_existing: false
  monitor_existing: false
  ignore_cache: false
  root_folder_path: /music
  monitor: all
  monitor_new_albums: all
  quality_profile: Lossless
  tag: kometa
  search: false
  lidarr_path: /music
  plex_path: /mnt/media/music
```

The settings may be declared globally or overridden in an individual library's `lidarr` mapping.

| Attribute | Description |
|:--|:--|
| `url`, `token` | Lidarr URL and API key. |
| `add_missing` | Reserved for future artist-add operations; Lidarr builders only return artists already tracked by Lidarr. |
| `add_existing` | Enables `lidarr_add_all_existing`, which adds the current Plex artists. |
| `upgrade_existing` | Changes an existing artist to the configured quality profile. |
| `monitor_existing` | Changes an existing artist's monitored state. |
| `ignore_cache` | Ignores Kometa's successful-add cache. |
| `root_folder_path` | Lidarr root folder for new artists. |
| `monitor` | Which current albums to monitor: `all`, `future`, `missing`, `existing`, `first`, `latest`, or `none`. |
| `monitor_new_albums` | Which albums released after an artist is added to monitor: `all`, `none`, or `new`. |
| `quality_profile` | Lidarr quality-profile name (case-insensitive) or numeric ID. |
| `tag` | Tag or list of tags applied to new artists. |
| `search` | Search for missing albums after adding an artist. |
| `lidarr_path` | Lidarr's view of the music root when its path differs from Plex's. |
| `plex_path` | Plex's corresponding music-root path. |

Use these library operations for artist-level synchronization:

```yaml
operations:
  lidarr_add_all_existing: true
  lidarr_remove_by_tag:
    - kometa
```

`lidarr_add_all_existing` adds every Plex artist with a valid MusicBrainz artist GUID. `lidarr_remove_by_tag` removes matching artists from Lidarr but preserves their files and does not create a Lidarr exclusion.
