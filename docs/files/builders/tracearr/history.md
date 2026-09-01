---
hide:
  - toc
---
# Tracearr History

The Tracearr builders below use the Public API history endpoints and their pagination and filtering support. Kometa prefers `/api/v2/public/history` and automatically falls back to `/api/v1/public/history` when v2 is unavailable.

| Builder | Description |
|:--------|:------------|
| `tracearr_popular`  | Gets items watched by the most unique Tracearr users. |
| `tracearr_watched`  | Gets items with the most completed Tracearr sessions. |
| `tracearr_trending` | Gets the most active items from recent Tracearr watch history. |
| `tracearr_rewatched` | Gets items repeatedly played by the same Tracearr user. |
| `tracearr_completed` | Gets the most recently completed items from the Tracearr watch history feed. |
| `tracearr_binged`    | Gets shows ranked by distinct completed episodes watched by a single Tracearr user. |
| `tracearr_transcoded` | Gets items ranked by Tracearr sessions that required audio or video transcoding. |
| `tracearr_watch_time` | Gets items ranked by total time watched. |
| `tracearr_in_progress` | Gets a user's most recently played unfinished movies and exact episodes. This builder is playlist-only and requires Tracearr v2 and `user`. |
| `tracearr_history`   | Gets every movie/show in the Tracearr watch history feed. |

| Attribute | Description | Required | Default |
|:----------|:------------|:--------:|:-------:|
| `list_days` | Number of days to look back in the history. | :fontawesome-solid-circle-xmark:{ .red } | `30` |
| `list_minimum` | Minimum activity required. This is unique users for `popular`; completed plays for `watched`/`completed`; repeat plays for `rewatched`; distinct completed episodes for `binged`; transcode plays for `transcoded`; total watched minutes for `watch_time`; and total plays for the other builders. | :fontawesome-solid-circle-xmark:{ .red } | `0` |
| `list_size` | Number of Movies/Shows to add to this list. | :fontawesome-solid-circle-xmark:{ .red } | `10` |
| `user` | Limits history to a Tracearr identity. Accepts the identity UUID, Tracearr username, Plex account ID, media-server user ID, or linked account username. Required by `tracearr_in_progress`. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `watched` | Filters plays by Tracearr's completed-watch state. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `minimum_progress` | Minimum play completion percentage from `0` through `100`. | :fontawesome-solid-circle-xmark:{ .red } | `1` for `in_progress` |
| `maximum_progress` | Maximum play completion percentage from `0` through `100`. | :fontawesome-solid-circle-xmark:{ .red } | `84` for `in_progress` |
| `transcode` | Filters plays by whether video or audio was transcoded. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `video_decision` | Filters video playback by `directplay`, `copy`, or `transcode`. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `audio_decision` | Filters audio playback by `directplay`, `copy`, or `transcode`. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `transcode_reason` | Case-insensitive text contained in one of Tracearr's transcode reasons. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `subtitle_decision` | Filters by the subtitle decision, such as `burn`. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `platform` | Filters by client platform. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `device` | Filters by playback device. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `resolution` | Filters by Tracearr's displayed source resolution, such as `4K`. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `source_video_codec` | Filters by source video codec, such as `hevc`. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `source_audio_codec` | Filters by source audio codec, such as `truehd`. | :fontawesome-solid-circle-xmark:{ .red } |  |
| `genre` | Filters by an exact, case-insensitive Tracearr genre. | :fontawesome-solid-circle-xmark:{ .red } |  |

The `sync_mode: sync` and `collection_order: custom` settings are recommended since the list is continuously updated.

Tracearr playlist builders can combine movie and show libraries from the same Plex server. A single playlist definition cannot combine Tracearr history from multiple Plex servers.

Kometa probes Tracearr's v2 Public API when connecting. When v2 is available, Kometa uses its history identity fields to match each play to its originating Plex library and exact Plex rating key. Movie playlists use the provider IDs supplied by Tracearr directly. Tracearr versions without v2 automatically use the v1 endpoint, and title/year matching is retained for older history records without library identity. Friendly cross-account user matching requires Tracearr v2; the other filters use whichever fields are available from the installed Tracearr version.

Identical history requests are reused during the same Kometa run, reducing repeated pagination and pressure on Tracearr's shared v2 API rate limit.

`tracearr_binged` requires at least two distinct completed episodes and works with Show libraries. In playlists, it returns shows only.

`tracearr_in_progress` requires Tracearr's v2 Public API. It examines the latest play for each movie or show so an older partial play is not returned after the user subsequently completed that item. Movies are matched by provider ID and shows add the exact unfinished episode using its Plex rating key. The builder is restricted to playlists to keep user-specific viewing activity out of shared Plex collections.

???+ warning "Tracearr Configuration"

    [Configuring Tracearr](../../../config/tracearr.md) in the config is required for this builder.

### Example Tracearr History Builder(s)

```yaml
collections:
  Tracearr History:
    sync_mode: sync
    collection_order: custom
    tracearr_history:
      list_days: 30
      list_size: 10
```

```yaml
collections:
  Most Watched by Time:
    sync_mode: sync
    collection_order: custom
    tracearr_watch_time:
      list_days: 30
      list_minimum: 60
      list_size: 20
      platform: Apple TV
```

```yaml
playlists:
  Continue Watching with Tracearr:
    sync_mode: sync
    collection_order: custom
    tracearr_in_progress:
      user: Anthony
      list_days: 30
      minimum_progress: 10
      maximum_progress: 84
      list_size: 20
```

```yaml
collections:
  Tracearr Popular:
    sync_mode: sync
    collection_order: custom
    tracearr_popular:
      list_days: 30
      list_size: 10
```
