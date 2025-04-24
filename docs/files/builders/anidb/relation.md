---
hide:
  - toc
---
# AniDB Relation

Finds all anime in the relation graph of the specified AniDB ID.

To see the relation graph of an anime use: `https://anidb.net/anime/<ANIDB_ID>/relation/graph` but replace `<ANIDB_ID>` with the AniDB ID you want to see therelations for.

**Value:** The expected input is an AniDB ID, AniDB Anime URL, or AniDB Anime Relation URL. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

### Example AniDB Relation Builder(s)

```yaml
collections:
  All Sword Art Online:
    anidb_relation: 8692
```
```yaml
collections:
  All Sword Art Online:
    anidb_relation: https://anidb.net/anime/8692
```
```yaml
collections:
  All Sword Art Online:
    anidb_relation: https://anidb.net/anime/8692/relation/graph
```