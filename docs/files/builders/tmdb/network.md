---
hide:
  - toc
---
# TMDb Network

Finds every item from the TMDb network's movie/show list.

This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

### Example TMDb Network Builder(s)

```yaml
collections:
  CBS:
    tmdb_network: 16 #(1)!
```

1.  https://www.themoviedb.org/network/16 also accepted
