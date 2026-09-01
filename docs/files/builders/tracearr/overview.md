---
hide:
  - toc
---
# Tracearr Builders

You can find items in your Plex using the watch history from your configured [Tracearr](https://docs.tracearr.com/) instance.

???+ warning "Tracearr Configuration"

    [Configuring Tracearr](../../../config/tracearr.md) in the config is required for any of these builders.

| Builder                           | Description                                                   |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:----------------------------------|:--------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`tracearr_popular`](history.md)   | Gets items watched by the most unique Tracearr users.               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_watched`](history.md)   | Gets items with the most completed Tracearr sessions.               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_trending`](history.md)  | Gets the most active items from recent Tracearr watch history.      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_rewatched`](history.md) | Gets items repeatedly played by the same Tracearr user.             | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_completed`](history.md) | Gets the most recently completed items from Tracearr history.       | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_binged`](history.md)    | Gets shows ranked by distinct completed episodes watched by one user. | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_transcoded`](history.md) | Gets items with the most sessions requiring transcoding.            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_watch_time`](history.md) | Gets items ranked by total time watched.                              | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_in_progress`](history.md) | Gets a user's unfinished movies and exact episodes.                   | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`tracearr_history`](history.md)   | Gets every movie/show in the Tracearr watch history feed.           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
