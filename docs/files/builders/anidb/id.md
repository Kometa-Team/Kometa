---
hide:
  - toc
---
# AniDB ID

Finds the anime specified by the AniDB ID.

The expected input is an AniDB ID or AniDB Anime URL. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

### Example AniDB ID Builder(s)

```yaml
collections:
  Sword Art Online Shows:
    anidb_id: 8692, 8691, 13494
```
```yaml
collections:
  Sword Art Online Shows:
    anidb_id: 
     - 8692
     - 8691
     - 13494
```
```yaml
collections:
  Sword Art Online Shows:
    anidb_id: https://anidb.net/anime/8692, https://anidb.net/anime/8691, https://anidb.net/anime/13494
```