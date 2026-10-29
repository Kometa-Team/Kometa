# Native mass metadata operations

`mass_metadata_update` uses the same provider sources, mappings, source order, and schedules for Silo, Jellyfin, and Emby as for Plex where the destination can represent the change. Supported changes go to native APIs rather than Plex batch-edit endpoints. Unsupported destinations and controls are reported during configuration, before scanning items. A supported write that the server rejects is reported with the item name while other metadata writes can continue.

| Operation | Silo | Jellyfin / Emby |
| :--- | :--- | :--- |
| `genre.source`, `genre.mappings` | Supported | Supported |
| `content_rating.source`, `content_rating.mappings` | Supported | Supported |
| `original_title` | Supported, including TMDb, AniDB, MAL, and literal titles | Supported, same sources |
| `studio` | Supported | Supported |
| `originally_available` | Movie release date, series first air date, or child air date | Premiere date |
| `added_at` | Not supported: no writable added-date field | Supported |
| `ratings` | Explicit named Silo targets and profile stars; see [Silo ratings](silo.md#mass-rating-updates) | Generic audience, critic, user, and episode ratings |
| `labels.severity` | Not supported: no item labels | Supported using tags; unrelated tags remain |
| `poster`, `background`, `logo` | Supported | Supported |
| `square_art` | Not supported: no corresponding artwork slot | Supported using the thumbnail slot |
| `collections.mode` | Not supported: no Plex collection visibility modes | Not supported: no Plex collection visibility modes |
| `backup` | Native snapshot | Native snapshot |

Provider values use their existing Kometa scales. Jellyfin/Emby critic scores convert the normalized 0–10 value to the native 0–100 field; audience and personal ratings remain 0–10. Profile-rating writes preserve current playback, favorite, and other user state. Silo keeps its named provider and whole-star rating rules. Native genres, classifications, studios, and dates can be combined into one write per item rather than being replayed through Plex's batch editor.

## Lock and clear controls

Jellyfin and Emby support locks for the corresponding native fields, including genres, classifications, original titles, studios, and community/critic ratings. Existing unrelated locks are preserved. `remove` clears and locks a supported field, while `reset` clears and unlocks it. Native date fields do not expose those individual locks: lock-only controls are rejected; remove/reset clear the value and report that the lock component is not supported. Numeric personal ratings have no field locks; use `clear` to remove a personal rating.

Silo's API exposes numeric lock identifiers without a field-name mapping used by this adapter. Kometa preserves those identifiers. Lock-only changes are reported as not supported. For ordinary metadata fields, remove/reset clear the value and report that the lock component is not supported. Silo's explicit rating targets instead use `clear` and reject the Plex-style remove/reset controls.

## Artwork

Native artwork updates retain provider selection, local assets, source order, language selection, and supported season/episode artwork. Native show, season, and episode files use the standard asset folder names and `Season01` / `S01E01` file names. `ignore_overlays` for posters checks server labels where available and local overlay backups, including on Silo. `ignore_locked` on Jellyfin/Emby also recognizes the item's global metadata lock.

The `plex` image provider and Plex per-image lock/unlock controls are not supported on native servers. YouTube Music image sources require the Plex music workflow and are reported as unsupported by these native adapters. Silo cannot honor `ignore_locked` for artwork with the available lock identifiers, so an image operation requesting that guarantee is skipped with an explicit message. Unsupported sources are removed from a source list; supported alternatives can still run.

## Native backups

Native backups contain a `native_metadata` section, grouped by server/library and stable item ID. They include supported metadata, provider IDs, ratings, and reported lock state; shows include season and episode records. Repeated titles do not overwrite one another. `exclude` and `add_blank_entries` are honored. `sync_tags` is a Plex metadata-file instruction, so it is reported as unsupported; native snapshots already store complete tag values.

These are native metadata snapshots, not Plex-compatible metadata files or automatic restore instructions. Artwork bytes and playback history are not included. The output avoids copying stream delivery URLs or authentication headers. Existing unrelated sections of the backup file are preserved.

The mappings follow the [Silo API contract used by the adapter](silo.md), [Emby item metadata](https://dev.emby.media/reference/pluginapi/MediaBrowser.Model.Dto.BaseItemDto.html), [Emby lock fields](https://dev.emby.media/reference/pluginapi/MediaBrowser.Model.Entities.MetadataFields.html), and [Jellyfin item metadata](https://kotlin-sdk.jellyfin.org/dokka/jellyfin-model/org.jellyfin.sdk.model.api/-base-item-dto/index.html).
