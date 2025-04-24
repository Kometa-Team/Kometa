---
hide:
  - toc
---
# Plex All

Finds every item in your library. Useful with [Filters](../filters.md).

The expected input is either true or false.

{%
    include-markdown "./sort-options.md"
%}

### Example Plex All Builder(s)

```yaml
collections:
  9.0 Movies:
    plex_all: true
    filters:
      user_rating.gte: 9
```