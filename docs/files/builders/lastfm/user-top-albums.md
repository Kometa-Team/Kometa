# Last.fm User Top Albums Builder

`lastfm_user_top_albums` creates an album-level collection in a Plex music library from a Last.fm user's most-played albums. It defaults to album level; `builder_level: album` is optional. It requires a [Last.fm connection](../../../config/lastfm.md).

```yaml title="Collection file"
collections:
  My Most Played Albums:
    lastfm_user_top_albums:
      username: YOUR_LASTFM_USERNAME
      period: overall
      limit: 50
    collection_order: custom
    sync_mode: sync
```

A username alone selects the overall top 50 albums. You can also supply a list of usernames or dictionaries. `period` accepts `overall`, `7day`, `1month`, `3month`, `6month`, or `12month`; `limit` accepts 1–1000. `collection_order: custom` keeps Last.fm's ranking.

Kometa first matches the Last.fm album MusicBrainz ID against Plex album GUIDs. If the ID has no Plex match or Last.fm supplies no valid ID, Kometa accepts a unique artist and album title match, ignoring case and typographic dash differences. This also handles cases where Last.fm identifies a particular release while Plex identifies its release group. Ambiguous or unmatched albums are skipped and shown under **Missing Albums from Library** when `show_missing` is enabled. With `save_report`, they appear in the library report under **Albums Missing**.
