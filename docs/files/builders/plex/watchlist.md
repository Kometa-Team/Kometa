---
hide:
  - toc
---
# Plex Watchlist

Finds every item in your Watchlist.

The expected input is the sort you want returned. It defaults to `added.asc`.

## Watchlist Sort Options

| Sort Option                                 | Description                                 |
|:--------------------------------------------|:--------------------------------------------|
| `title.asc`<br>`title.desc`                 | Sort by Title                               |
| `release.asc`<br>`release.desc`             | Sort by Release Date (Originally Available) |
| `critic_rating.asc`<br>`critic_rating.desc` | Sort by Critic Rating                       |
| `added.asc`<br>`added.desc`                 | Sort by Date Added to your Watchlist        |

The `sync_mode: sync` and `collection_order: custom` Setting are recommended.

### Example Plex Watchlist Builder(s)

```yaml
collections:
  My Watchlist:
    plex_watchlist: critic_rating.desc
    collection_order: custom
    sync_mode: sync
```