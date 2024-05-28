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

??? blank "`asset_directory` - Used to define where local assets are located.<a class="headerlink" href="#asset-directory" title="Permanent link">¶</a>"

    <div id="asset-directory" />Specify the directories where assets (posters, backgrounds, etc) are located.

    ???+ tip 
    
        Assets can be stored anywhere on the host system that Kometa has visibility of (i.e. if using docker, the 
        directory must be mounted/visible to the docker container).
    
    <hr style="margin: 0px;">
    
    **Attribute:** `asset_directory`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** Any Directory or List of Directories

    **Default Value:** `[Directory containing YAML config]/assets`

    ???+ example "Example"
        
        ```yaml
        settings:
          asset_directory: config/movies
        ```

        ```yaml
        settings:
          asset_directory: 
            - config/assets/movies
            - config/assets/collections
        ```

??? blank "`asset_folders` - Used to control the asset directory folder structure.<a class="headerlink" href="#asset-folders" title="Permanent link">¶</a>"

    <div id="asset-folders" />While `true`, Kometa will search the `asset_directory` for a dedicated folder per item vs 
    while false will look for an image. 
    
    i.e. When `true` the example path would be `<asset_directory_path>/Star Wars/poster.png` instead of 
    `<asset_directory_path>/Star Wars.png`.

    <hr style="margin: 0px;">
    
    **Attribute:** `asset_folders`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          asset_folders: true
        ```

??? blank "`asset_depth` - Used to control the depth of search in the asset directory.<a class="headerlink" href="#asset-depth" title="Permanent link">¶</a>"

    <div id="asset-depth" />Specify how many folder levels to scan for an item within the asset directory.
    
    At each asset level, Kometa will look for either `medianame.ext` [such as Star Wars.png] or a dedicated folder 
    containing `poster.ext`.
    
    i.e. `<path_to_assets>/Star Wars/poster.png` and `<path_to_assets>/Star Wars.png` are both asset depth 0, whilst 
    `<path_to_assets>/Movies/Star Wars/poster.png` and `<path_to_assets>/Movies/Star Wars.png` are both asset level 1.
    
    ???+ tip
    
        `asset_folders` must be set to `true` for this to take effect.
    
        increasing the amount of levels to scan will reduce performance

    <hr style="margin: 0px;">
    
    **Attribute:** `asset_depth`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** Any Integer 0 or greater

    **Default Value:** `0`

    ???+ example "Example"
        
        ```yaml
        settings:
          asset_depth: 2
        ```

??? blank "`create_asset_folders` - Used to automatically create asset folders when none exist.<a class="headerlink" href="#create-asset-folders title="Permanent link">¶</a>"

    <div id="create-asset-folders" />Whilst searching for assets, if an asset folder cannot be found within the 
    `asset_directory` one will be created.

    Asset Searches can happen in a number of ways.

    * Any Collection specified under the `collections` header in a Collection File.

    * Any Item specified under the `metadata` header in a Collection File.

    * Any Playlist specified under the `playlists` header in a Playlist File.

    * Any Item in a library that is running the `assets_for_all` Library Operation.

    * Any Item that has an Overlay applied to it.

    * Any Item found by a Builder while the definition also has `item_assets: true` specified. 

    <hr style="margin: 0px;">
    
    **Attribute:** `create_asset_folders`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          create_asset_folders: true
        ```

??? blank "`prioritize_assets` - Used to prioritize `asset_directory` images over all other images types.<a class="headerlink" href="#prioritize-assets" title="Permanent link">¶</a>"

    <div id="prioritize-assets" />When determining which image to use on an item prioritize the `asset_directory` over 
    all other images types.

    <hr style="margin: 0px;">
    
    **Attribute:** `prioritize_assets`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          prioritize_assets: true
        ```

??? blank "`dimensional_asset_rename` - Used to automatically rename asset files based on their dimensions.<a class="headerlink" href="#dimensional-asset-rename" title="Permanent link">¶</a>"

    <div id="dimensional-asset-rename" />Whilst searching for assets, scan the folders within the `asset_directory` and 
    if an asset poster (i.e. `/ASSET_NAME/poster.ext`) was not found, rename the first image found that has a height 
    greater than or equal to its width to `poster.ext`. If an asset background (i.e. `/ASSET_NAME/background.ext`), 
    rename the first image found that has a width greater than its height to `background.ext`.
    
    ???+ tip
    
        `asset_folders` must be set to `true` for this to take effect.

    <hr style="margin: 0px;">
    
    **Attribute:** `dimensional_asset_rename`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          dimensional_asset_rename: true
        ```

??? blank "`download_url_assets` - Used to download url images into the asset directory.<a class="headerlink" href="#download-url-assets" title="Permanent link">¶</a>"

    <div id="download-url-assets" />Whilst searching for assets, download images set within Collection/Metadata/Playlist 
    files( i.e. images set by `url_poster` or `url_background`) into the asset folder if none are already present.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `download_url_assets`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          download_url_assets: true
        ```

??? blank "`show_missing_season_assets` - Used to show any missing season assets.<a class="headerlink" href="#show-missing-season-assets" title="Permanent link">¶</a>"

    <div id="show-missing-season-assets" />Whilst searching for assets, when scanning for assets for a TV Show, if 
    Season posters are found (i.e. `/ASSET_NAME/Season##.ext`), notify the user of any seasons which do not have an 
    asset image.
    
    ???+ tip "Shows/Hides messages like these for seasons/albums"

      "Asset Warning: No poster found for '{item_title}' in the assets folder '{directory}'"

      "Asset Warning: No poster '{name}' found in the assets folders"

      "Missing Season {season_number} Poster"

    <hr style="margin: 0px;">
    
    **Attribute:** `show_missing_season_assets`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_missing_season_assets: true
        ```

??? blank "`show_missing_episode_assets` - Used to show any missing episode assets.<a class="headerlink" href="#show-missing-episode-assets" title="Permanent link">¶</a>"

    <div id="show-missing-episode-assets" />Whilst searching for assets, when scanning for assets for a TV Show, if an 
    Episode Title Card is found (i.e. `/ASSET_NAME/S##E##.ext`), notify the user of any episodes which do not have an 
    asset image.
    
    ???+ tip "Shows/Hides messages like these for episodes"

      "Asset Warning: No poster found for '{item_title}' in the assets folder '{directory}'"

      "Asset Warning: No poster '{name}' found in the assets folders"

      "\nMissing S##E## Title Card"

    <hr style="margin: 0px;">
    
    **Attribute:** `show_missing_episode_assets`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_missing_episode_assets: true
        ```

??? blank "`show_asset_not_needed` - Used to show/hide the `update not needed` messages.<a class="headerlink" href="#show-asset-not-needed" title="Permanent link">¶</a>"

    <div id="show-asset-not-needed" />Whilst searching for assets, show or hide the `update not needed` messages.

    <hr style="margin: 0px;">
    
    **Attribute:** `show_asset_not_needed`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_asset_not_needed: true
        ```

??? blank "`sync_mode` - Used to set the `sync_mode` for collections and playlists.<a class="headerlink" href="#sync-mode" title="Permanent link">¶</a>"

    <div id="sync-mode" />Sets the `sync_mode` for collections and playlists. Setting the `sync_mode` directly in a 
    collection or playlist definition will override the `sync_mode` for that definition.

    <hr style="margin: 0px;">
    
    **Attribute:** `sync_mode`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:**

    <table class="clearTable">
      <tr><td>`sync`</td><td>Will add and remove any items that are added/removed from the source builder.</td></tr>
      <tr><td>`append`</td><td>Will only add items that are added from the source builder, but will not remove anything even if it is removed from the source builder.</td></tr>
    </table>

    **Default Value:** `append`

    ???+ example "Example"
        
        ```yaml
        settings:
          sync_mode: sync
        ```

??? blank "`default_collection_order` - Used to set the `collection_order` for every collection run.<a class="headerlink" href="#default-collection-order" title="Permanent link">¶</a>"

    <div id="default-collection-order" />Set the `collection_order` for every collection run by Kometa unless the 
    collection has a specific `collection_order`.
    
    ???+ tip
    
        `custom` cannot be used if more than one builder is being used for the collection (such as `imdb_list` and 
        `trakt_list` within the same collection).

    <hr style="margin: 0px;">
    
    **Attribute:** `default_collection_order`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:**

    <table class="clearTable">
      <tr><td>`release`</td><td>Order Collection by Release Dates</td></tr>
      <tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr>
      <tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr>
      <tr><td colspan="2">[Any `plex_search` sort option](../files/builders/plex.md#sort-options)</td></tr>
    </table>

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        settings:
          default_collection_order: release
        ```

??? blank "`minimum_items` - Used to control minimum items requires to build a collection/playlist.<a class="headerlink" href="#minimum-items" title="Permanent link">¶</a>"

    <div id="minimum-items" />Set the minimum number of items that must be found in order to build or update a 
    collection/playlist.

    <hr style="margin: 0px;">
    
    **Attribute:** `minimum_items`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** Integer greater than 0

    **Default Value:** `1`

    ???+ example "Example"
        
        ```yaml
        settings:
          minimum_items: 5
        ```

??? blank "`delete_below_minimum` - Used to delete collections below `minimum_items`<a class="headerlink" href="#delete-below-minimum" title="Permanent link">¶</a>"

    <div id="delete-below-minimum" />When a collection is run, delete the collection if it is below the minimum number 
    specified by `minimum_items`.
    
    ???+ tip
    
        Relies on `minimum_items` being set to the desired integer.

    <hr style="margin: 0px;">
    
    **Attribute:** `delete_below_minimum`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
        settings:
          delete_below_minimum: true
        ```

??? blank "`delete_not_scheduled` - Used to delete collections not scheduled.<a class="headerlink" href="#delete-not-scheduled" title="Permanent link">¶</a>"

    <div id="delete-not-scheduled" />If a collection is skipped due to it not being scheduled, delete the collection.

    <hr style="margin: 0px;">
    
    **Attribute:** `delete_not_scheduled`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
        settings:
        settings:
          delete_not_scheduled: true
        ```

??? blank "`run_again_delay` - Used to control the number of minutes to delay running `run_again` collections.<a class="headerlink" href="#run-again-delay" title="Permanent link">¶</a>"

    <div id="run-again-delay" />Set the number of minutes to delay running `run_again` collections after daily run is 
    finished.
    
    For example, if a collection adds items to Sonarr/Radarr, the library can automatically re-run "X" amount of time 
    later so that any downloaded items are processed.
    
    ???+ tip
    
        A collection is a `run_again` collection if it has the `run_again` [Setting](../files/settings.md) attribute set 
        to true.

    <hr style="margin: 0px;">
    
    **Attribute:** `run_again_delay`

    **Levels with this Attribute:** Global
    
    **Accepted Values:** Any Integer 0 or greater

    **Default Value:** `0`

    ???+ example "Example"
        
        ```yaml
        settings:
          run_again_delay: 5
        ```

??? blank "`missing_only_released` - Used to filter unreleased items from missing lists.<a class="headerlink" href="#missing-only-released" title="Permanent link">¶</a>"

    <div id="missing-only-released" />Whilst running a collection or playlist, when Kometa handles missing items to 
    either report it to the user, report it to a file, or send it to Radarr/Sonarr all unreleased items will be 
    filtered out.

    <hr style="margin: 0px;">
    
    **Attribute:** `missing_only_released`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
        settings:
          missing_only_released: true
        ```

??? blank "`show_unmanaged` - Used to show collections not managed by Kometa.<a class="headerlink" href="#show-unmanaged" title="Permanent link">¶</a>"

    <div id="show-unmanaged" />List all collections not managed by Kometa at the end of each run.

    <hr style="margin: 0px;">
    
    **Attribute:** `show_unmanaged`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_unmanaged: false
        ```

??? blank "`show_unconfigured` - Used to show collections not in the current run.<a class="headerlink" href="#show-unconfigured" title="Permanent link">¶</a>"

    <div id="show-unconfigured" />List all collections not configured in the current Kometa run at the end of each run.

    <hr style="margin: 0px;">
    
    **Attribute:** `show_unconfigured`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_unconfigured: false
        ```

??? blank "`show_filtered` - Used to show filtered items.<a class="headerlink" href="#show-filtered" title="Permanent link">¶</a>"

    <div id="show-filtered" />List all items which have been filtered out of a collection or playlist (i.e. if it 
    doesn't meet the filter criteria)

    <hr style="margin: 0px;">
    
    **Attribute:** `show_filtered`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_filtered: true
        ```

??? blank "`show_options` - Used to show attribute options from plex.<a class="headerlink" href="#show-options" title="Permanent link">¶</a>"

    <div id="show-options" />While `show_options` is true the available options for an attribute when using 
    `plex_search`, `smart_filter` or `filters` will be shown.

    i.e. a `smart_filter` on the `genre` attribute will return all of the attributes within the specified library.

    <hr style="margin: 0px;">
    
    **Attribute:** `show_options`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_options: true
        ```

??? blank "`show_missing` - Used to show missing items from collections or playlists.<a class="headerlink" href="#show-missing" title="Permanent link">¶</a>"

    <div id="show-missing" />While `show_missing` is true items missing from collections or playlists will be displayed.

    <hr style="margin: 0px;">
    
    **Attribute:** `show_missing`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_missing: false
        ```

??? blank "`only_filter_missing` - Used to have the `filter` only apply to missing items.<a class="headerlink" href="#only-filter-missing" title="Permanent link">¶</a>"

    <div id="only-filter-missing" />Only items missing from a collection will be filtered. **Only specific filters can 
    filter missing. See [Filters](../files/filters.md) for more information.**
    
    ???+ note
    
        This can be used to filter which missing media items get sent to Sonarr/Radarr.

    <hr style="margin: 0px;">
    
    **Attribute:** `only_filter_missing`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
        settings:
          only_filter_missing: true
        ```

??? blank "`show_missing_assets` - Used to print a message when assets are missing.<a class="headerlink" href="#show-missing-assets" title="Permanent link">¶</a>"

    <div id="show-missing-assets" />Display missing asset warnings for items, collections, and playlists.

    <hr style="margin: 0px;">
    
    **Attribute:** `show_missing_assets`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          show_missing_assets: false
        ```

??? blank "`save_report` - Used to save a report YAML file.<a class="headerlink" href="#save-report" title="Permanent link">¶</a>"

    <div id="save-report" />Save a report of the items added, removed, filtered, or missing from collections to a YAML 
    file in the same directory as the file run.

    <hr style="margin: 0px;">
    
    **Attribute:** `save_report`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `true`

    ???+ example "Example"
        
        ```yaml
        settings:
          save_report: false
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
          tvdb_language: en
        ```

??? blank "`ignore_ids` - List of TMDb/TVDb IDs to ignore.<a class="headerlink" href="#ignore-ids" title="Permanent link">¶</a>"

    <div id="ignore-ids" />Set a list or comma-separated string of TMDb/TVDb IDs to ignore in all collections.
    
    ???+ note
    
        This does not apply to `smart_filter` Collections.

    <hr style="margin: 0px;">
    
    **Attribute:** `ignore_ids`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** List or comma-separated string of TMDb/TVDb IDs

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        settings:
          ignore_ids: 572802,695721
        ```

??? blank "`ignore_imdb_ids` - List of IMDb IDs to ignore.<a class="headerlink" href="#ignore-imdb-ids" title="Permanent link">¶</a>"

    <div id="ignore-imdb-ids" />Set a list or comma-separated string of IMDb IDs to ignore in all collections.
    
    ???+ note
    
        Rhis does not apply to `smart_filter` Collections.

    <hr style="margin: 0px;">
    
    **Attribute:** `ignore_imdb_ids`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** List or comma-separated string of IMDb IDs

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        settings:
          ignore_imdb_ids: tt6710474,tt1630029
        ```

??? blank "`item_refresh_delay` - Time to wait between each `item_refresh`.<a class="headerlink" href="#item-refresh-delay" title="Permanent link">¶</a>"

    <div id="item-refresh-delay" />Specify the number of seconds to wait between each `item_refresh` of every movie/show in a collection/playlist.
    
    ???+ note
    
        Useful if your Plex Media Server is having issues with high request levels.

    <hr style="margin: 0px;">
    
    **Attribute:** `item_refresh_delay`

    **Levels with this Attribute:** Global/Library/Collection/Playlist
    
    **Accepted Values:** Any Integer 0 or greater (value is in seconds)

    **Default Value:** `0`

    ???+ example "Example"
        
        ```yaml
        settings:
          item_refresh_delay: 5
        ```

??? blank "`playlist_sync_to_users` - Set the default playlist `sync_to_users`.<a class="headerlink" href="#playlist-sync-to-users" title="Permanent link">¶</a>"

    <div id="playlist-sync-to-users" />Set the default playlist `sync_to_users`. To Sync a playlist to only yourself 
    leave `playlist_sync_to_users` blank.
    
    ???+ note
    
        sharing playlists with other users will not share any posters associated with the playlist, this is a Plex 
    limitation.

    <hr style="margin: 0px;">
    
    **Attribute:** `playlist_sync_to_users`

    **Levels with this Attribute:** Global/Playlist
    
    **Accepted Values:** `all`, list of users, or comma-separated string of users

    **Default Value:** `all`

    ???+ example "Example"
        
        ```yaml
        settings:
          playlist_sync_to_users: 
            - user1
            - user2
        ```

??? blank "`playlist_exclude_users` - Set the default playlist `exclude_users`.<a class="headerlink" href="#playlist-exclude-users" title="Permanent link">¶</a>"

    <div id="playlist-exclude-users" />Set the default playlist `exclude_users`.

    <hr style="margin: 0px;">
    
    **Attribute:** `playlist_exclude_users`

    **Levels with this Attribute:** Global/Playlist
    
    **Accepted Values:** list of users or comma-separated string of users

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        settings:
          playlist_exclude_users: 
            - user1
            - user2
        ```

??? blank "`playlist_report` - Used to print out a playlist report.<a class="headerlink" href="#playlist-report" title="Permanent link">¶</a>"

    <div id="playlist-report" />Set `playlist_report` to true to print out a playlist report at the end of the log.

    <hr style="margin: 0px;">
    
    **Attribute:** `playlist_report`

    **Levels with this Attribute:** Global
    
    **Accepted Values:** `true` or `false`

    **Default Value:** `false`

    ???+ example "Example"
        
        ```yaml
        settings:
          playlist_report: true
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

??? blank "`custom_repo` - Used to set up the custom `repo` [file block type](files.md#location-types-and-paths).<a class="headerlink" href="#custom-repo" title="Permanent link">¶</a>"

    <div id="custom-repo" />Specify where the `repo` attribute's base is when defining `collection_files`, `metadata_files`, `playlist_file` and `overlay_files`.
    
    ???+ note
    
        Ensure you are using the raw GitHub link (i.e. 
        https://github.com/Kometa-Team/Community-Configs/tree/master/meisnate12)

    <hr style="margin: 0px;">
    
    **Attribute:** `custom_repo`

    **Levels with this Attribute:** Global
    
    **Accepted Values:** Link to repository base

    **Default Value:** `None`

    ???+ example "Example"
        
        ```yaml
        settings:
          custom_repo: https://github.com/Kometa-Team/Community-Configs/tree/master/meisnate12
        ```

??? blank "`overlay_artwork_filetype` - Used to control the filetype used with overlay images.<a class="headerlink" href="#overlay-filetype" title="Permanent link">¶</a>"

    <div id="overlay-filetype" />Used to control the filetype used with overlay images.  This setting will only be applied to images generated after the value is added to your config.

    <hr style="margin: 0px;">
    
    **Attribute:** `overlay_artwork_filetype`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:**

    <table class="clearTable">
      <tr><td>`jpg`</td><td>Use JPG files for saving Overlays</td></tr>
      <tr><td>`png`</td><td>Use PNG files for saving Overlays</td></tr>
      <tr><td>`webp_lossy`</td><td>Use Lossy WEBP files for saving Overlays</td></tr>
      <tr><td>`webp_lossless`</td><td>Use Lossless WEBP files for saving Overlays</td></tr>
    </table>

    **Default Value:** `jpg`

    ???+ example "Example"
        
        ```yaml
        settings:
          overlay_artwork_filetype: png
        ```

??? blank "`overlay_artwork_quality` - Used to control the JPG or Lossy WEBP quality used with overlay images.<a class="headerlink" href="#overlay-quality" title="Permanent link">¶</a>"

    <div id="overlay-quality" />Used to control the JPG or Lossy WEBP quality used with overlay images. This setting 
    will only be applied to images generated after the value is added to your config.

    <hr style="margin: 0px;">
    
    **Attribute:** `overlay_artwork_quality`

    **Levels with this Attribute:** Global/Library
    
    **Accepted Values:** Any Integer 1-100 [Values over 95 are not recommended and may result in excessive image size, 
    perhaps too large to be uploaded to Plex.

    **Default Value:** `None` [when no value is provided the standard 75 is used]

    ???+ example "Example"
        
        ```yaml
        settings:
          overlay_artwork_quality: 95
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
    run_order: #(1)!
    - collections
    - metadata
    - operations
    - overlays
    minimum_items: 3 #(2)!
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
  minimum_items: 1 #(4)!
```

1.  Sets the `run_order` specifically for the Movies library
2.  Sets the `minimum_items` attribute specifically for the Movies library
3.  Sets the global `run_order` which will apply to all libraries unless a library-level `run_order` is found, as 
showcased in the above example
4.  Sets the global `minimum_items` which will apply to all libraries unless a library-level `minimum_items` is found, 
as showcased in the above example
