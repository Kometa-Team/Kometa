# MDBList Builders

Collect movies and shows from [MDBList](https://mdblist.com/) lists or its
JustWatch streaming charts.

## Choose a builder

| Builder | Finds | Supports | Playlists |
|:--------|:------|:---------|:----------|
| [`mdblist_list`](#mdblist-list) | Items in specific lists | Movies, shows, listed episodes | Yes |
| [`mdblist_streaming`](#mdblist-streaming) | JustWatch streaming chart entries | Movies, shows | No |

Use `collection_order: custom` to retain the returned order and `sync_mode: sync`
to keep collection membership synchronized as the source changes.

!!! note "MDBList refreshes sources periodically"

    MDBList data can lag behind third-party sites by days, weeks, or months.
    Results and metadata may differ from what you see on the original source.

## Lists {#mdblist-list}

`mdblist_list` accepts a full [MDBList list URL](https://mdblist.com/toplists/),
or a dictionary with the options below. For multiple sources, use a **YAML list**;
a comma-separated string will not work.

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `url` | String | Full list URL, required in dictionary form |
| `limit` | Integer | Limit the number of items to search for |
| `sort_by` | Sort option | Override the list's saved order; see [sort options](#sort-options) |

For episode lists, set `builder_level: episode` to create an episode collection.
In mixed movie/show playlists, MDBList uses its unified endpoint: the response
order is preserved, including any interleaving of movies and shows, without grouping by type.

<span id="example-mdblist-list-builders"></span>

=== "URL string"

    Follows the Top Watched Movies of the Week list using its saved sort order.
    The builder value is a full URL string.

    ```yaml
    collections:
      Top Watched Movies of the Week:
        mdblist_list: https://mdblist.com/lists/linaspurinis/top-watched-movies-of-the-week
        collection_order: custom
        sync_mode: sync
    ```

=== "Limit and sorting"

    Selects up to 10 movies from that list, requesting highest IMDb ratings first.
    `limit` is an integer and `imdbrating.desc` is a sort string. Custom collection
    ordering is required for the requested order to appear in Plex.

    ```yaml
    collections:
      Top 10 Weekly Picks by IMDb Rating:
        mdblist_list:
          url: https://mdblist.com/lists/linaspurinis/top-watched-movies-of-the-week
          limit: 10
          sort_by: imdbrating.desc
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiple lists"

    Combines items from two sources using a YAML list. Replace the second URL
    with another MDBList list URL. The sources are combined, rather than used
    as AND/OR filters.

    ```yaml
    collections:
      Combined MDBList Picks:
        mdblist_list:
          - https://mdblist.com/lists/linaspurinis/top-watched-movies-of-the-week
          - https://mdblist.com/lists/your_username/your-list
        collection_order: custom
        sync_mode: sync
    ```

### Sort options {#sort-options}

Append `.asc` for ascending or `.desc` for descending order, such as
`imdbrating.desc`. If omitted, the source list's saved order is used.
Set `collection_order: custom` for the returned order to be reflected in Plex.

??? info "Available sort fields"

    | Field | Orders by |
    |:------|:----------|
    | `rank` | MDBList Rank |
    | `score` | MDBList Score |
    | `score_average` | MDBList Average Score |
    | `released` | Release Date |
    | `releasedigital` | Digital Release Date |
    | `imdbrating` | IMDb Rating |
    | `imdbvotes` | IMDb Votes |
    | `imdbpopular` | IMDb Popular |
    | `tmdbpopular` | TMDb Popular |
    | `rogerebert` | RogerEbert Score |
    | `rtomatoes` | Rotten Tomatoes Score |
    | `rtaudience` | Rotten Tomatoes Audience Score |
    | `metacritic` | Metacritic Score |
    | `myanimelist` | MyAnimeList Score |
    | `letterrating` | Letterboxd Rating |
    | `lettervotes` | Letterboxd Votes |
    | `last_air_date` | Last Air Date |
    | `budget` | Budget |
    | `revenue` | Revenue |
    | `runtime` | Runtime |
    | `title` | Title |
    | `sort_title` | Sort Title |
    | `random` | Random (Randomized Daily) |
    | `usort` | User Sort (not available for external lists) |
    | `added` | Date Added (not available for external lists) |

### External lists {#external-mdblists}

External MDBList lists mirror lists from another site. For example,
`https://mdblist.com/lists/chazlarson/external/2868` mirrors
`https://imdb.com/list/ls089009459`.

An external list is accessible when **either**:

- The owner of your MDBList API key also owns the external list.
- The external list's owner has unchecked **Make your external lists private** in their account settings.

This example follows the mirrored Esquire list, provided one of those access
conditions is met. External lists do not support the `usort` or `added` sort fields.

```yaml
collections:
  Esquire 60 Scariest Movies of All Time:
    mdblist_list: https://mdblist.com/lists/chazlarson/external/2868
    collection_order: custom
    sync_mode: sync
```

## Streaming charts {#mdblist-streaming}

`mdblist_streaming` selects entries from MDBList's
[JustWatch streaming chart](https://api.mdblist.com/docs/#/Official%20Lists/justwatch_streaming_charts_retrieve).
The library type determines whether it requests movies or shows. Playlists are
not supported because they have no single media type.

Use a dictionary of options, or `{}` for the defaults. Values are case-insensitive;
use a code or displayed name, and country values also accept a locale.

| Attribute | Value | Default |
|:----------|:------|:--------|
| `country` | Country code, locale, or name | `US` / United States |
| `period` | Period code or name | `1` / Daily |
| `provider` | JustWatch provider code or name | All providers |
| `genre` | JustWatch genre code or name | All genres |

=== "Default chart"

    In a movie library, selects the daily US movie chart across all providers
    and genres. In a show library, the same configuration selects shows.
    `{}` is an empty dictionary, rather than a boolean switch.

    ```yaml
    collections:
      Daily Streaming Picks:
        mdblist_streaming: {}
        collection_order: custom
        sync_mode: sync
    ```

=== "Named values"

    In a show library, selects the weekly UK Netflix action-show chart.
    Country, provider, and genre use names; `7` is the weekly period code.

    ```yaml
    collections:
      Weekly Netflix Action Shows:
        mdblist_streaming:
          country: United Kingdom
          period: 7
          provider: Netflix
          genre: Action
        collection_order: custom
        sync_mode: sync
    ```

=== "Codes and locale"

    Selects the same chart using the `en_GB` locale, `7d` weekly code, `nfx`
    provider code, and `act` genre code. These are strings; the library still
    determines the media type.

    ```yaml
    collections:
      Weekly Netflix Action Picks:
        mdblist_streaming:
          country: en_GB
          period: 7d
          provider: nfx
          genre: act
        collection_order: custom
        sync_mode: sync
    ```

### Streaming values

<span id="countries"></span>

??? info "Countries"

    | Code | Locale | Name |
    |:-----|:-------|:-----|
    | `all` |  | All countries |
    | `US` | `en_US` | United States |
    | `GB` or `UK` | `en_GB` | United Kingdom |
    | `CA` | `en_CA` | Canada |
    | `AU` | `en_AU` | Australia |
    | `DE` | `de_DE` | Germany |

<span id="periods"></span>

??? info "Periods"

    | Code | Name |
    |:-----|:-----|
    | `1` or `1d` | Daily |
    | `7` or `7d` | Weekly |
    | `30` or `30d` | Monthly |

<span id="providers"></span>

??? info "Providers"

    | Code | Name |
    |:-----|:-----|
    | `all` | All providers |
    | `nfx` | Netflix |
    | `amp` | Amazon Prime Video |
    | `atp` | Apple TV+ |
    | `dnp` | Disney+ |
    | `mxx` | Max |
    | `hlu` | Hulu |
    | `pct` | Peacock Premium |
    | `pcp` | Peacock Premium Plus |
    | `ppp` | Paramount+ Premium |
    | `ppe` | Paramount+ Essential |
    | `cru` | Crunchyroll |
    | `fuv` | fuboTV |
    | `acp` | AMC+ |
    | `shd` | Shudder |
    | `stz` | Starz |
    | `epx` | MGM+ |
    | `dpu` | Discovery+ |
    | `mbi` | MUBI |
    | `crc` | Criterion Channel |
    | `act` | Acorn TV |
    | `bbo` | BritBox |
    | `knp` | Kanopy |
    | `rkc` | The Roku Channel |
    | `ptv` | Pluto TV |
    | `tbv` | Tubi |
    | `plx` | Plex |
    | `vuf` | Fandango at Home Free |

<span id="genres"></span>

??? info "Genres"

    | Code | Name |
    |:-----|:-----|
    | `all` | All genres |
    | `act` | Action |
    | `ani` | Animation |
    | `cmy` | Comedy |
    | `crm` | Crime |
    | `doc` | Documentary |
    | `drm` | Drama |
    | `fnt` | Fantasy |
    | `hst` | History |
    | `hrr` | Horror |
    | `rma` | Romance |
    | `scf` | Science Fiction |
    | `trl` | Thriller |
