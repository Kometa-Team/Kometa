# YouTube Music List Builder

`ytmusic_list` creates a collection from a public YouTube Music playlist. Paste the playlist link, or use its playlist ID. No sign-in or YouTube Music setup is needed for public playlists.

This builder uses the playlist you choose, so it has no country setting. For top artists by country, use [`ytmusic_top_artists`](top-artists.md). For chart playlists by country, use [dynamic charts](charts.md).

```yaml title="Collection file"
collections:
  My YouTube Music Playlist:
    ytmusic_list: https://music.youtube.com/playlist?list=PLC7LNuBoMA-o
    collection_order: custom
    sync_mode: sync
```

You can also provide just the playlist ID, or a list of playlist links and IDs. Set `collection_order: custom` to keep the playlist order. If the same Plex track appears more than once, it is included once at its first position.

To include at most 50 tracks, use `ytmusic_list: {playlist: PLC7LNuBoMA-o, limit: 50}`. Kometa can also use the playlist description and cover when available. Details you set for the collection take priority.

Kometa matches playlist tracks to your Plex library using the artist and track name, and checks the duration and album when available. Tracks it cannot match appear in the missing-tracks log and report. Versions with similar names and lengths may occasionally be confused, so review the collection if the exact recording matters.
