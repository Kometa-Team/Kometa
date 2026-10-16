---
hide:
  - toc
---
# Apple Music and iTunes Chart Builders

The Apple Music and iTunes chart builders match ranked chart entries to exact artist and title values in a Plex Music library.

| Builder | Description | Works with Music | Works with Playlists and Custom Sort |
|:--|:--|:--:|:--:|
| [`apple_chart`](chart.md) | Gets ranked songs or albums from Apple Music country charts | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`itunes_chart`](chart.md) | Gets ranked songs or albums from iTunes country charts | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

Both builders accept US, UK, JP, DE, FR, IT, and RU. France, Italy, and Russia use EU chart pages. They default to songs and can use `type: album` for album-level collections. Rows without a positive integer rank for the selected country are skipped. Use `collection_order: custom` to keep the country's chart rank order.

See [Apple Music and iTunes Charts](chart.md) for configuration examples and source page details.
