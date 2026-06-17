# Changelog

All notable changes to Kometa will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased - Currently in Nightly or Develop]

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Comprehensive config validation with `--validate`, `--validate-level`, `--validate-schema`, and `--schema-path` CLI flags. Supports syntax, structure, full, and schema-level validation with a gap report showing missing/extra fields. - `--validate` implies an immediate run, like `--run-libraries`.
- `--validate-file` and `--validate-dir` CLI flags for standalone and batch YAML validation against auto-detected schema types: config, collection, metadata, overlay, and playlist. Output is written to `validate.log`.
- `modules/validator.py` with `ConfigValidator` for multi-level config validation and `FileSetValidator` for standalone/batch YAML validation with schema type detection.
- Expanded `json-schema/config-schema.json` with full coverage and added per-type schemas: `collection-schema.json`, `metadata-schema.json`, `overlay-schema.json`, and `playlist-schema.json`.
- Plex square art support: upload `square.ext` assets for movies, shows, seasons, albums, and playlists via `find_and_upload_assets`. Extends metadata file items and library operations.
- `apprise` and `schedule_overlays` to the config JSON schema.
- `plex_csm` and `plex_csm0` sources to `mass_content_rating_update`, reading CSM age ratings from Plex's own cached `commonSenseMedia.ageRatings` without requiring an external API key.
- GraphQL support for IMDb charts retrieval, with a fallback to the old method if the GraphQL request fails. (Fixes #3006)
- New `text_file` builder.
- Spellcheck to the pre-commit configuration.
- `language` parameter to `mass_poster_update` and `mass_background_update` operations to override TMDb language for image fetching, for example `xx` for textless posters.
- Reporting for deactivated Trakt accounts when Trakt returns a 410.
- Batched collection alterations for add/remove operations in groups of 100 to avoid `400 Bad Request` errors on very long URLs.
- Early exit if more than one `--SOMETHING-only` flag is set.
- People data caching for media items, since it is unlikely to change.
- Initial support for SIMKL.com, including trending lists and the DVD releases list.
- Letterboxdpy-backed adapter for Kometa's existing Letterboxd builders, preserving existing Letterboxd builder names.
- Apprise as a webhook notification provider.
- Extended default `Metacritic Must See` collection to work with TV.
- Support for boxd.it short urls for Letterboxd share lists
### Changed

- The `tmdb_discover` YAML validator now rejects unknown keys, checks value types, requires `certification_country` and `certification` to co-occur, requires `watch_region` with any watch-provider or monetization key, and enforces mutual exclusivity between movie-only and TV-only parameters.
- `with_watch_providers` and `without_watch_providers` now require `watch_region` at validation time, matching the TMDb Discover API requirement. This is stricter than the runtime check in `builder.py`.
- SQLite cache is now used for TMDb queries in `check_filters` and `check_missing_filters` instead of bypassing it with `ignore_cache=True`.
- Plex items are only force-reloaded in the overlay loop when `reapply_overlays` is set; normal runs reuse the session cache.
- Collection membership checks in `add_to_collection` and `run_collections_again` now use set lookups instead of list scans, reducing complexity from O(n×m) to O(n).
- Quickstart docs updated to explain limitations.
- Trakt and MAL flow pages updated.
- Letterboxd builder docs updated to reflect letterboxdpy-backed filtering, ordering, and incremental behaviour.
- Valid `font_style` values for the default Inter font are now documented, with a note that valid styles are font-specific. (Fixes #2925)
- Schema documentation now explicitly calls out that the schema file only supports `config.yml`.
- E4 added to the network overlay and show network collection. (Fixes #2975)

### Removed

- Reciperr builder because the site has not responded for a while.

### Fixed

- TMDb collection, movie, and show 404 responses now raise a dedicated `tmdb.NotFound`, mirroring the existing `tvdb.NotFound` pattern. `validate_tmdb_ids` now logs an actionable hint for stale collection IDs pointing franchise-default users to the `exclude` template variable.
- TVDb 5xx server errors now raise `TVDbServerError`, which allows tenacity to retry them up to 6 times instead of aborting the item after a single flaky 5xx response.
- Letterboxd list/watchlist parsing has been updated for the React-based `LazyPoster` markup, which replaced the `data-film-id` nodes used by the `letterboxd_list`, `letterboxd_user_films`, and `letterboxd_user_reviews` builders.
- `KeyError` on Plex NFO build.
- `list index out of range` error when processing IMDb charts. (Fixes #3006)
- TMDb language is now reflected in `mass_poster_update`; cache extension updated.
- FILMIN logo size reduced.
- FILMIN white logo size reduced.
- Top-ten-pirated default list replaced with an updated Kometa-controlled list.
- Streaming default's `run_definition` now honours `use_all: false`; previously, dynamic keys without an explicit `use_<key>` ran regardless. (Fixes #2922)
- Overlay backdrops with `back_line_color` set but no `back_line_width` no longer crash; `back_line_width` now defaults to 1 in that case. (Fixes #2645)
- `trakt_chart` watched/collected URLs now use `/movies/watched/{period}`, `/shows/watched/{period}`, `/movies/collected/{period}`, and `/shows/collected/{period}`. The default period is now `weekly`, and recommendations now use `/recommendations/movies` and `/recommendations/shows`. (Fixes #3057)
- TVDb 4xx responses for series/movies removed or merged on TVDb now raise a dedicated `tvdb.NotFound`, so missing-show iteration and TVDb-filter paths log them at debug instead of error. Stale TVDb IDs returned by TMDb `external_ids` no longer spam logs or trigger webhook failure notifications. (Fixes #3047)
- Kometa's AniList season translation from `current` now matches AniList.
- Cached Plex items are now invalidated after each batch edit in operations so the overlay phase reads post-operation values, such as updated ratings, instead of stale pre-operation values. This fixes rating overlays not updating when `mass_critic_rating_update`, or audience/user equivalents, runs before overlays in the same Kometa pass. (Fixes #2357)
- MDBList Sync Progress percentage no longer overflows for lists over 1000 items, for example `6378/378 (1687%)`. List metadata is now fetched upfront to get the true total item count. (Fixes #3157)
- `Movies Removed` report entries no longer miss the release year; titles now match the `Movies Missing` format, for example `The Grapes of Wrath (1939)`. (Fixes #2028)
- When `run_order` places `operations` before `collections`, configured collections are no longer incorrectly reported as unconfigured by `show_unconfigured` or targeted by `delete_collections: configured: true`. (Fixes #1968)
- Letterboxd Top 100 Western now uses the official list.
- TMDb collection requests that return 404 because the collection was deleted upstream now raise a dedicated `tmdb.NotFound`. When the ID was auto-discovered by a default, such as the `franchise` default scanning `tmdb_collection` IDs from the library, the collection is skipped as `Ignored` instead of failing with a critical error and webhook notification. IDs in user-authored config files still raise as before.
- Dynamic collection titles with unresolved template variables in `title_format`, such as `<<limit>>` from a template `default:` block or `<<key>>` from per-key dynamic variables, no longer cause `delete_collections: configured: true` to incorrectly treat those collections as unconfigured and delete them. (Fixes #1904)
- `mass_imdb_parental_labels` now uses IMDb's GraphQL API instead of scraping `/parentalguide`, avoiding silent label failures caused by IMDb's CloudFront WAF returning HTTP 202 with an empty body. (Fixes #3053)
- `ZeroDivisionError` crash in `plex_update_in_batches` when running `mass_genre_update`, `mass_imdb_parental_labels`, or any operation producing multiple label/genre groups per item. Cache eviction introduced by #3156 is now scoped to rating updates only via an `evict_cache` parameter, and a defensive guard prevents future empty-list crashes. (Fixes #3163)

## [v2.3.1] - 2026-04-01

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Switching to using GraphQL for IMDB charts retrieval, with a fallback to the old method if the GraphQL request fails. #3006
- Added new `text_file` builder.
- Reciperr site hasn't responded for a while, so the builder has been removed.
- Added spellcheck to precommit configuration
- Added `language` parameter to `mass_poster_update` and `mass_background_update` operations to override TMDb language for image fetching (e.g. `xx` for textless posters)

### Fixed

- Catch KeyError on Plex NFO build.
- Fixing "list index out of range" error when processing imdb charts #3006
- TMDB language now reflected in mass_poster_update; cache extension
- Reduce size of FILMIN logo
- Replace top-ten-pirated default list with an updated, kometa-controlled one.

## [v2.3.0] - 2026-02-09

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added `|` as a preferred delimiter for run times.
- Added an optional setting `plex_bulk_edit_batch_size` in operations to control how many items are processed in a single batch.
- Added new filters `show_title` and `season_title`
- Added Producer's Cut to resolution/edition default overlay
- Added incremental parsing support to Letterboxd `user_films` and `user_reviews` builders for improved performance with large collections
- Change MDBList module to use API rather than JSON endpoint.
- Add visible (X/Y) logging while processing missing items.
- Add new `mal_all` genre option to include Explicit Genres, Themes and Demographics.
- Replace AniDB scraping with purpose-built cache server. Removed popular builder. (Fixes #2932)
- Removes authentication-related AniDB configuration entries.
- IMDB "Document is empty" no longer CRITICAL

### Changed

- Python 3.9 is no longer supported as it is End-of-Life, please use Python 3.10+
- Sync MDBList sort options with MDBList API Docs
- Add docs around Plex token types, add Plex Token generation form
- Tweak AniDB docs to reflect loss of tag builder and reduced config.

### Fixed

- Fix a logic error that caused an infinite loop on reauthentication with private Trakt Lists
- Pin dockerfile to Python 3.13.x, since 3.14.1 introduces memory bloat issues
- Improve API-based handling of MDBList "external" lists.
- Sync MDBList sort options with MDBList API Docs
- Update several networks to cater for updated names
- Adjust behavior of `mdb_commonsense` and `mdb_commonsense0` content rating operations to reflect current response from MDBList.

## [v2.2.2] - 2025-10-06

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added `|` as a preferred delimiter for run times.
- Added an optional setting `plex_bulk_edit_batch_size` in operations to control how many items are processed in a single batch.
- Added new filters `show_title` and `season_title`
- Added Producer's Cut to resolution/edition default overlay

### Changed

- Sponsor's Images are now listed on the ReadMe, Wiki Homepage, and acknowledgements page.
- Updated the Sponsorship Tier Rewards (credit to @mrbuckwheet for sponsoring and driving the updates)
- Fixed an issue where the home page logo and shield images appeared as raw text
- Fixed an issue where the builder overview page had multiple dead links
- Added some clarification on Library types to defaults pages
- Add Movistar Plus + as streaming service
- Add Atres Player as streaming service
- Add AMC+ as streaming service
- Add Filmin as streaming service
- Update BAFTA Best Films to include BAFTA Award for Best Film From Any Source
- separators placeholder now work with minimum items. (Fixes #2806)

### Fixed

- Don't assume details of the IMDb API response structure, offer "private list" as a possible cause of no IDs found
- Fix `overlay_special_text` cache table schema to use TEXT for `rating_key` to be consistent with other tables
- the list now acts as a list (Fixes #2802)
- Fixes logic issue with reauthenticating trakt
- Fixes an issue with the `dovi` attribute of `plex_search` where shows and seasons never returned anything
- Fixes `.regex` tag filters

## [v2.2.1] - 2025-08-13

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added `file_logo` and `url_logo` as metadata image options **credit to @Joost1991**
- Added support for updating logos via the asset directories as well **credit to @Joost1991**
- Added support for `dovi` search attribute for Plex builders (requires PMS 1.41.6.9606 or above)
- IMDb episodes found in a list for a show collection will now add that episode's show to the collection
- Added `force_refresh` Trakt setting; this tells Kometa to refresh the token on every run without checking it first
- Added a log of the response from Trakt which triggers the "No Valid Lists" error.
- Added `assets_for_all_collections` library operation; this tells Kometa to add asset artwork to unmanaged and unconfigured collections

### Changed

- Added overlay guide
- Added TrueNAS walkthrough
- Added notes on Github tokens
- Added screenshot of UNRaid Console menu
- [Franchise] Updates 'NCIS' list to include NCIS: Origins and NCIS: Tony & Ziva. Added 'Spartacus', 'Death in Paradise' and 'Reacher' to the franchise lists
- [Universe] Change the DC Animated Universe list to a mdblist

### Fixed

- Fixed an issue where Playlists could not add to both Radarr and Sonarr in a single run
- Fixed an issue where `trakt_list_details` would not find a list's summary if it was an "official" Trakt list
- Fixed an issue where log file paths with >2 periods would cause a ValueError
- Fixed an issue with IMDb Awards
- Restored image language settings after change in base image
- Fixed an issue with IMDb List and Watchlist

## [v2.2.0] - 2025-03-31

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added the `character` search option to the `imdb_search` builder
- Added ability to use Show-level ratings at the season and episode level for Overlays if the original source does not provide ratings at the season or episode level. This is accomplished using (Special Text Variables)[https://kometa.wiki/en/latest/files/overlays/#special-text-variables] but is not yet available for the `Ratings` Defaults file.
- Add `show_unfiltered` setting to display items which make it through a filter
- Allow `sync_to_trakt_list` on episode-level collections
- Logic added to Kometa to create `config.yml` if it does not exist from the `config.yml.template` file. If the template file cannot be found, Kometa will attempt to download it from GitHub.
- When using `mass_poster_update`, added `ignore_locked` and `ignore_overlays` attributes which will prevent Kometa from resetting the image if the poster field is locked (i.e. a previous mass poster update) or if the item has an Overlay. This can effectively act as a differential update system.
- When using `mass_background_update`, added `ignore_locked` attribute which will prevent Kometa from resetting the image if the poster field is locked (i.e. a previous mass poster update). This can effectively act as a differential update system.
- Added `date` option for schedules
- Added the `--low-priority/-lp` (`KOMETA_LOW_PRIORITY`) command line argument option to run the process at a lower priority. **credit to @planetrocky**
- Added `trakt`, `omdb_metascore`, `omdb_tomatoes` ratings sources for mass operations.
- Added `trakt` ratings source for mass episode operations.
- Added GitHub token validation during config validation.
- Added `plex` ratings source for mass operations.
- Add recently-added ratings sources to special-text overlays.
- Added IMDb Interests (sub-genres) to `imdb_search` builder
- Allow `server_preroll` to accept a list
- Changed default `overlay_artwork_filetype` to `webp_lossy` and `overlay_artwork_quality` to 90
- Added `ntfy` as a notification option
- Added `scale_width` and `scale_height` overlay options.
- Added `tmdb_deathday` **credit to @Kevin2kkelly**

### Changed

- Python 3.8 is no longer supported. The minimum version of Python required is now 3.9.
- Added "getting started" page
- Added page to describe all the YAML files
- Updated Synology page for DSM 7.2 and added a disclaimer about what it covers
- Added "undoing changes" page
- Added more detail to the "sorting" page
- Fixed incorrect content rating mappings in various Default files
- Fixes an issue where Prime Video overlays/collections would not be built when the `watch_region` is set to AU or NL
- Fixes an issue where Rotten Tomatoes Verified Hot wasn't working
- Updates `Alien vs Predator` and `X-Men` lists to new lists which include most recent releases
- Added `style` template variable for Streaming and Chart defaults, allowing user to choose color or white logos for collection posters
- Added `Paramount+ with Showtime` to both `Paramount+` and `Showtime` for Networks and Streaming, any existing weighting is unchanged.
- Added Aymara language with Bolivian flag to audio/subtitle overlay languages (credit to popeadam)
- Added `size` setting to languages overlay to double the overlay size.
- Added `hide_text` setting to languages overlay to only show the flags and hide the country text.
- Added `openmatte` edition to default resolution overlay.
- Added `Metacritic Must See Movies` to `other_chart`.
- Moved several `universe` and `playlist` default lists away from Trakt and over to IMDb and MDBList
- Removed default emojis from `seasonal` due to Plex issue with emojis and updated some lists
- Removed BritBox and replaced with ITVX in `streaming` following service shutdown

### Fixed

- Fixed the `cast` search option for the `imdb_search` builder
- `imdb_list` sort was not being parsed correctly (Fixes #2258)
- Fixes `letterboxd_list` rating filter to use a 1-10 rating vs 1-100 to reflect how letterboxd ratings work on their website
- Enhance handling of smart collections in deletion (Fixes #2274)
- Fixed the `ids_to_anidb` lookup for anime movies and shows
- Fixes an issue where episode overlays sometimes wouldn't be added
- Fixes an issue with IMDb Parental Labels not working
- Fixes an issue where OMDb returned `N/A` as the content rating
- Fixes an issue where `plex_collectionless` doesn't work if the item was added to a collection in the same run
- Added a page that discusses the different YAML files and what they do.
- Modifies default value presentation for default metadata files.
- Fixes an issue causing IMDB collection to fail due to duplicate keys
- Removed Blog from the Navigation due to lack of time for updating/maintaining it
- by updating version of tmdbapi dependency (Fixes #2354)
- Added Start Time, Finished and Run Time to Summary of run.
- Fixed an issue where custom repositories would not work correctly if the URL did not end in a trailing `/` character.
- Kometa will now check for `.yaml` extension in filenames if `.yml` is not found and vice-versa
- Log files will now follow the naming convention of `kometa.log`, `kometa-1.log` (previous run), `kometa-2.log` (2 runs ago) etc.
- Kometa will no longer automatically sync playlists to all users if you do not specify who you want to sync them to. Only the server admin will receive playlists unless otherwise specified using `sync_to_users` or `playlist_sync_to_users`
- `tmdb_person` would pass an integer if the name started with an integer (i.e. `50 Cent` would pass `50` which resolved to `Catherine Deneuve`) (Fixes #2385)
- Fixes an issue where `show_missing` would display missing movies against show libraries (closes #2351)
- Fixed an OMDb API issue where API key would intermittently be treated as invalid
- Fixed an issue where Kometa would try to upload and cache images larger than Plex allows (10mb is the upper limit)
- Fixes an issue where `use_subtitles` would ignore `flag_alignment: left`
- Fixed typo `radarr_tag_list` instead of `radarr_taglist` in `builder` module causing `Collection Error: radarr_taglist attribute is blank`
- Fixed NoneError when using a blank `radarr_taglist` or `sonarr_taglist`.
- Fixes an issue with boolean filter matching.
- Fixes an issue where the decade default collection names were incorrect.
- Fixes the playlist default to automatically work with a supplied list.
- Remove an unnecessary request to Plex while processing overlays.
- Fixes issue with ICheckMovies parsing.
- Fixes issue with Letterboxd parsing.
- Fixes issue with the `mojo_domestic` BoxOfficeMojo Builder.
- Fixes an issue updating Trakt User Ratings when the show doesn't exist on TVDb.
- count display issue (Fixes #2560)

## [v2.1.0] - 2024-09-30

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Introducing the [Kometa Blog](https://blog.kometa.wiki) - a new home for all kometa-related news stories, ranging from showcasing our community creations to providing you with important updates.
- Added [`letterboxd_user_lists`](https://kometa.wiki/en/latest/files/dynamic_types/#letterboxd-user-lists) Dynamic Collection Type
- Added `item_analyze` item detail to analyze each item in a collection

### Changed

- F1 session naming improvements
- Added new studios : Disney Television Animation, DisneyToon Studios, Dynamic Planning, Film4 Productions, Golden Harvest, Hungry Man, Screen Gems, Shaw Brothers, Studio Live, The Stone Quarry
- ; change xmen list to a new one (Fixes #2150)
- Added `A Quiet Place: Day One` to the `A Quiet Place` collection in the `franchise` Defaults file
- Add `minimum_items_<<key>>` to universe Default file
- Added workaround to `Streaming` for TMDb issue with TMDb Discover

### Fixed

- Fixed multiple anime `int()` Errors
- `verify_ssl` wasn't working when downloading images (Fixes #2100)
- Fixed an issue with `delete_collections` where items were being deleted if they only matched one criteria vs all criteria
- Fixed `imdb_watchlist`
- AniDB Builder type conversion error (Fixes #2135)
- Add handling for blank secrets (Fixes #2169)
- `clean_bundles`, `optimize`, and `empty_trash` not working as global attributes (Fixes #2176)
- `total_runtime` will now trigger an overlay update (Fixes #2186)
- an image on the docs was a dead link (Fixes #2195)
- Fixes sort order of resolution collections
- ".any" not accepted for a variety of imdb_search parameters (Fixes #2228)
- Fixes `streaming` defaults adding and removing items randomly
- Fixes missing TMDb Discover parameters
- Fixes `imdb_chart` error when using `trending_india`
- Added error information to help with #2201
- Added warning to TMDb Discover builder regarding ongoing bug with using `popularity.desc` as sort order

## [v2.0.2] - 2024-05-31

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Checks requirement versions to print a message if one needs to be updated
- Added the `mass_added_at_update` operation to mass set the Added At field of Movies and Shows.
- Add automated Anime Aggregations for AniDB matching
- Added `total_runtime` as a special text overlay variable.
- Added `top_tamil`, `top_telugu`, `top_malayalam`, `trending_india`, `trending_tamil`, and `trending_telugu` as options for `imdb_chart`
- Added the `sort_by` attribute to `imdb_list`

### Changed

- Changed the `overlay_artwork_filetype` Setting to accept `webp_lossy` and `webp_lossless` while the old attribute `webp` will be treated as `webp_lossy`.
- Added Letterboxd Default [Collections](https://kometa.wiki/en/latest/defaults/chart/letterboxd/) and [Ribbon](https://kometa.wiki/en/latest/defaults/overlays/ribbon/)

### Fixed

- `anilist_userlist` `score` attribute wasn't being validated correctly (Fixes #2034)
- Error when trying to symlink the logs folder (Fixes #1367)
- TMDb IDs were being ignored on the report (Fixes #2028)
- Fixes a bug when parsing a comma-separated string of ints
- Fixes `imdb_chart` only getting 25 results
- Fixes `imdb_list` not returning items

## [v2.0.1] - 2024-05-02

### Added

- Added `overlay_artwork_filetype` and `overlay_artwork_quality` settings to control the filetype and quality of overlay images. Users can select from JPG, PNG and WEBP.

### Changed

- Added `starting_only` template variable to the `mal` Collection Default.
- Changed streaming defaults to use names as their keys vs their TMDb IDs as keys
- Fixed `amazon` ID in `streaming` when region is `CA`

### Fixed

- Catch bad ID data from Plex
- Fixes `- git` file calls
- Ignore empty Environment Variables
- Fixes collections being deleted under certain conditions when using translations

## [v2.0.0] - 2024-04-25

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Add Page Topics Options to `imdb_search`
- Add `lxml` Docker Version using an old lxml version that supports more cpus

### Changed

- Plex Meta Manager is now rebranded as Kometa!
- Add `use_all` template variable to default collections, which allows all collections to be disabled with one variable.
- Let conditional `.not` and `.exists` work with default variables

### Fixed

- `download_url_assets` was causing `url_background` to upload as a poster (Fixes #1965)
- Ignore validating TPDb links (Fixes #1969)

## [v1.21.1] - 2024-04-22

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Add Page Topics Options to `imdb_search`
- Add `lxml` Docker Version using an old lxml version that supports more cpus

### Changed

- Let conditional `.not` and `.exists` work with default variables

### Fixed

- `download_url_assets` was causing `url_background` to upload as a poster (Fixes #1965)
- Ignore validating TPDb links (Fixes #1969)

## [v1.21.0] - 2024-04-04

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added new [BoxOfficeMojo Builder](https://metamanager.wiki/en/latest/files/builders/mojo/) - credit to @nwithan8 for the suggestion and initial code submission
- Added `monitor_existing` to sonarr and radarr. To update the monitored status of items existing in plex to match the `monitor` declared.
- Added [Gotify](https://gotify.net/) as a notification service. Thanks @krstn420 for the initial code.
- Added [Trakt and MyAnimeList Authentication Page](https://metamanager.wiki/en/latest/config/auth/) allowing users to authenticate against those services directly from the wiki. credit to @chazlarson for developing the script
- Added TVDb filters
- Cache TMDb Episode Calls
- Added Direct Rating Overlays without having to update the rating in plex
- Added TPDb Rate Limit

### Changed

- Reworked PMM Default Streaming [Collections](https://metamanager.wiki/en/latest/defaults/both/streaming) and [Overlays](https://metamanager.wiki/en/latest/defaults/overlays/streaming) to utilize TMDB Watch Provider data, allowing users to customize regions without relying on mdblist. This data will be more accurate and up-to-date now.
- As a result of this change, if you are using custom images with this defaults file, you must replace any mention of `<<key>>` in the filename with `<<originals_key>>`.
- Added new [`trakt_chart` attributes](https://metamanager.wiki/en/latest/files/builders/trakt/#trakt-chart) `network_ids`, `studio_ids`, `votes`, `tmdb_ratings`, `tmdb_votes`, `imdb_ratings`, `imdb_votes`, `rt_meters`, `rt_user_meters`, `metascores` and removed the deprecated `network` attribute
- Trakt Builder `trakt_userlist` value `recommendations` removed and `favorites` added.
- Mass Update operations now can be given a list of sources to fall back on when one fails including a manual source.
- `mass_content_rating_update` has a new source `mdb_age_rating`
- `mass_originally_available_update` has a new source `mdb_digital`
- `plex` attributes `clean_bundles`, `empty_trash`, and `optimize` can now take any schedule options to be run only when desired.
- Allows users to use the Admin username when specifying playlist users. Thanks @benbou8231!
- Allows `verify_ssl` to be set specifically for plex. Thanks @FestiveKyle!
- Updated Plex Item Advance Preferences.
- Add new [Overlay Special Text Options](https://metamanager.wiki/en/latest/files/overlays/#special-text-variables) to directly print ratings to overlays without operations.

### Removed

- Due to FlixPatrol moving a lot of their data behind a paywall and them reworking their pages to remove IMDb IDs and TMDb IDs the flixpatrol builders and default files have been removed. There currently are no plans to re-add them.

### Fixed

- Fixed the Rate Limit on MDbList calls
- Fixed collection fields being locked during batch edits when they shouldn't be
- Fixed awards dynamic collections where `latest` wasn't pulling the correct values
- Fixed `imdb_watchlist`
- Fixed `trakt_userlist`
- Fixed an issue where sometimes the resolution default overlay would be off center
- Fixed multiple issues with playlist deletion. Thanks @benbou8231!
- Fixed an issue where dynamic collection errors would sometimes appear before the title of the Dynamic Collection.
- Fixed IMDb Null issue
- Fixed mapper operations not working without a mass update operation
- Fixed episode rating mass update operations
- Fixed metadata backup issue where Artist, Album, and Track ratings were not being backed up
- Fixed an issue with the IMDb hash changing

## [v1.20.0] - 2024-01-07

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Introduced (Run Order)[https://metamanager.wiki/en/latest/config/settings/#run-order] attribute which allows the user to amend the way that each library is executed.
- Introduced [IMDb Search Builder](https://metamanager.wiki/en/latest/files/builders/imdb/#imdb-search) following IMDb UI rework.
- `imdb_list` can no longer be used for Title or Keyword Searches, these must be transferred to `imdb_search` builders.
- Introduced [IMDb Award Builder](https://metamanager.wiki/en/latest/files/builders/imdb/#imdb-award).
- Added IMDb Awards to [Dynamic Collection Types](https://metamanager.wiki/en/latest/files/dynamic_types/#imdb-awards)
- PMM Default `other_awards` has been deprecated and replace with new award PMM Default files:
- [`berlinale`](https://metamanager.wiki/en/latest/defaults/award/berlinale/) - Berlin International Film Festival Awards
- [`cesar`](https://metamanager.wiki/en/latest/defaults/award/cesar/) - César Awards
- [`nfr`](https://metamanager.wiki/en/latest/defaults/award/nfr/) - National Film Registry
- [`pca`](https://metamanager.wiki/en/latest/defaults/award/pca/) - People's Choice Awards
- [`razzie`](https://metamanager.wiki/en/latest/defaults/award/razzie/) - Razzie Awards
- [`tiff`](https://metamanager.wiki/en/latest/defaults/award/tiff/) - Toronto International Film Festival Awards
- [`venice`](https://metamanager.wiki/en/latest/defaults/award/venice/) - Venice Film Festival Awards
- Reintroduced [Flixpatrol Builder](https://metamanager.wiki/en/latest/builders/flixpatrol/) following introduction of paywalled API.
- Added a JSON Schema file which will assist users in validating their configuration file when using a code-aware text editor such as VSCode and VSCodium. This is a work in progress and will help identify basic errors such as specifying "yes" when the available options are "true" and "false"
- If you run into any validation issues which you don't understand, ask in our Discord Server

### Changed

- Redesigned Wiki with new landing page and new layout using mkdocs.
- Introduced batchMultiEdits - this is a major feature introduction that we hope will increase performance for all users. This is a behind-the-scenes change that the user does not need to do anything to take advantage of.
- Updated `overlay_path` to `overlay_files` and split `metadata_path` into `collection_files` and `metadata_files`.
- Moved `remove_overalys`, `reapply_overlays`, and `reset_overlays` to the [library level](https://metamanager.wiki/en/latest/config/libraries/#remove-overlays) instead of under `overlay_path`.
- Removed `schedule` from under `overlay_path` and replaced it with the library level attribute [`schedule_overlays`](https://metamanager.wiki/en/latest/config/libraries/#schedule-overlays).
- Removed library-level and collection-level logging, all logging is handled in the meta.log
- Added the `score` attribute to the [`anilist_userlist`](https://metamanager.wiki/en/latest/files/builders/anilist/#anilist-userlist) builder.
- Added the `episode_actor` attribute to the [`plex_search`](https://metamanager.wiki/en/latest/files/builders/plex/#plex-search) builder.
- [PMM Default Award Files](https://metamanager.wiki/en/latest/defaults/files/#award-collections) have been reworked to use the `imdb_award` builder and `imdb_awards` dynamic collection type.
- Reintroduced [Flixpatrol Chart Defaults Collections](https://metamanager.wiki/en/latest/defaults/chart/flixpatrol/).
- Added Trakt Anticipated to [Trakt Chart Defaults Collections](https://metamanager.wiki/en/latest/defaults/chart/trakt/).
- Added DE Content Rating as a PMM Default [Collection](https://metamanager.wiki/en/latest/defaults/both/content_rating_de/) and [Overlay](https://metamanager.wiki/en/latest/defaults/overlays/content_rating_de/)
- Added `schedule` and `schedule_<<key>>` template variables to most defaults.

### Fixed

- Fixed `(404) not_found` error that presented itself in PMS 1.32.7, as outlined [here](https://discord.com/channels/822460010649878528/1099773891733377065/1174751954367422585)
- Fixed issue that would prevent `file_poster` from overriding `url_poster` in the PMM Defaults.
- Removed `--cache-libraries` Environment Variable due to inconsistent behaviour that could cause issues.
- Fixed issue with `mass_poster_update` incorrectly updating episode posters when it shouldn't.
- Fixed issue with `delete_collection_named` running in a collection even if the collection wasn't scheduled to run.
- GitHub issues closed: #1438, #1542, #1563, #1568, #1571, #1585, #1609, #1618, #1621, #1623, #1632, #1636, #1642, #1662, #1666, #1670, #1674, #1688, #1705, #1712, #1749, #1781, #1772, #1786,

## [v1.19.1] - 2023-09-20

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Add `tmdb_vote_average` as a [Filter](https://metamanager.wiki/en/latest/metadata/filters.html#id7). thanks @tenshiak
- Add `tmdb_birthday` [Detail](https://metamanager.wiki/en/latest/metadata/details/metadata.html) which controls if a collection is visible based on a `tmdb_person`'s birthday.
- Add `match` [attribute](https://metamanager.wiki/en/latest/metadata/metadata/movie.html#matching-movies) to match movies within Plex to items within the Metadata file.
- Add `delete_collections_named` to [Shared Collection Variables](https://metamanager.wiki/en/latest/defaults/collection_variables.html)
- Add support for (GitHub Personal Access Tokens)[https://metamanager.wiki/en/latest/config/github.html] in config files. thanks @chazlarson
- Add runtime support for Shows, Seasons, Artists, and Albums.
- Add multiple ranges to the schedule system.

### Changed

- Python Version
- Drops Support for Python 3.7
- New Defaults Features
- New Default Translations of Danish, Dutch, Italian, Norwegian Bokmål, Portuguese (Brazil), and Spanish.
- New [Network](https://metamanager.wiki/en/latest/defaults/overlays/network.html) Default Overlay. thanks @bullmoose20, @JohnFawkes and @arial-Z
- New Content Rating US [Movies](https://metamanager.wiki/en/latest/defaults/overlays/content_rating_us_movie.html)/[Shows](https://metamanager.wiki/en/latest/defaults/overlays/content_rating_us_show.html) and [Content Rating UK](https://metamanager.wiki/en/latest/defaults/overlays/content_rating_uk.html) Default Overlay.
- Add `file_poster`, `file_poster_<<key>>`, `url_background`, `url_background_<<key>>`, `file_background`, `file_background_<<key>>`, `sort_prefix`, `sort_title`, and `name_mapping` as [Collection Variables](https://metamanager.wiki/en/latest/defaults/collection_variables.html).
- Add new Separator Color Styles.
- Closes #1461 Added Runtime for Shows, Seasons, Artists, and Albums
- Standardized overlay sizes for `- pmm: networks` and `- pmm: streaming`
- Rebrand HBO Max to Max.
- Add additional studios and networks
- Add Heritage Months to [Seasonal Defaults File](https://metamanager.wiki/en/latest/defaults/movie/seasonal.html)

### Fixed

- Fixes issue with IMDb Collections not building due to HTML structure changes. (Fixes #1496)
- Fixes FlixPatrol failed to parse error for most users. (Fixes #1445)
- Fixes issue with renaming assets (Fixes #1457)
- Fixes a Docstring. (Fixes #1379)
- Fixes issue with percent sign not appearing on some rating overlays. (Fixes #1478)
- Fixes albums not having locations (Fixes #1480)
- Fixes incorrect language code for Philippines in Languages Defaults file. (Fixes #1490)
- Fixes incorrect default value for starting attribute in "Year" collections. (Fixes #1378)
- #1380 #1472 Fixes various docs issues and typos (Fixes #1379)
- `radarr_remove_by_tag` and `sonarr_remove_by_tag` being validated as bool instead of strings. thanks @chazlarson (Fixes #1518)
- Fixes secrets not being redacted from Run Command in log files (Fixes #1531)
- Fixes issue with validating filenames as part of `dimensional_asset_rename`. thanks @chazlarson
- Fixes an issue where renamed collections could be incorrectly deleted.
- Fixes bug when defining users for `sync_to_users` for Playlists.
- Fixes bug where using mdb or metacritic as rating source on Ratings Overlay would not work correctly.
- Fixes bug where TMDb Filters using a modifier were ignored.
- Fixes bug with `mal_search` when using the `sfw` attribute
- Fixes bug where sorting a collection would fail if the collection name had a `,` in it.
- Fixes run_end webhooks.
- Fixes Letterboxd issue

## [v1.19.0] - 2023-04-10

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added `episode_year` as a dynamic collection option.
- Added `mass_studio_update` [library operation](https://metamanager.wiki/en/latest/config/operations.html#mass-studio-update).
- Changes Environment Variable/Run Argument list separator from `,` to `|`.
- Added `PMM_LOG_REQUESTS`/`--log-requests` Environment Variable/Run Argument which will log every single HTTP request in the log.
- Added EXIF Tags to Overlayed Images to be able to determine if they have an overlay or not.
- Added `anidb`, `anidb_3_0`, `anidb_2_5`, `anidb_2_0`, `anidb_1_5`, `anidb_1_0`, `anidb_0_5` options to the [`mass_genre_update` Library Operation](https://metamanager.wiki/en/latest/config/operations.html#mass-genre-update).
- Added `ignore_cache` to [`radarr`](https://metamanager.wiki/en/latest/config/radarr.html) and [`sonarr`](https://metamanager.wiki/en/latest/config/sonarr.html) Settings and `radarr_ignore_cache` and `sonarr_ignore_cache` to [Radarr/Sonarr Definition Settings](https://metamanager.wiki/en/latest/metadata/details/arr.html).
- Closes #1286 Updates Synology Walkthrough with DSM7 images.
- Closes #1159 Added support for official trakt lists.
- Closes #1251 When resetting Overlays Seasons where theres no poster will use the show poster.
- Templates can now be used with metadata updates.
- `allowed_library_types` Definition Setting has been changed to `run_definition` the old attribute will still work in the same way.
- Added `mapping_id`, `run_definition`, `update_seasons`, and `update_episodes` to Metadata definitions.
- Added a [Ratings Explained](https://metamanager.wiki/en/latest/home/guides/ratings.html) page to the Wiki to help explain how PMM interacts with the various Ratings.
- Add more options to the [`mass_imdb_parental_labels` Library Operation](https://metamanager.wiki/en/latest/config/operations.html#mass-imdb-parental-labels).
- Added `imdb_keyword` as a [Tag Filter](https://metamanager.wiki/en/latest/metadata/filters.html#tag-filters).
- Added `has_edition` as a [Boolean Filter](https://metamanager.wiki/en/latest/metadata/filters.html#boolean-filters).
- Added `has_stinger` and `stinger_rating` as [Filters](https://metamanager.wiki/en/latest/metadata/filters.html) based on http://www.mediastinger.com
- When editing episode metadata the key can now be either episode number, episode title, or episodeoriginally released date.
- The Collectionless builder now can work with other builders.
- Added `country` as an option for Shows when using the builders `plex_search` and `smart_filter`.
- Added [Config Secrets](https://metamanager.wiki/en/latest/home/environmental.html#config-secrets) and the ability to load Environment Variables using a `.env` File inside your config folder.

### Changed

- New Translation Portal
- New Translation Portal located at [translations.metamanager.wiki](https://translations.metamanager.wiki/projects/plex-meta-manager/defaults/). If anyone is willing to help fill in what we have or add your own language feel free to sign up. If you have questions either contact us on Discord or in the Discussions on GitHub.
- New PMM Companion Scripts
- [PMM Overlay Reset](https://metamanager.wiki/en/latest/home/scripts/overlay-reset.html): Script to Hard Reset PMM Overlays back to Default.
- [Plex Image Cleanup](https://metamanager.wiki/en/latest/home/scripts/image-cleanup.html): Script to clean up Old Uploaded Images in Plex.
- New Defaults Features
- Removed Translations from the defaults directory and in to their own [repo](https://github.com/meisnate12/PMM-Translations) which is managed at [translations.metamanager.wiki](https://translations.metamanager.wiki/projects/plex-meta-manager/defaults/).
- Added `minimum_rating`, `fresh_rating`, and `maximum_rating` as template variable options to the [Ratings Overlays](https://metamanager.wiki/en/latest/defaults/overlays/ratings.html) to control which ratings get displayed.
- Added the ability to update Overlay Defaults Positioning with just setting the alignment variables.
- Added [Based On...](https://metamanager.wiki/en/latest/defaults/both/based.html) Collection Default.
- Added Signature Style, DIIIVOY Style, and DIIIVOY Color Style to [`actor`](https://metamanager.wiki/en/latest/defaults/both/actor.html), [`directors`](https://metamanager.wiki/en/latest/defaults/movie/director.html), [`producers`](https://metamanager.wiki/en/latest/defaults/movie/producer.html), and [`writers`](https://metamanager.wiki/en/latest/defaults/movie/writer.html).
- Added new editions to the [editions Overlay File](https://metamanager.wiki/en/latest/defaults/overlays/resolution.html).
- Added `delete_playlist` and `delete_playlist_<<key>>` as template variable options to the [Playlist Default](https://metamanager.wiki/en/latest/defaults/playlist.html).
- Added `region` as a template variable options to the [`streaming` Overlay](https://metamanager.wiki/en/latest/defaults/overlays/streaming.html) and [`streaming` Collection](https://metamanager.wiki/en/latest/defaults/both/streaming.html) to allow these lists to show items in that region.
- Added AppleTV to te [FlixPatrol Default](https://metamanager.wiki/en/latest/defaults/overlays/flixpatrol.html).
- Added `radarr_search` and `sonarr_search` as template variable options to all Collection Defaults.
- Updated `network` and `franchise` defaults.
- Added `include` as a template variable options to the people collections ([`actor`](https://metamanager.wiki/en/latest/defaults/both/actor.html), [`director`](https://metamanager.wiki/en/latest/defaults/movie/director.html), [`producer`](https://metamanager.wiki/en/latest/defaults/movie/producer.html), [`writer`](https://metamanager.wiki/en/latest/defaults/movie/writer.html)) to specifically include the list of actors.

### Fixed

- Fixes Bug with `--time` that caused the times not to display correctly.
- Fixes `mal_search` search bug.
- corrects bug setting TMDb region. (Fixes #1277)
- Fixes a Bug where missing items items wouldn't be sent to radarr if no items were found in the library.
- Fixes a Bug with template conditionals causing them to sometimes use the wrong result.
- Wiki error. (Fixes #1285)
- Fixes a Bug with the `mass_poster_update` and `mass_background_update` Library Operations where they would sometimes throw a 406 Error.
- Fixes a Bug with the `mass_poster_update` Library Operation where it would also update backgrounds in addition to posters.
- Fixes multiple unnecessary items loads from plex.
- Fixes a Bug with using year filters with no modifier.
- Fixes a Bug where the `dimensional_asset_rename` Setting would rename title cards and season posters to show posters.
- Fixes [`trakt_userlist` Builder](https://metamanager.wiki/en/latest/metadata/builders/trakt.html#trakt-userlist) where option `recommended` should have been `recommendations`.
- Fixes overlay remove/reset operations.
- Closes #1325 Fixes a Bug where `tmdb_vote_count` would be rejected as a filter.
- Closes #1189 Fixes a Bug in the Resolution Default where the position would be completely off when changed.
- Closes #1336 Fixed "Mass Originally Available Update" attribute name within the wiki.
- Closes #1327 Fixed an issue where searching for item assets could take longer than expected.
- Closes #1346 Fixed an issue where using `PMM_TIME` with multiple times could ignore all but the last specified time.

## [v1.18.3] - 2023-01-16

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added new collection_order `custom.desc` ([FR](https://features.metamanager.wiki/features/p/reverse-sort-collectionorder-custom))
- Added webp Image Support ([FR](https://features.metamanager.wiki/features/p/support-webp-image-extensions))
- Added Spanish Defaults Translation
- Added Delete Webhooks
- Added collection detail `delete_collections_named` to delete any collections listed while running this collection definition.

### Fixed

- Franchise Defaults no longer ignore collection_section and sort_title (Fixes #1187)
- Fixed Italian Defaults Translation
- Fixed TMDb Modified Filters
- Fixed ValueError from Anime IDs

## [v1.18.2] - 2023-01-03

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added new collection_order `custom.desc` ([FR](https://features.metamanager.wiki/features/p/reverse-sort-collectionorder-custom))
- Added webp Image Support ([FR](https://features.metamanager.wiki/features/p/support-webp-image-extensions))
- Added Spanish Defaults Translation
- Added Delete Webhooks

### Fixed

- Fixed Italian Defaults Translation
- Fixed TMDb Modified Filters
- Fixed ValueError from Anime IDs

## [v1.18.1] - 2022-12-22

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Now supports Python 3.11
- Wiki CSS update thanks to @YozoraXCII
- Added `languages` template variable to the languages default
- Added `mdb_average` as an option for `mass_update_*_ratings`
- Added `custom_keys` dynamic collection attribute
- Better Error handling for move errors
- Added Sonarr v4 support
- Added `album_genre`, `album_mood`, `album_style`, and `track_mood` as dynamic collection types
- Added `only_run_on_create` to only run collections when the collection doesn't exist already
- Added `exclude_user` as an option for playlist definitions

### Fixed

- Fixed positioning issues with the resolution/editions default and the ratings default
- Fixed Metadata Asset Failures
- Fixed `smart_label` collection counts
- Fixed `delete_collections` operation
- Fixed using `include` with the defaults
- Content mapper error (Fixes #1174)
- Fixed mal builder errors
- (Fixes #1224)
- Fixed audio_codec and video_format defaults regex patterns
- Fixed tvdb xpaths for their builders and operations
- Fixed overlays to allow only suppression of overlays which exist inside the same file

## [v1.18.0] - 2022-11-09

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added support for editions in `plex_search`, `smart_filter`, `filters`, special text overlays, and metadata editing.
- Added `item_edition` [item metadata detail](https://metamanager.wiki/en/latest/metadata/details/metadata.html#item-metadata-details) to update the edition of items in a collection
- Added `edition` [dynamic collection type](https://metamanager.wiki/en/latest/metadata/dynamic.html#edition)
- Added `last_episode_aired_or_never` [date filter](https://metamanager.wiki/en/latest/metadata/filters.html#date-filters). thanks @axsuul#0591
- Added `versions` [number filter](https://metamanager.wiki/en/latest/metadata/filters.html#number-filters)
- Added `imdb_watchlist` [builder](https://metamanager.wiki/en/latest/metadata/builders/imdb.html#imdb-watchlist)
- Added `item_genre` [item metadata detail](https://metamanager.wiki/en/latest/metadata/details/metadata.html#item-metadata-details) to update the genres of items in a collection
- Added `plex_watchlist` [Builder](https://metamanager.wiki/en/latest/metadata/builders/plex.html#plex-watchlist)
- Added `current_year` to `plex_search`, `smart_filter`, and `filter` year/decade attributes.
- Added `stroke_width` and `stroke_color` as options for text overlays
- Added multiple new [special text variables](https://metamanager.wiki/en/latest/metadata/overlay.html#special-text-variables) and modifiers.
- Added support for the [AniDB API](https://metamanager.wiki/en/latest/config/anidb.html)
- Added `mass_original_title_update` [library operation](https://metamanager.wiki/en/latest/config/operations.html)
- Added many new options to the various mass_update [library operations](https://metamanager.wiki/en/latest/config/operations.html)
- Added the ability to give a list of sorts with `plex_search` and `smart_filter` to create a tiered sort
- Added `edition_filter` to [Movie metadata edits](https://metamanager.wiki/en/latest/metadata/metadata/movie.html#special-attributes) to allow searching for an item to include an edition.
- Added `--delete-labels` Run Commands to delete all labels in any library run.
- Added `season_label`, `episode_label`, `artist_label`, and `track_label` as `plex_search` options
- Moved alot of System Message to Trace Mode only to help declutter the meta.log file.
- Added Redacted Config File to the meta.log

### Changed

- New Packaged Defaults System
- All the old PMM Defaults (i.e. `- git: PMM\...` Files) are now packaged into PMM locally and can be accessed using `- pmm: ...`
- Added Common Sense Selection [Movie](https://www.commonsensemedia.org/reviews/category/movie/tag/common-sense-selections-31822)] and [Show](https://www.commonsensemedia.org/reviews/category/tv/tag/common-sense-selections-31822) collections to [`chart/other`](https://metamanager.wiki/en/latest/defaults/chart/other.html)
- Added [Common Sense Media Content Rating Collections](https://metamanager.wiki/en/latest/defaults/both/content_rating_cs.html), called with `- pmm: content_rating_cs` and to be used in combination with operation [`mass_content_rating_update: mdb_commonsense`](https://metamanager.wiki/en/latest/config/operations.html#mass-content-rating-update).
- Added several [visual styles for Separators](https://metamanager.wiki/en/latest/defaults/separators.html#separator-styles) to match PLEX's Categories theming. Called using `sep_style` template variable.
- Removed special_release and incorporated it into [resolution](https://metamanager.wiki/en/latest/defaults/overlays/resolution.html).
- Enhanced [resolution](https://metamanager.wiki/en/latest/defaults/overlays/resolution.html) to support both dovetail overlays with resolutions and box overlays when resolutions are not being used. Regexes were enhanced to support the new TRaSH naming guides with the `{edition-` naming scheme.
- Added [Common Sense Age Rating](https://metamanager.wiki/en/latest/defaults/overlays/commonsense.html) overlays, called with `- pmm: commonsense` and to be used in combination with operation [`mass_content_rating_update: mdb_commonsense`](https://metamanager.wiki/en/latest/config/operations.html#mass-content-rating-update).
- Added [mediastinger](https://metamanager.wiki/en/latest/defaults/overlays/mediastinger.html) overlays to indicate mid-credits and post-credits scenes, called with `- pmm: mediastinger`
- Removed `imdb_top_250`, `oscars`, `mc_must_see`, `rt_cert_fresh` and `commonsense_selection` Overlays in favor of adding them all into the new combined [Ribbon Overlay](https://metamanager.wiki/en/latest/defaults/overlays/ribbon.html).
- Added the new [Versions Overlay](https://metamanager.wiki/en/latest/defaults/overlays/versions.html) which Added a visual indicator of multiple versions of media, called with `- pmm: versions`
- Removed the `audio_languages` Overlay and replaced it with the [Audio/Subtitle Language Count Overlay](https://metamanager.wiki/en/latest/defaults/overlays/language_count.html), called with `- pmm: language_count`.
- Added Translations for the default collection name and summary (we're working on images). Currently we have `en`, `fr`, `de`, `da`, and `pt-br` if anyone wants to translate pmm to another language ping a team member on discord and let them know you wanna contribute.

### Fixed

- Fix metadata assets (Fixes #1014)
- `.yaml` can be used (Fixes #1067)
- report file doesn't have to exist (Fixes #1095)
- Fixes `plex_search`s with `episode_collection`
- Fixes Album Overlays
- Fixes Addon Images
- Fix Configs Repo Versioning
- Fixes codec and profile filters
- Fixes Ratings Error

## [v1.17.3] - 2022-08-10

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- [Special Text Overlays](https://metamanager.wiki/en/latest/metadata/overlay.html#special-text-variables) have been added
- Add mdb_myanimelsit as a mass rating option
- Use jpg for final overlay images instead of pngs to conserve space

### Fixed

- Fixes how suppress works with weights
- Fixes asset download
- ca count (Fixes #978)
- startswith error (Fixes #979)
- suppress agent not support messages for other libraries (Fixes #945)
- similar_artists works now (Fixes #984)
- `ignore_blank_results` will allow for blank smart collections (Fixes #984)

## [v1.17.2] - 2022-07-20

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Closes #959 New method for MyAnimeList authorization which doesn't rely on inputting anything into PMM
- Removed `mass_trakt_rating_update` in favor of the new `trakt_user` option for other mass_rating update methods the old option still works if its there
- Cleaner asset warnings
- Added [Conditional Variables](https://metamanager.wiki/en/nightly/metadata/templates.html#conditionals) in templates
- New source repo for [Anime ID Conversion ](https://github.com/meisnate12/Plex-Meta-Manager-Anime-IDs/)
- Added `episode_release` add a `plex_search` and `smart_filter` sort option
- New Versioning System for User Configs
- Added `ignore_blank_results` to suppress blank result errors
- Added `reapply_overlays` and `reset_overlays` to ignore the cache and reset to either tmdb or plex default when overlaying

### Fixed

- Fixes Timeout not being set until after dynamic collections
- Fixes InputError on float valued overlays
- Fixes Overlay Blur
- Fixes Mass Episode Updates
- Fixes off center overlays and addon overlays when the text is larger than the image
- Fixes truncated Images Error
- Fixes `arr_taglist`
- Fixes `mass_genre_update: imdb`
- Fixes `flixpatrol_url` returning no items
- `alt_title` will use title over the mapping name (Fixes #948)
- `anidb_popular` now returns items again (Fixes #954)
- `trakt_userlist` sort works again (Fixes #967)
- Fixes Album AttributeError (Fixes #974)

## [v1.17.1] - 2022-06-28

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added IMDb Interfaces as a direct source for mass editing operations (This is much quicker than using any other API for IMDb metadata and can easily be updated daily with new ratings)
- Added `.rated` option to `plex_seach` and `smart_filter` rating number attributes
- Added the ability to use an addon image with a text overlay to all be in on backdrop. You can control the options for this with the `addon_offset` and `addon_position` overlay attributes.
- Added the `back_align` overlay attribute to control the alignment of overlays inside a backdrop
- Added `video_codec`, `video_profile`, `audio_codec`, `audio_profile`, `channels`, `height`, `width`, and `aspect` [filters](https://metamanager.wiki/en/latest/metadata/filters.html)
- Added  `mass_episode_audience_rating_update`, `mass_episode_critic_rating_update`, and `mass_episode_user_rating_update` Library operations
- PMM now Added a label to track collections as PMM collections
- Added [overlay queues](https://metamanager.wiki/en/latest/metadata/overlay.html#overlay-queues)
- Added `episode_critic_rating` and `episode_audience_rating` options to `plex_seach` and `smart_filter`
- Allows IMDb Topic Search as `imdb_list`
- Added library level `template_variables`
- Added `font_style` for Vaiable Font Files
- Closes #912 local yaml files dont need `.yml` specified
- Closes #914 Added `non_existing` schedule option
- `linux/arm/v7` docker builds are now supported

### Fixed

- Fixes using the same overlay name more than once
- Fixes `plex_collectionless`
- Fixes MdbList None Error
- Fixes MyAnimeList Genres
- Fixes multiple issues using assets and overlays
- Unknown Error: 'NoneType' object has no attribute 'lower' (Fixes #870)
- 'Episode' object has no attribute '_autoReload' (Fixes #895)
- Local Guide Updated (Fixes #897)
- Playlists were unable to be deleted (Fixes #910)
- PMM now uses labels to determine managed collections (Fixes #916)
- Fix using -rm with.yml (Fixes #919)
- Season Assets work with overlayed shows (Fixes #924)
- url_poster now works with overlays (Fixes #927)
- strip the whole word (Fixes #928)
- `trakt_chart` `year` attribute should have been `years` (Fixes #937)
- 'NoneType' object is not iterable (Fixes #941)

## [v1.17.0] - 2022-05-26

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- There's two standout new features in Plex Meta Manager 1.17.0
- The new [Overlay System](https://metamanager.wiki/en/latest/metadata/overlay.html) which is many times more powerful then the previous one
- A brand new set of [Default Metadata/Overlay Files](https://metamanager.wiki/en/latest/home/guides/defaults.html) which can all be called and customized from you config file to make a variety of collections.
- Closes #345 Tv Episodes Can now have overlays
- Closes #463 Added direct to Discord notifications (just use a discord webhook)
- Closes #557 Added `sync_to_trakt` [collection/playlist setting](https://metamanager.wiki/en/latest/metadata/details/setting.html)
- Closes #569 Blur Overlay can be applied to episodes
- Closes #591 Added direct to Slack notifications (just use a slack webhook)
- Closes #592 Add progress Indicator for Overlays
- Closes #497 Added `radarr_upgrade_existing` and `sonarr_upgrade_existing` [Arr Details](https://metamanager.wiki/en/latest/metadata/details/arr.html)
- Closes #601 Metadata Files can match [Movies](https://metamanager.wiki/en/latest/metadata/metadata/movie.html#movies)/[Shows](https://metamanager.wiki/en/latest/metadata/metadata/show.html) by their TMDB/TVDb ID or IMDb ID
- Closes #610 Asset path can be declared per [metadata_file](https://metamanager.wiki/en/latest/config/paths.html#asset-directory)
- Closes #710 changed `save_missing` to `save_report` and expanded it to include added removed and filtered
- Closes #738 Expand Summary with times and better messages
- Closes #784 Added `radarr_taglist` and `radarr_all` [Radarr Builders](https://metamanager.wiki/en/latest/metadata/builders/radarr.html) and `sonarr_taglist` and `sonarr_all` [Sonarr Builders](https://metamanager.wiki/en/latest/metadata/builders/sonarr.html)
- Closes #785 Added `mal_search` [MyAnimeList Builder](https://metamanager.wiki/en/latest/metadata/builders/myanimelist.html#myanimelist-search)
- Closes #831 Implemented a runtime cache to ease loading from Plex
- Closes #863 fixes dynamic collections `move_prefix` and Added the `collection_sort` template variable
- Closes #864 Added `--playlists-only` [Run Commands](https://metamanager.wiki/en/latest/home/environmental.html)
- Added MdbList Sort `rank`
- Added `.regex` modifier for tags in `filters` and `plex_search`es
- Generate a Unique Identifier per instance of PMM
- Added `episodes`, `seasons`, `albums`, and `tracks` [Special Filters](https://metamanager.wiki/en/latest/metadata/filters.html#special-filters) to filter shows/artists by a percentage match of their child items
- Added label edits to seasons and episodes
- Added `all` schedule option
- Added `delete_playist` [Playlist Attribute](https://metamanager.wiki/en/latest/metadata/playlist.html#special-playlist-attributes) and `playlist_report` [Setting](https://metamanager.wiki/en/latest/config/settings.html#playlist-report)
- Added `prioritize_assets` [Setting](https://metamanager.wiki/en/latest/config/settings.html#prioritize-assets) which will tell PMM to use your assets folder over specified image URLs
- Added `--cache-libraries` to not have to redo the initial plex load when run multiple times a day
- Added [`number`](https://metamanager.wiki/en/latest/metadata/dynamic.html#number) and [`custom`](https://metamanager.wiki/en/latest/metadata/dynamic.html#custom) dynamic collection types

### Changed

- Deprecation Warning
- Brand new Overlays system that now has multiple overlays per item and positional overlays, but due to this system the old system had to be deprecated

### Fixed

- Fixes Notifiarr error where errors were not being cleared
- Latin Encoding Error (Fixes #834)
- Account for bad dates from TVDb (Fixes #838)
- 'TMDbShow' object has no attribute 'poster_path' (Fixes #841)
- AniList Boolean Searches were incorrectly formatted (Fixes #844)
- then to than (Fixes #867)

## [v1.16.5] - 2022-04-17

### Fixed

- Fix Library Operations not running

## [v1.16.4] - 2022-04-16

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- More sort options for mdblists
- Add `_encoded` options to template variables
- Closes #667 Any actor can now be searched
- Added `collection_filtering` for smart collections
- Added template variables per metadata file
- Added an `external_template` section in the metadata file

### Fixed

- trakt_recomendations now works with custom order (Fixes #818)
- Fixes using multiple templates
- multiple other small bugs (Fixes #813)

## [v1.16.3] - 2022-04-01

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added `version` Webhook to let you know when there's a new version available
- Added `show_unmatched` attribute to `plex_search` and `smart_filter`
- Added `reciperr_list` builder.
- Closes #796 Collection sorting has been moved back to when the collection is run and only sorts what's necessary
- Added `f1_season` metadata attribute. [Formula 1 Metadata Guide](https://metamanager.wiki/en/latest/home/guides/formula.html)
- Added `tmdb_upcoming`, `tmdb_airing_today`, `tmdb_on_the_air` builders.
- Added `region` to TMDb and `tmdb_region` setting.
- Closes #800 Trakt Pin can now be added to the config vs having to input in the script
- Closes #801 and Closes #802 Added `resolution`, `subtitle_language`, `audio_language`, and `decade` dynamic collection types
- Closes #751 Added `trakt_chart` and `trakt_userlist` to replace most trakt builders. The old builders will still work but if you want to use the new filters you have to use the new version of the builder.
- Closes #804 Added `remove_title_parentheses` library operation.
- Added more possible filters to a `letterboxd_list` builder.

### Fixed

- Key error (Fixes #793)
- Fixes multiple other small bugs

## [v1.16.2] - 2022-03-16

### Added

- Added a new cache for TMDb Movies and Shows to help with multiple loads
- Added an update available message at the beginning and end of the meta.log
- Added `mass_imdb_parental_labels` library operation to add parental guidance tags as labels.
- Closes #699 and Closes #771 added `mass_content_rating_update` library operation. Thanks, @YozoraXCII
- Closes #739 Added anidb as an option to `mass_genre_update`, `mass_audience_rating_update`, and `mass_critic_rating_update`
- Closes #750 Added `mass_originally_available_update` library operation.
- Closes #768 added the `anilist_userlist` AniList Builder. Thanks, @Frazzer951
- Closes #774 key and key_name are added as template variables in dynamic collections

### Changed

- Breaking Change
- `genre_mapper` now functions differently it should be an easy change but the old way will not work with 1.16.2 check the [wiki](https://metamanager.wiki/en/latest/config/operations.html#genre-mapper) for the update.

### Fixed

- `plex_pilots` should work with playlists (Fixes #769)
- all key values are lists (Fixes #776)
- ARM Docker Image was failing due to tini (Fixes #780)
- Fixes multiple other small bugs

## [v1.16.1] - 2022-03-12

### Added

- Closes #743 Use tini to properly shut down the docker container Thanks! @saltydk
- Closes #758, Closes #754, Closes #763 Added `director`, `writer`, `producer`, `content_rating`, `original_language`, `origin_country`, `resolution` (Thanks! @YozoraXCII),  `subtitle_language`, and `audio_language` as [dynamic collection](https://metamanager.wiki/en/latest/metadata/dynamic.html) types
- Added `origin_country` as a [Filter](https://metamanager.wiki/en/latest/metadata/filters.html)

### Fixed

- Fixes multiple dynamic collection bugs

## [v1.16.0] - 2022-03-08

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Closes #581 and closes #600 Added `dynamic_collections` to PMM
- changes webhooks `radarr_adds`/`sonarr_adds` now send title along with id.
- `item_lock_poster`, `item_lock_background`, and `item_lock_title` now unlock the attributes when set to false.
- Added `.count_gt`, `.count_gte`, `.count_lt`, and `.count_lte` modifiers for Tag Filters.
- Closes #468 Added `metadata_backup` library operation to extract all locked metadata from plex to a format readable by PMM.
- Added a partial load to TMDbAPIs which loads information from TMDb faster.
- Closes #660 Added `blank_collection` collection attribute to create an empty collection.
- Added `tmdb_type` and `tmdb_status` as Filters.
- Closes #671 Added `cache_builders` which will save builders search results for x number of days.
- Added `today` as an option for date attributes from `plex_search`, `smart_filter`, and ` filters`.
- Assumes square images are posters for `dimensional_asset_rename`. Thanks @aljohn92!
- Added `update_blank_track_titles` library operation which will search for blank tracks and put the tracks sortTitle as the title.
- Added `sort_by` to `mdblist_list` builder.
- Added more options to `mass_critic_rating` and `mass_audience_rating` thanks to mdbList.
- Closes #684 Added `mass_content_rating` library operation.
- Closes #683 Added Client Identifier.
- Added a cache length to both omdb and mdblist.
- Closes #675 Added `--ignore-ghost` to have the pmm not print the temporary prompts that are not logged
- Closes #640 custom log wrapper to automatically hide secret values from the logs
- Added the ability to customize `smart_label`.
- Closes #579 Added `limit` detail.
- Closes #727 Added `trakt_watchlist` and `trakt_collection` to custom sort
- Closes #712 Added `with_title_translation`, `with_name_translation`, and `with_overview_translation` to `tmdb_discover`.
- Added list of changed playlists/collections to the end run webhook.
- #745 Added `trakt_recommended_personal` Trakt Builder Thanks @fouadchamoun
- Closes #653 New Wiki
- Closes #701 Added `url_theme` and `file_theme` to be able to edit the collection theme

### Changed

- Brand New Wiki
- Check it out at [metamanager.wiki](https://metamanager.wiki)

### Fixed

- Fixes arrapi version detection.
- Fixes error when an episode doesnt have a season/episode number.
- Fixes rakingKey mistype.
- `show_missing_episode_assets` display error. (Fixes #658)
- Fixes validate key error.
- Fixes smart_filter validation .
- Fixes custom order for season and episode collections.
- Fixes `plex_collectionless` exclude error.
- Fixes duration to allow for numbers greater then 10.
- Fixes Season00 assets.
- Fixes Metadata lookup will search without a year on alt title
- Only loads items once for only library operations (Fixes #542)
- `metadata_backup` now can sync with a metadata file (Fixes #664)
- `minimum_items` now respects the items already in the collection not just what pmm found. (Fixes #661)
- Closes #686 Catch Summary Error that is the result of a bug in plex.
- Playlist can be run without having to have a metadata file in the library. (Fixes #698)
- Fixes deleting collections (Fixes #724)
- Incorrect number filtering when attribute value is equal to 0 (Fixes #736)
- 'Track' object has no attribute 'sortTitle' (Fixes #744)

## [v1.15.1] - 2022-01-25

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Added [MdbList Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/MdbList-Builders) thanks @linaspurinis
- Closes #582 Added `--run-metadata-files` run command to only run specific metadata files
- Closes #585 Genre can be mapped to Nothing to have them removed instead
- Closes #586 Added `tmdb_genre` Tag Filter
- Closes #593 Added `show_asset_not_needed` Setting to control the asset update not needed messages
- Closes #594 Added `show_missing_season_assets` Setting to show missing episode title cards
- Closes #596 added `item_refresh_delay` to pause between item_refresh of items on a collection/playlist Thanks @axsuul
- Closes #607 duration filter now accepts a decimal value for times less than a minute
- Closes #609 Added `non_item_remove_label` to remove this give labels from any item not found by the collection
- Closes #620 Added IDs sent to *arrs to the collection webhook
- Closes #630 Added `custom_repo` global setting to define your own repo like the community GitHub.
- Closes #650 add `plex_pilots` tv episode builder which grabs the first episode of every show in your library.

### Fixed

- sort_by Error (Fixes #603)
- Doesn't throw an error if an item doesn't have advance preferences (Fixes #608)
- `tmdb_collections` are now considered managed (Fixes #624)
- Music Library and Playlist Assets work now (Fixes #629, #634)
- Track Metadata is updated (Fixes #633)
- genre_mapper works again (Fixes #647)

## [v1.15.0] - 2022-01-11

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- Expands [Filters](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Filters) to work with every item type from all library types.
- `plex_all` now works for every `collection_level`
- Closes #189: Added Music Library Support
- Closes #238 Added Collection Summary at the end of the run.
- Added `default_collection_order` to Settings which will set every non-smart collection to this collection order
- Added `--delete-collections` to delete all collections (even ones not managed by PMM) at the beginning of a run.
- Added `genre_collections` [library operation](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Operations-Attributes#genre-collections) to automatically build collections based on the Genres in your Plex.
- Added `--library-first` to run library operations first before collections during the run.
- Added OMDb Lookup Search as a fallback when imdb episodes fail to match
- Added `download_url_assets` to Settings so if you are using url_poster or url_background in your collection config this will download the image to your asset folder if no image is found in the assets folder already.
- Closes #570 allows `<<collection_name>>` to be used under the defaults.
- Closes #571 allows you to set a template variable to null to make it optional for that collection.

### Fixed

- fix int error for filters (Fixes #551)
- Add more Arr checks (Fixes #552)
- `dictionary_variable` Error (Fixes #558)

## [v1.14.1] - 2021-12-29

### Added

- Requirements have been updated; make sure to upgrade the requirements if running locally.
- `original_language` filter now works with shows
- allow blank users to only sync playlists to yourself

### Fixed

- Cached Episode ID Fix
- fix Trakt Authorization not saving
- fix `tmdb_collections`
- better checking of arr filepaths

## [v1.14.0] - 2021-12-26

### Added

- Performance Increase with less calls to Plex
- Closes #484 Playlist Support
- Closes #495 Added `imdb_chart` Builder
- Added `has_collection` and `has_overlay` Collection Filters
- Closes #534 Added Support for the [XBMC NFO Movie and TV Agents](https://github.com/gboudreau/XBMCnfoMoviesImporter.bundle)
- Added `asset_depth` setting to determine how many nested folders to search in the assets folder (the more depth the longer it takes)
- Added `schedule: never` to not run a collection ever
- Added schedule at the library level
- changes collection changes webhook to support URLs instead of images if available
- Overloads the `collection_order` Collection Detail add more sort options for normal collections
- Allow multiple suffixes for the `tmdb_collections` Library Operation
- Added `show_options` setting which when set to true will show all options available to you when a plex_search validation fails
- Closes #513 Added `dimensional_asset_rename` as a library and global setting which will automatically rename assets with their height greater than their width to poster.ext and width greater than their heights to background.ext
- Closes #515 Added support for IMDb Episodes
- Closes #517 Added `radarr_remove_by_tag` and `sonarr_remove_by_tag` library operations
- Added `dictionary_variables` to `tmdb_collections`
- Added schedule options to `visible_library`, `visible_home`, and `visible_shared`
- Added `mass_collection_mode` library operation
- Closes #527 Remove commas from collection names for arr tags

### Changed

- Requirments Update (requirements will need to be reinstalled)
- Updated ArrAPI requirement to 1.3.0
- Updated lxml requirement to 4.7.1

### Fixed

- Sonarr series_type Error (Fixes #500)
- flixpatrol limit was ignored (Fixes #506)
- Smart Filters no builder fix (Fixes #523)
- Better Webhook handling (Fixes #529)
- tmdb_person error (Fixes #540)
- Updates Notifiarr web urls

## [v1.13.3] - 2021-12-10

### Added

- added deleted to the collection_changes webhook which is true if the collection was deleted on the run
- more options are allowed for episode and season collections including `item_lock_background`, `item_lock_poster`, `item_lock_title`, and `item_refresh`.
- Closes #391 added `item_tmdb_season_titles` collection detail to force a show to use TMDb Season Names

### Fixed

- NoneType Error (Fixes #491)
- Fixes Range Error
- Fixes Sonarr/Radarr add error with trailing `/`

## [v1.13.2] - 2021-12-08

### Added

- Closes #421 Added `tmdb_collections` [Library Operation](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Operations-Attributes) to automate TMDb Collections.
- Added `schedule: range(MM/DD-MM/DD)` as a [schedule option](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Schedule-Detail) to only run a collection in that range.
- Added `delete_not_scheduled` as a global/library setting and as a collection detail which deletes any collection that was skipped due to schedule.
- Added `only_filter_missing` as a global/library setting and as a collection detail which makes the filter applied only act on missing items.
- When syncing Labels you can now provide an empty list to remove all labels.
- Closes #438 Radarr/Sonarr now check for paths when adding existing and when adding new TMDB IDs and display all differences found to the user.
- Consolidate `collection_creation`, `collection_addition`, and `collection_removal` webhook options into `collection_changes` (everything should work the same)
- Closes #232 Added `genre_mapper` [Library Operation](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Operations-Attributes) to map genres to other genres.
- Closes #295 Added`show_missing_season_assets` as a global/library setting to show missing season poster from assets
- Closes #358 Added `move_collection_prefix` to templates which when given a list or comma-separated string of prefixes that you want to be moved to the end of the `<<collection_name>>` ie if you have `move_collection_prefix: The` and the collection is called `The Avengers` then `<<collection_name>>` is replaced with `Avengers, The` instead of `The Avengers`.
- Closes #379 Added `ignore_ids` and `ignore_imdb_ids` as global/library settings and as collection details to ignore TMDB/TVDb IDs and IMDb IDs
- Closes #486 Added `server_preroll` as a collection detail so you can schedule whatever string you want to be sent to the `Movie pre-roll video` Text box in Plex under Settings -> Extras.
- Closes #327 Added ARM support to the docker image

### Changed

- Requirments Update (requirements will need to be reinstalled)
- Updated ArrAPI requirement to 1.2.8

### Fixed

- Fixes Webhook start and end payloads.
- Fixes custom sort not working for flixpatrol builders and plex_search.
- Fixes AniList default to be the correct season in December.
- Fixes collection_level display bug.

## [v1.13.1] - 2021-11-30

### Added

- Closes #441 added `list_minimum` as an option to [Tautulli Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Tautulli-Builders)
- Closes #448 When using `radarr_add_all`/`sonarr_add_all` [Library Operation](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Operations-Attributes) or when using radarr/sonarr's `add_existing` option PMM now uses the existing path of the movie when adding to radarr/sonarr. if you plex path differs from your radarr/sonarr path you can use `plex_path` and `radarr_path`/`sonarr_path` under the [Radarr](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Radarr-Attributes)/[Sonarr](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Sonarr-Attributes).
- Add the ability to store what TMDb/TVDb IDs have been added to Radarr/Sonarr in the cache to avoid unnecessary calls.
- Added `item_lock_poster`, `item_lock_background`, and `item_lock_title` (Thanks @axsuul for the Pull)
- Closes #430 and Closes #464 Added missing TMDb Discover Options including `with_watch_providers`, `without_watch_providers`, `watch_region`, `with_watch_monetization_types`, `with_status`, `include_video`, and `with_release_type`.
- Added [FlixPatrol.com](https://flixpatrol.com/) [Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/FlixPatrol-Builders) `flixpatrol_url`, `flixpatrol_demographics`, `flixpatrol_popular`, and `flixpatrol_top`

### Changed

- Requirments Update (requirements will need to be reinstalled)
- Updated PlexAPI requirement to 4.8.0
- Updated ArrAPI requirement to 1.2.7

### Fixed

- Fixes Webhook response error and catches webhooks errors
- Fixes OMDb apikey validation
- Fixes asset_directory not being allow to be blank

## [v1.13.0] - 2021-11-17

### Added

- Added [Webhook](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Webhooks-Attributes) functionality for error notifications, run start, run end summary, collection creation, collection additions, and collection removals.
- Added [Notifiarr](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Notifiarr-Attributes) support to the Webhooks.
- Added Library [Operations](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Operations-Attributes) which are methods that effect your entire library.
- Add GitHub Actions for automatic Docker deployment
- When using the Plex Movie Agent or the Plex TV Series Agent the lock state of collection tags will no longer be changed
- Now uses the `includeGuids` parameter to greatly speed up the loading of GUIDs when using the Plex Movie Agent or the Plex TV Series Agent
- Closes #397 Added `item_refresh` as a collection detail to refresh the metadata of all items in the collection.
- Closes #418 Added period to `trakt_collected`, `trakt_recommended`, and `trakt_watched`. New Trakt Builders are `trakt_collected_daily`, `trakt_collected_weekly`, `trakt_collected_monthly`, `trakt_collected_yearly`, `trakt_collected_all`, `trakt_recommended_daily`, `trakt_recommended_weekly`, `trakt_recommended_monthly`, `trakt_recommended_yearly`, `trakt_recommended_all`, `trakt_watched_daily`, `trakt_watched_weekly`, `trakt_watched_monthly`, `trakt_watched_yearly`, and `trakt_watched_all`.
- Added `tvdb_language` to choose which language TV Series Names and Summaries are in by using the ISO-639-1 Language Codes. Leave blank for the original language. Defaults to the original language if the provided language is not found.
- Added `delete_collections_with_less` and `delete_unmanaged_collections` as library operations.
- Closes #423 Added IMDb Filmography Search
- Closes #424 Radarr and Sonarr now respect their respective Exclusion Lists
- Closes #428 Added Season backgrounds to assets directory.
- Closes #432 Added `trakt_boxoffice` as a Trakt Builder

### Changed

- Requirments Update (requirements will need to be reinstalled)
- Updated PlexAPI requirement to 4.7.1
- Updated ArrAPI requirement to 1.2.3
- Updated lmxl requirement to 4.6.4
- Updated ruamel.yaml requirement to 0.17.17
- Updated pathvalidate requirement to 2.5.0

### Fixed

- `title.is` `plex_search` was not working (Fixes #398)
- Fixes missing ymal files are now utf-8 encoded
- Fixes timout issue
- Fixes Misplaced Sonarr Bracket
- Fixes Removing Collection Tags
- Fixes Tautulli same variable name Error
- Fixes None Seconds Error
- Fixes Bad/Wrong Rating Key
- Fixes No ID in a Trakt List
- Fixes `delete_below_minimum`
- Fixes MyAnimeList int errors
- Fixes MyAnimeList and AniDbs Caches
- Fixes `trakt_popular` trying to get TVDb IDs for Movies
- Sonarr Error (Fixes #427)
- PMM_WIDTH error (Fixes #435)

## [v1.12.2] - 2021-09-13

### Added

- Added `anilist_trending` Collection Builder
- Added `country` and `source` as `anilist_search` attributes and `trending` as an `anilist_search` sort option
- Added `collection_name` Collection Detail to specify the collection name in plex as different than the mapping name
- Close #356 Added `collection_minimum` as a Setting and Collection Detail that will only add to a collection if the Collection Builders find at least as many items as the minimum.
- Added `delete_below_minimum` as a Setting and Collection Detail that will delete an existing collection if the Collection Builders do not find at least as many items as the minimum.
- Closes #390 Added `.is` and `.isnot` to as a String modifier for Searches and Collection Filters.

### Changed

- Requirments Update (requirements will need to be reinstalled)
- Updated pillow requirement to 8.3.2

### Fixed

- `anidb_search` fix (Fixes #369, #382)
- time validation error (Fixes #380)
- Updated Support for MyAnimeList Agent and changed the anime-to-tv list (Fixes #381)
- numbered mapping names fix (Fixes #387)

## [v1.12.1] - 2021-08-24

### Added

- Closes #365 Added `collection_level` which can be set to season or episode to create collections of that type from `plex_search` or `trakt_list` builders
- Closes #366 Doesn't map Other Video libraries
- Added `revert_overlay` which when added to an overlay collection and set to true, it will revert all overlays back to their original posters
- Added `mal_studio`

### Fixed

- Fixes indent issue (Fixes #363)
- Fix Trakt trending (Fixes #367)
- Fixes `anilist_search`
- Fixes `plex_search` and `smart_filter` to work for every attribute in the UI

## [v1.12.0] - 2021-08-16

### Added

- Added From @Critical-Impact #331 - AniDB Authentication for mature content in the AniDB Builders and the new `anidb_tag` Collection Builder.
- Added From @axsuul #351 - Added `first_episode_aired` Collection Filter
- Added `last_episode_aired` Collection Filter
- Closes #306 - Added a Session to PMM so it won't open as many connections.
- Closes #308 - Added Custom sorting to collections. Use `collection_order: custom` with a max of one builder per collection.
- Closes #348 - PMM only runs missing when it's needed.
- Part of #341 - Added `validate_builders` as a collection detail which will cause the collection to continue if a builder fails.
- Closes #317 - Added `stevenlu_popular` as a collection builder that uses [Steven Lu's Popular Movies List](https://movies.stevenlu.com/) to get a Movie List.
- Closes #336 - Added `missing_only_released` to settings at all levels which when set to true will filter missing items from a collection that have yet to be released.
- Closes #328 - Added `create_asset_folders` which when set to true while using `assets_for_all` PMM will create the Movie/Shows Folder for assets to be placed in.
- Closes #316 - Added `mass_trakt_rating_update` to update every movie/show's user rating in the library to match your custom rating on Trakt if there is one.
- Closes #347 - Added `mal_genre` and `mal_producer` Collection Builders.
- Closes #360 - Added `folder` as an option for `metadata_path` which will run every YAML file in the folder as a metadata file.
- Closes #318 - Added `anilist_search` detailed on the [Anilist Builders](https://github.com/meisnate12/Plex-Meta-Manager/wiki/AniList-Builders#anilist-search) Page.
- Added direct IMDb mapping for the cache
- Added `show_filtered`, `show_missing`, `save_missing`, and `item_assets` as Collection Level Details.
- Added `--no-missing` parameter to have PMM run without any of the missing movie/show functions.
- Added `tvdb` as an option for `mass_genre_update`.

### Changed

- Requirments Update (requirements will need to be reinstalled)
- Updated PlexAPI requirement to 4.7.0
- Updated arrapi requirement to 1.1.2
- Updated tmdbv3api requirement to 1.7.6
- removed trakt.py requirement

### Fixed

- Trakt Usernames with spaces or special characters should now work (Fixes #166)
- Fixed Display of Season and Episode Numbers. (Fixes #335)
- Fixes Letterboxd lists.
- Fixes Overlay and change its management from the PMM cache to labels in Plex. (This updates automatically)
- Fixes `item_radarr_tag` and `item_sonarr_tag` so they will add the tag to missing items that already exist in Radarr/Sonarr.
- Various other small fixes

## [v1.11.3] - 2021-07-12

### Fixed

- Fixed No Attribute Error when using `build_collection: false`
- Fixed bug in tag removal that caused PMM to remove all tags

## [v1.11.2] - 2021-07-08

### Fixed

- duplicated collections (Fixes #323)
- Filters now work with overlays and other item edits
- `collection_mode` now works for smart collections

## [v1.11.1] - 2021-07-06

### Fixed

- Fixes Multiple Overlay bugs
- Fixes 500 Error Bug
- Fixes `resolution` for shows

## [v1.11.0] - 2021-07-05

### Added

- Shows Loading output now
- Closes #260 Added the ability to change the visible options of a collection with `visible_library`, `visible_home`, and `visible_shared`
- Closes #263 Plex Assets only update when changed now
- Closes #286 Added `.regex` modifier to String and Date [Collection Filter](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Collection-Filters).
- Closes #287 Added poster overlay detailed [here](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Image-Overlay-Detail)
- Closes #290 Added `item_radarr_tag`, `item_radarr_tag.sync`, `item_radarr_tag.remove`, `item_sonarr_tag`, `item_sonarr_tag.sync` and `item_sonarr_tag.remove` which can be used to edit the tags of the movies/series in the collection in radarr/sonarr
- Closes #296 Display message when assets folder isn't found
- Closes #307 to update item assets in a collection you now must use `item_assets: true` in the collection config
- Closes #313 Added `split_duplicates` as a [Library Attribute](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Libraries-Attributes) which will split apart all duplicates at the beginning of every run
- Added a new `history` [Collection Filter](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Collection-Filters).
- Added ICheckMovies Builders `icheckmovies_list` and `icheckmovies_list_details`

### Changed

- Requirments Update (requirements will need to be reinstalled)
- Updated PlexAPI requirement to 4.6.1
- Added pillow requirement
- Added arrapi requirement

### Fixed

- (Fixes #293)
- Fixed IMDb Conversion Error
- Various other small fixes

## [v1.10.0] - 2021-05-30

### Added

- Item edits can be done while using `build_collection: false`
- Added more options to [Smart Filter](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Smart-Builders#smart-filter) and [Plex Search](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Plex-Builders#plex-search). `smart_filter` and `plex_search` now have all the same attributes and `plex_search` now uses `and` and `all` to match [Plex's Advance Filters](https://support.plex.tv/articles/201273953-collections/)
- Added more options to [Collection Filters](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Collection-Filters).

### Fixed

- `mass_update` fix (Fixes #278)
- blank smart searches fail instead of corrupting your plex DB (Fixes #280)
- Various other small fixes

## [v1.9.3] - 2021-05-26

### Added

- Added logging sections and Collection Run Time
- Added the ability to run the script at multiple times in one day
- Closes #274 - Added `--no-countdown` flag to not display the countdown while the script waits to run

### Fixed

- Fixes `.remove` for tags
- speed up IMDb (Fixes #267)
- Added smart collection validation (Fixes #268)
- Fixes various small errors

## [v1.9.2] - 2021-05-20

### Added

- Added better logging
- Added `--collections-only` and `--libraries-only` flags to only run parts of PMM
- Added `.remove` to any details that could use `.sync` to only remove tags
- Closes #235 - use `radarr_add_all` or `sonarr_add_all` as a [Library Attribute](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Libraries-Attributes) to add all items in your plex library
- Closes #245 - Added `build_collection` which when set to false
- Closes #247 - `hdr` added to `smart_filter`
- Closes #248 - Smart Collections now can edit the items inside them

### Changed

- Added [pathvalidate](https://github.com/thombashi/pathvalidate) requirement (requirements will need to be reinstalled)

### Fixed

- faster loading of item guids (Fixes #258)
- Fixes various small errors

## [v1.9.1] - 2021-05-17

### Fixed

- Fixed an issue where `smart_label` collections wouldn't change sort type
- Fixed an issue where `sync_mode: sync` wasn't removing items no longer in the collection

## [v1.9.0] - 2021-05-16

### Added

- Now supports multiple metadata paths from either in your filesystem or directly from a URL or the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs) repository all detailed on the [Libraries Attributes Wiki Page](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Libraries-Attributes#metadata-path)
- Overhauled how IDs are converted and how the cache is stored to be faster overall
- Added `.gt`, `.gte`, `.lt`, and `.lte` to plex_seach in place of of `.greater` and `.less`
- Closes #174 - Added `mass_audience_rating_update` and `mass_critic_rating_update` to be able to update every item in your library to match the rating on either `tmdb` or `imdb`
- Closes #217 - Added `filepath` as a [Collection Filter](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Collection-Filters)
- Closes #225 - Added more image options when not using asset folders detailed on the [Settings Attributes Wiki Page](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Settings-Attributes#image-asset-directory)
- Closes #226 - Added `smart_label` and `smart_filter` described on the [Smart Builders Wiki Page](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Smart-Builders)
- Closes #239 - Added `validate` attribute to `plex_search` which defaults to true and when set to false the collection won't error out on validation
- Closes #241 - Added `clean_bundles`, `empty_trash`, and `optimize` to the plex attribute and by default, they're set to false. If these are true PMM will run the specified operation on the library at the end of the run

### Fixed

- fixed asset mapping (Fixes #168)
- Program would error if specific tags were absent from the yaml file (Fixes #215)
- Collectionless now ignores itself (Fixes #220)
- arr tags must be lowercase (Fixes #223)
- episode ordering advance options didn't work (Fixes #228)
- edits were failing (Fixes #234)
- Fixes issue where the Arms Server could only take 100 IDs at a time
- Fixes an issue with templates not adding the right values to collections
- Fixes error with Tautulli where an item wouldn't be added if the item had changed in plex
- Various other small fixes

## [v1.8.0] - 2021-04-23

### Added

- Added more catching of Timeout Errors to keep the script running
- Changed how to sync labels from using `label: labels` and `label_sync_mode: sync` to just `label.sync: labels`
- Declaring library type is no longer needed
- Added `tmdb_movie` and `tmdb_show` as ways to update metadata of an item.
- Closes #5 - Now Supports Multiple Occurrences of Movies/Shows
- Closes #168 - You can set the new setting attribute to false `asset_folders: false` to have the asset directory look for the title as filename vs folder name i.e. `assets/Star Wars.png` vs `assets/Star Wars/poster.png`
- Closes #171 and Closes #172 - Added arm-server to convert anime ids and cached it for faster conversions
- Closes #175 - You can set the new setting attribute to true `assets_for_all: true` to have the script check your assets folder for every item in your library. The filename/folder name in your assets directory must match the folder name the media is stored in. i.e. if you have `Movies/Star Wars (1977)/Star Wars (1977) [1080p].mp4` then your asset directory would look at `assets/Star Wars (1977)/poster.png` for the poster
- Closes #187 - Added user_rating to plex_search and filters
- Closes #193 - Can add Labels and edit advance metadata of items in collections using `item_label`, `item_label.sync`, `item_episode_sorting`, `item_keep_episodes`, `item_delete_episodes`, `item_season_display`, `item_episode_ordering`, `item_metadata_language`, `item_use_original_title`
- Closes #209 - added `url_poster`, `file_poster`, `url_background`, and `file_background` under the metadata map, season map, and episode map to edit the poster and background

### Fixed

- - Bug Fixes for editing metadata of episodes and seasons (Fixes #184, #199)
- Added check to prevent error (Fixes #206)
- Fix for searching by audio language (Fixes #208)
- Various other small fixes

## [v1.7.2] - 2021-04-08

### Fixed

- Mixed up season and episode (Fixes #184)
- fixed sonarr error and other small bugs

## [1.7.1] - 2021-04-05

### Added

- Closes #155 - Added `added`, `added.not`, `originally_available`, and `originally_available.not` plex_searches which take an integer and represent `in the last` and `not in the last`
- Closes #167 - Can now edit Movies advance options
- Closes #173 - IMDb Keyword searches are now allowed

### Changed

- Requirments Update
- **Updated PlexAPI requirement to 4.5.2 (requirements will need to be reinstalled)**

### Fixed

- Small fix for `filters`
- Updated Metadata template file

## [v1.7.0] - 2021-04-05

### Added

- Closes #152 - Added the `network` filter to `plex_search` for the **New Plex TV Agent Only**
- Closes #153 - Added `audience_rating` and `critic_rating` to `plex_search`
- Closes #156 - Added `--resume <collection_name>` as a command line argument
- Closes #158 - Added every [Radarr](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Radarr-Attributes)/[Sonarr](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Sonarr-Attributes) option when adding a movie/show as a global or library attribute each with its own Collection Detail to override the attribute and split `add_to_arr` into `radarr_add` and `sonarr_add`
- Added a few extra printouts

### Fixed

- Catches the error so the script can continue (Fixes #150)
- Keep going if `plex_search` validation fails (Fixes #151)
- Plex Library Names can use special characters (Fixes #154)
- `trakt_watchlist` bug (Fixes #157)
- error with `rating` (Fixes #163)
- error with daily `schedule` (Fixes #164)
- Various other small fixes

## [v1.6.4] - 2021-03-27

### Added

- Closes #145 - Added `trakt_collection`

### Fixed

- plex_search bug (Fixes #148)
- Fixed debugging issue

## [v1.6.3] - 2021-03-26

### Fixed

- forgot more.items and other errors (Fixes #141)

## [v1.6.2] - 2021-03-26

### Fixed

- forgot another.items (Fixes #139)

## [v1.6.1] - 2021-03-26

### Fixed

- forgot.items (Fixes #139)

## [v1.6.0] - 2021-03-26

### Added

- Updated PlexAPI requirement to 4.5.1 (requirements will need to be reinstalled)
- Closes #27, Closes #78 - Completely rebuilt `plex_search` see [here](https://github.com/meisnate12/Plex-Meta-Manager/wiki/Plex-Builders#plex-search) for more details.
- Closes #136 - Added a new ability to edit show's advanced details

### Fixed

- `tmdb_discover` date format bug (Fixes #126)
- `content_rating` filter bug (Fixes #132)
- `trakt_trending` key bug (Fixes #133)
- `file_background` bug (Fixes #135)

## [v1.5.1] - 2021-03-18

### Added

- Closes #107 - Added command-line arguments as Environmental variables

### Fixed

- Collectionless now check collection IDs instead of Names (Fixes #47)
- add error handling for Tautulli (Fixes #63)
- AniList Bug (Fixes #118)
- Fixes reading episode numbers (Fixes #120)
- Trakt List Errors (Fixes #121)

## [v1.5.0] - 2021-03-15

### Added

- Updated PlexAPI requirement to 4.4.1 (requirements will need to be reinstalled)
- Added - Added AniList Support with new AniList Builders: `anilist_id`, `anilist_popular`, `anilist_relations`, `anilist_season`, `anilist_studio`, and `anilist_top_rated`.
- Added - Added new Trakt Builders: `trakt_collected`, `trakt_popular`, `trakt_recommended`, and `trakt_watched`.
- Closes #98 - Added new Collection Filter: `audio_track_title` and `audio_track_title.not`
- Closes #102 - Added letterboxd lookups to the cache

### Fixed

- Bug with `duration` filter (Fixes #66)
- allows multiple `title` plex searches via a list (Fixes #100)
- Mapping Issues when no IMDb ID was found (Fixes #101)
- Letterboxd List Errors (Fixes #102)

## [v1.4.0] - 2021-03-09

### Added

- Added - Mass editing of genres from tmdb or omdb using `mass_genre_update` along with OMDb support
- Added - Letterboxd Builders `letterboxd_list` and `letterboxd_list_details` and collection detail `letterboxd_description`
- Closes #77 - Support for New TV Agent
- Closes #82 - Added Season posters to the asset directory
- Closes #88 - Added `title` plex search option
- Closes #92 - Added collection builders: `trakt_list_details`, `tvdb_list_details`, `tvdb_show_details`, and `tvdb_movie_details`. Added collection details: `trakt_description`, `tvdb_summary`, `tvdb_description`, `tvdb_poster`, and `tvdb_background`.

### Fixed

- Displays a better Error Message (Fixes #79)
- Updating Show Images was broken (Fixes #82)
- Made what causes Collections to Fail more specific (Fixes #84)
- Error with TMDb Details methods (Fixes #89)
- Cache was being used when it shouldn't (Fixes #90)
- Forgot argument (Fixes #91)
- TMDb Show IDs weren't being converted to TVDb IDs (Fixes #92)

## [v1.3.0] - 2021-03-02

### Added

- Added - Displays Daily Run Runtime
- Added - Added `tmdb_vote_count` Filter
- Closes #62 - Sonarr now has the `season_folder` attribute which defaults to true
- Closes #65 - Added `run_again` mode to rerun adding movies to collections at the end of the run or on a delay at the end of the run
- Closes #66 - Added `duration` filter
- Closes #67 - Added the `optional` attribute to templates to specify optional variables
- Closes #70 - Added `tmdb_actor`, `tmdb_actor_details`, `tmdb_crew`, `tmdb_crew_details`, `tmdb_director`, `tmdb_director_details`, `tmdb_producer`, `tmdb_producer_details`, `tmdb_writer`, and `tmdb_writer_details` TMDb Builders

### Fixed

- Missing Metadata file would cause the whole run to fail (Fixes #55)
- TVDb Display Error (Fixes #56)
- schedule error (Fixes #71)

## [v1.2.2] - 2021-02-22

### Fixed

- KeyError (Fixes #53)

## [v1.2.1] - 2021-02-22

### Added

- Added - `timeout` attribute

### Fixed

- KeyError (Fixes #51)

## [v1.2.0] - 2021-02-21

### Added

- Added `settings` to config and moved some attributes from `plex` to `settings`. The program will automatically update the config.
- Added `show_missing` and `save_missing` as global, library, or collection level attributes that will or will not show/save movies missing from collections
- Closes #19 - Templates have been added
- Closes #26 - Two new ways to only run specific collections
- Closes #29 - Added arr tags using
- Closes #49 - Add ability to edit collection labels

### Fixed

- Movies weren't adding to collections when added to the cache (Fixes #28)
- tagline error (Fixes #31)
- missing movies mapping error (Fixes #37)
- Trakt Mapping error (Fixes #48)

## [v1.1.0] - 2021-02-14

### Added

- Closes #6 - Add movie posters by folder
- Closes #13 - Added the `original_language` collection filter and the `show_filtered` option to the `plex` and collections attributes
- Added the `show_unmanaged` option to the `plex` attribute

### Fixed

- `original_title` works for shows (Fixes #3)
- MyAnimeList connection always said failed (Fixes #17)
- added handling for multiple anime IDs (Fixes #22)
- `tvdb_show` not working correctly (Fixes #24)

## [v1.0.3] - 2021-02-11

### Changed

- wrong variable (Fixes #18)

## [v1.0.2] - 2021-02-11

### Changed

- called the wrong class (Fixes #15)

## [v1.0.1] - 2021-02-11

### Changed

- Radarr id bug (Fixes #7)
- forgot an import (Fixes #10)

## [v1.0.0] - 2021-02-08

### Changed

- Release of version 1.0.0

[Unreleased]: https://github.com/Kometa-Team/Kometa/compare/v2.3.1...HEAD
[v2.3.1]: https://github.com/Kometa-Team/Kometa/compare/v2.3.0...v2.3.1
[v2.3.0]: https://github.com/Kometa-Team/Kometa/compare/v2.2.2...v2.3.0
[v2.2.2]: https://github.com/Kometa-Team/Kometa/compare/v2.2.1...v2.2.2
[v2.2.1]: https://github.com/Kometa-Team/Kometa/compare/v2.2.0...v2.2.1
[v2.2.0]: https://github.com/Kometa-Team/Kometa/compare/v2.1.0...v2.2.0
[v2.1.0]: https://github.com/Kometa-Team/Kometa/compare/v2.0.2...v2.1.0
[v2.0.2]: https://github.com/Kometa-Team/Kometa/compare/v2.0.1...v2.0.2
[v2.0.1]: https://github.com/Kometa-Team/Kometa/compare/v2.0.0...v2.0.1
[v2.0.0]: https://github.com/Kometa-Team/Kometa/compare/v1.21.1...v2.0.0
[v1.21.1]: https://github.com/Kometa-Team/Kometa/compare/v1.21.0...v1.21.1
[v1.21.0]: https://github.com/Kometa-Team/Kometa/compare/v1.20.0...v1.21.0
[v1.20.0]: https://github.com/Kometa-Team/Kometa/compare/v1.19.1...v1.20.0
[v1.19.1]: https://github.com/Kometa-Team/Kometa/compare/v1.19.0...v1.19.1
[v1.19.0]: https://github.com/Kometa-Team/Kometa/compare/v1.18.3...v1.19.0
[v1.18.3]: https://github.com/Kometa-Team/Kometa/compare/v1.18.2...v1.18.3
[v1.18.2]: https://github.com/Kometa-Team/Kometa/compare/v1.18.1...v1.18.2
[v1.18.1]: https://github.com/Kometa-Team/Kometa/compare/v1.18.0...v1.18.1
[v1.18.0]: https://github.com/Kometa-Team/Kometa/compare/v1.17.3...v1.18.0
[v1.17.3]: https://github.com/Kometa-Team/Kometa/compare/v1.17.2...v1.17.3
[v1.17.2]: https://github.com/Kometa-Team/Kometa/compare/v1.17.1...v1.17.2
[v1.17.1]: https://github.com/Kometa-Team/Kometa/compare/v1.17.0...v1.17.1
[v1.17.0]: https://github.com/Kometa-Team/Kometa/compare/v1.16.5...v1.17.0
[v1.16.5]: https://github.com/Kometa-Team/Kometa/compare/v1.16.4...v1.16.5
[v1.16.4]: https://github.com/Kometa-Team/Kometa/compare/v1.16.3...v1.16.4
[v1.16.3]: https://github.com/Kometa-Team/Kometa/compare/v1.16.2...v1.16.3
[v1.16.2]: https://github.com/Kometa-Team/Kometa/compare/v1.16.1...v1.16.2
[v1.16.1]: https://github.com/Kometa-Team/Kometa/compare/v1.16.0...v1.16.1
[v1.16.0]: https://github.com/Kometa-Team/Kometa/compare/v1.15.1...v1.16.0
[v1.15.1]: https://github.com/Kometa-Team/Kometa/compare/v1.15.0...v1.15.1
[v1.15.0]: https://github.com/Kometa-Team/Kometa/compare/v1.14.1...v1.15.0
[v1.14.1]: https://github.com/Kometa-Team/Kometa/compare/v1.14.0...v1.14.1
[v1.14.0]: https://github.com/Kometa-Team/Kometa/compare/v1.13.3...v1.14.0
[v1.13.3]: https://github.com/Kometa-Team/Kometa/compare/v1.13.2...v1.13.3
[v1.13.2]: https://github.com/Kometa-Team/Kometa/compare/v1.13.1...v1.13.2
[v1.13.1]: https://github.com/Kometa-Team/Kometa/compare/v1.13.0...v1.13.1
[v1.13.0]: https://github.com/Kometa-Team/Kometa/compare/v1.12.2...v1.13.0
[v1.12.2]: https://github.com/Kometa-Team/Kometa/compare/v1.12.1...v1.12.2
[v1.12.1]: https://github.com/Kometa-Team/Kometa/compare/v1.12.0...v1.12.1
[v1.12.0]: https://github.com/Kometa-Team/Kometa/compare/v1.11.3...v1.12.0
[v1.11.3]: https://github.com/Kometa-Team/Kometa/compare/v1.11.2...v1.11.3
[v1.11.2]: https://github.com/Kometa-Team/Kometa/compare/v1.11.1...v1.11.2
[v1.11.1]: https://github.com/Kometa-Team/Kometa/compare/v1.11.0...v1.11.1
[v1.11.0]: https://github.com/Kometa-Team/Kometa/compare/v1.10.0...v1.11.0
[v1.10.0]: https://github.com/Kometa-Team/Kometa/compare/v1.9.3...v1.10.0
[v1.9.3]: https://github.com/Kometa-Team/Kometa/compare/v1.9.2...v1.9.3
[v1.9.2]: https://github.com/Kometa-Team/Kometa/compare/v1.9.1...v1.9.2
[v1.9.1]: https://github.com/Kometa-Team/Kometa/compare/v1.9.0...v1.9.1
[v1.9.0]: https://github.com/Kometa-Team/Kometa/compare/v1.8.0...v1.9.0
[v1.8.0]: https://github.com/Kometa-Team/Kometa/compare/v1.7.2...v1.8.0
[v1.7.2]: https://github.com/Kometa-Team/Kometa/compare/1.7.1...v1.7.2
[1.7.1]: https://github.com/Kometa-Team/Kometa/compare/v1.7.0...1.7.1
[v1.7.0]: https://github.com/Kometa-Team/Kometa/compare/v1.6.4...v1.7.0
[v1.6.4]: https://github.com/Kometa-Team/Kometa/compare/v1.6.3...v1.6.4
[v1.6.3]: https://github.com/Kometa-Team/Kometa/compare/v1.6.2...v1.6.3
[v1.6.2]: https://github.com/Kometa-Team/Kometa/compare/v1.6.1...v1.6.2
[v1.6.1]: https://github.com/Kometa-Team/Kometa/compare/v1.6.0...v1.6.1
[v1.6.0]: https://github.com/Kometa-Team/Kometa/compare/v1.5.1...v1.6.0
[v1.5.1]: https://github.com/Kometa-Team/Kometa/compare/v1.5.0...v1.5.1
[v1.5.0]: https://github.com/Kometa-Team/Kometa/compare/v1.4.0...v1.5.0
[v1.4.0]: https://github.com/Kometa-Team/Kometa/compare/v1.3.0...v1.4.0
[v1.3.0]: https://github.com/Kometa-Team/Kometa/compare/v1.2.2...v1.3.0
[v1.2.2]: https://github.com/Kometa-Team/Kometa/compare/v1.2.1...v1.2.2
[v1.2.1]: https://github.com/Kometa-Team/Kometa/compare/v1.2.0...v1.2.1
[v1.2.0]: https://github.com/Kometa-Team/Kometa/compare/v1.1.0...v1.2.0
[v1.1.0]: https://github.com/Kometa-Team/Kometa/compare/v1.0.3...v1.1.0
[v1.0.3]: https://github.com/Kometa-Team/Kometa/compare/v1.0.2...v1.0.3
[v1.0.2]: https://github.com/Kometa-Team/Kometa/compare/v1.0.1...v1.0.2
[v1.0.1]: https://github.com/Kometa-Team/Kometa/compare/v1.0.0...v1.0.1
[v1.0.0]: https://github.com/Kometa-Team/Kometa/releases/tag/v1.0.0
