# Apple Music and iTunes Charts

`apple_chart` and `itunes_chart` build track-level collections from country charts. Use `type: album` to build an album-level collection; the level defaults to tracks for songs and albums for the album chart. Kometa keeps only rows with a positive integer in the selected country's column, sorts those rows by that rank, then matches exact artist and title values in Plex. When multiple track matches exist, the earliest known album release is selected. Unmatched chart items are skipped.

```yaml title="Apple Music collection"
collections:
  UK Apple Songs:
    apple_chart:
      country: UK
    collection_order: custom

  France Apple Albums:
    apple_chart:
      country: FR
      type: album
    collection_order: custom
```

```yaml title="iTunes collection"
collections:
  US iTunes Songs:
    itunes_chart:
      country: US
    collection_order: custom
```

`country` accepts the following codes. France, Italy, and Russia use EU chart pages.

| Shortcode | Country |
|:--|:--|
| US | United States |
| UK | United Kingdom |
| JP | Japan |
| DE | Germany |
| FR | France |
| IT | Italy |
| RU | Russia |

`type` accepts `track`, `song`, or `album` and defaults to `track`. For `apple_chart`, songs use `apple_songs` and albums use `apple_albums`; for `itunes_chart`, songs use `ww`/`eu` and albums use `aww`/`eua`. Set `collection_order: custom` to order Plex matches by the selected country's chart rank.
