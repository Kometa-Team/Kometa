# Apple Music and iTunes Builders

Build collections from Apple Music or iTunes country charts by matching chart
artists and titles to your Plex Music library. Both builders support music,
playlists, and custom sorting.

## Choose a builder

| Builder | Source |
|:--------|:-------|
| `apple_chart` | Apple Music country charts |
| `itunes_chart` | iTunes country charts |

## Chart options {#apple-music-and-itunes-charts}

Both builders use the same dictionary options. Songs default to track-level
collections; `type: album` uses album level.

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `country` | Country code below | Country chart to use |
| `type` | `track`, `song`, `album`; default `track` | Songs or albums |

| Code | Country |
|:-----|:--------|
| `US` | United States |
| `UK` | United Kingdom |
| `JP` | Japan |
| `DE` | Germany |
| `FR` | France |
| `IT` | Italy |
| `RU` | Russia |

## Examples

=== "Country songs"

    Selects songs ranked in the UK Apple Music chart. `UK` is a country-code
    string; omitting `type` uses the default track level. Custom ordering keeps
    the selected country's chart rank.

    ```yaml
    collections:
      UK Apple Songs:
        apple_chart:
          country: UK
        collection_order: custom
    ```

=== "Album level"

    Selects albums from the France Apple Music chart. `type: album` changes the
    collection level as well as the chart; it does not select individual songs.

    ```yaml
    collections:
      France Apple Albums:
        apple_chart:
          country: FR
          type: album
        collection_order: custom
    ```

=== "iTunes source"

    Selects songs from the US iTunes chart using the same country dictionary
    format. Replace `apple_chart` with `itunes_chart` to change the source.

    ```yaml
    collections:
      US iTunes Songs:
        itunes_chart:
          country: US
        collection_order: custom
    ```

## Ranking and matching

Only rows with a positive integer rank in the selected country's column are
included, in rank order. `collection_order: custom` preserves that order in Plex.
Kometa matches exact artist and title values. If several tracks match, it selects
the one with the earliest known album release. Unmatched chart items are skipped.
