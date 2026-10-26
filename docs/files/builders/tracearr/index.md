# Tracearr Builders

Select library items from your [Tracearr](https://docs.tracearr.com/) watch history.
All builders support custom sorting and playlists; collection support varies below.

!!! warning "Configure Tracearr first"

    Every builder requires [Tracearr configuration](../../../config/tracearr.md).
    Playlists can combine movie and show libraries from one Plex server, but
    cannot combine Tracearr history from multiple Plex servers.

## Choose a builder

| Builder | Selects / ranks by | Collections |
|:--------|:------------------|:------------|
| `tracearr_popular` | Most unique users | Movies, shows |
| `tracearr_watched` | Most completed sessions | Movies, shows |
| [`tracearr_watched_media`](#tracearr-watched-media) | Distinct completed or partially watched media, recent first | Movies, shows, episodes |
| `tracearr_trending` | Recent activity | Movies, shows |
| `tracearr_rewatched` | Repeat plays by the same user | Movies, shows |
| `tracearr_completed` | Most recent completions | Movies, shows |
| `tracearr_binged` | Distinct completed episodes watched by one user | Shows only |
| `tracearr_transcoded` | Sessions requiring audio or video transcoding | Movies, shows |
| `tracearr_watch_time` | Total watched time | Movies, shows |
| [`tracearr_in_progress`](#continue-watching) | A user's unfinished movies and exact episodes | Playlist only |
| `tracearr_history` | Items in the watch-history feed | Movies, shows |

Use `collection_order: custom` to preserve returned order and `sync_mode: sync`
to keep membership synchronized on Kometa runs.

## History options {#tracearr-history}

These options apply to the history builders; `tracearr_watched_media` has its own
[options](#tracearr-watched-media). All are optional except `user` for
`tracearr_in_progress`.

### Activity and user

| Attribute | Value / purpose | Default |
|:----------|:----------------|:--------|
| `list_days` | Number of days to look back | `30` |
| `list_size` | Maximum items to add | `10` |
| `list_minimum` | Minimum activity, measured as below | `0` |
| `user` | Identity UUID, Tracearr username, Plex account ID, media-server user ID, or linked account username | No user filter |
| `watched` | Completed-watch state filter | No filter |
| `minimum_progress` | Completion percentage, 0-100 | `1` for in-progress |
| `maximum_progress` | Completion percentage, 0-100 | `84` for in-progress |

`list_minimum` counts unique users for popular, completed plays for watched and
completed, repeat plays for rewatched, distinct completed episodes for binged,
transcode plays for transcoded, and watched **minutes** for watch time. Other
history builders use total plays.

### Playback filters

Omit an attribute to leave it unfiltered.

| Attribute | Value / purpose |
|:----------|:----------------|
| `transcode` | Whether audio or video was transcoded |
| `video_decision`, `audio_decision` | `directplay`, `copy`, `transcode` |
| `transcode_reason` | Case-insensitive text contained in a transcode reason |
| `subtitle_decision` | Subtitle decision, such as `burn` |
| `platform` | Client platform, such as `Apple TV` |
| `device` | Playback device |
| `resolution` | Displayed source resolution, such as `4K` |
| `source_video_codec` | Source video codec, such as `hevc` |
| `source_audio_codec` | Source audio codec, such as `truehd` |
| `genre` | Exact, case-insensitive Tracearr genre |

### History examples {#tracearr-history-builders}

`tracearr_binged` requires at least two distinct completed episodes. In playlists,
it returns shows only.

<span id="example-tracearr-history-builders"></span>

=== "Popular items"

    Selects up to 10 items from the last 30 days, ranked by unique users. These
    numeric options control the lookback window and result count.

    ```yaml
    collections:
      Tracearr Popular:
        tracearr_popular:
          list_days: 30
          list_size: 10
        collection_order: custom
        sync_mode: sync
    ```

=== "Watched time and platform"

    Selects up to 20 items with at least 60 watched minutes over the last 30 days
    on Apple TV. Here `list_minimum` is minutes, not a play count; `platform` is
    a string filter. Results rank by total watched time.

    ```yaml
    collections:
      Most Watched on Apple TV:
        tracearr_watch_time:
          list_days: 30
          list_minimum: 60
          list_size: 20
          platform: Apple TV
        collection_order: custom
        sync_mode: sync
    ```

## Distinct watched media {#tracearr-watched-media}

`tracearr_watched_media` selects distinct media records, rather than a chart
ranked by completed sessions. It requires the watched-media capability available
in newer Tracearr v2 versions; early v2 versions may not provide it.

| Attribute | Purpose | Default |
|:----------|:--------|:--------|
| `list_size` | Maximum movies, shows, or episodes | `10` |
| `list_days` | Restrict to media whose last watched day is within this many days | All time |
| `user` | Same identity forms as history options | All users |
| `min_state` | `watched` for completed media; `partial` for both partial and complete | `watched` |

Results remain recent-first. With `builder_level: episode`, episodes can be
selected directly. Mixed movie/show playlists merge both types into one recent-first list.

=== "Completed media"

    Selects up to 100 distinct items completed by Anthony across all time.
    Replace the username with the Tracearr identity you want. This is not the
    most-played ranking returned by `tracearr_watched`.

    ```yaml
    collections:
      Watched by Anthony:
        tracearr_watched_media:
          user: Anthony
          min_state: watched
          list_size: 100
        collection_order: custom
        sync_mode: sync
    ```

=== "Partial or complete"

    Selects up to 50 distinct items active in the last 30 days, including both
    partially and completely watched items. `partial` is a minimum state string,
    not a request for unfinished items only.

    ```yaml
    collections:
      Recently Active Media:
        tracearr_watched_media:
          user: Anthony
          min_state: partial
          list_days: 30
          list_size: 50
        collection_order: custom
        sync_mode: sync
    ```

## Continue watching

!!! important "Playlist and user required"

    `tracearr_in_progress` requires Tracearr v2, a `user`, and a playlist definition.
    It is not supported in shared Plex collections.

The builder examines the latest play for each movie or show, so a later completion
supersedes an older partial play. Movies match by provider ID; shows add the exact
unfinished episode by Plex rating key.

This example selects up to 20 unfinished items for Anthony with 10-84 percent
completion in the last 30 days. The bounds are numeric percentages, not ratings.
Replace the user and library names with your own.

```yaml
playlists:
  Continue Watching with Tracearr:
    libraries: Movies, TV Shows
    tracearr_in_progress:
      user: Anthony
      list_days: 30
      minimum_progress: 10
      maximum_progress: 84
      list_size: 20
    collection_order: custom
    sync_mode: sync
```

## Matching and version support

History uses v2 when available and falls back to v1 otherwise. v2 can identify
the originating Plex library and exact rating key; older records without library
identity retain title/year matching. Friendly cross-account user matching requires
v2. Playback filters depend on fields supplied by your installed Tracearr version.

Watched-media matching uses TMDb or IMDb IDs for movies and TVDb, TMDb, or IMDb
IDs for shows. Episodes use the parent TVDb ID with season and episode numbers,
falling back to an episode IMDb ID. This builder requires its dedicated v2 capability.
