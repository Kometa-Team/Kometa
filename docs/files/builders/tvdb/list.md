---
hide:
  - toc
---
# TVDb List

Finds every item in a [TVDb List](https://www.thetvdb.com/lists) or [TVDb UserList](https://www.thetvdb.com/lists/custom)

The expected input is a TVDb List URL or TVDb UserList URL. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a 
comma-separated string.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

???+ tip "Details Builder"

    You can replace `tvdb_list` with `tvdb_list_details` if you would like to fetch and use the description from the list

### Example TVDb List Builder(s)

```yaml
collections:
  Arrowverse:
    tvdb_list: https://www.thetvdb.com/lists/arrowverse
    collection_order: custom
    sync_mode: sync
```
```yaml
collections:
  Saved by the Bell:
    tvdb_list: https://www.thetvdb.com/lists/6957
    collection_order: custom
    sync_mode: sync
```

* You can update the collection details with the TVDb list's description and poster by using `tvdb_list_details`.
* You can specify multiple lists in `tvdb_list_details` but it will only use the first one to update the collection details.

```yaml
collections:
  Arrowverse:
    tvdb_list_details: https://www.thetvdb.com/lists/arrowverse
    collection_order: custom
    sync_mode: sync
```
