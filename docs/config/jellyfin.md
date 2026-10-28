---
search:
  boost: 3
hide:
  - toc
---
# Jellyfin and Emby Attributes

[Jellyfin](https://jellyfin.org/) and [Emby](https://emby.media/) are media servers. A library uses one when its [`server`](libraries.md#server) attribute names a `media_servers` entry with `type: jellyfin` or `type: emby`. That library does not need a `plex` block. [`tmdb`](tmdb.md) stays required.

Both servers use the MediaBrowser API. Kometa sends `token` on the `X-Emby-Token` header. `user` selects the user for catalog and playlist calls. When `user` is omitted, Kometa uses the first administrator from `/Users`.

Connection logs include the remote server name, version, and available OS information from `/System/Info`. Missing OS details are logged as not reported. Failure to read this optional information warns without preventing library setup.

Movie and TV libraries can build boxset collections and playlists. Kometa can edit titles, summaries, tags, genres, and studios, and it can upload poster, backdrop, logo, banner, and overlay images. A local file is uploaded as bytes. A URL is sent to the server, which downloads it. Plex smart-filter addresses are not accepted. A collection that needs a dynamic Plex filter stops with an error for that collection.

Jellyfin collection sort titles use its custom sort-name field, including separator collections. If Jellyfin or Emby reports no primary image, Kometa retries the configured poster even when its local artwork cache records an earlier upload.

Emby sort-title updates write both `ForcedSortName` and `SortName`, matching its native metadata editor. This applies to people collections, separators, and other configured sort titles.

Kometa also locks the Emby `SortName` field while preserving existing field locks, then reads back the saved sort title. A value that was not retained reports an error instead of a successful edit.

Verification accepts differences in accents and letter case, such as `Toshirō Mifune` becoming `Toshiro Mifune`, while still checking the section prefix and name.

New Jellyfin collections are created with locked metadata to prevent automatic movie-franchise matches from replacing their names. If an existing collection was renamed by a provider, Kometa can recover it when its original `[boxset]` folder exactly and uniquely matches the requested name. Recovery restores the name, locks metadata, and clears the incorrect provider IDs; the collection then continues through configured metadata and artwork updates.

Actor, director, producer, and writer dynamic collections use the credits stored on the selected server. Their discovery cache is scoped to that server, library, profile/user, and item; credits cached from another server are not reused. Missing crew credits must be populated on Jellyfin or Emby before Kometa can discover and match those people.

Dynamic content-rating, genre, studio, and country collections discover values from the library's native metadata. Content-rating defaults match the stored `OfficialRating`; enabling several countries' rating defaults does not translate a movie's rating into those countries' classification systems.

Audio- and subtitle-language dynamic collections discover language codes from native media streams across all reported versions, including external subtitle tracks. Track details are reused during the run. Tracks without a language code are omitted.

Three-letter language codes are normalized to their two-letter equivalents when available (for example, `eng` to `en` and `fra`/`fre` to `fr`) for both discovery and matching. Languages without a two-letter equivalent retain their code.

Resolution dynamic collections discover video resolutions across reported media versions. Collection keys use the defaults' `480`, `576`, `720`, `1080`, `2k`, `4k`, and `8k` forms; matching also accepts their `p` equivalents. Items without video dimensions are omitted.

Year and decade dynamic collections use native production years. Decades cover ten calendar years (for example, 1990–1999); missing or invalid years are omitted from discovery.

### Search and filtering fields

Jellyfin and Emby evaluate `plex_search`, supported `smart_filter` definitions, and ordinary `filters` against native metadata. Smart filters produce ordinary collections rebuilt on each Kometa run. The `validate` boolean is a control option, not a field to match. Unknown fields still produce an explicit error.

| Metadata | Fields |
| :--- | :--- |
| Titles and descriptions | `title`, `summary`, `original_title`, `sort_title`, `tagline`, `show_title`, `album_title`, `type`, `status`/`show_status` |
| Tags and people | `genre`, `studio`, `country`, `content_rating`, `label`, `collection`, `actor`, `director`, `producer`, `writer`, `artist`, `album_artist` |
| Dates | `release`, `added`, `last_played`, `ended`, `updated` |
| Years and counts | `year`, `decade`, `versions`, `seasons`, `episodes`, `season_number`, `episode_number` |
| Video | `resolution`, `aspect`, `width`, `height`, `video_codec`, `video_profile`, `video_range`, `video_bit_depth`, `video_bitrate`, `frame_rate`, `reference_frames`, `dovi_profile`, `dovi_level` |
| Audio and subtitles | `channels`, `audio_codec`, `audio_profile`, `audio_track_title`, `subtitle_track_title`, `audio_language`, `subtitle_language`, `original_language`, `audio_bit_depth`, `audio_sample_rate`, `audio_bitrate` |
| Files | `filepath`, `folder`/`folder_location`, `container`, `edition`, `file_size`, `bitrate` |
| Duration and ratings | `duration`/`runtime`, `duration_seconds`, `audience_rating`, `critic_rating`, `user_rating` |
| Flags | `duplicate`, `hdr`, `has_dolby_vision`/`dovi`, `hdr10plus`, `interlaced`, `atmos`, `has_edition`, `has_subtitles`, `is_3d`, `watched`, `unwatched`/`unplayed`, `is_favorite`, `is_in_progress`/`progress`, `unmatched`, `is_missing`, `is_locked` |
| Playback | `plays`, `position_seconds`, `progress_ratio` |

Numeric fields support equality, `.not`, `.gt`, `.gte`, `.lt`, and `.lte`. Text supports contained text, `.is`, `.isnot`, `.not`, `.begins`, `.ends`, and `.regex`. Tags accept comma-separated alternatives, `.and`, and `.count_gt`/`.count_gte`/`.count_lt`/`.count_lte`. Dates support relative day counts, `.before`/`.after` dates, and `.regex`. Nested `all`/`any` groups accept mappings or lists. Boolean fields require YAML `true` or `false`.

Duration is in minutes unless `duration_seconds` is selected. Total `bitrate` is in `kbps`; stream bit rates are in bits per second. Ratings use a 0–10 scale, including conversion of native critic scores from 0–100. `progress` is a boolean in-progress selector; `progress_ratio` is a fraction from the server's played percentage. Missing numeric, date, and boolean values do not match, including negative filters. An original audio language is available only when the server explicitly marks an audio stream as original. Episode and season counts use the corresponding reported counts, not unrelated recursive item totals.

`sort_by` supports ascending or descending supported numeric, text, and date fields, with unknown values last, plus a positive `limit`. Media details are fetched only for fields that need them and reused during the run. Collection membership is loaded on demand and refreshed after Kometa changes membership. Labels match native `Tags`/`TagItems`. Fields that exist only in Plex are not inferred from unrelated metadata.

These mappings follow the [Jellyfin item contract](https://kotlin-sdk.jellyfin.org/dokka/jellyfin-model/org.jellyfin.sdk.model.api/-base-item-dto/index.html), [Jellyfin stream contract](https://kotlin-sdk.jellyfin.org/dokka/jellyfin-model/org.jellyfin.sdk.model.api/-media-stream/index.html), and [Emby item contract](https://dev.emby.media/reference/pluginapi/MediaBrowser.Model.Dto.BaseItemDto.html). A field may remain unknown when the selected server, version, or user does not report it.

Local searches display an item counter and write periodic scan checkpoints to the log. Metadata-only filters, such as people, years, and genres, use catalog metadata without fetching every item's media details. Technical filters fetch those details as needed and reuse them during the run.

The shared Jellyfin/Emby client retries transient connection failures and timeouts up to twice, waiting 1 then 2 seconds, for reads, item metadata updates/deletions, and collection membership changes. Only the failed request or batch is retried. A deletion that returns 404 after a connection failure is treated as complete. After a failed collection-creation response, Kometa first searches for an exact name match and reuses its ID; creation is retried only if none is found. Ambiguous matches or failed recovery lookups stop processing instead of blindly creating another collection. Other write operations are not automatically replayed.

```yaml title="config.yml Jellyfin sample"
tmdb:
  apikey: ################################
media_servers:
  Cinema:
    type: jellyfin
    url: http://192.168.1.12:8096
    token: ####################
    user: USER_ID
    timeout: 60
    verify_ssl: true
libraries:
  Films:
    server: Cinema
    collection_files:
      - default: basic
```

```yaml title="config.yml Emby sample"
tmdb:
  apikey: ################################
media_servers:
  Theater:
    type: emby
    url: http://192.168.1.12:8096
    token: ####################
libraries:
  Films:
    server: Theater
    collection_files:
      - default: basic
```

`Films` uses the named server. Add a `plex` block when another library in the same file uses Plex.

<div class="annotate" markdown>

| Attribute    | Description                                                                                          | Allowed Values (default in **bold**)                         |                  Required                  |
|:-------------|:-----------------------------------------------------------------------------------------------------|:-------------------------------------------------------------|:------------------------------------------:|
| `type`       | Media server type.                                                                                   | `jellyfin` or `emby`                                         | :fontawesome-solid-circle-check:{ .green } |
| `url`        | Server URL.                                                                                          | Any valid URL<br><strong>Example:</strong> `http://192.168.1.12:8096` | :fontawesome-solid-circle-check:{ .green } |
| `token`      | API key.                                                                                             | Any valid API key                                            | :fontawesome-solid-circle-check:{ .green } |
| `user`       | User id for catalog and playlist calls. Omit to use the first administrator.                        | Any user id                                                  |  :fontawesome-solid-circle-xmark:{ .red }  |
| `timeout`    | Timeout for server communication, in seconds.                                                        | Integer, e.g. **`60`**                                       |  :fontawesome-solid-circle-xmark:{ .red }  |
| `verify_ssl` | Enable or disable SSL verification for this server.                                                 | `true`, `false`, or leave **blank**                          |  :fontawesome-solid-circle-xmark:{ .red }  |

</div>

Libraries that omit `server` keep using `plex`.

Jellyfin and Emby do not execute Plex smart-filter URIs. Supported `smart_filter` definitions are rebuilt as ordinary collections on each Kometa run using local metadata. Nested `all`/`any` expressions support the same fields as local overlay selectors, plus `release` and `added` with positive day counts. Missing dates and future dates do not match a recent-date window. Supported selection sorts are `title`, `release`, `added`, and `year` with `.asc`/`.desc`; sorting occurs before `limit` is applied. The server's supported collection display order is applied separately. `default: basic` Newly Released works this way; New Episodes skips movie libraries and still requires unsupported episode-level filtering on show libraries. Unknown fields/options and `smart_url` remain explicit errors.

People defaults use native `People` metadata for actor, director, writer, and producer discovery and filtering. Person names resolved by `tmdb_person` are substituted for `tmdb` in selectors. Local collection selection also supports `audience_rating` (`CommunityRating`) and `critic_rating` (`CriticRating`) sorts, applied before any limit; unsupported collection display orders still warn and retain the server's display order.

Simple `smart_label` definitions with an external list builder or a supported local `plex_all`/`plex_search` selector are converted to ordinary collections rebuilt each run, retaining filters, sorting, and limits. This includes sort-only smart labels and dictionaries whose only condition is `all: {label: <<smart_label>>}`, such as seasonal and aspect defaults. Aspect filters read native video aspect ratios, falling back to frame dimensions. Additional label conditions and definitions without a supported selector remain unsupported.

Emby collections are created with the builder's initial members. New blank collections are not supported. Emby chooses the collection's location; Kometa does not pass the movie library as its parent.

Emby tags are read from `TagItems` when needed and tag edits include both `Tags` and `TagItems`. Overlay removal discovers items through the `Overlay` tag and local original-poster backups, so originals saved before tag tracking was fixed can still be restored. Keep the library's original-poster backup directory until removal completes.

`collection_order: release` and `alpha` apply the native `DisplayOrder` field on both Jellyfin and Emby. Ascending `release.asc` and `title.asc` expressions are also supported. Jellyfin additionally supports ascending `added`, `year`, `duration`, and `content_rating` expressions. Existing metadata is preserved, and matching display orders are not rewritten. Client browsing preferences may override this default.

Exact external-list ordering (`custom`/`custom.desc`), descending sort defaults, and multiple sort fields are not currently applied by this adapter. Kometa warns and retains the server's display order; membership and item sort titles are not changed to approximate unsupported ordering. Collection metadata and artwork updates still apply.

Supported `plex_search` overlay expressions are evaluated locally against item and media-source metadata. Nested `all`/`any` groups support title, year, resolution, edition, filepath, HDR, Dolby Vision, genre, studio, and country selectors. String fields support regex and basic text comparisons. Resolution is derived from video-stream dimensions, including cropped 4K video; HDR/Dolby Vision use the available video-range and Dolby Vision profile fields. Details are reused within a run. Missing metadata does not match, including negative filters. Edition matching requires an explicit `EditionName`; it is not inferred from a version's display name. Unsupported fields, sort/limit/type options, and modifiers report errors. This adds selector matching, not blanket compatibility with every Plex overlay definition or rendering feature.

The `duplicate` search selector matches items with multiple media sources (alternate versions) on Jellyfin and Emby. Kometa loads media-source details as needed. Unknown source counts match neither `duplicate: true` nor `duplicate: false`; separate catalog entries are not detected as duplicates.
