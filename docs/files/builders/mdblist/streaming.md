---
hide:
  - toc
---
# MDBList Streaming

`mdblist_streaming` builds a collection from MDBList's [JustWatch streaming chart](https://api.mdblist.com/docs/#/Official%20Lists/justwatch_streaming_charts_retrieve). It uses the Plex library type automatically: movie libraries request movie charts and show libraries request show charts.

The builder defaults to the United States (`US`), the daily chart, and all providers and genres. It cannot be used in playlists because a playlist has no single media type. Values are case-insensitive; use either the code or the displayed name.

| Attribute | Description | Default |
|:----------|:------------|:--------|
| `country` | Country code, locale, or name. | `US` / United States |
| `period` | Chart period code or name. | `1` / Daily |
| `provider` | JustWatch provider code or name. | All providers |
| `genre` | JustWatch genre code or name. | All genres |

### Countries

| Code | Locale | Name |
|:-----|:-------|:-----|
| `all` |  | All countries |
| `US` | `en_US` | United States |
| `GB` or `UK` | `en_GB` | United Kingdom |
| `CA` | `en_CA` | Canada |
| `AU` | `en_AU` | Australia |
| `DE` | `de_DE` | Germany |

### Periods

| Code | Name |
|:-----|:-----|
| `1` or `1d` | Daily |
| `7` or `7d` | Weekly |
| `30` or `30d` | Monthly |

### Providers

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

### Genres

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

Use `collection_order: custom` to retain MDBList's chart order.

```yaml
collections:
  Daily Streaming Movies:
    mdblist_streaming: {}
    collection_order: custom
    sync_mode: sync

  Weekly Netflix Action Shows:
    mdblist_streaming:
      country: United Kingdom
      period: 7
      provider: Netflix
      genre: Action
    collection_order: custom
    sync_mode: sync
```
