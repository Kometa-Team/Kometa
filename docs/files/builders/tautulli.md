# Tautulli Builders

You can find items in your Plex using the features of [Tautulli](https://tautulli.com/).

[Configuring Tautulli](../../config/tautulli.md) in the config is required for any of these builders.

It has watch analytics that can show the most watched or most popular Movies/Shows in each Library.

| Attribute                                      | Description                         |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:-----------------------------------------------|:------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`tautulli_popular`](#tautulli-popularwatched) | Gets the Tautulli Most Popular List | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tautulli_watched`](#tautulli-popularwatched) | Gets the Tautulli Most Watched List | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

## Tautulli Popular/Watched

Both Tautulli Popular and Tautulli Watched have the same sub-attributes detailed below.

| Attribute      | Description                                                |                 Required                 | Default |
|:---------------|:-----------------------------------------------------------|:----------------------------------------:|:-------:|
| `list_days`    | Number of Days to look back of the list.                   | :fontawesome-solid-circle-xmark:{ .red } |  `30`   |
| `list_minimum` | Minimum Number of Users Watching/Plays to add to the list. | :fontawesome-solid-circle-xmark:{ .red } |   `0`   |
| `list_size`    | Number of Movies/Shows to add to this list.                | :fontawesome-solid-circle-xmark:{ .red } |  `10`   |

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

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
