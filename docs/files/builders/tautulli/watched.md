---
hide:
  - toc
---
# Tautulli Watched

| Attribute      | Description                                                |                 Required                 | Default |
|:---------------|:-----------------------------------------------------------|:----------------------------------------:|:-------:|
| `list_days`    | Number of Days to look back of the list.                   | :fontawesome-solid-circle-xmark:{ .red } |  `30`   |
| `list_minimum` | Minimum Number of Users Watching/Plays to add to the list. | :fontawesome-solid-circle-xmark:{ .red } |   `0`   |
| `list_size`    | Number of Movies/Shows to add to this list.                | :fontawesome-solid-circle-xmark:{ .red } |  `10`   |

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

???+ warning "Tautulli Configuration"
    
    [Configuring Tautulli](../../../config/tautulli.md) in the config is required for any of these builders.

### Example Tautulli Watched Builder(s)

```yaml
collections:
  Most Watched Movies (30 Days):
    sync_mode: sync
    collection_order: custom
    tautulli_watched:
      list_days: 30
      list_size: 10
```
```yaml
collections:
  Plex Popular:
    tautulli_popular:
      list_days: 30
      list_size: 20
    tautulli_watched:
      list_days: 30
      list_size: 20
    sync_mode: sync
    summary: Movies Popular on Plex
    collection_order: alpha
```

