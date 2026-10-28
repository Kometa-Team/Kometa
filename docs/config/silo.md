---
search:
  boost: 3
hide:
  - toc
---
# Silo Attributes

[Silo](https://silo.pzyzbyx.pw/api/v2/docs) is a media server. A library uses Silo when its [`server`](libraries.md#server) attribute names a `media_servers` entry. That library does not need a `plex` block. [`tmdb`](tmdb.md) stays required.

Silo libraries can create and update manual collections and smart collections. A smart collection takes a Silo query document. Plex smart filter addresses are not accepted. Posters, backdrops, logos, and overlays are set from a URL. Kometa publishes a local image to [transfer.kometa.wiki](https://transfer.kometa.wiki) and gives Silo that URL. A URL Kometa already has, such as a TMDb image, is given to Silo directly. Labels, deleting an item, and playlists are not available. A collection that needs one of those stops with an error for that collection.

Kometa calls Silo's `/api/v2` API. `token` is a session token or an API key sent on the `Authorization` header. When `profile_id` is set, catalog reads send it on the `X-Profile-Id` header. Silo has no clean bundles, empty trash, or optimize operation, so those Plex settings are skipped for a Silo library.

Connection logs include the server version/revision reported by `/api/v2/system/info`. That endpoint does not report the server OS, so Kometa explicitly logs it as not reported. An unavailable information endpoint warns without preventing library setup.

```yaml title="config.yml Silo sample"
tmdb:
  apikey: ################################
media_servers:
  Shelf:
    type: silo
    url: http://192.168.1.12:8090
    token: ####################
    profile_id: PROFILE_ID
    timeout: 60
    verify_ssl: true
libraries:
  Films:
    server: Shelf
    collection_files:
      - default: basic
```

`Films` uses the Silo server named `Shelf`. Add a `plex` block when another library in the same file uses Plex.

With Kometa's cache enabled, resolved Silo TMDb, TVDb, and IMDb IDs persist between runs and refresh according to `cache_expiration`. Kometa still lists the catalog each run, but avoids individual detail requests for entries with fresh cached IDs. Disabling the cache restores per-run ID lookups.

Collection summary updates use Silo's native description field. Kometa does not add its automatic collection label on Silo. Collection `sort_title` is skipped with a warning. Explicit collection label, content rating, Plex collection mode, filtering, and visibility options are not supported.

`collection_order: release` and `alpha` set Silo's native default sort. `custom`/`custom.asc` preserve the builder's order, and `custom.desc` reverses it; extra members retained in append mode follow the builder's items. Custom ordering changes manual member positions by removing and re-adding members whose positions differ, because Silo's add endpoint preserves existing positions. If a re-add fails, Kometa attempts to restore that member at its old position. These requests are not atomic: an interruption can leave a partial order, and a failed restoration can leave a missing member. Rerun Kometa to reconcile membership and ordering. Do not edit the same collection concurrently while sorting.

Single-field sort expressions support `title`, `release`, `added`, `year`, `duration`, and `content_rating`, each with `.asc` or `.desc`. Multiple sort fields and other sort expressions report errors rather than silently changing their meaning. Silo clients can override the collection default with their own browsing sort.

Collection artwork supports posters and backdrops. Collection logos and square artwork are skipped with warnings; local files for those unsupported types are not published. Item logos remain supported.

Native rating overlays support `silo_imdb`, `silo_tmdb`, `silo_tomatoes`, `silo_tomatoesaudience`, and `silo_user`. Use the `_rating` suffix for text variables and value filters. These read Silo's stored rating metadata and the active profile's personal rating, without external provider requests. See [Ratings overlays](../defaults/overlays/ratings.md).

Silo dynamic actor collections read cast metadata; director, writer, and producer discovery reads the corresponding crew jobs. Person smart filters match native names, including names resolved by `tmdb_person` for `default: actor`.

Collections using the `separator` template are skipped with a note on Silo because collection sort titles are unavailable. Other collections in the same defaults file continue to run. Existing separators are not automatically deleted.

Collection `sort_title`, `label`, `label.remove`, `label.sync`, `visible_library`, `visible_home`, and `visible_shared` settings warn and skip on Silo. Supported metadata and artwork continue updating, including artwork on yearly award and seasonal collections. Plex visibility settings do not change Silo's home-screen placement or sharing.

Dynamic language collections (`default: audio_language` and `default: subtitle_language`) discover language codes across all file versions and tracks, reusing item details within the run. Subtitle discovery includes embedded and external tracks. Missing track languages are ignored. Smart filters support `audio_language` and `subtitle_language` with `.is`/`.not` modifiers and language-code lists.

Resolution and content-rating defaults also use native Silo metadata. Resolution discovery includes all file versions and translates default keys such as `480`, `1080`, and `4k` into Silo's resolution values. Content-rating collections match Silo's stored certification strings; choosing a regional default such as `content_rating_nz` does not fetch or replace certifications in Silo.

Decade and year collections use Silo's stored years. Decade filters cover the entire decade. The decade default's `critic_rating.desc` sort uses Silo's stored Rotten Tomatoes critic score; missing scores are not fetched. Override `sort_by` with `release.desc`, `title.asc`, or another supported field to choose a different order.

Country, region, and continent defaults discover countries through Silo's library/profile-scoped catalog facets, cached for the run. Codes such as `US` are exposed as country names for the defaults, and generated filters match both native codes and legacy country-name values.

Silo overlay tracking uses Kometa's local original-poster backups and overlay cache instead of server labels. Keep the overlay backup directory to preserve originals for later updates and removal. Plex legacy overlay-label cleanup does not run on Silo.

After publishing a local image to transfer.kometa.wiki, Kometa waits 0.75 seconds before asking Silo to download it. Counting one upload and one download per image, sequential processing averages at most about 2.7 requests per second before network overhead, below the transfer host's sustained limit of 3 requests per second. This also applies when restoring original posters. Direct remote image URLs do not incur this delay. Other clients and burst limits can still cause rate limiting.

Kometa spaces all Silo API requests at least 0.5 seconds apart (at most two requests per second per server), including catalog reads, queries, collection detail reads, additions, removals, sorting, and retries. Library clients targeting the same normalized API base URL share a thread-safe limiter within the Kometa process, even when using different tokens or profiles. Time spent on requests counts toward this interval. Separate Kometa processes and other applications do not share this limiter. Silo's 429 responses still use `Retry-After` or backoff; other clients and stricter server limits can still cause throttling.

Silo evaluates a subset of `plex_search` overlay selectors locally using catalog item details. Nested `all`/`any` groups support `title`, `year`, `resolution`, `edition`, `filepath`, `hdr`, `has_dolby_vision`, `genre`, `studio`, and `country`. String fields accept `.regex`, `.is`, `.not`, `.isnot`, `.begins`, and `.ends`; HDR and Dolby Vision selectors require boolean values. Item details are reused within a run. Filepath matching requires Silo to expose `file_path` to the configured user; missing metadata does not match, including negative filters. Dolby Vision matching uses Silo's `overlay_summary.hdr` value. Unknown fields and modifiers report errors rather than selecting the entire library. Plex sorting/limit/type options are not yet supported in these local selectors. This selector support does not imply full compatibility with every Plex overlay definition or rendering feature.

Silo smart collections accept native query documents under `smart_filter`. Kometa discovers genres, studios, networks, and countries from library metadata for dynamic collections, including `default: genre`. It translates their tag filters (including lists and `.is`/`.not` modifiers) and flat `all`/`any` groups containing `release` or `added` with positive day counts, including the **Newly Released** collection from `default: basic`. Supported `sort_by` fields are `release`, `added`, `title`, and `year`, with `.asc` or `.desc`; `limit` caps the complete result. Other Plex filter expressions, including the **New Episodes** default, are not currently translated and report an unsupported-filter error.

<div class="annotate" markdown>

| Attribute    | Description                                                                                          | Allowed Values (default in **bold**)                         |                  Required                  |
|:-------------|:-----------------------------------------------------------------------------------------------------|:-------------------------------------------------------------|:------------------------------------------:|
| `type`       | Media server type.                                                                                   | `silo` or `plex`                                             | :fontawesome-solid-circle-check:{ .green } |
| `url`        | Server URL. Kometa adds `/api/v2` when a Silo URL does not already end with it.                     | Any valid URL<br><strong>Example:</strong> `http://192.168.1.12:8090` | :fontawesome-solid-circle-check:{ .green } |
| `token`      | Session token or API key.                                                                            | Any valid token                                              | :fontawesome-solid-circle-check:{ .green } |
| `profile_id` | Silo profile whose catalog Kometa reads. A profile Silo does not recognize is reported with the server's user and profile ids. | Any profile id                                               |  :fontawesome-solid-circle-xmark:{ .red }  |
| `timeout`    | Timeout for Silo communication, in seconds.                                                          | Integer, e.g. **`60`**                                       |  :fontawesome-solid-circle-xmark:{ .red }  |
| `verify_ssl` | Enable or disable SSL verification for this server.                                                 | `true`, `false`, or leave **blank**                          |  :fontawesome-solid-circle-xmark:{ .red }  |
| `db_cache`   | Plex database cache size in MB. Used when `type` is `plex`.                                          | Integer, e.g. **`40`**                                       |  :fontawesome-solid-circle-xmark:{ .red }  |

</div>

A `type: plex` entry is another Plex server. Its `url`, `token`, `timeout`, `verify_ssl`, and `db_cache` replace that library's `plex` values. Options such as `empty_trash` stay on the `plex` block.

Libraries that omit `server` keep using `plex`.

If a collection disappears between listing and reloading during collection operations, Kometa warns and skips it rather than aborting the library run. Other reload errors still surface as failures.
