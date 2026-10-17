# Last.fm User Top Tracks Builder

`lastfm_user_top_tracks` creates a track-level collection in a Plex music library from a Last.fm user's most-played tracks. It defaults to track level; `builder_level: track` is optional. It requires a [Last.fm connection](../../../config/lastfm.md).

???+ warning "Track matching can be uncertain"

    Last.fm supplies at most one album for a track, even when that recording appears on several releases, and its album data may be missing or point to a different release from the one in Plex. When a MusicBrainz track ID is unavailable, Kometa relies on the artist, title, and a close duration, then tries that single album. A unique match can still be the wrong version if releases share those details. Check the resulting collection when different recordings or editions matter.

```yaml title="Collection file"
collections:
  My Most Played Tracks:
    lastfm_user_top_tracks:
      username: YOUR_LASTFM_USERNAME
      period: overall
      limit: 50
    collection_order: custom
    sync_mode: sync
```

A username alone selects the overall top 50 tracks. You can also supply a list of usernames or dictionaries. `period` accepts `overall`, `7day`, `1month`, `3month`, `6month`, or `12month`; `limit` accepts 1–1000. `collection_order: custom` keeps Last.fm's ranking.

Kometa matches a MusicBrainz track ID to a Plex track GUID first. If that does not identify one Plex track, it matches an artist and track title with duration within two seconds, requiring exactly one Plex track. If that fails, it uses the album returned by Last.fm and accepts an artist, album, and track title match only if it is unique in Plex. Name comparisons ignore case and treat typographic dashes like regular hyphens. Last.fm's chart response includes neither album nor duration; track details may omit either. Tracks without enough information or with ambiguous Plex matches are skipped and appear under **Missing Tracks from Library** when `show_missing` is enabled. With `save_report`, they appear in the library report under **Tracks Missing**.
