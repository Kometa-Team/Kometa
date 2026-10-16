---
hide:
  - toc
---
# Tautulli Builders

You can find items in your Plex using the features of [Tautulli](https://tautulli.com/).

Tautulli builders use its popular and most-played lists. `tautulli_popular` gets popular items and `tautulli_top` gets the most-played items across movies, shows, and music. For music libraries, set `builder_level` to choose artists, albums, or tracks. `tautulli_watched` remains available as an alias for `tautulli_top`.

???+ warning "Tautulli Configuration"
    
    [Configuring Tautulli](../../../config/tautulli.md) in the config is required for any of these builders.

| Builder                                         | Description                                       |             Works with Movies              |              Works with Shows              |              Works with Music              |    Works with Playlists and Custom Sort    |
|:------------------------------------------------|:--------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`tautulli_popular`](popular.md)                | Gets the Tautulli Most Popular List               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tautulli_top`](top.md)                        | Gets the Tautulli Top List                       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
