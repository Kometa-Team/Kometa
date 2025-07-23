---
hide:
  - toc
---
# MyAnimeList ID

Gets the anime specified by the MyAnimeList ID.

The expected input is a MyAnimeList ID. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

???+ warning "MyAnimeList Configuration"

    [Configuring MyAnimeList](../../../config/myanimelist.md) in the config is required for any of these builders to function.

### Example MyAnimeList ID Builder(s)

```yaml
collections:
  Cowboy Bebop:
    mal_id: 23, 219
```
