---
hide:
  - toc
---
# AniDB Tag Name

Finds anime with specific AniDB tag names. This builder supports multiple tags and searches by tag name (e.g., "action", "comedy") rather than tag ID.

The expected input is either a single tag name, a list of tag names, or a dictionary with `tags` and optional `min_weight` parameters.

Multiple tags can be specified to find anime that match all of the given tags. Tag names are case-insensitive.

### Example AniDB Tag Name Builder(s)

```yaml
collections:
  Action Anime:
    anidb_tag_name: action
    collection_order: custom
    sync_mode: sync
```
```yaml
collections:
  Action Comedy Anime:
    anidb_tag_name:
      - action
      - comedy
    collection_order: custom
    sync_mode: sync
```
```yaml
collections:
  High-Weight Action Anime:
    anidb_tag_name:
      tags: action
      min_weight: 300
    collection_order: custom
    sync_mode: sync
```
```yaml
collections:
  Action Comedy (High Weight):
    anidb_tag_name:
      tags:
        - action
        - comedy
      min_weight: 400
    collection_order: custom
    sync_mode: sync
```

### Tag Weight

Tag weights in AniDB indicate how strongly a tag applies to an anime:

- **600+**: Core theme/element
- **400-599**: Significant element
- **200-399**: Notable element  
- **0-199**: Minor element

Using `min_weight` filters results to only include anime where the tag(s) meet the minimum weight threshold.

### Common Tag Names

| Tag Name      | Description                      |
|:--------------|:---------------------------------|
| action        | Action-oriented content          |
| adventure     | Adventure themes                 |
| comedy        | Comedic content                  |
| drama         | Dramatic storytelling            |
| fantasy       | Fantasy settings/elements        |
| horror        | Horror themes                    |
| mecha         | Giant robots/mechanical themes   |
| military      | Military themes                  |
| mystery       | Mystery/detective themes         |
| romance       | Romantic relationships           |
| sci-fi        | Science fiction themes           |
| slice of life | Everyday life scenarios          |
| sports        | Sports-related content           |
| supernatural  | Supernatural elements            |
| thriller      | Thriller/suspense themes         |

## Attributes

| Attribute    | Description                                          | Required |
|:-------------|:-----------------------------------------------------|:--------:|
| `tags`       | Single tag name or list of tag names                 | Yes      |
| `min_weight` | Minimum tag weight (0-1000, default: 0)              | No       |

**Note:** The `mature` setting from your AniDB configuration controls whether mature/adult anime are included in the results.
