---
hide:
  - toc
---
# Spotify Builders

The `spotify_chart` builder adds chart tracks to a Plex Music collection or playlist by matching the chart's artist and song titles.

| Builder | Description | Works with Music | Works with Playlists and Custom Sort |
|:--|:--|:--:|:--:|
| [`spotify_chart`](chart.md) | Gets tracks from a Spotify daily or weekly country chart | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

Set `chart` to `daily` or `weekly`. When Plex returns multiple exact artist and track matches, Kometa chooses the one from the earliest known album release. Use `collection_order: custom` to preserve the chart's position order.

See [Spotify Chart Builder](chart.md) for configuration examples and supported country codes.
