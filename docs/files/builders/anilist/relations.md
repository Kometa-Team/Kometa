---
hide:
  - toc
---
# AniList Relations

Finds the anime specified by the AniList ID and every relation in its relation tree except Character and Other relations.

The expected input is an AniList ID. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

### Example AniList Relations Builder(s)

```yaml
collections:
  One Piece:
    anilist_relations: 21
```