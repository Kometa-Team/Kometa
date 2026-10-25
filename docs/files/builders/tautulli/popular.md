---
hide:
  - toc
---
# Tautulli Popular

| Attribute      | Description                                                |                 Required                 | Default |
|:---------------|:-----------------------------------------------------------|:----------------------------------------:|:-------:|
| `list_days`    | Number of Days to look back of the list.                   | :fontawesome-solid-circle-xmark:{ .red } |  `30`   |
| `list_minimum` | Minimum Number of Users Watching/Plays to add to the list. | :fontawesome-solid-circle-xmark:{ .red } |   `0`   |
| `list_size`    | Number of items to add to this list.                       | :fontawesome-solid-circle-xmark:{ .red } |  `10`   |
| `list_buffer`  | Additional items to request when filtering movie/show results (older Tautulli versions only). | :fontawesome-solid-circle-xmark:{ .red } | `list_size * 3` |

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

???+ warning "Tautulli Configuration"
    
    [Configuring Tautulli](../../../config/tautulli.md) in the config is required for any of these builders.

### Example Tautulli Popular Builder(s)

```yaml
collections:
  Most Popular Movies (30 Days):
    sync_mode: sync
    collection_order: custom
    tautulli_popular:
      list_days: 30
      list_size: 10
```
```yaml
collections:
  Plex Popular:
    tautulli_popular:
      list_days: 30
      list_size: 20
    tautulli_top:
      list_days: 30
      list_size: 20
    sync_mode: sync
    summary: Movies Popular on Plex
    collection_order: alpha
```
```yaml
playlists:
  Plex Popular:
    libraries: Movies
    tautulli_popular:
      list_days: 30
      list_size: 20
    sync_mode: sync
    summary: Movies Popular on Plex
```

## Music

On a music library, `tautulli_popular` uses Tautulli's Popular Music list. Set `builder_level` to `artist`, `album`, or `track` to choose the output level. It defaults to `artist`. Artist and album results aggregate Tautulli's music stats; track results count distinct listeners from Tautulli history within `list_days`. `list_minimum` is the minimum listener count for the selected item.

```yaml
collections:
  Popular Music Tracks:
    builder_level: track
    tautulli_popular:
      list_days: 30
      list_size: 20
      list_minimum: 1
    sync_mode: sync
    collection_order: custom
```
