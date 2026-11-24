# Silo: differences from Plex

This page describes how Kometa's Silo adapter differs from its Plex adapter. The differences apply to what Kometa implements through Silo's API, rather than every feature in the Silo application. See the [Silo connection reference](silo.md) for setup, fields, and examples.

## Connecting and selecting a library

Define a `media_servers` entry with `type: silo`, then select it with the library's `server` attribute. A Silo-only configuration does not require a root `plex` block; `tmdb` remains required. Kometa uses Silo's v2 API and the profile selected by `profile_id` or a unique `profile_name`. Credentials and profile affect the catalog and personal ratings that Kometa can see.

Use `silo_all` for native all-item builders. Supported `plex_all` and `plex_search` definitions are compatibility forms, not a connection to Plex or a guarantee that every Plex field is available.

## Collections, searches, and defaults

| Plex-oriented behavior | What happens on Silo |
| :--- | :--- |
| Smart collections | Silo accepts its own query documents under `smart_filter`. Supported rules can create native smart collections. Rules requiring local evaluation become ordinary collections rebuilt on Kometa runs, with the fallback logged. |
| Plex smart-filter addresses | Not accepted. Use native query documents or supported metadata rules. |
| Item labels | No equivalent is exposed by the adapter. Label-based selectors and writes are unavailable. |
| Collection sort titles and labels | These options warn and skip; supported metadata and artwork continue. |
| Collection visibility | `visible_library` manages a library section, `visible_home` manages the acting profile's Home row, and `visible_shared` manages the default Home row for other profiles. Personal overrides remain in effect. See [promotion settings](silo.md). |
| Configured collection tracking | Collection names are compared with the current configuration. This does not record who created a collection. |
| Managed collection tracking | No `Kometa` or `PMM` ownership label is written. Silo collections are treated as unmanaged by the shared label-based checks. |
| Playlists and item deletion | Unsupported by this adapter. Deleting a collection is a separate supported operation. |

Discovery and filters read the selected library/profile's native metadata. Missing values are not manufactured, and unsupported fields report errors. Available genres, studios, networks, countries, keywords, and people are searchable metadata, not Kometa management labels. File paths and other technical fields require the acting account to have access to those details.

Country, region, and continent defaults use native country facets. Network defaults use Silo's stored network metadata. See the [supported search fields](silo.md#search-and-filter-fields) when adapting Plex collection or overlay definitions.

## Overlay tracking without server labels

Kometa uses local state in place of an `Overlay` label:

| Local state | Purpose |
| :--- | :--- |
| `config/overlays/<library mapping name> Original Posters/<Silo item ID>.jpg`, `.png`, or `.webp` | Saves the original poster and identifies that item as overlaid. |
| Library-specific SQLite cache records | Store applied overlay definitions, resolved values, and poster comparisons for later runs. |

Preserve both when moving Kometa. A metadata YAML backup does not contain the image files or tracking records. Mapping names come from the library keys in the Kometa configuration; changing a key changes its backup directory. Files are associated with Silo item IDs, not external provider IDs. A new installation or rebuilt catalog does not automatically rediscover that association.

`assets_for_all` and poster operations using `ignore_overlays` recognize local backups and protect those posters. Overlay removal restores a matching local asset or original backup, then deletes the backup and saved overlay state after success. Failed uploads keep the backup. Setting `remove_overlays: true` and running the overlay stage requests removal; merely disabling overlay definitions does not.

Deleting only the cache can cause overlays to render again, but retained originals still identify overlaid items. Deleting the backups loses that marker and the saved originals; cache records alone do not identify Silo items for removal. See [tracking without labels](silo.md#tracking-without-labels) for recovery details and the consequences of `delete_collections.managed` filters.

## Artwork delivery

Silo receives artwork through URLs. Kometa publishes local posters, assets, and rendered overlays to [transfer.kometa.wiki](https://transfer.kometa.wiki), then asks Silo to download them. Unlike a direct Plex upload, this requires the transfer host and Silo to be able to reach the published image. Existing remote URLs, such as provider artwork, go directly to Silo.

Publishing local images includes a short delay to respect the transfer host's rate limit. Optional `pace_requests: true` also spaces Silo API requests. These are separate controls; retries and other clients can still affect throughput. See the connection reference for timing details.

## Metadata, ratings, and maintenance

Silo stores named provider scores rather than Plex's generic critic and audience slots. Use `silo_imdb`, `silo_tmdb`, `silo_tomatoes`, or `silo_tomatoesaudience` targets. Generic critic/audience and episode rating targets are unsupported. Stored provider values can also supply overlays without additional external rating requests.

Personal ratings use the acting profile's whole 1–5 stars. Kometa accepts its usual 0–10 scores, divides by two, rounds half values upward, and clamps to 1–5 stars; use `clear` to remove a rating. Values can therefore lose precision compared with Plex. Backup and restore normalize personal ratings to the regular 0–10 metadata format.

Metadata operations and restores cover the attributes listed in [native mass metadata operations](native_metadata.md). Silo's opaque lock identifiers are preserved rather than edited as Plex field locks. Artwork operations requesting an unsupported `ignore_locked` guarantee are skipped explicitly.

Plex maintenance operations do not run on Silo. Automatic `split_duplicates` is unsupported because Silo's grouping repair requires explicit file and target selections. Theme-song and theme-video uploads are also unavailable through this adapter.

## Caching and external changes

Catalogs, details, and resolved provider IDs persist when caching is enabled, scoped to the server, credentials, profile, and library. External additions and playback changes become visible after cache expiration or explicit refresh. Successful native writes invalidate persisted data for that scope. Unlike the Jellyfin/Emby catalog path, Silo does not perform the same fresh server-ID comparison before every saved catalog reuse.

See also [Jellyfin differences](jellyfin_differences.md) and [Emby differences](emby_differences.md).
