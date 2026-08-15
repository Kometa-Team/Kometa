---
hide:
  - toc
---

# Plex ID

The `plex_id` builder finds items already in Plex using their Plex metadata ID. It accepts a single ID or a list of IDs. Each value can be either a bare 24-character metadata ID or a complete `plex://` GUID.

```yaml
collections:
  Selected Plex Movies:
    plex_id:
      - 5d7768243c3c2a001fbca85b
      - plex://movie/5d776824880197001ec901ab
```

For show-part collections, episode GUIDs such as `plex://episode/63e3eedd166819851638a317` are also supported. Values that do not exist in the configured library are skipped with a warning.

This builder does not guarantee that the resulting collection follows the order of the configured IDs.
