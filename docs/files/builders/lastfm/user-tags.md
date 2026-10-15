# Last.fm User Tags Builder

`lastfm_user_tags` builds a Plex music collection from the artists, albums, or tracks a Last.fm user has personally tagged. It defaults to artist level. Set `builder_level: album` or `builder_level: track` for the other levels. It requires a [Last.fm connection](../../../config/lastfm.md).

```yaml title="Collection file"
collections:
  My Tagged Albums:
    builder_level: album
    lastfm_user_tags:
      username: YOUR_LASTFM_USERNAME
      tag: favourites
      limit: 50
    sync_mode: sync
```

Both `username` and `tag` are required. `limit` defaults to 50 and accepts 1–1000. You can supply a list of user/tag dictionaries to combine them. `builder_level` determines whether Kometa requests the user's tagged artists, albums, or tracks; a collection contains one level. Kometa matches MusicBrainz IDs first, then unique names using the [shared music matching rules](user-top-tracks.md). Unmatched items use the usual missing artist, album, or track reporting.
