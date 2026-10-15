# Last.fm Global Charts Builders

`lastfm_chart_top_artists` and `lastfm_chart_top_tracks` use Last.fm's documented global chart API methods. They require a [Last.fm connection](../../../config/lastfm.md) and default to artist- and track-level collections respectively.

```yaml title="Collection file"
collections:
  Global Top Artists:
    lastfm_chart_top_artists: 50
    collection_order: custom
    sync_mode: sync
  Global Top Tracks:
    lastfm_chart_top_tracks:
      limit: 50
    collection_order: custom
    sync_mode: sync
```

The value is a result limit from 1 through 1000, either directly or as `limit` in a dictionary. `collection_order: custom` preserves order after matching to Plex. Artists use MusicBrainz IDs and unique name matching. Tracks use the [track matching hierarchy](user-top-tracks.md), including its uncertainty around track versions. Missing items use the usual music reports.

???+ note "API charts and the website"

    These builders use `chart.getTopArtists` and `chart.getTopTracks`. Their rankings may differ from the live [Last.fm charts page](https://www.last.fm/charts). Last.fm does not document API chart methods for that page's **Top New Releases** or **Most Loved** sections, so those sections are not available through these builders.
