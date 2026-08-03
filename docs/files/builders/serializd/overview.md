---
search:
  boost: 2
---

# Serializd Builders

Serializd builders use Serializd's JSON API to find shows. They are available only for show libraries and require [Serializd authentication](../../../config/serializd.md) in the Kometa configuration file.

| Builder | Description |
| ------- | ----------- |
| [`serializd_list`](list.md) | Finds every show in a public Serializd list. |
| [`serializd_watchlist`](watchlist.md) | Finds every show in the authenticated user's or another public user's watchlist. |
| [`serializd_trending`](charts.md) | Finds a limited number of shows from Trending TV Shows. |
| [`serializd_popular`](charts.md) | Finds a limited number of shows from Popular TV Shows. |
| [`serializd_featured`](charts.md) | Finds a limited number of shows from Featured Shows. |

These builders do not scrape Serializd web pages. Private or otherwise API-inaccessible content produces a builder error.
