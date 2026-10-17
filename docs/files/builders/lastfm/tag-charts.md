# Last.fm Tag Charts Builder

`lastfm_tag_charts` builds a Plex music collection from Last.fm's top artists, albums, or tracks for a tag. It defaults to artist level. Set `builder_level: album` or `builder_level: track` for the other levels. It requires a [Last.fm connection](../../../config/lastfm.md).

```yaml title="Collection file"
collections:
  Top Dance Tracks:
    builder_level: track
    lastfm_tag_charts:
      tag: dance
      limit: 50
    collection_order: custom
    sync_mode: sync
```

You can use the tag name alone, such as `lastfm_tag_charts: dance`, or a dictionary with `tag` and `limit`. `limit` defaults to 50 and accepts 1–1000. A list of tags or dictionaries combines their results. `collection_order: custom` preserves the order returned by Last.fm. Kometa matches MusicBrainz IDs first, then unique names using the [shared music matching rules](user-top-tracks.md). Unmatched items use the usual missing artist, album, or track reporting.
