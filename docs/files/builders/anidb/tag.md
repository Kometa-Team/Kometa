---
hide:
  - toc
---
# AniDB Tag

Finds anime with a specific AniDB tag ID.

The expected input is an AniDB tag ID with an optional `limit` parameter.

You can find tag IDs by browsing tags at [https://utilities.kometa.wiki/tags](https://utilities.kometa.wiki/tags).

### Example AniDB Tag Builder(s)

```yaml
collections:
  Military Anime:
    anidb_tag: 36
    collection_order: custom
    sync_mode: sync
```
```yaml
collections:
  Top 10 Military Anime:
    anidb_tag:
      tag_id: 36
      limit: 10
    collection_order: custom
    sync_mode: sync
```
```yaml
collections:
  Future Setting:
    anidb_tag:
      tag_id: 2626
      limit: 50
    collection_order: custom
    sync_mode: sync
```

### Tag ID Examples

| Tag Name | Tag ID |
|:---------|-------:|
| Military | 36     |
| Future   | 2626   |
| Comedy   | 2853   |
| Action   | 2604   |
| Fantasy  | 2849   |
| Sci-Fi   | 2846   |

## Attributes

| Attribute | Description                                          | Required |
|:----------|:-----------------------------------------------------|:--------:|
| `tag_id`  | AniDB Tag ID                                         | Yes      |
| `limit`   | Maximum number of anime to return (default: 1000)    | No       |

**Note:** The `mature` setting from your AniDB configuration controls whether mature/adult anime are included in the results.
