---
search:
  boost: 5 
---
# Settings

## Overview

The `settings:` attribute and subsequent settings can be used to command various aspects of the functionality of Kometa.

Examples of these settings include the ability to:

* Cache each Plex GUID and IDs to increase performance
* Create asset folders for collections so that custom posters can be stored for upload.
* Use a custom repository as the base for all `git` Metadata files.

The settings attribute and attributes can be specified individually per library, or can be inherited from the global 
value if it has been set. If an attribute is specified at both the library and global level, then the library level 
attribute will take priority.

There are some attributes which can be specified at the collection level using [Settings](../files/settings.md).

Attributes set at the collection level will take priority over any library or global-level attribute.

## Attributes

The available setting attributes which can be set at each level are outlined below:


??? blank "`assets_create_folders` - Used to automatically create asset folders when none exist.<a class="headerlink" href="#create-asset-folders" title="Permanent link">¶</a>"

    <div id="create-asset-folders" />Whilst searching for assets, if an asset folder cannot be found within the 
    `assets_directory`, one will be created.

    Asset searches can be triggered by:
    
    * Collections specified under the `collections` header in a Collection File.
    * Items specified under the `metadata` header in a Collection File.
    * Playlists specified under the `playlists` header in a Playlist File.
    * Items in a library running the `assets_for_all` operation.
    * Items with an Overlay applied.
    * Items found by a Builder when `item_assets: true` is specified.

    <hr style="margin: 0px;">
    
    **Attribute:** `assets_create_folders` (`create_asset_folders` also accepted)

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          assets_create_folders: true
        ```

??? blank "`assets_depth` - Used to control the depth of search in the asset directory.<a class="headerlink" href="#asset-depth" title="Permanent link">¶</a>"

    <div id="asset-depth" />Specify how many folder levels to scan for an item within the asset directory.
    
    At each asset level, Kometa will look for either an image file (e.g. `Star Wars.png`) or a dedicated folder 
    containing an image (e.g. `poster.png`).
    
    For instance, `<path_to_assets>/Star Wars/poster.png` and `<path_to_assets>/Star Wars.png` are both asset depth 0, 
    while `<path_to_assets>/Movies/Star Wars/poster.png` is asset depth 1.
    
    ???+ tip
        `assets_folders` must be set to `true` for this to take effect.
    
        Increasing the number of levels to scan may reduce performance.

    <hr style="margin: 0px;">
    
    **Attribute:** `assets_depth` (`asset_depth` also accepted)

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** Any Integer 0 or greater

    **Default Value:** `0`

    ???+ example "Example"
        
        ```yaml
        settings:
          assets_depth: 2
        ```

??? blank "`assets_dimensional_rename` - Used to automatically rename asset files based on their dimensions.<a class="headerlink" href="#dimensional-asset-rename" title="Permanent link">¶</a>"

    <div id="dimensional-asset-rename" />Whilst scanning for assets, if a folder in the `assets_directory` does not contain 
    a correctly named poster or background, the first image meeting certain dimension criteria will be renamed accordingly.
    
    ???+ tip
        Note that `assets_folders` must be set to `true` for this to take effect.

    <hr style="margin: 0px;">
    
    **Attribute:** `assets_dimensional_rename` (`dimensional_asset_rename` also accepted)

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          assets_dimensional_rename: true
        ```


??? blank "`assets_display_missing` - Used to display a message when assets are missing.<a class="headerlink" href="#assets-display-missing" title="Permanent link">¶</a>"

    <div id="assets-display-missing" />Display warnings for missing assets in items, collections, or playlists.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `assets_display_missing` (`show_missing_assets` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          assets_display_missing: false
        ```

??? blank "`assets_display_missing_for_seasons` - Used to show any missing season assets.<a class="headerlink" href="#assets-display-missing-for-seasons" title="Permanent link">¶</a>"

    <div id="assets-display-missing-for-seasons" />Whilst scanning for assets for a TV show, notify if season posters 
    (e.g. `/ASSET_NAME/Season##.ext`) are missing.
    
    ???+ tip "Shows/Hides messages for seasons/albums"
    
      "Asset Warning: No poster found for '{item_title}' in the assets folder '{directory}'"  
      "Asset Warning: No poster '{name}' found in the assets folders"  
      "Missing Season {season_number} Poster"
    
    <hr style="margin: 0px;">
    
    **Attribute:** `assets_display_missing_for_seasons` (`show_missing_season_assets` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          assets_display_missing_for_seasons: true
        ```

??? blank "`assets_display_missing_for_episodes` - Used to show any missing episode assets.<a class="headerlink" href="#assets-display-missing-for-episodes" title="Permanent link">¶</a>"

    <div id="assets-display-missing-for-episodes" />Whilst scanning for assets for a TV show, notify if episode title cards 
    (e.g. `/ASSET_NAME/S##E##.ext`) are missing.
    
    ???+ tip "Shows/Hides messages for episodes"
    
      "Asset Warning: No poster found for '{item_title}' in the assets folder '{directory}'"  
      "Asset Warning: No poster '{name}' found in the assets folders"  
      "Missing S##E## Title Card"
    
    <hr style="margin: 0px;">
    
    **Attribute:** `assets_display_missing_for_episodes` (`show_missing_episode_assets` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          assets_display_missing_for_episodes: true
        ```

??? blank "`assets_directory` - Used to define where local assets are located.<a class="headerlink" href="#assets-directory" title="Permanent link">¶</a>"

    <div id="assets-directory" />Specify the directories where assets (posters, backgrounds, etc) are located.

    ???+ tip 
        Assets can be stored anywhere on the host system that Kometa has visibility of (i.e. if using docker, the 
        directory must be mounted/visible to the docker container).

    ??? warning
        Kometa will not create asset directories.  Asset directories you specify here need to exist already.

    <hr style="margin: 0px;">
    
    **Attribute:** `assets_directory` (`asset_directory` also accepted)

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** Any Directory or List of Directories

    **Default Value:** `[Directory containing YAML config]/assets`

    ???+ example "Example"
        
        ```yaml
        settings:
          assets_directory: config/movies
        ```

        ```yaml
        settings:
          assets_directory: 
            - config/assets/movies
            - config/assets/collections
        ```


??? blank "`assets_download_from_urls` - Used to download URL-based images into the asset directory.<a class="headerlink" href="#assets-download-from-urls" title="Permanent link">¶</a>"

    <div id="assets-download-from-urls" />Whilst scanning for assets, download images specified by URLs (e.g. `url_poster` or `url_background`) 
    into the asset folder if they are not already present.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `assets_download_from_urls` (`download_url_assets` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          assets_download_from_urls: true
        ```

??? blank "`assets_folders` - Used to control the asset directory folder structure.<a class="headerlink" href="#asset-folders" title="Permanent link">¶</a>"

    <div id="asset-folders" />While `true`, Kometa will search the `assets_directory` for a dedicated folder per item versus 
    looking for an image when `false`. 
    For example, when `true` the expected path would be `<asset_directory_path>/Star Wars/poster.png` instead of 
    `<asset_directory_path>/Star Wars.png`.

    <hr style="margin: 0px;">
    
    **Attribute:** `assets_folders` (`asset_folders` also accepted)

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          assets_folders: true
        ```

??? blank "`assets_only_display_changes` - Used to show/hide the 'update not needed' messages.<a class="headerlink" href="#assets-only-display-changes" title="Permanent link">¶</a>"

    <div id="assets-only-display-changes" />While scanning for assets, determines whether to show messages indicating that updates are not needed.

    <hr style="margin: 0px;">
    
    **Attribute:** `assets_only_display_changes` (`show_asset_not_needed` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          assets_only_display_changes: true
        ```

??? blank "`assets_prioritize` - Used to prioritize images from the assets directory over other image sources.<a class="headerlink" href="#prioritize-assets" title="Permanent link">¶</a>"

    <div id="prioritize-assets" />When determining which image to use for an item, prioritizes the image from 
    `assets_directory` over other image sources.

    Standard priority is:
    
    1. `url_poster`
    2. `file_poster`
    3. `tmdb_poster`
    4. `tvdb_poster`
    5. Asset directory
    6. `tmdb_person`
    7. `tmdb_collection_details`
    8+. Other methods

    This setting forces the asset to win over the `url_poster` if both are available.

    <hr style="margin: 0px;">
    
    **Attribute:** `assets_prioritize` (`prioritize_assets` also accepted)

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          assets_prioritize: true
        ```

??? blank "`cache` - Used to control Kometa's cache database.<a class="headerlink" href="#cache" title="Permanent link">¶</a>"

    <div id="cache" />Allow Kometa to create and maintain a local cache database for faster subsequent processing. The 
    cache file is created in the same directory as the configuration file.

    <hr style="margin: 0px;">
    
    **Attribute:** `cache`

    **Levels with this Attribute:** Global
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          cache: true
        ```

??? blank "`cache_expiration` - Used to control how long data is cached for.<a class="headerlink" href="#cache-expiration" title="Permanent link">¶</a>"

    <div id="cache-expiration" />Set the number of days before each cache mapping expires and has to be re-cached.

    <hr style="margin: 0px;">
    
    **Attribute:** `cache_expiration`

    **Levels with this Attribute:** Global
    
    **Accepted Values:** Integer greater than 0

    **Default Value:** `60`

    ???+ example "Example"
        
        ```yaml
        settings:
          cache_expiration: 30
        ```

??? blank "`collections_default_order` - Used to set the collection order for every collection run.<a class="headerlink" href="#collections-default-order" title="Permanent link">¶</a>"

    <div id="collections-default-order" />Set the default order for collections unless a specific order is defined in a collection.
    
    ???+ tip
        Note: `custom` cannot be used if multiple builders are used in the same collection.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_default_order` (`default_collection_order` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:**
    
    <table class="clearTable">
      <tr><td>`release`</td><td>Order by Release Dates</td></tr>
      <tr><td>`alpha`</td><td>Order Alphabetically</td></tr>
      <tr><td>`custom`</td><td>Order via the Builder's order</td></tr>
      <tr><td colspan="2">[Any `plex_search` sort option](../files/builders/plex.md#sort-options)</td></tr>
    </table>
    
    **Default Value:** `None`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_default_order: release
        ```


??? blank "`collections_delete_below_minimum` - Used to delete collections below the minimum items threshold.<a class="headerlink" href="#collections-delete-below-minimum" title="Permanent link">¶</a>"

    <div id="collections-delete-below-minimum" />If a collection's item count is below the value defined in 
    `collections_minimum_items`, it will be deleted.
    
    ???+ tip
        Depends on `collections_minimum_items` being set appropriately.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_delete_below_minimum` (`delete_below_minimum` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `false`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_delete_below_minimum: true
        ```

??? blank "`collections_delete_not_scheduled` - Used to delete collections that are not scheduled.<a class="headerlink" href="#collections-delete-not-scheduled" title="Permanent link">¶</a>"

    <div id="collections-delete-not-scheduled" />Deletes collections that are skipped due to not being scheduled.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_delete_not_scheduled` (`delete_not_scheduled` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `false`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_delete_not_scheduled: true
        ```

??? blank "`collections_filter_only_missing_items` - Used to apply filters only to missing items.<a class="headerlink" href="#collections-filter-only-missing-items" title="Permanent link">¶</a>"

    <div id="collections-filter-only-missing-items" />Only items missing from a collection will be subject to filtering.  
    See [Filters](../files/filters.md) for more details.
    
    ???+ note
        This setting can control which missing media items are sent to Sonarr/Radarr.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_filter_only_missing_items` (`only_filter_missing` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `false`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_filter_only_missing_items: true
        ```

??? blank "`collections_ignore_ids` - List of TMDb/TVDb IDs to ignore.<a class="headerlink" href="#collections-ignore-ids" title="Permanent link">¶</a>"

    <div id="collections-ignore-ids" />Set a list or comma-separated string of TMDb/TVDb IDs to ignore in all collections.
    
    ???+ note
        This does not apply to `smart_filter` collections.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_ignore_ids` (`ignore_ids` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** List or comma-separated string of TMDb/TVDb IDs
    
    **Default Value:** `None`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_ignore_ids: 572802,695721
        ```

??? blank "`collections_ignore_imdb_ids` - List of IMDb IDs to ignore.<a class="headerlink" href="#collections-ignore-imdb-ids" title="Permanent link">¶</a>"

    <div id="collections-ignore-imdb-ids" />Set a list or comma-separated string of IMDb IDs to ignore in all collections.
    
    ???+ note
        This does not apply to `smart_filter` collections.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_ignore_imdb_ids` (`ignore_imdb_ids` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** List or comma-separated string of IMDb IDs
    
    **Default Value:** `None`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_ignore_imdb_ids: tt6710474,tt1630029
        ```


??? blank "`collections_item_refresh_delay` - Time to wait between each item refresh.<a class="headerlink" href="#collections-item-refresh-delay" title="Permanent link">¶</a>"

    <div id="collections-item-refresh-delay" />Specify the number of seconds to wait between each `item_refresh` in collections/playlists.
    
    ???+ note
        Useful for reducing load on your Plex Media Server.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_item_refresh_delay` (`item_refresh_delay` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** Any Integer 0 or greater (seconds)
    
    **Default Value:** `0`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_item_refresh_delay: 5
        ```

??? blank "`collections_minimum_items` - Used to control the minimum number of items required for a collection/playlist.<a class="headerlink" href="#collections-minimum-items" title="Permanent link">¶</a>"

    <div id="collections-minimum-items" />Sets the minimum number of items that must be found to build or update a collection/playlist.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `collections_minimum_items` (`minimum_items` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** Integer greater than 0
    
    **Default Value:** `1`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_minimum_items: 5
        ```

??? blank "`collections_run_again_delay` - Used to control the delay (in minutes) for re-running collections.<a class="headerlink" href="#collections-run-again-delay" title="Permanent link">¶</a>"

    <div id="collections-run-again-delay" />Sets the delay (in minutes) before a `run_again` collection is executed.
    
    ???+ tip
        Useful when waiting for external processes (e.g. downloads) to complete.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_run_again_delay` (`run_again_delay` also accepted)
    
    **Levels with this Attribute:** Global
    
    **Accepted Values:** Any Integer 0 or greater
    
    **Default Value:** `0`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_run_again_delay: 5
        ```

??? blank "`collections_sync_mode` - Used to set the sync mode for collections and playlists.<a class="headerlink" href="#collections-sync-mode" title="Permanent link">¶</a>"

    <div id="collections-sync-mode" />Sets the sync mode for collections and playlists. Defining the sync mode within a 
    collection or playlist overrides this global setting.

    <hr style="margin: 0px;">
    
    **Attribute:** `collections_sync_mode` (`sync_mode` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:**
    
    <table class="clearTable">
      <tr><td>`sync`</td><td>Adds and removes items based on the source builder.</td></tr>
      <tr><td>`append`</td><td>Adds items from the source builder without removing existing items.</td></tr>
    </table>
    
    **Default Value:** `append`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          collections_sync_mode: sync
        ```
    
    ???+ tip "What does this mean?"
        You have a Trakt list of ten movies. Running Kometa creates a collection from the list.
        The next day, if the list changes:
        
        - With `sync`: the collection is updated to match the list exactly.
        - With `append`: new items are added without removing the originals.

??? blank "`github_custom_repo` - Used to set up the custom repository base for file blocks.<a class="headerlink" href="#github-custom-repo" title="Permanent link">¶</a>"

    <div id="github-custom-repo" />Specifies the base URL for `collection_files`, `metadata_files`, `playlist_file` and `overlay_files`.
    
    ???+ note
        Ensure you use the raw GitHub link (e.g., https://github.com/Kometa-Team/Community-Configs/tree/master/meisnate12).

    <hr style="margin: 0px;">
    
    **Attribute:** `github_custom_repo` (`custom_repo` also accepted)
    
    **Levels with this Attribute:** Global
    
    **Accepted Values:** Link to repository base
    
    **Default Value:** `None`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          github_custom_repo: https://github.com/Kometa-Team/Community-Configs/tree/master/meisnate12
        ```

??? blank "`logs_display_filtered` - Used to show items filtered out of collections/playlists.<a class="headerlink" href="#logs-display-filtered" title="Permanent link">¶</a>"

    <div id="logs-display-filtered" />Lists items that have been filtered out based on the applied criteria.

    <hr style="margin: 0px;">
    
    **Attribute:** `logs_display_filtered` (`show_filtered` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `false`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          logs_display_filtered: true
        ```

??? blank "`logs_display_missing` - Used to show missing items from collections/playlists.<a class="headerlink" href="#logs-display-missing" title="Permanent link">¶</a>"

    <div id="logs-display-missing" />When enabled, items missing from collections/playlists will be listed.

    <hr style="margin: 0px;">
    
    **Attribute:** `logs_display_missing` (`show_missing` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          logs_display_missing: false
        ```

??? blank "`logs_display_options` - Used to show attribute options from Plex.<a class="headerlink" href="#logs-display-options" title="Permanent link">¶</a>"

    <div id="logs-display-options" />When enabled, available options for an attribute (e.g. via `plex_search` or `smart_filter`) will be displayed.

    <hr style="margin: 0px;">
    
    **Attribute:** `logs_display_options` (`show_options` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `false`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          logs_display_options: true
        ```

??? blank "`logs_display_unfiltered` - Used to show items that pass filtering.<a class="headerlink" href="#logs-display-unfiltered" title="Permanent link">¶</a>"

    <div id="logs-display-unfiltered" />Lists items that meet the filter criteria and are included in collections/playlists.

    <hr style="margin: 0px;">
    
    **Attribute:** `logs_display_unfiltered` (`show_unfiltered` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `false`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          logs_display_unfiltered: true
        ```


??? blank "`logs_display_unconfigured` - Used to show collections not configured in the current run.<a class="headerlink" href="#logs-display-unconfigured" title="Permanent link">¶</a>"

    <div id="logs-display-unconfigured" />List all collections not configured in the current Kometa run at the end of each run.

    <hr style="margin: 0px;">
    
    **Attribute:** `logs_display_unconfigured` (`show_unconfigured` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          logs_display_unconfigured: false
        ```

??? blank "`logs_display_unmanaged` - Used to show collections not managed by Kometa.<a class="headerlink" href="#logs-display-unmanaged" title="Permanent link">¶</a>"

    <div id="logs-display-unmanaged" />List all collections not managed by Kometa at the end of each run.

    <hr style="margin: 0px;">
    
    **Attribute:** `logs_display_unmanaged` (`show_unmanaged` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          logs_display_unmanaged: false
        ```


??? blank "`logs_exclude_unreleased_from_missing` - Used to filter out unreleased items from missing lists.<a class="headerlink" href="#logs-exclude-unreleased-from-missing" title="Permanent link">¶</a>"

    <div id="logs-exclude-unreleased-from-missing" />When processing missing items, unreleased media will be filtered out.

    <hr style="margin: 0px;">
    
    **Attribute:** `logs_exclude_unreleased_from_missing` (`missing_only_released` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `false`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          logs_exclude_unreleased_from_missing: true
        ```


??? blank "`logs_save_report` - Used to save a report YAML file.<a class="headerlink" href="#logs-save-report" title="Permanent link">¶</a>"

    <div id="logs-save-report" />Saves a YAML report detailing items added, removed, filtered, or missing in collections/playlists.

    <hr style="margin: 0px;">
    
    **Attribute:** `logs_save_report` (`save_report` also accepted)
    
    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `true`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          logs_save_report: false
        ```


??? blank "`playlists_exclude_from` - Set the default playlist exclusion list.<a class="headerlink" href="#playlists-exclude-from" title="Permanent link">¶</a>"

    <div id="playlists-exclude-from" />Specifies the default users to exclude from a playlist.

    <hr style="margin: 0px;">
    
    **Attribute:** `playlists_exclude_from` (`playlist_exclude_users` also accepted)
    
    **Levels with this Attribute:** Global/Playlist
    
    **Accepted Values:** A list of users or a comma-separated string
    
    **Default Value:** `None`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          playlists_exclude_from: 
            - user1
            - user2
        ```

??? blank "`playlists_report` - Used to print a playlist report.<a class="headerlink" href="#playlists-report" title="Permanent link">¶</a>"

    <div id="playlists-report" />When enabled, prints a report of playlist details at the end of the log.

    <hr style="margin: 0px;">
    
    **Attribute:** `playlists_report` (`playlist_report` also accepted)
    
    **Levels with this Attribute:** Global
    
    **Accepted Values:** `true` or `false`
    
    **Default Value:** `false`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          playlists_report: true
        ```

??? blank "`playlists_sync_to` - Set the default playlist sync target.<a class="headerlink" href="#playlists-sync-to" title="Permanent link">¶</a>"

    <div id="playlists-sync-to" />Specifies the default users to sync a playlist to. To sync only to yourself, leave this setting blank.
    
    ???+ note
        Note that sharing playlists does not share associated posters due to Plex limitations.

    <hr style="margin: 0px;">
    
    **Attribute:** `playlists_sync_to` (`playlist_sync_to_users` also accepted)
    
    **Levels with this Attribute:** Global/Playlist
    
    **Accepted Values:** `all`, a list of users, or a comma-separated string of users
    
    ???+ example "Example"
        
        ```yaml
        settings:
          playlists_sync_to: 
            - user1
            - user2
        ```

??? blank "`overlays_filetype` - Used to control the file type for overlay images.<a class="headerlink" href="#overlays-filetype" title="Permanent link">¶</a>"

    <div id="overlays-filetype" />Determines the file type for overlay images. This setting only affects images generated after its addition.

    <hr style="margin: 0px;">
    
    **Attribute:** `overlays_filetype` (`overlay_artwork_filetype` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:**
    
    <table class="clearTable">
      <tr><td>`jpg`</td><td>Use JPG files for overlays</td></tr>
      <tr><td>`png`</td><td>Use PNG files for overlays</td></tr>
      <tr><td>`webp_lossy`</td><td>Use lossy WEBP files for overlays</td></tr>
      <tr><td>`webp_lossless`</td><td>Use lossless WEBP files for overlays</td></tr>
    </table>
    
    **Default Value:** `webp_lossy`
    
    ???+ example "Example"
        
        ```yaml
        settings:
          overlays_filetype: png
        ```

??? blank "`overlays_quality` - Used to control the quality for JPG or lossy WEBP overlays.<a class="headerlink" href="#overlays-quality" title="Permanent link">¶</a>"

    <div id="overlays-quality" />Sets the quality for overlay images. This value only applies to newly generated images.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `overlays_quality` (`overlay_artwork_quality` also accepted)
    
    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** Any Integer between 1 and 100 (values over 95 may result in large file sizes)
    
    **Default Value:** `None` (defaults to 90 when not provided)
    
    ???+ example "Example"
        
        ```yaml
        settings:
          overlays_quality: 90
        ```

??? blank "`report_path` - Used to specify the location of `save_report`.<a class="headerlink" href="#report-path" title="Permanent link">¶</a>"

    <div id="report-path" />Specify the location where `save_report` is saved.

    <hr style="margin: 0px;">
    
    **Attribute:** `report_path`

    **Levels with this Attribute:** Library

    **Accepted Values:** YAML file path location

    **Default Value:** `[Directory containing YAML config]/[Library Mapping Name]_report.yml`

    ???+ example "Example"
        
        ```yaml
        settings:
          report_path: config/TV_missing_report.yml
        ```

??? blank "`run_order` - Used to specify the run order of the library components.<a class="headerlink" href="#run-order" title="Permanent link">¶</a>"

    <div id="run-order" />Specify the run order of the library components [Library Operations, Collection Files and 
    Overlay Files]

    <hr style="margin: 0px;">
    
    **Attribute:** `run_order`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** List or comma-separated string which must include `operations`, `metadata` and `overlays` in 
    any order

    **Default Value:** `operations,metadata,collections,overlays`

    ???+ example "Example"
        
        ```yaml
        settings:
          run_order:
          - collections
          - overlays
          - operations
          - metadata
        ```

??? blank "`tvdb_language` - Specify the language to query TVDb in.<a class="headerlink" href="#tvdb-language" title="Permanent link">¶</a>"

    <div id="tvdb-language" />Specify the language to query TVDb in.
    
    ???+ note
    
        If no language is specified or the specified language is not found then the original language is used.

    <hr style="margin: 0px;">
    
    **Attribute:** `tvdb_language`

    **Levels with this Attribute:** Global
    
    **Accepted Values:** [Any ISO 639-2 Language Code](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        settings:
          tvdb_language: eng
        ```

## Default Values

The below in an extract of the `config.yml.template` and is the initial values that are set if you follow any of the 
installation guides.

???+ tip

    We suggest users review each of these settings and amend as necessary, these are just default values to get you 
    started.

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

The below showcases how to set a library-level setting, assuming that the attribute is listed as a library-level 
compatible attribute in the above table.

If no library-level attribute is set, then the global attribute is used.

???+ tip

    Press the :fontawesome-solid-circle-plus: icon to learn more

```yaml
libraries:
  Movies:
    settings:
      run_order: #(1)!
      - collections
      - metadata
      - operations
      - overlays
      collections_minimum_items: 3 #(2)!
    collection_files:
      # stuff here
    overlay_files:
      # stuff here
    operations:
      # stuff here
  TV Shows:
    collection_files:
      # stuff here
    overlay_files:
      # stuff here
    operations:
      # stuff here
settings:
  run_order: #(3)!
  - operations
  - overlays
  - collections
  - metadata
  collections_minimum_items: 1 #(4)!
```

1.  Sets the `run_order` specifically for the Movies library
2.  Sets the `collections_minimum_items` attribute specifically for the Movies library
3.  Sets the global `run_order` which will apply to all libraries unless a library-level `run_order` is found, as 
showcased in the above example
4.  Sets the global `collections_minimum_items` which will apply to all libraries unless a library-level `collections_minimum_items` is found, 
as showcased in the above example