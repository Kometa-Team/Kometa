# Last.fm User Recent Tracks Builder

`lastfm_user_recent_tracks` creates a track-level collection from a user's recent scrobbles, newest play first. It defaults to track level and requires a [Last.fm connection](../../../config/lastfm.md).

???+ warning "Track matching can be uncertain"

    Last.fm supplies at most one album for a track, even when that recording appears on several releases, and its album data may be missing or point to a different release from the one in Plex. When a MusicBrainz track ID is unavailable, Kometa relies on the artist, title, and a close duration, then tries that single album. A unique match can still be the wrong version if releases share those details. Check the resulting collection when different recordings or editions matter.

```yaml title="Collection file"
collections:
  Recently Played Tracks:
    lastfm_user_recent_tracks:
      username: YOUR_LASTFM_USERNAME
      limit: 50
    collection_order: custom
    sync_mode: sync
```

A username alone selects the latest 50 completed scrobbles; a currently playing track is excluded. `limit` accepts 1–1000 and counts scrobbles before duplicate tracks are removed. Optional `from` and `to` values are Unix timestamps in seconds (UTC) that restrict the play-time range; `from` must not be later than `to`. `collection_order: custom` preserves newest-first order after duplicates are removed.

The builder uses the same [track matching and missing-item reporting](user-top-tracks.md) as `lastfm_user_top_tracks`. It tries the album recorded with the scrobble after MusicBrainz ID and duration matching. Review the matching warning on that page if different versions of a track matter.
