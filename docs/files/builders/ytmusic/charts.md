# YouTube Music Dynamic Charts

Use `dynamic_collections` to create track collections from YouTube Music charts. Kometa creates a collection for each chart available in the selected section and country. No sign-in or YouTube Music setup is needed.

```yaml title="Collection file"
dynamic_collections:
  YouTube Music Genre Charts:
    type: ytmusic_genre_charts
    data:
      country: US
      limit: 50
```

Choose `ytmusic_video_charts` or `ytmusic_genre_charts` for video or genre charts. `data.country` is optional and defaults to worldwide charts; enter a two-letter code such as `US` for a specific country. `data.limit` can cap the number of tracks in each collection. You can also use options such as `include`, `exclude`, `title_format`, and `sync`. To build a collection from one playlist, use its link or ID with [`ytmusic_list`](list.md).

For example, `ytmusic_video_charts` can create collections such as “Top 100 Music Videos United States” and “Top 100 Shorts United States.” `ytmusic_genre_charts` can create collections such as “Top 50 Pop Music Videos United States” and “Top 50 Rock Music Videos United States.” The charts shown in YouTube Music may vary from those available to Kometa, and only available charts become collections.

On each run, Kometa logs every genre key as `<playlist ID> | <genre name>`. Use either value in `exclude` to skip a genre:

```yaml
dynamic_collections:
  YouTube Music Genre Charts:
    type: ytmusic_genre_charts
    data:
      country: US
      limit: 50
    exclude:
      - PL4fGSI1pDJn77aK7sAW2AT0oOzo5inWY8 # Pop playlist key
      - Rock # Or exclude by displayed genre name
```

Kometa keeps each chart's track order. It can use the chart description and cover when available; details you set for a collection take priority. Available chart sections and names vary by country.

## Supported countries

These country codes are currently available. The list may change, and every chart type may not be available in every country. Use `global` for worldwide charts:

```text
AE, AR, AT, AU, BE, BO, BR, CA, CH, CL, CO, CR, CZ, DE, DK, DO, EC, EE, EG, ES, FI, FR, GB
GT, HK, HN, HU, ID, IE, IL, IN, IS, IT, JP, KE, KR, LU, MX, MY, NG, NI, NL, NO, NZ, PA, PE
PH, PL, PT, PY, RO, RS, RU, SA, SE, SG, SV, TH, TR, TW, TZ, UA, UG, US, UY, VN, ZA, ZW, ZZ
```
