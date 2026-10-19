---
hide:
  - toc
---
# Tautulli Top

???+ tip "Tautulli Watched"

    This builder was previously `tautulli_watched` but has been renamed due to supporting Music libraries

| Attribute      | Description                                                |                 Required                 | Default |
|:---------------|:-----------------------------------------------------------|:----------------------------------------:|:-------:|
| `list_days`    | Number of Days to look back of the list.                   | :fontawesome-solid-circle-xmark:{ .red } |  `30`   |
| `list_minimum` | Minimum Number of Users Watching/Plays to add to the list. | :fontawesome-solid-circle-xmark:{ .red } |   `0`   |
| `list_size`    | Number of items to add to this list.                       | :fontawesome-solid-circle-xmark:{ .red } |  `10`   |
| `list_buffer`  | Additional items to request when filtering results (older Tautulli versions only). | :fontawesome-solid-circle-xmark:{ .red } | `list_size * 3` |

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

???+ warning "Tautulli Configuration"
    
    [Configuring Tautulli](../../../config/tautulli.md) in the config is required for any of these builders.

`tautulli_watched` is accepted as a backward-compatible alias for `tautulli_top`.

On music libraries, set `builder_level` to `artist`, `album`, or `track` to choose results from Tautulli's Top Music list. The default is `album`. Artist and album results aggregate Tautulli's music stats; track results count plays from Tautulli history within `list_days`. `list_minimum` is the minimum play count for the selected item.

### Example Tautulli Top Builder(s)

```yaml
collections:
  Most Watched Movies (30 Days):
    sync_mode: sync
    collection_order: custom
    tautulli_top:
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
collections:
  Top Music Albums:
    builder_level: album
    tautulli_top:
      list_days: 90
      list_size: 15
      list_minimum: 2
    sync_mode: sync
    collection_order: custom
```
