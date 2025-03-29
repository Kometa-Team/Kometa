---
hide:
  - toc
---
# ICheckMovies Builders

You can find items using the lists on [ICheckMovies.com](https://www.icheckmovies.com/) (ICheckMovies). 

| Builder                                   | Description                                |             Works with Movies              |             Works with Shows             |    Works with Playlists and Custom Sort    |
|:------------------------------------------|:-------------------------------------------|:------------------------------------------:|:----------------------------------------:|:------------------------------------------:|
| [`icheckmovies_list`](#icheckmovies-list) | Finds every movie in the ICheckMovies List | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |

## ICheckMovies List

Finds every movie in the ICheckMovies List.

The expected input is a ICheckMovies List URL. Multiple values are supported as either a list or a comma-separated string.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

???+ tip "Details Builder"

    You can replace `icheckmovies_list` with `icheckmovies_list_details` if you would like to fetch and use the description from the list

### Example ICheckMovies List Builder(s)

```yaml
collections:
  Vulture’s 101 Best Movie Endings:
    icheckmovies_list: https://www.icheckmovies.com/lists/academy+award+-+best+picture
    collection_order: custom
    sync_mode: sync
```

* You can update the collection details with the ICheckMovies List's description by using `icheckmovies_list_details`.
* You can specify multiple collections in `icheckmovies_list_details` but it will only use the first one to update the collection summary.

```yaml
collections:
  Vulture’s 101 Best Movie Endings:
    icheckmovies_list_details: https://www.icheckmovies.com/lists/academy+award+-+best+picture
    collection_order: custom
    sync_mode: sync
```
