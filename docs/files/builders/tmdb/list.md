---
hide:
  - toc
---
# TMDb List

Finds every item in the TMDb List.

This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

### Example TMDb List Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  Top 50 Grossing Films of All Time (Worldwide):
    tmdb_list: 10 #(1)!
    collection_order: custom
    sync_mode: sync
  Marvel & DC Universes:
    tmdb_list_details: #(2)!
      - 1 #(3)!
      - 3
    collection_order: custom
    sync_mode: sync
```

1. https://www.themoviedb.org/list/10 also accepted
2. You can replace `tmdb_list` with `tmdb_list_details` if you would like to fetch and use the TMDb collection's summary, poster, and background from the list
3. You can specify multiple lists in `tmdb_list_details` but it will only use the first one to update the collection details
