---
hide:
  - toc
---
# Listrr Builders

You can find every movie or show currently in a [Listrr](https://listrr.pro/) list.

???+ warning "Listrr Configuration"

    [Configuring Listrr](../../../config/listrr.md) in the config is required for these builders.

| Builder | Description | Works with Movies | Works with Shows | Works with Playlists and Custom Sort |
|:--------|:------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`listrr_list`](list.md) | Finds every item in a Listrr list. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`listrr_list_details`](list.md) | Same items as `listrr_list`, and stores the list description as the summary. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

A Listrr list is either movies or shows. A movie list on a show library fails, and a show list on a movie library fails. A playlist accepts either kind of list and keeps that list's ids. One Listrr list is never a mix of movies and shows.

There are no episode ids in this API, so these builders are not available on an episode collection.
