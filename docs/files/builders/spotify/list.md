---
hide:
  - toc
---
# Spotify

The `spotify_list` builder creates a track collection from a Spotify playlist. It requires the root-level [Spotify connection](../../../config/spotify.md) and a Plex Music library. Spotify permits the API to read playlist items only when the authorized account owns the playlist or is a collaborator.

!!! warning "Spotify-owned playlists"

    Spotify-owned personalized playlists, including Release Radar, Discover Weekly, Daily Mixes, and similar Made for You playlists, are not accessible through the Spotify Web API. They cannot be fetched with `spotify_list`, even when they are saved in your Spotify library or supplied by playlist ID.

```yaml
collections:
  All:
    spotify_list: https://open.spotify.com/playlist/37i9dQZF1FwLliIcKXtMsW
```

The builder also accepts the 22-character playlist ID directly:

```yaml
collections:
  All:
    spotify_list: 37i9dQZF1FwLliIcKXtMsW
```

You can also use an exact, case-insensitive name for a playlist in the authorized Spotify account's library. The name must identify exactly one playlist; use a URL or ID when multiple library playlists share a name. The playlist must still be owned by the authorized account or shared with it as a collaborator:

```yaml
collections:
  Release Radar:
    spotify_list: Release Radar
```

Use `spotify_list_details` to also apply the playlist description and primary Spotify artwork to the Plex collection. Kometa adds a Spotify source link to the collection summary for attribution:

```yaml
collections:
  All:
    spotify_list_details: https://open.spotify.com/playlist/37i9dQZF1FwLliIcKXtMsW
```

Kometa sets `builder_level: track` automatically. If it is specified explicitly, it must also be `track`.

Spotify tracks are resolved against local Plex tracks using normalized title, artist, and album metadata. Matching disc and track numbers are preferred. If either position differs, Kometa falls back to a duration match within seven seconds. Missing tracks are included in the standard missing-items report when `show_missing` is enabled.

## Liked Songs

Use `spotify_liked: me` to create a collection from the liked songs belonging to the Spotify account that authorized Kometa:

```yaml
collections:
  Liked Songs:
    spotify_liked: me
```

## Top Tracks

Use `spotify_top` with `short`, `medium`, or `long` to build a collection from your Spotify top tracks over roughly the last four weeks, six months, or year:

```yaml
collections:
  Top Tracks This Month:
    spotify_top: short
```

## Recently Played

Use `spotify_recent: me` to create a collection from your 50 most recently played Spotify tracks:

```yaml
collections:
  Recently Played:
    spotify_recent: me
```

## Saved Albums

Use `spotify_saved: me` to create an album-level collection from the albums saved to your Spotify library:

```yaml
collections:
  Saved Albums:
    spotify_saved: me
```
