---
hide:
  - toc
---
# IMDb List

???+ danger "Important Notice"

    Due to recent changes in IMDb's code, `imdb_list` can no longer be used for any url which starts with 
    `https://www.imdb.com/search/` or `https://www.imdb.com/filmosearch/`.

    These must instead use the [IMDb Search Builder](#imdb-search)


Finds every item in an IMDb List.

| List Parameter | Description                                                                                                                                                                                                                                                                                                                                   |
|:---------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `list_id`      | Specify the IMDb List ID. **This attribute is required.**<br>**Options:** The ID that starts with `ls` found in the URL of the list. (ex. `ls005526372`)                                                                                                                                                                                      |
| `limit`        | Specify how items you want returned by the query.<br>**Options:** Any Integer `0` or greater where `0` get all items.<br>**Default:** `0`                                                                                                                                                                                                     |
| `sort_by`      | Choose from one of the many available sort options.<br>**Options:** `custom.asc`, `custom.desc`, `title.asc`, `title.desc`, `rating.asc`, `rating.desc`, `popularity.asc`, `popularity.desc`, `votes.asc`, `votes.desc`, `release.asc`, `release.desc`, `runtime.asc`, `runtime.desc`, `added.asc`, `added.desc`<br>**Default:** `custom.asc` |

Multiple values are supported as a list only a comma-separated string will not work.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

### Example IMDb List Builder(s)

```yaml
collections:
  James Bonds:
    imdb_list: 
      list_id: ls006405458
      limit: 100
      sort_by: rating.asc
    collection_order: custom
    sync_mode: sync
```

You can search multiple lists in one collection by using a list.

```yaml
collections:
  Christmas:
    imdb_list:
      - list_id: ls025976544
        limit: 10
        sort_by: rating.asc
      - list_id: ls003863000
        limit: 10
        sort_by: rating.asc
      - list_id: ls027454200
        limit: 10
        sort_by: rating.asc
      - list_id: ls027886673
        limit: 10
        sort_by: rating.asc
      - list_id: ls097998599
        limit: 10
        sort_by: rating.asc
    sync_mode: sync
    collection_order: alpha
```