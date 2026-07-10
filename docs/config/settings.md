---
search:
  boost: 5
hide:
  - toc
---
# Settings

## Overview

The `settings:` attribute controls global Kometa behavior such as run order, caching, assets, collection sync behavior, reports, logging, and network options.

Settings can be defined globally under the top-level `settings:` block. Many settings can also be overridden per library under `libraries: -> LIBRARY_NAME: -> settings:`. When a setting is present at both levels, the library-level value takes priority for that library.

Kometa accepts both the new grouped setting paths and the original flat setting names. New configs should use the grouped paths shown below.

## Setting Groups

- [Run Settings](#run-settings)
- [Cache Settings](#cache-settings)
- [Asset Settings](#asset-settings)
- [Collection Settings](#collection-settings)
- [Playlist Settings](#playlist-settings)
- [Metadata Settings](#metadata-settings)
- [Missing Item Settings](#missing-item-settings)
- [Overlay Settings](#overlay-settings)
- [Report Settings](#report-settings)
- [Logging Settings](#logging-settings)
- [Network Settings](#network-settings)

### Run Settings

###### Run Order { #run-order }

??? info "`order` - Controls which major Kometa phases run and in what order."
    **Attribute:** `order`

    **Original Attribute:** `run_order`

    **Levels:** Global/Library

    **Accepted Values:** List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string containing `operations`, `metadata`, `collections`, and `overlays`.

    **Default Value:** `operations, metadata, collections, overlays`

    ???+ example "Example"

        ```yaml
        settings:
          run:
            order:
              - operations
              - metadata
              - collections
              - overlays
        ```

###### Rerun Delay { #run-again-delay }

??? info "`rerun_delay` - Sets the delay between repeat runs."
    **Attribute:** `rerun_delay`

    **Original Attribute:** `run_again_delay`

    **Levels:** Global

    **Accepted Values:** Integer number of minutes.

    **Default Value:** `0`

    ???+ example "Example"

        ```yaml
        settings:
          run:
            rerun_delay: 2
        ```

### Cache Settings

###### Cache Enabled { #cache }

??? info "`enabled` - Enables Kometa's local cache database."
    Kometa uses the cache to improve performance and to track applied overlays. Disabling the cache can cause overlays to be reapplied every run.

    **Attribute:** `enabled`

    **Original Attribute:** `cache`

    **Levels:** Global

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

    ???+ example "Example"

        ```yaml
        settings:
          cache:
            enabled: true
        ```

###### Cache Expiration Days { #cache-expiration }

??? info "`expiration_days` - Sets how long cached values remain valid."
    **Attribute:** `expiration_days`

    **Original Attribute:** `cache_expiration`

    **Levels:** Global

    **Accepted Values:** Integer number of days greater than `0`.

    **Default Value:** `60`

    ???+ example "Example"

        ```yaml
        settings:
          cache:
            expiration_days: 60
        ```

### Asset Settings

###### Asset Directories { #asset-directory }

??? info "`directories` - Defines where local assets are stored."
    Asset directories can contain local posters, backgrounds, logos, and square art.

    **Attribute:** `directories`

    **Original Attribute:** `asset_directory`

    **Levels:** Global/Library

    **Accepted Values:** Directory path or list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of directory paths.

    **Default Value:** `[config directory]/assets`

    ???+ example "Example"

        ```yaml
        settings:
          assets:
            directories:
              - config/assets/movies
              - config/assets/collections
        ```

###### Asset Folders { #asset-folders }

??? info "`use_folders` - Controls whether assets are stored in dedicated folders."
    When `true`, Kometa looks for item folders such as `Star Wars/poster.png`. When `false`, Kometa looks for direct image files such as `Star Wars.png`.

    **Attribute:** `use_folders`

    **Original Attribute:** `asset_folders`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

    ???+ example "Example"

        ```yaml
        settings:
          assets:
            use_folders: true
        ```

###### Asset Search Depth { #asset-depth }

??? info "`search_depth` - Controls how many nested folder levels are searched for assets."
    `use_folders` must be `true` for this setting to affect folder matching. Higher values can reduce performance.

    **Attribute:** `search_depth`

    **Original Attribute:** `asset_depth`

    **Levels:** Global/Library

    **Accepted Values:** Integer `0` or greater.

    **Default Value:** `0`

    ???+ example "Example"

        ```yaml
        settings:
          assets:
            search_depth: 2
        ```

###### Create Asset Folders { #create-asset-folders }

??? info "`create_folders` - Creates missing asset folders when needed."
    **Attribute:** `create_folders`

    **Original Attribute:** `create_asset_folders`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          assets:
            create_folders: false
        ```

###### Prioritize Assets { #prioritize-assets }

??? info "`prioritize` - Prefers local assets over images from metadata sources."
    **Attribute:** `prioritize`

    **Original Attribute:** `prioritize_assets`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          assets:
            prioritize: false
        ```

###### Dimensional Asset Rename { #dimensional-asset-rename }

??? info "`dimensional_rename` - Renames downloaded assets with image dimensions."
    **Attribute:** `dimensional_rename`

    **Original Attribute:** `dimensional_asset_rename`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          assets:
            dimensional_rename: false
        ```

###### Download URL Assets { #download-url-assets }

??? info "`download_from_urls` - Downloads URL-based artwork into the asset directory."
    **Attribute:** `download_from_urls`

    **Original Attribute:** `download_url_assets`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          assets:
            download_from_urls: false
        ```

### Collection Settings

###### Collection Sync Mode { #sync-mode }

??? info "`sync_mode` - Controls whether Kometa only adds items or also removes missing items."
    **Attribute:** `sync_mode`

    **Original Attribute:** `sync_mode`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `append` or `sync`.

    **Default Value:** `append`

    ???+ example "Example"

        ```yaml
        settings:
          collections:
            sync_mode: append
        ```

###### Collection Minimum Items { #minimum-items }

??? info "`minimum_items` - Sets the minimum item count required for a collection."
    **Attribute:** `minimum_items`

    **Original Attribute:** `minimum_items`

    **Levels:** Global/Library/Definition

    **Accepted Values:** Integer `1` or greater.

    **Default Value:** `1`

    ???+ example "Example"

        ```yaml
        settings:
          collections:
            minimum_items: 1
        ```

###### Default Collection Order { #default-collection-order }

??? info "`default_order` - Sets the default Plex sort order for collections."
    **Attribute:** `default_order`

    **Original Attribute:** `default_collection_order`

    **Levels:** Global/Library

    **Accepted Values:** Any valid Plex collection sort value.

    **Default Value:** No default.

    ???+ example "Example"

        ```yaml
        settings:
          collections:
            default_order: release
        ```

###### Delete Below Minimum { #delete-below-minimum }

??? info "`delete_below_minimum` - Deletes collections below the minimum item count."
    **Attribute:** `delete_below_minimum`

    **Original Attribute:** `delete_below_minimum`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          collections:
            delete_below_minimum: false
        ```

###### Delete Not Scheduled { #delete-not-scheduled }

??? info "`delete_not_scheduled` - Deletes collections skipped because they are not scheduled."
    **Attribute:** `delete_not_scheduled`

    **Original Attribute:** `delete_not_scheduled`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          collections:
            delete_not_scheduled: false
        ```

###### Auto Sort Hubs { #auto-sort-hubs }

??? info "`auto_sort_hubs` - Sorts Plex recommendation hubs created from collections."
    **Attribute:** `auto_sort_hubs`

    **Original Attribute:** `auto_sort_hubs`

    **Levels:** Global/Library

    **Accepted Values:** `sort_title`, `sort_title.desc`, `alpha`, `alpha.desc`, `configured`, `configured.desc`, or `random`.

    **Default Value:** No default.

    ???+ example "Example"

        ```yaml
        settings:
          collections:
            auto_sort_hubs: sort_title
        ```

### Playlist Settings

###### Playlist Sync To Users { #playlist-sync-to-users }

??? info "`sync_to_users` - Sets which Plex users receive synced playlists."
    **Attribute:** `sync_to_users`

    **Original Attribute:** `playlist_sync_to_users`

    **Levels:** Global

    **Accepted Values:** List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" }, comma-separated string of users, `all`, or blank for the server owner.

    **Default Value:** Blank.

    ???+ example "Example"

        ```yaml
        settings:
          playlists:
            sync_to_users: all
        ```

###### Playlist Exclude Users { #playlist-exclude-users }

??? info "`exclude_users` - Excludes Plex users from playlist syncing."
    **Attribute:** `exclude_users`

    **Original Attribute:** `playlist_exclude_users`

    **Levels:** Global

    **Accepted Values:** List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" }, comma-separated string of users, or `all`.

    **Default Value:** Blank.

    ???+ example "Example"

        ```yaml
        settings:
          playlists:
            exclude_users: Managed User
        ```

###### Playlist Report { #playlist-report }

??? info "`show_report` - Includes playlist processing details in reports."
    **Attribute:** `show_report`

    **Original Attribute:** `playlist_report`

    **Levels:** Global

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

    ???+ example "Example"

        ```yaml
        settings:
          playlists:
            show_report: true
        ```

### Metadata Settings

###### TVDb Language { #tvdb-language }

??? info "`tvdb_language` - Sets the TVDb language used for metadata lookups."
    **Attribute:** `tvdb_language`

    **Original Attribute:** `tvdb_language`

    **Levels:** Global

    **Accepted Values:** TVDb language code or `default`.

    **Default Value:** `default`

    ???+ example "Example"

        ```yaml
        settings:
          metadata:
            tvdb_language: eng
        ```

###### Metadata Refresh Delay { #item-refresh-delay }

??? info "`refresh_delay` - Waits after refreshing item metadata."
    **Attribute:** `refresh_delay`

    **Original Attribute:** `item_refresh_delay`

    **Levels:** Global/Library

    **Accepted Values:** Integer number of seconds.

    **Default Value:** `0`

    ???+ example "Example"

        ```yaml
        settings:
          metadata:
            refresh_delay: 0
        ```

###### Ignore IDs { #ignore-ids }

??? info "`ignore_ids` - Ignores specific TMDb or TVDb IDs in missing item processing."
    **Attribute:** `ignore_ids`

    **Original Attribute:** `ignore_ids`

    **Levels:** Global/Library/Definition

    **Accepted Values:** List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of TMDb/TVDb IDs.

    **Default Value:** Blank.

    ???+ example "Example"

        ```yaml
        settings:
          metadata:
            ignore_ids:
              - 572802
        ```

###### Ignore IMDb IDs { #ignore-imdb-ids }

??? info "`ignore_imdb_ids` - Ignores specific IMDb IDs in missing item processing."
    **Attribute:** `ignore_imdb_ids`

    **Original Attribute:** `ignore_imdb_ids`

    **Levels:** Global/Library/Definition

    **Accepted Values:** List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of IMDb IDs.

    **Default Value:** Blank.

    ???+ example "Example"

        ```yaml
        settings:
          metadata:
            ignore_imdb_ids:
              - tt6710474
        ```

### Missing Item Settings

###### Filter Unreleased Missing Items { #missing-only-released }

??? info "`filter_unreleased` - Filters unreleased items out of missing item results."
    **Attribute:** `filter_unreleased`

    **Original Attribute:** `missing_only_released`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          missing:
            filter_unreleased: false
        ```

###### Only Filter Missing { #only-filter-missing }

??? info "`only_filter_missing` - Applies collection filters only to missing item checks."
    **Attribute:** `only_filter_missing`

    **Original Attribute:** `only_filter_missing`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          missing:
            only_filter_missing: false
        ```

### Overlay Settings

###### Overlay Filetype { #overlay-artwork-filetype }

??? info "`filetype` - Sets the file type used for generated overlay artwork."
    **Attribute:** `filetype`

    **Original Attribute:** `overlay_artwork_filetype`

    **Levels:** Global/Library

    **Accepted Values:** `jpg`, `png`, `webp_lossy`, or `webp_lossless`.

    **Default Value:** `webp_lossy`

    ???+ example "Example"

        ```yaml
        settings:
          overlays:
            filetype: webp_lossy
        ```

###### Overlay Quality { #overlay-artwork-quality }

??? info "`quality` - Sets image quality for generated overlay artwork."
    **Attribute:** `quality`

    **Original Attribute:** `overlay_artwork_quality`

    **Levels:** Global/Library

    **Accepted Values:** Integer from `1` to `100`.

    **Default Value:** `90`

    ???+ example "Example"

        ```yaml
        settings:
          overlays:
            quality: 90
        ```

### Report Settings

###### Save Report { #save-report }

??? info "`save` - Saves YAML report files for processed libraries."
    **Attribute:** `save`

    **Original Attribute:** `save_report`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

    ???+ example "Example"

        ```yaml
        settings:
          reports:
            save: false
        ```

###### Report Path { #report-path }

??? info "`path` - Overrides the default report file path."
    **Attribute:** `path`

    **Original Attribute:** `report_path`

    **Levels:** Global/Library

    **Accepted Values:** File path.

    **Default Value:** `[config directory]/[library name]_report.yml`

    ???+ example "Example"

        ```yaml
        settings:
          reports:
            path: config/reports/movies.yml
        ```

### Logging Settings

###### Show Options { #show-options }

??? info "`options` - Shows available options when invalid values are used."
    **Attribute:** `options`

    **Original Attribute:** `show_options`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

###### Show Unmanaged { #show-unmanaged }

??? info "`unmanaged` - Logs Plex collections that Kometa does not manage."
    **Attribute:** `unmanaged`

    **Original Attribute:** `show_unmanaged`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

###### Show Unconfigured { #show-unconfigured }

??? info "`unconfigured` - Logs Plex collections not configured in Kometa files."
    **Attribute:** `unconfigured`

    **Original Attribute:** `show_unconfigured`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

###### Show Filtered { #show-filtered }

??? info "`filtered` - Logs items excluded by collection filters."
    **Attribute:** `filtered`

    **Original Attribute:** `show_filtered`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

###### Show Unfiltered { #show-unfiltered }

??? info "`unfiltered` - Logs items kept after collection filters."
    **Attribute:** `unfiltered`

    **Original Attribute:** `show_unfiltered`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

###### Show Missing { #show-missing }

??? info "`missing` - Logs missing items found during collection processing."
    **Attribute:** `missing`

    **Original Attribute:** `show_missing`

    **Levels:** Global/Library/Definition

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

###### Show Missing Assets { #show-missing-assets }

??? info "`missing_assets` - Logs missing collection and item assets."
    **Attribute:** `missing_assets`

    **Original Attribute:** `show_missing_assets`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

###### Show Missing Season Assets { #show-missing-season-assets }

??? info "`missing_seasons` - Logs missing season assets."
    **Attribute:** `missing_seasons`

    **Original Attribute:** `show_missing_season_assets`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

###### Show Missing Episode Assets { #show-missing-episode-assets }

??? info "`missing_episodes` - Logs missing episode assets."
    **Attribute:** `missing_episodes`

    **Original Attribute:** `show_missing_episode_assets`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `false`

###### Show Unused Assets { #show-asset-not-needed }

??? info "`unused_assets` - Logs assets not needed by configured libraries."
    **Attribute:** `unused_assets`

    **Original Attribute:** `show_asset_not_needed`

    **Levels:** Global/Library

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

### Network Settings

###### Verify SSL { #verify-ssl }

??? info "`verify_ssl` - Verifies SSL certificates for outbound network requests."
    **Attribute:** `verify_ssl`

    **Original Attribute:** `verify_ssl`

    **Levels:** Global

    **Accepted Values:** `true` or `false`.

    **Default Value:** `true`

    ???+ warning

        Disabling SSL verification is not recommended unless you understand the security tradeoff.

    ???+ example "Example"

        ```yaml
        settings:
          network:
            verify_ssl: true
        ```

###### Custom Repo { #custom-repo }

??? info "`custom_repo` - Overrides the default Kometa defaults repository."
    **Attribute:** `custom_repo`

    **Original Attribute:** `custom_repo`

    **Levels:** Global

    **Accepted Values:** GitHub repository URL, raw GitHub URL, or blank.

    **Default Value:** Blank.

    ???+ example "Example"

        ```yaml
        settings:
          network:
            custom_repo: https://github.com/Kometa-Team/Defaults/tree/nightly/
        ```

## Default Values

The following excerpt from `config.yml.template` shows the default grouped settings block used by new configs.

???+ tip

    Review these settings before running Kometa. They are starting values, not recommendations for every setup.

~~~yaml
settings: {%
  include-markdown "../../config/config.yml.template"
  comments=false
  preserve-includer-indent=false
  start="settings:"
  end="webhooks:"
%}
~~~

## Example Library-Level Settings

Library-level settings use the same grouped structure and override global settings only for that library.

```yaml
libraries:
  Movies:
    settings:
      run:
        order:
          - collections
          - metadata
          - operations
          - overlays
      collections:
        minimum_items: 3
    collection_files:
      - default: imdb
    overlay_files:
      - default: ribbon
settings:
  run:
    order:
      - operations
      - overlays
      - collections
      - metadata
  collections:
    minimum_items: 1
```
