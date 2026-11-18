# YouTube Music Builders

Collect tracks and artists from public YouTube Music playlists and charts.

!!! note "Public access"

    No sign-in is needed for the public playlists, dynamic charts, or top-artist
    charts described here. See [YouTube Music settings](../../../config/ytmusic.md)
    for service settings.

## Choose a source

| Source | Creates | Input |
|:-------|:--------|:------|
| [`ytmusic_list`](#youtube-music-list-builder) | Track collection from a public playlist | Playlist URL, ID, or dictionary |
| [`ytmusic_top_artists`](#youtube-music-top-artists-builder) | Artist collection | `true` for global, or country dictionary |
| [Dynamic charts](#youtube-music-dynamic-charts) | One track collection per available chart | `dynamic_collections` configuration |

For regular collections, use `collection_order: custom` to preserve source order
and `sync_mode: sync` to keep membership synchronized. Tracks appearing more than
once are kept only at their first position.

## Playlists {#youtube-music-list-builder}

`ytmusic_list` accepts a public playlist URL or ID, or a YAML list combining links
and IDs. Dictionary form uses `playlist` and optional `limit`.

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `playlist` | URL or playlist ID string | Source playlist |
| `limit` | Integer | Maximum tracks to include |

The selected playlist determines the source; this builder has no country option.

=== "URL string"

    Follows the public playlist in source order. Replace the example link with
    the playlist you want to use.

    ```yaml
    collections:
      My YouTube Music Playlist:
        ytmusic_list: https://music.youtube.com/playlist?list=PLC7LNuBoMA-o
        collection_order: custom
        sync_mode: sync
    ```

=== "ID and integer limit"

    Selects at most 50 tracks using the playlist ID instead of its full URL.
    `playlist` is a string and `limit` is an integer. Replace the example ID.

    ```yaml
    collections:
      My YouTube Music Top 50:
        ytmusic_list:
          playlist: PLC7LNuBoMA-o
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```

Kometa can use the playlist description and cover when available. Collection
details you set explicitly take priority.

## Top artists {#youtube-music-top-artists-builder}

`ytmusic_top_artists` creates an artist-level collection, matching artists by name.
Use `true` for the global chart or a dictionary with `country`. Country defaults
to `global`; two-letter country codes are also accepted.

=== "Boolean"

    Selects worldwide top artists. `true` is an unquoted boolean, rather than
    a country name or a result count.

    ```yaml
    collections:
      Global Top Artists:
        ytmusic_top_artists: true
        collection_order: custom
    ```

=== "Country dictionary"

    Selects the US top-artists chart. `US` is a two-letter country-code string;
    it changes the chart location without changing the artist collection level.

    ```yaml
    collections:
      US Top Artists:
        ytmusic_top_artists:
          country: US
        collection_order: custom
    ```

Missing artists and ambiguous name matches appear in the missing-artists report.

## Dynamic charts {#youtube-music-dynamic-charts}

Use `dynamic_collections` to create one track collection for each available chart
in a selected country and section. This differs from `collections`, where each
entry configures a single collection.

| Option | Values / purpose |
|:-------|:-----------------|
| `type` | `ytmusic_video_charts` for video charts; `ytmusic_genre_charts` for genre charts |
| `data.country` | Two-letter country code or `global`; defaults to worldwide |
| `data.limit` | Optional integer cap per collection |
| `include`, `exclude` | Select or skip available chart keys or names |
| `title_format` | Format generated collection titles |
| `sync` | Dynamic collection synchronization option |

Available chart names and sections vary by country and may differ from those
shown on the YouTube Music website. Only charts available to Kometa produce
collections. Examples include Top 100 Music Videos and Top 100 Shorts for video
charts, or Top 50 Pop and Top 50 Rock Music Videos for genre charts.

=== "Country and per-chart limit"

    Creates collections for available US genre charts, with at most 50 tracks
    in each collection. `US` is a country string; `50` limits each generated
    collection, rather than the number of collections.

    ```yaml
    dynamic_collections:
      YouTube Music Genre Charts:
        type: ytmusic_genre_charts
        data:
          country: US
          limit: 50
    ```

=== "Exclude by key or name"

    Creates US genre-chart collections except the Pop playlist key and the Rock
    genre. On each run, Kometa logs genre keys as `<playlist ID> | <genre name>`;
    use either value in the YAML exclusion list.

    ```yaml
    dynamic_collections:
      YouTube Music Genre Charts:
        type: ytmusic_genre_charts
        data:
          country: US
          limit: 50
        exclude:
          - PL4fGSI1pDJn77aK7sAW2AT0oOzo5inWY8
          - Rock
    ```

Each chart retains its track order. Its description and cover can be used when
available; explicit collection details take priority.

## Country reference {#supported-countries}

<span id="youtube-music-top-artists-builder-supported-countries"></span>

These codes are documented for both dynamic charts and top artists; use `global`
for worldwide. Availability may change, and not every chart type is available
in every country.

??? info "Country codes"

    ```text
    AE, AR, AT, AU, BE, BO, BR, CA, CH, CL, CO, CR, CZ, DE, DK, DO, EC, EE, EG, ES, FI, FR, GB
    GT, HK, HN, HU, ID, IE, IL, IN, IS, IT, JP, KE, KR, LU, MX, MY, NG, NI, NL, NO, NZ, PA, PE
    PH, PL, PT, PY, RO, RS, RU, SA, SE, SG, SV, TH, TR, TW, TZ, UA, UG, US, UY, VN, ZA, ZW, ZZ
    ```

## Track matching

Playlist tracks are matched to Plex by artist and track name, checking duration
and album when available. Unmatched tracks appear in the missing-tracks log and
report. Similar names and lengths can cause version mismatches; review results
when the exact recording matters.
