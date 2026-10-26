# Spotify Builders

Use `spotify_chart` to collect chart tracks from a Spotify daily or weekly country
chart. It supports Plex Music collections, playlists, and custom sorting.

## Chart options {#spotify-chart-builder}

The builder takes a dictionary:

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `country` | Country code or name | Select the country chart |
| `chart` | `daily`, `weekly` | Select the chart period |

Country codes are case-insensitive. `UK` and `United Kingdom` map to `gb`;
`USA` and `United States` map to `us`; `UAE` and `United Arab Emirates` map to `ae`.
Other two-letter codes are passed through and work only if a matching chart page exists.

## Examples

=== "Code and daily chart"

    Selects tracks from the UK daily chart. Both values are strings; `UK` is
    mapped to Spotify's `gb` country chart. Custom ordering keeps chart positions,
    and synchronization updates membership as the chart changes.

    ```yaml
    collections:
      Spotify UK Daily:
        spotify_chart:
          country: UK
          chart: daily
        collection_order: custom
        sync_mode: sync
    ```

=== "Name and weekly chart"

    Selects the weekly US chart using a country name instead of a two-letter code.
    `United States` maps to the same country as `US` or `USA`.

    ```yaml
    collections:
      Spotify US Weekly:
        spotify_chart:
          country: United States
          chart: weekly
        collection_order: custom
        sync_mode: sync
    ```

## Track matching

Kometa matches exact artist and track titles in your Plex Music library. When
several tracks match, it selects the one on the album with the earliest known
release date. Unmatched chart tracks are skipped.

## Country reference

??? info "Supported country codes and names"

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
