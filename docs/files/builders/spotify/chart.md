# Spotify Chart Builder

`spotify_chart` builds a track-level collection from a Spotify country chart. It matches exact artist and track titles in your Plex Music library. When Plex has multiple exact matches, Kometa chooses the track on the album with the earliest known release date. Unmatched chart tracks are skipped.

```yaml title="Collection file"
collections:
  Spotify UK Daily:
    spotify_chart:
      country: UK
      chart: daily
    collection_order: custom
    sync_mode: sync
```

`country` accepts one of the two-letter codes listed below or a country name listed after them. Codes are case-insensitive; other two-letter codes are passed through and work only if a matching chart page exists. `UK` and `United Kingdom` map to Spotify's `gb` chart, `USA` and `United States` map to `us`, and `UAE` / `United Arab Emirates` map to `ae`.

`chart` must be `daily` or `weekly`.

Supported country codes:

| Shortcode | Country |
|:--|:--|
| AE | United Arab Emirates |
| AR | Argentina |
| AT | Austria |
| AU | Australia |
| BE | Belgium |
| BG | Bulgaria |
| BO | Bolivia |
| BR | Brazil |
| BY | Belarus |
| CA | Canada |
| CH | Switzerland |
| CL | Chile |
| CO | Colombia |
| CR | Costa Rica |
| CY | Cyprus |
| CZ | Czech Republic |
| DE | Germany |
| DK | Denmark |
| DO | Dominican Republic |
| EC | Ecuador |
| EE | Estonia |
| EG | Egypt |
| ES | Spain |
| FI | Finland |
| FR | France |
| GB | United Kingdom |
| GR | Greece |
| GT | Guatemala |
| HK | Hong Kong |
| HN | Honduras |
| HR | Croatia |
| HU | Hungary |
| ID | Indonesia |
| IE | Ireland |
| IL | Israel |
| IN | India |
| IS | Iceland |
| IT | Italy |
| JP | Japan |
| KE | Kenya |
| KR | South Korea |
| KZ | Kazakhstan |
| LT | Lithuania |
| LU | Luxembourg |
| LV | Latvia |
| MA | Morocco |
| MX | Mexico |
| MY | Malaysia |
| NG | Nigeria |
| NI | Nicaragua |
| NL | Netherlands |
| NO | Norway |
| NZ | New Zealand |
| PA | Panama |
| PE | Peru |
| PH | Philippines |
| PL | Poland |
| PT | Portugal |
| PY | Paraguay |
| RO | Romania |
| RS | Serbia |
| RU | Russia |
| SA | Saudi Arabia |
| SE | Sweden |
| SG | Singapore |
| SI | Slovenia |
| SK | Slovakia |
| SV | El Salvador |
| TH | Thailand |
| TR | Turkey |
| TW | Taiwan |
| UA | Ukraine |
| US | United States |
| UY | Uruguay |
| VE | Venezuela |
| VN | Vietnam |
| ZA | South Africa |
