---
hide:
  - toc
---
# TMDb Company

Finds every movie from the TMDb company's movie list.

This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

### Example TMDb Company Builder(s)

```yaml
collections:
  Studio Ghibli:
    tmdb_company: 10342 #(1)!
```

1. https://www.themoviedb.org/company/10342 also accepted
