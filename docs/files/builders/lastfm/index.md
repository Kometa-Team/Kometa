# Last.fm Builders

Collect artists, albums, and tracks from Last.fm charts, tags, and listening history.

!!! warning "Configure Last.fm first"

    These builders use a Plex Music library and require the
    [Last.fm service connection](../../../config/lastfm.md). Public user charts
    do not require that user's account login.

## Choose a builder

| Builder | Finds | Default collection level |
|:--------|:------|:-------------------------|
| [`lastfm_chart_top_artists`](#lastfm-global-charts-builders) | Global top artists | Artist |
| [`lastfm_chart_top_tracks`](#lastfm-global-charts-builders) | Global top tracks | Track |
| [`lastfm_tag_charts`](#lastfm-tag-charts-builder) | Top items for a tag | Artist; album or track supported |
| [`lastfm_user_tags`](#lastfm-user-tags-builder) | Items personally tagged by a user | Artist; album or track supported |
| [`lastfm_user_top_artists`](#lastfm-user-top-artists-builder) | A user's most-played artists | Artist |
| [`lastfm_user_top_albums`](#lastfm-user-top-albums-builder) | A user's most-played albums | Album |
| [`lastfm_user_top_tracks`](#lastfm-user-top-tracks-builder) | A user's most-played tracks | Track |
| [`lastfm_user_loved_tracks`](#lastfm-user-loved-tracks-builder) | A user's loved tracks, newest loved first | Track |
| [`lastfm_user_recent_tracks`](#lastfm-user-recent-tracks-builder) | Completed scrobbles, newest play first | Track |

Use `collection_order: custom` to preserve the returned order after matching and
`sync_mode: sync` to keep membership synchronized. A collection contains one music
level; set `builder_level: album` or `builder_level: track` for tag builders when
needed. Those levels are already the defaults for album- and track-specific builders.

## Shared options

| Option | Applies to | Value / default |
|:-------|:-----------|:----------------|
| `limit` | All builders | Integer, 1-1000; tag and user builders default to `50` |
| `username` | User builders | Last.fm username string |
| `period` | User top artists, albums, tracks | `overall`, `7day`, `1month`, `3month`, `6month`, `12month`; default `overall` |

Username-only forms for user top charts, loved tracks, and recent tracks use
50 results. User top charts also accept lists of usernames or dictionaries to
combine charts. Replace placeholder usernames in the examples with real usernames.

## Global charts {#lastfm-global-charts-builders}

Pass a result limit directly, or as `limit` in a dictionary. This example selects
up to 50 global top tracks; `50` is an integer count. Use
`lastfm_chart_top_artists` to select artists instead, or dictionary form such as
`lastfm_chart_top_tracks: {limit: 50}`.

```yaml
collections:
  Global Top Tracks:
    lastfm_chart_top_tracks: 50
    collection_order: custom
    sync_mode: sync
```

!!! note "API charts differ from the website"

    These builders use `chart.getTopArtists` and `chart.getTopTracks`. Rankings
    may differ from the live [Last.fm charts page](https://www.last.fm/charts).
    That page's Top New Releases and Most Loved sections have no documented
    API chart methods and are not available through these builders.

## Tag charts {#lastfm-tag-charts-builder}

`lastfm_tag_charts` accepts a tag string, such as `dance`, or a dictionary with
`tag` and optional `limit`. A YAML list of tags or dictionaries combines results.

This example selects up to 50 Dance tracks. `builder_level: track` changes the
default artist level, while `tag: dance` is the source tag string.

```yaml
collections:
  Top Dance Tracks:
    builder_level: track
    lastfm_tag_charts:
      tag: dance
      limit: 50
    collection_order: custom
    sync_mode: sync
```

## Personal tags {#lastfm-user-tags-builder}

`lastfm_user_tags` requires both `username` and `tag`, with an optional `limit`.
A YAML list of user/tag dictionaries combines sources.

Selects up to 50 albums this user has personally tagged `favourites`. This uses
personal tags, rather than the global top chart for that tag. The collection's
album level determines which type of tagged item Last.fm is asked for.

```yaml
collections:
  My Tagged Albums:
    builder_level: album
    lastfm_user_tags:
      username: YOUR_LASTFM_USERNAME
      tag: favourites
      limit: 50
    sync_mode: sync
```

## User top charts

<span id="lastfm-user-top-artists-builder"></span>
<span id="lastfm-user-top-albums-builder"></span>
<span id="lastfm-user-top-tracks-builder"></span>

Use `lastfm_user_top_artists`, `lastfm_user_top_albums`, or `lastfm_user_top_tracks`
with a username or a dictionary of `username`, `period`, and `limit`.
A username alone selects the overall top 50 at the corresponding music level.

=== "Period and album level"

    Selects up to 50 of the user's most-played albums over the last month.
    `1month` is a period string and `50` is an integer count. Album level is
    automatic for this builder; `builder_level: album` is optional.

    ```yaml
    collections:
      My Monthly Top Albums:
        lastfm_user_top_albums:
          username: YOUR_LASTFM_USERNAME
          period: 1month
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```

=== "Track level"

    Selects up to 50 of the user's all-time most-played tracks. The track-level
    default means this selects recordings rather than artists or whole albums.

    ```yaml
    collections:
      My Most Played Tracks:
        lastfm_user_top_tracks:
          username: YOUR_LASTFM_USERNAME
          period: overall
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiple artist charts"

    Combines two users' top artists. Artists retain their chart order within
    each source, with duplicates kept only at their first position. Replace both
    usernames; each dictionary sets its own time period and limit.

    ```yaml
    collections:
      Friends' Top Artists:
        lastfm_user_top_artists:
          - username: FIRST_LASTFM_USERNAME
            period: 1month
            limit: 25
          - username: SECOND_LASTFM_USERNAME
            period: overall
            limit: 25
        collection_order: custom
        sync_mode: sync
    ```

## Loved tracks {#lastfm-user-loved-tracks-builder}

Accepts a username or a dictionary with `username` and `limit`. This selects
up to 50 loved-track results, newest loved first. The limit is counted before
duplicate tracks are removed, so the resulting collection may contain fewer tracks.

```yaml
collections:
  My Loved Tracks:
    lastfm_user_loved_tracks:
      username: YOUR_LASTFM_USERNAME
      limit: 50
    collection_order: custom
    sync_mode: sync
```

## Recent tracks {#lastfm-user-recent-tracks-builder}

Accepts a username or a dictionary with `username`, `limit`, and optional time bounds.
Currently playing tracks are excluded. The limit counts completed scrobbles before
deduplication; the remaining tracks retain newest-play-first order.

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `from` | Unix timestamp in seconds, UTC | Start of play-time range |
| `to` | Unix timestamp in seconds, UTC | End of range; must not be earlier than `from` |

This example selects up to 50 scrobbles from January 2024 using numeric UTC
Unix timestamps, rather than date strings. Duplicates are removed after selection.

```yaml
collections:
  Tracks Played in January 2024:
    lastfm_user_recent_tracks:
      username: YOUR_LASTFM_USERNAME
      from: 1704067200
      to: 1706745599
      limit: 50
    collection_order: custom
    sync_mode: sync
```

## Matching and missing items

Kometa tries MusicBrainz IDs first, then accepts unique name-based matches.
Comparisons ignore case and treat typographic dashes like regular hyphens.

| Level | Matching sequence |
|:------|:------------------|
| Artist | Valid MusicBrainz artist ID against Plex `mbid://` GUID, then a unique artist name |
| Album | MusicBrainz album ID against Plex album GUIDs, then a unique artist and album title |
| Track | MusicBrainz track ID against Plex track GUIDs, then a unique artist/title match with duration within two seconds, then a unique artist/album/title match |

Artist matching does not require Lidarr. Fetching artist MusicBrainz IDs may
require a separate API call per chart artist, so large limits take longer.
Album name fallback also handles Last.fm release IDs versus Plex release-group IDs.
Tag builders use these same music matching rules.

!!! warning "Track versions can be uncertain"

    Last.fm supplies at most one album per track, even if it appears on several
    releases; that album may be absent or differ from Plex. Top-track chart
    responses contain neither album nor duration, and track details may omit
    either. Loved tracks can also lack an ID or album. Recent tracks use the
    album recorded with the scrobble after ID and duration matching.
    Even a unique match can be the wrong version when recordings share names
    and lengths. Review results when the exact recording matters.

Ambiguous matches and items without enough information are skipped. With
`show_missing`, unmatched items appear under **Missing Artists from Library**,
**Missing Albums from Library**, or **Missing Tracks from Library**. With
`save_report`, the library report includes missing artists with available
MusicBrainz IDs, **Albums Missing**, and **Tracks Missing**. Ambiguous name matches
are also marked in the log.
