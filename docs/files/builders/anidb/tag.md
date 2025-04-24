---
hide:
  - toc
---
# AniDB Tag

Finds anime with the specified AniDB Tag the options are detailed below. 

| Attribute | Description                                                   |                  Required                  | Default |
|:----------|:--------------------------------------------------------------|:------------------------------------------:|:-------:|
| `tag`     | AniDB Tag ID to search by                                     | :fontawesome-solid-circle-check:{ .green } |   N/A   |
| `limit`   | Number of Anime to query from AniDB (use 0 for all; max: 500) |  :fontawesome-solid-circle-xmark:{ .red }  |    0    |

### Example AniDB Tag Builder(s)

```yaml
collections:
  Pirates Anime:
    anidb_tag:
      tag: 1700
      limit: 500
    sync_mode: sync
```

To find a list of AniDB tags, go to the [AniDB Anime](https://anidb.net/tag) page. On the tag you want, copy the link and find the tag ID at the end of the url.
