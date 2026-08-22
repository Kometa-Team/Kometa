---
hide:
  - toc
---
# FlickList Personal Data

Finds items from the configured FlickList API key's own watchlist, favorites, watched history, up-next queue,
or tracked shows.

???+ warning "FlickList Configuration"

    [Configuring FlickList](../../../config/flicklist.md) in the config is required for these builders. Each
    of these builders reads the `read`-scoped personal data of whichever FlickList account the configured
    `api_key` belongs to.

Each of these builders accepts a blank value or `true`:

```yaml
collections:
  FlickList Watchlist:
    flicklist_watchlist:
    collection_order: custom
    sync_mode: sync

  FlickList Favorites:
    flicklist_favorites: true
    collection_order: custom
    sync_mode: sync

  FlickList Watched:
    flicklist_watched:
    sync_mode: sync

  FlickList Tracked:
    flicklist_tracked:
    collection_order: custom
    sync_mode: sync
```

`flicklist_up_next` and `flicklist_tracked` are show-library only, since a next-unwatched-episode queue and a
tracked-shows list are both inherently show concepts.

`flicklist_up_next` additionally accepts an integer limit on how many upcoming episodes to return:

```yaml
collections:
  FlickList Up Next:
    flicklist_up_next: 20
    collection_order: custom
    sync_mode: sync
```

| Builder               | Blank/`true` means     | Also accepts  | Library restriction |
|:----------------------|:-----------------------|:--------------|:--------------------|
| `flicklist_watchlist` | Entire watchlist       | —             | Movies and Shows    |
| `flicklist_favorites` | Entire favorites list  | —             | Movies and Shows    |
| `flicklist_watched`   | Entire watched history | —             | Movies and Shows    |
| `flicklist_up_next`   | All up-next episodes   | Integer limit | Shows only          |
| `flicklist_tracked`   | Every tracked show     | —             | Shows only          |
