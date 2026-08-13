---
hide:
  - toc
---

# Plex Rating Key

The `plex_rating_key` builder finds items already in Plex using their numeric Plex rating key. It accepts a single rating key or a list.

```yaml
collections:
  Selected Plex Movies:
    plex_rating_key:
      - 123
      - 456
```

Rating keys are local to a Plex server and can change if a library is rebuilt. Use [`plex_id`](id.md) when a stable Plex metadata identifier is available.

This builder does not guarantee that the resulting collection follows the order of the configured rating keys.
