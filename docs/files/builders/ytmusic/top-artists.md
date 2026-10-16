# YouTube Music Top Artists Builder

`ytmusic_top_artists` creates an artist collection from YouTube Music's top artists chart. You can use worldwide or country-specific charts. No sign-in is needed; see [YouTube Music settings](../../../config/ytmusic.md).

```yaml title="Collection file"
collections:
  Global Top Artists:
    ytmusic_top_artists: true
    collection_order: custom

  US Top Artists:
    ytmusic_top_artists:
      country: US
    collection_order: custom
```

`country` is optional and defaults to `global`. Use a two-letter country code such as `US`, or enter `global`. Set `collection_order: custom` to keep the chart order. Kometa matches artists by name; artists that are missing from Plex or have an ambiguous match appear in the missing-artists report.

## Supported countries

These country codes are currently available. You can also use `global` for worldwide charts. Availability may change over time:

```text
AE, AR, AT, AU, BE, BO, BR, CA, CH, CL, CO, CR, CZ, DE, DK, DO, EC, EE, EG, ES, FI, FR, GB
GT, HK, HN, HU, ID, IE, IL, IN, IS, IT, JP, KE, KR, LU, MX, MY, NG, NI, NL, NO, NZ, PA, PE
PH, PL, PT, PY, RO, RS, RU, SA, SE, SG, SV, TH, TR, TW, TZ, UA, UG, US, UY, VN, ZA, ZW, ZZ
```
