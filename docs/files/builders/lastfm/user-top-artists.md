# Last.fm User Top Artists Builder

`lastfm_user_top_artists` creates an artist collection in a Plex music library from a Last.fm user's most-played artists. It requires a [Last.fm connection](../../../config/lastfm.md). The Last.fm account can be public; no account login is required.

```yaml title="Collection file"
collections:
  My Most Played Artists:
    lastfm_user_top_artists:
      username: YOUR_LASTFM_USERNAME
      period: 1month
      limit: 50
    collection_order: custom
```

A username alone selects the overall top 50 artists. You can also provide a list of usernames or dictionaries to combine charts.

Set `collection_order: custom` to keep the Last.fm ranking in the Plex collection. If multiple charts are provided, artists appear in chart order for each chart, with duplicates included only at their first position.

| Option | Description | Default |
| --- | --- | --- |
| `username` | Last.fm username. | Required |
| `period` | `overall`, `7day`, `1month`, `3month`, `6month`, or `12month`. | `overall` |
| `limit` | Maximum artists from the chart, from 1 to 1000. | `50` |

Kometa first matches a valid MusicBrainz artist ID from Last.fm to the artist's `mbid://` Plex GUID. If the ID has no Plex match or Last.fm supplies no valid ID, it accepts a unique artist-name match, ignoring case and typographic dash differences. Ambiguous matches are skipped. Matching does not require Lidarr. Retrieving MusicBrainz IDs can require a separate Last.fm API call for each chart artist, so large limits take longer.

Unmatched artists appear together under **Missing Artists from Library** when `show_missing` is enabled. With `save_report`, Kometa saves their names and available MusicBrainz IDs in the library report, like missing movies and shows. Ambiguous Plex name matches are marked in the log and skipped.
