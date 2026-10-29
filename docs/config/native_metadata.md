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

Both servers support individual locks for genres, classifications, studios, and tags. Emby additionally supports original-title and community/critic-rating locks; Jellyfin does not expose those lock-field names. Unsupported lock-only requests are rejected during configuration. Existing unrelated locks are preserved. `remove` clears and locks a supported field, while `reset` clears and unlocks it. Native date fields do not expose those individual locks: lock-only controls are rejected. For release dates and other writable values without individual locks, remove/reset clear the value and report that the lock component is not supported. Added dates can be replaced, but remove/reset are rejected rather than claiming to clear a date that the server retains. Numeric personal ratings have no field locks. Emby accepts `clear`; Jellyfin ignores null numeric personal scores, so its `user` and `episode_user` clear operations are rejected during configuration. Community and critic scores can still be cleared on both servers.

Silo's API exposes numeric lock identifiers without a field-name mapping used by this adapter. Kometa preserves those identifiers. Lock-only changes are reported as not supported. For ordinary metadata fields, remove/reset clear the value and report that the lock component is not supported. Silo's explicit rating targets instead use `clear` and reject the Plex-style remove/reset controls.

## Artwork

Native artwork updates retain provider selection, local assets, source order, language selection, and supported season/episode artwork. Native show, season, and episode files use the standard asset folder names and `Season01` / `S01E01` file names. `ignore_overlays` for posters checks server labels where available and local overlay backups, including on Silo. `ignore_locked` on Jellyfin/Emby also recognizes the item's global metadata lock.

The `plex` image provider and Plex per-image lock/unlock controls are not supported on native servers. YouTube Music image sources require the Plex music workflow and are reported as unsupported by these native adapters. Silo cannot honor `ignore_locked` for artwork with the available lock identifiers, so an image operation requesting that guarantee is skipped with an explicit message. Unsupported sources are removed from a source list; supported alternatives can still run.

## Native backups

Native backups use the regular `metadata` file format and public metadata field names. Movies use TMDb IDs and shows use TVDb IDs when available, otherwise using IMDb or title/year matching. Seasons and episodes are nested by number. `exclude`, `add_blank_entries`, and `sync_tags` are honored; `sync_tags: true` writes `.sync` tag attributes, including empty lists to clear tags. Internal server IDs, raw API fields, and lock-state records are not exported as metadata attributes. Existing `native_metadata` snapshots are retained when present, but new backups write to `metadata`. Silo, Jellyfin, and Emby can apply their supported backup attributes through `metadata_files`, including nested seasons and episodes. Plain tag entries add values; `.remove` removes values; `.sync` replaces the list and accepts an empty list to clear it. Scalar ratings use the regular 0–10 scale. Other metadata-file features, such as provider-driven edits and artwork directives, are not yet supported by this native restore path and produce an explicit error. Silo restores text, dates, studios, genres, countries, and personal ratings through its native APIs. Personal ratings are exported on the regular 0–10 scale and converted back to Silo’s 1–5 stars on restore. Regenerate older Silo backups containing personal ratings to obtain the corrected scale. Generic critic/audience scores and browser-only tag fields are rejected on Silo; use native rating operations for provider scores.

The output uses the same metadata syntax as Plex backups. Artwork bytes, playback history, and raw server-specific fields are not included. Existing unrelated sections and custom metadata attributes are preserved. The regular `studio` attribute holds one studio, so only the first reported studio is exported.

The mappings follow the [Silo API contract used by the adapter](silo.md), [Emby item metadata](https://dev.emby.media/reference/pluginapi/MediaBrowser.Model.Dto.BaseItemDto.html), [Emby lock fields](https://dev.emby.media/reference/pluginapi/MediaBrowser.Model.Entities.MetadataFields.html), and [Jellyfin item metadata](https://kotlin-sdk.jellyfin.org/dokka/jellyfin-model/org.jellyfin.sdk.model.api/-base-item-dto/index.html).

## Jellyfin and Emby API audit

The metadata mappings use native item fields: `Genres`, `OfficialRating`, `OriginalTitle`, `Studios`, `PremiereDate`, `DateCreated`, `Tags`, `CommunityRating`, and `CriticRating`. Metadata writes preserve the remaining item document and unrelated locks. Personal scores go through user-data endpoints and preserve playback and favorite state. Episode ratings use the same native fields, with TMDb episode provider IDs or a positional fallback when the external score is requested. Poster/background/logo/square artwork uses Primary/Backdrop/Logo/Thumb image endpoints. Backups use the regular metadata format described above.

The existing generic rating **targets** remain `audience` (community score), `critic`, `user`, and their `episode_` counterparts. These servers do not expose separate writable IMDb/TMDb rating slots. `CustomRating` is a parental classification override, not a numeric rating; likes/dislikes and favorites are separate user-state fields and are not automatically converted into scores.

The following additional rating **sources** read the configured server's stored scores:

| Jellyfin source | Emby source | Native value / Kometa scale |
| :--- | :--- | :--- |
| `jellyfin_community` | `emby_community` | `CommunityRating`, 0–10 |
| `jellyfin_audience` | `emby_audience` | Alias for the community source |
| `jellyfin_critic` | `emby_critic` | `CriticRating`, 0–100 converted to 0–10 |
| `jellyfin_user` | `emby_user` | Numeric personal Rating, 0–10 |

These sources work in mass rating updates and the ratings overlay default. Sources require the matching server type; unsupported cross-server sources are rejected before item processing. Missing or invalid scores do not overwrite the destination. Zero is preserved as a valid numeric score. Provider identity is not inferred from a stored community/critic value, so overlay defaults use generic audience/critic artwork rather than claiming a particular provider.

```yaml
operations:
  mass_metadata_update:
    ratings:
      critic: imdb
      audience: tmdb
      user: jellyfin_community
      episode_audience: tmdb
```

### Version splitting

`split_duplicates: true` is supported by the Jellyfin and Emby adapters using `DELETE /Videos/{itemId}/AlternateSources`. This separates alternate versions; it does not delete media files. Failed splits are reported with the item title while other items continue. After a successful split, Kometa reloads items and provider-ID mappings and discards stale search/detail caches. Server permissions and native grouping rules still apply. Silo splitting remains unsupported because its repair API requires explicit file and target selections.

This audit follows [Jellyfin item updates](https://github.com/jellyfin/jellyfin/blob/master/Jellyfin.Api/Controllers/ItemUpdateController.cs), [Jellyfin lock fields](https://github.com/jellyfin/jellyfin/blob/master/MediaBrowser.Model/Entities/MetadataField.cs), [Jellyfin user-data updates](https://github.com/jellyfin/jellyfin/blob/master/Emby.Server.Implementations/Library/UserDataManager.cs), [Emby item metadata](https://dev.emby.media/reference/pluginapi/MediaBrowser.Model.Dto.BaseItemDto.html), [Emby user-data updates](https://dev.emby.media/reference/RestAPI/PlaystateService/postUsersByUseridItemsByItemidUserdata.html), and [Emby version splitting](https://dev.emby.media/reference/RestAPI/VideosService.html).
