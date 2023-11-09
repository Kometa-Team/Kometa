---
search:
  boost: 5 
---
# Settings

## Overview
The `settings:` attribute and subsequent settings can be used to command various aspects of the functionality of Plex Meta Manager.

Examples of these settings include the ability to:

* Cache each Plex GUID and IDs to increase performance
* Create asset folders for collections so that custom posters can be stored for upload.
* Use a custom repository as the base for all `git` Metadata files.

The settings attribute and attributes can be specified individually per library, or can be inherited from the global value if it has been set. If an attribute is specified at both the library and global level, then the library level attribute will take priority.

There are some attributes which can be specified at the collection level using [Setting Details](../builders/details/definition.md).

Attributes set at the collection level will take priority over any library or global-level attribute.

## Attributes

The available setting attributes which can be set at each level are outlined below:


| Attribute                                                     | Global Level | Library Level | Collection/Playlist Level |
|:--------------------------------------------------------------|:------------:|:-------------:|:-------------------------:|
| [`cache`](#cache)                                             |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`cache_expiration`](#cache-expiration)                       |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`asset_directory`](#image-asset-directory)                   |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`asset_folders`](#image-asset-folders)                       |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`asset_depth`](#asset-depth)                                 |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`create_asset_folders`](#create-asset-folders)               |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`prioritize_assets`](#prioritize-assets)                     |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`dimensional_asset_rename`](#dimensional-asset-rename)       |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`download_url_assets`](#download-url-assets)                 |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`show_missing_season_assets`](#show-missing-season-assets)   |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`show_missing_episode_assets`](#show-missing-episode-assets) |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`show_asset_not_needed`](#show-asset-not-needed)             |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`sync_mode`](#sync-mode)                                     |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`default_collection_order`](#default-collection-order)       |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`minimum_items`](#minimum-items)                             |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`delete_below_minimum`](#delete-below-minimum)               |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`delete_not_scheduled`](#delete-not-scheduled)               |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`run_again_delay`](#run-again-delay)                         |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`missing_only_released`](#missing-only-released)             |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`show_unmanaged`](#show-unmanaged-collections)               |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`show_unconfigured`](#show-unconfigured-collections)         |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`show_filtered`](#show-filtered)                             |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`show_options`](#show-options)                               |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`show_missing`](#show-missing)                               |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`only_filter_missing`](#only-filter-missing)                 |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`show_missing_assets`](#show-missing-assets)                 |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`save_report`](#save-report)                                 |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`tvdb_language`](#tvdb-language)                             |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`ignore_ids`](#ignore-ids)                                   |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`ignore_imdb_ids`](#ignore-imdb-ids)                         |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`item_refresh_delay`](#item-refresh-delay)                   |   :fontawesome-solid-circle-check:{ .green }    |    :fontawesome-solid-circle-check:{ .green }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`playlist_sync_to_users`](#playlist-sync-to-users)           |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`playlist_exclude_users`](#playlist-exclude-users)           |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |          :fontawesome-solid-circle-check:{ .green }          |
| [`playlist_report`](#playlist-report)                         |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`custom_repo`](#custom-repo)                                 |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`verify_ssl`](#verify-ssl)                                   |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |         :fontawesome-solid-circle-xmark:{ .red }          |
| [`check_nightly`](#check-nightly)                             |   :fontawesome-solid-circle-check:{ .green }    |   :fontawesome-solid-circle-xmark:{ .red }    |         :fontawesome-solid-circle-xmark:{ .red }          |

## Cache
Cache the Plex GUID and associated IDs for each library item for faster subsequent processing. The cache file is created in the same directory as the configuration file.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>true</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Cache Expiration
Set the number of days before each cache mapping expires and has to be re-cached.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>60</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>any integer</td>
  </tr>
</table>

## Image Asset Directory
Specify the directory where assets (posters, backgrounds, etc) are located.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>[Directory containing YAML config]/assets</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>any directory</td>
  </tr>
</table>

## Image Asset Folders
Search the `asset_directory` for a dedicated folder. Set to true if each poster is within its own directory.<br>
i.e. `assets/Star Wars/poster.png` instead of `assets/Star Wars.png`

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>true</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Asset Depth

Specify how many folder levels to scan for an item within the asset directory<br>
At each asset level, PMM will look for either `medianame.ext` [such as Star Wars.png] or a dedicated folder containing `poster.ext`<br>
i.e. `assets/Star Wars/poster.png` and `assets/Star Wars.png` are both asset depth 0
and `assets/Movies/Star Wars/poster.png` and `assets/Movies/Star Wars.png` are both asset level 1

* `asset_folders` must be set to `true` for this to take effect.
* increasing the amount of levels to scan will reduce performance

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>0</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>any integer</td>
  </tr>
</table>

## Create Asset Folders

Whilst searching for assets, if an asset folder cannot be found within the `asset_directory` one will be created.

Asset Searches can happen in a number of ways.

* Any Collection specified under the `collections` header in a Metadata File.
* Any Item specified under the `metadata` header in a Metadata File.
* Any Playlist specified under the `playlists` header in a Playlist File.
* Any Item in a library that is running the `assets_for_all` Library Operation.
* Any Item that has an Overlay applied to it.
* Any Item found by a Builder while the definition also has `item_assets: true` specified. 

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Prioritize Assets
When determining which image to use on an item prioritize the `asset_directory` over all other images types.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Dimensional Asset Rename
Whilst searching for assets, scan the folders within the `asset_directory` and if an asset poster (i.e. `/ASSET_NAME/poster.ext`) was not found, rename the first image found that has a height greater than or equal to its width to `poster.ext`. If an asset background (i.e. `/ASSET_NAME/background.ext`), rename the first image found that has a width greater than its height to `background.ext`.
* `asset_folders` must be set to `true` for this to take effect.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Download URL Assets
Whilst searching for assets, download images set within Metadata/Playlist files( i.e. images set by `url_poster` or `url_background`) into the asset folder if none are already present.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Show Missing Season Assets
Whilst searching for assets, when scanning for assets for a TV Show, if Season posters are found (i.e. `/ASSET_NAME/Season##.ext`), notify the user of any seasons which do not have an asset image.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Show Missing Episode Assets
Whilst searching for assets, when scanning for assets for a TV Show, if an Episode Title Card is found (i.e. `/ASSET_NAME/S##E##.ext`), notify the user of any episodes which do not have an asset image.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Show Asset Not Needed
Whilst searching for assets, show or hide the `update not needed` messages.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Sync Mode
Set the default `sync_mode` for collections.

* `sync` will add and remove any items that are added/removed from the source builder
* `append` will only add items that are added from the source builder, but will not remove anything even if it is removed from the source builder.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>append</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>append</code> or <code>sync</code>
    </td>
  </tr>
</table>

## Default Collection Order

Set the default `collection_order` for every collection run by PMM.

* `custom` cannot be used if more than one builder is being used for the collection (such as `imdb_list` and `trakt_list` within the same collection)

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>None</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>release</code>: Order Collection by Release Dates<br>
    <code>alpha</code>: Order Collection Alphabetically<br>
    <code>custom</code>: Order Collection Via the Builder Order<br>
    Any <code>plex_search</code> sort option<sup>1</sup><br>
    </td>
  </tr>
</table>

<sup>1</sup> `plex_search` sort options can be found [here](plex.md#sort-options)

## Minimum Items
Set the minimum number of items that must be found in order to build or update a collection/playlist.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>1</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>any integer</td>
  </tr>
</table>

## Delete Below Minimum

When a collection is run, delete the collection if it is below the minimum number specified by `minimum_items`.

* Relies on `minimum_items` being set to the desired integer.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Delete Not Scheduled
If a collection is skipped due to it not being scheduled, delete the collection.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Run Again Delay

Set the number of minutes to delay running `run_again` collections after daily run is finished.

For example, if a collection adds items to Sonarr/Radarr, the library can automatically re-run "X" amount of time later so that any downloaded items are processed.

* A collection is a `run_again` collection if it has the `run_again` [Setting Detail](../builders/details/definition.md) attribute set to true.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>1</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>any integer</td>
  </tr>
</table>

## Missing Only Released

Whilst running a collection, all unreleased missing items will be filtered out from the [missing YAML file](../builders/details/definition.md)

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Show Unmanaged Collections

List all collections not managed by Plex Meta Manager at the end of each run.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>true</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Show Filtered
List all items which have been filtered out of a collection (i.e. if it doesn't meet the filter criteria)

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Show Options
While `show_options` is true the available options for an attribute when using `plex_search`, `smart_filter` or `filters` will be shown.
i.e. a `smart_filter` on the `genre` attribute will return all of the attributes within the specified library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>


## Show Missing
While `show_missing` is true items missing from collections will be displayed.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>true</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Only Filter Missing

Only items missing from a collection will be filtered. **Only specific filters can filter missing. See [Filters](../metadata/filters.md) for more information.** 

* this can be used to filter which missing media items get sent to Sonarr/Radarr

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Show Missing Assets
Display missing asset warnings

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>true</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Save Report
Save a report of the items added, removed, filtered, or missing from collections to a YAML file in the same directory as your Metadata file.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>true</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## TVDb Language

Specify the language to query TVDb in.

* If no language is specified or the specified language is not found then the original language is used.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>None</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>Any ISO 639-2 Language Code<sup>1</sup></td>
  </tr>
</table>

<sup>1</sup> Language Codes can be found [here](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)

## Ignore IDs

Set a list or comma-separated string of TMDb/TVDb IDs to ignore in all collections.

* this does not apply to `smart_filter` Collections

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>None</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>List or comma-separated string of TMDb/TVDb IDs</td>
  </tr>
</table>

## Ignore IMDb IDs

Set a list or comma-separated string of IMDb IDs to ignore in all collections.

* this does not apply to `smart_filter` Collections

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>None</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>List or comma-separated string of IMDb IDs</td>
  </tr>
</table>

## Item Refresh Delay

Specify the amount of time to wait between each `item_refresh` of every movie/show in a collection/playlist.

* Useful if your Plex Media Server is having issues with high request levels.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>0</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>any integer</td>
  </tr>
</table>

## Playlist Sync to Users

Set the default playlist `sync_to_users`. To Sync a playlist to only yourself leave `playlist_sync_to_users` blank.

* sharing playlists with other users will not share any posters associated with the playlist, this is a Plex limitation.
<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>all</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>all</code>, list of users, or comma-separated string of users</td>
  </tr>
</table>

## Playlist Exclude Users
Set the default playlist `exclude_users`.
<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code> </code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>list of users or comma-separated string of users</td>
  </tr>
</table>

# Playlist Report
Set `playlist_report` to true to print out a playlist report at the end of the log.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
  </tr>
</table>

## Custom Repo

Specify where the `repo` attribute's base is when defining `metadata_path`, `playlist_file` and `overlay_path`.

* Ensure you are using the raw GitHub link (i.e. https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/meisnate12 )

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>None</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td>link to base repository</td>
  </tr>
</table>

## Verify SSL

Turn SSL Verification on or off.

* set to false if your log file shows any errors similar to "SSL: CERTIFICATE_VERIFY_FAILED"
<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>true</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>

## Check Nightly

Will check nightly for updates instead of develop. 

* This does not affect which version of PMM is grabbed when using `git pull` or any other update mechanism, it is only used for the initial version check when PMM runs to specify if a new version is available.
* It is recommended to set this to `true` if you primarily use the `nightly` branch

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th>Default Value</th>
    <td><code>false</code></td>
  </tr>
  <tr>
    <th>Allowed Values</th>
    <td><code>true</code> or <code>false</code>
    </td>
  </tr>
</table>
