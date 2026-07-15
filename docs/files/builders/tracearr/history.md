---
hide:
  - toc
---
# Tracearr History

The Tracearr builders below all derive from the `/api/v1/public/history` endpoint and use its pagination and filtering support.

| Builder | Description |
|:--------|:------------|
| `tracearr_popular`  | Gets items watched by the most unique Tracearr users. |
| `tracearr_watched`  | Gets items with the most completed Tracearr sessions. |
| `tracearr_trending` | Gets the most active items from recent Tracearr watch history. |
| `tracearr_rewatched` | Gets items repeatedly played by the same Tracearr user. |
| `tracearr_completed` | Gets the most recently completed items from the Tracearr watch history feed. |
| `tracearr_binged`    | Gets shows ranked by distinct completed episodes watched by a single Tracearr user. |
| `tracearr_transcoded` | Gets items ranked by Tracearr sessions that required audio or video transcoding. |
| `tracearr_history`   | Gets every movie/show in the Tracearr watch history feed. |

| Attribute      | Description                                                 |                 Required                 | Default |
|:---------------|:------------------------------------------------------------|:----------------------------------------:|:-------:|
| `list_days`    | Number of days to look back in the history.                              | :fontawesome-solid-circle-xmark:{ .red } | `30` |
| `list_minimum` | Minimum activity count required. This is unique users for `popular`, completed sessions for `watched`/`completed`, repeat plays beyond a user's first play for `rewatched`, distinct completed episodes watched by one user for `binged`, transcode sessions for `transcoded`, and total sessions for the other builders. | :fontawesome-solid-circle-xmark:{ .red } | `0`  |
| `list_size`    | Number of Movies/Shows to add to this list.                              | :fontawesome-solid-circle-xmark:{ .red } | `10` |

The `sync_mode: sync` and `collection_order: custom` settings are recommended since the list is continuously updated.

Tracearr playlist builders can combine movie and show libraries from the same Plex server. A single playlist definition cannot combine Tracearr history from multiple Plex servers.

`tracearr_binged` requires at least two distinct completed episodes and works with Show libraries. In playlists, it returns shows only.

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
  Tracearr Popular:
    sync_mode: sync
    collection_order: custom
    tracearr_popular:
      list_days: 30
      list_size: 10
```
