# Lidarr All

`lidarr_all` includes every artist currently tracked in Lidarr.

Kometa matches the Lidarr MusicBrainz artist ID to a Plex artist GUID first. If the ID cannot identify one Plex artist, it uses the Lidarr artist name only when that name matches exactly one Plex artist, ignoring case.

```yaml
collections:
  All Lidarr Artists:
    lidarr_all: true
    sync_mode: sync
```
