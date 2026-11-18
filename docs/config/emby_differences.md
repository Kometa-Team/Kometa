# Emby: differences from Plex

This page describes how Kometa's Emby adapter differs from its Plex adapter. It covers the adapter's behavior, rather than every feature available in Emby itself. Use the [connection reference](jellyfin.md) for setup and supported search fields.

## Connecting and selecting a library

Define a `media_servers` entry with `type: emby`, then select it with the library's `server` attribute. An Emby-only configuration does not require a root `plex` block; `tmdb` remains required. `token` is an API key. The optional `user` selects the account used for catalog, playlist, and personal-rating requests; without it, Kometa selects the first administrator.

Use `emby_all` for native all-item builders. Supported uses of `plex_all` and `plex_search` are compatibility names: they do not imply support for arbitrary Plex filters or URLs.

## Collections, searches, and defaults

| Plex-oriented behavior | What happens on Emby |
| :--- | :--- |
| Native smart collections | Supported `smart_filter` definitions become ordinary boxset collections rebuilt on Kometa runs. Changes between runs do not automatically update membership. |
| Plex smart-filter URLs and addresses | Not accepted. Use supported local fields or an external builder. |
| Smart labels | Supported simple `smart_label` definitions become ordinary collections; more complex unsupported forms report errors. |
| Collection visibility and Plex collection modes | They have no native equivalent. Shared mass collection-mode settings warn and skip. |
| Collection sort title | Kometa writes `ForcedSortName` and `SortName`, locks `SortName`, and verifies the saved result. Existing unrelated locks remain. |
| Collection display order | Native release and alphabetical order are supported. A client's browsing preferences can override that default. |
| People and metadata-based defaults | Discovery reads credits, classifications, genres, and other metadata stored on Emby. Missing server credits are not inferred from another media server. |

Searches and ordinary collection filters use native catalog and media-source metadata. Missing values do not match, including negative filters; unsupported fields and options produce explicit errors. Classifications are the stored `OfficialRating` values: enabling multiple countries' defaults does not translate them into other classification systems. The [connection reference](jellyfin.md#search-and-filtering-fields) lists supported fields and modifiers.

## Tags, overlays, and local state

Kometa maps labels to Emby tags. Those tags can identify Kometa-managed collections and overlaid items. A local original-poster backup also marks an item as overlaid, even if its `Overlay` tag is empty or has been removed on the server.

Preserve `config/overlays/<library mapping name> Original Posters/` together with the configuration's SQLite `.cache` file when moving Kometa. Backups store original artwork; the cache stores applied overlay definitions, values, and comparisons. Metadata YAML backups do not include that state. Image backups are associated with Emby item IDs, not TMDb or TVDb IDs; a catalog rebuild can change those associations.

`assets_for_all` and poster operations using `ignore_overlays` preserve overlaid posters. During removal, Kometa restores a matching local asset or saved original before deleting the backup. A failed upload keeps the backup. `remove_overlays: true` requests removal during the overlay stage; commenting out overlay definitions alone does not remove them. Episode overlays use landscape canvases.

Local images upload directly, while remote artwork URLs are sent to Emby for download. Kometa retries transient fixed-slot replacements and checks the backdrop list before retrying an interrupted background download. Changed or unverifiable lists remain errors. If Emby itself returns HTTP 500 when serving an original poster, Kometa cannot render that overlay; it reports the item error and continues with other items. Replacing the artwork or investigating the Emby logs may be necessary.

## Metadata, ratings, and maintenance

Native operations support the documented metadata destinations, sources, mappings, and schedules. Native metadata-file restore accepts regular backup attributes, not every Plex metadata-file directive. See [native mass metadata operations](native_metadata.md) for the supported field and control combinations.

Emby exposes generic community/audience and critic scores. Kometa uses its standard 0–10 scale, converting native critic percentages as needed. Sources `emby_audience`, `emby_critic`, and `emby_user` read stored server scores without assuming which provider populated them.

Emby supports individual original-title and community/critic-rating locks that the Jellyfin adapter cannot expose. Emby also accepts clearing numeric personal ratings. These differences do not make Emby field locks identical to Plex's; unsupported lock-only and date-clearing controls are rejected or reported as described in the native metadata reference.

`split_duplicates` separates grouped versions using the Emby alternate-source endpoint. It does not delete media files or merge separate catalog entries. Plex clean-bundles, empty-trash, and optimize operations are skipped. Theme-song and theme-video uploads are unsupported by this adapter.

## Caching and failures

Saved catalogs and item details are scoped to the server, credentials, user, and library. A lightweight server-ID listing validates membership before catalog reuse. Added and removed IDs trigger a refresh and are logged; unchanged membership preserves cached metadata until expiration or explicit refresh. Native metadata writes patch matching cache records, and artwork writes invalidate the affected detail record.

Transient connection and gateway failures have bounded retries. Persistent failures still surface: image-operation errors name the artwork type, and a catalog read failure can stop that library's processing. Retrying does not repair broken server artwork or guarantee that a reverse proxy remains available.

See also [Jellyfin differences](jellyfin_differences.md) and [Silo differences](silo_differences.md).
