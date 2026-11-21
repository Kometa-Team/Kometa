# Jellyfin: differences from Plex

This page describes how the Jellyfin adapter differs from the Plex adapter in Kometa. It covers Kometa behavior, rather than every feature available in Jellyfin itself. Use the [connection reference](jellyfin.md) for setup and the full list of supported search fields.

## Connecting and selecting a library

Define a `media_servers` entry with `type: jellyfin`, then select it with the library's `server` attribute. A Jellyfin-only configuration does not need a root `plex` block; `tmdb` is still required. Use an API key for `token`. The optional `user` selects the account used for catalog, playlist, and personal-rating calls; otherwise Kometa selects the first administrator.

Use `jellyfin_all` for native all-item builders. Supported uses of `plex_all` and `plex_search` remain available for compatibility, but those names do not make a Jellyfin library accept arbitrary Plex filters or URLs.

## Collections, searches, and defaults

| Plex-oriented behavior | What happens on Jellyfin |
| :--- | :--- |
| Native smart collections | Supported `smart_filter` definitions become ordinary boxset collections, rebuilt when Kometa runs. They do not update continuously between runs. |
| Plex smart-filter URLs and addresses | Not accepted. Replace them with supported local search fields or builders. |
| Smart labels | Supported simple `smart_label` definitions become ordinary collections. Additional label conditions and unsupported selectors still produce errors. |
| Collection visibility and Plex collection modes | They have no native equivalent. Shared mass collection-mode settings warn and skip. |
| Collection metadata providers | New collections are metadata-locked to prevent automatic franchise matches from replacing their names. Existing provider-renamed collections can be recovered only when the original boxset folder uniquely matches the requested name. |
| Collection sort title | Uses the Jellyfin custom sort-name field. Client browsing preferences can override the configured display order. |
| People, genre, country, and classification defaults | Discovery uses metadata populated on Jellyfin. Missing credits or classifications are not filled automatically by discovery. Enabling several classification-country defaults does not translate stored ratings. |
| TV studio defaults | TV `studio` dynamic collections are skipped; use `network` for the values stored in show `Studios`. Movie studio defaults remain supported. |

Supported searches and collection filters are evaluated against native catalogs and media details. Missing metadata does not match, including negative filters. Unknown fields and unsupported Plex options report errors. See [search and filtering fields](jellyfin.md#search-and-filtering-fields) before moving an existing Plex definition unchanged.

## Labels, overlays, and local state

Kometa maps labels to Jellyfin tags. Those tags can mark Kometa-managed collections and overlaid items. Original-poster backups also count as overlay markers, so an item can still be treated as overlaid when its `Overlay` tag is absent.

Keep `config/overlays/<library mapping name> Original Posters/` and the configuration's SQLite `.cache` file when moving an installation. Backups preserve original artwork; cache records preserve applied overlay definitions and values. A metadata YAML backup does not contain either. Backup filenames use Jellyfin item IDs rather than provider IDs, so rebuilding the server catalog can break those associations.

`assets_for_all` and poster operations with `ignore_overlays` protect posters identified as overlaid. Removing an overlay restores a matching asset or saved original, then deletes the backup after a successful upload. Disabling overlay definitions alone does not request removal; use `remove_overlays: true` and run the overlay stage. Native episodes use landscape overlay canvases.

Local artwork is uploaded directly. For remote URLs, Jellyfin downloads the image. Kometa retries transient fixed-slot replacements; backdrop retries first check that the server image list is unchanged. An uncertain result remains an error to avoid blindly appending another backdrop.

## Metadata, ratings, and maintenance

Native metadata operations support the documented sources, mappings, schedules, and destinations, rather than all Plex field controls. Metadata-file restore supports the regular backup attributes; it is not a complete implementation of every Plex metadata-file directive. See [native mass metadata operations](native_metadata.md).

Jellyfin has generic audience/community and critic score destinations. Kometa normalizes scores to its usual 0–10 scale. The `jellyfin_audience`, `jellyfin_critic`, and `jellyfin_user` sources read scores already stored on this server; the generic score slots do not identify an external provider.

Jellyfin does not expose the same individual lock fields as Plex. Lock-only requests for original titles and community/critic scores are unsupported. Clearing a numeric personal rating is also unsupported because Jellyfin ignores the null value. Supported individual locks and existing unrelated locks are preserved.

`split_duplicates` separates grouped alternate versions through the native Jellyfin endpoint; it does not delete files or find separate duplicate catalog entries. Plex clean-bundles, empty-trash, and optimize operations do not run on Jellyfin. Theme-song and theme-video uploads are unsupported by this adapter.

## Caching and external changes

With caching enabled, catalogs and details persist between runs. Before reusing a catalog, Kometa checks its current server item IDs. Added or removed IDs trigger a fresh catalog and are logged with titles and IDs. Unchanged membership retains cached metadata, so external metadata and playback changes require expiration or an explicit refresh. Cache identity includes the server, credentials, user, and library; a Plex cache is not reused as a Jellyfin cache.

See also [Emby differences](emby_differences.md) and [Silo differences](silo_differences.md).
