---
hide:
  - toc
---
# FlickList Builders

You can find items using lists and personal data from [FlickList](https://flicklist.tv/).

???+ warning "FlickList Configuration"

    [Configuring FlickList](../../../config/flicklist.md) in the config is required for any of these builders.

| Builder                              | Description                                                         | Works with Movies                          | Works with Shows                           | Works with Playlists and Custom Sort       |
|:-------------------------------------|:--------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`flicklist_list`](list.md)          | Finds every item in a FlickList list.                               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`flicklist_user_lists`](list.md)    | Finds every item across a FlickList user's public lists.            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`flicklist_watchlist`](personal.md) | Finds every item in the configured FlickList user's watchlist.      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`flicklist_favorites`](personal.md) | Finds every item in the configured FlickList user's favorites.      | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`flicklist_watched`](personal.md)   | Finds every item the configured FlickList user has watched.         | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`flicklist_up_next`](personal.md)   | Finds the configured FlickList user's next-unwatched-episode queue. | :fontawesome-solid-circle-xmark:{ .red }   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`flicklist_tracked`](personal.md)   | Finds shows the configured FlickList user is tracking.              | :fontawesome-solid-circle-xmark:{ .red }   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`flicklist_ratings`](ratings.md)    | Finds every item the configured FlickList user has rated.           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
