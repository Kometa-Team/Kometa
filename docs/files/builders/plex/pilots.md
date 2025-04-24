---
hide:
  - toc
---
# Plex Pilots

Gets the first episode of every show in your library. This only works with `builder_level: episode`

{%
    include-markdown "./sort-options.md"
%}

### Example Plex Pilots Builder(s)

```yaml
collections:
  Pilots:
    builder_level: episode
    plex_pilots: true
```