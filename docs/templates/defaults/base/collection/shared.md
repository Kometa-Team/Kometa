=== "Shared Template Variables"

    File paths need to be valid in the context where Kometa is running; this is primarily an issue when running in docker, as Kometa inside the container cannot see host paths.

    | Variable | Description | Values |
    |:---------|:------------|:-------|
    | `collection_mode` | Controls the collection mode of all collections in a Defaults File. | <table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table> |
    | `collection_section` | Changes the sort order of the collection sections against other default collection sections. (Use quotes to not lose leading zeros `"05"`) | Any number |
    | `delete_collections_named` | Used to delete any collections in your plex named one of the given collections. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of Collection Names to delete |
    | `file_background_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the background filepath of the key's collection. | Filepath directly to the Image |
    | `file_background` | Sets the background filepath for all collections. | Filepath directly to the Image |
    | `file_logo_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the logo filepath of the key's collection. | Filepath directly to the Image |
    | `file_logo` | Sets the logo filepath for all collections. | Filepath directly to the Image |
    | `file_poster_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the poster filepath of the key's collection. | Filepath directly to the Image |
    | `file_poster` | Sets the poster filepath for all collections. | Filepath directly to the Image |
    | `file_square_art_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the square art filepath of the key's collection. | Filepath directly to the Image |
    | `file_square_art` | Sets the square art filepath for all collections. | Filepath directly to the Image |
    | `ignore_ids` | Set a List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of TMDb/TVDb IDs to ignore in all collections. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of TMDb/TVDb IDs |
    | `ignore_imdb_ids` | Set a List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of IMDb IDs to ignore in all collections. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of IMDb IDs |
    | `hub_priority_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the position priority for the key's collection's Recommendation Hub row. | **Default:** `hub_priority`<br>Integer greater than 0 |
    | `hub_priority` | Sets the position priority for all collections in a Defaults File. Collections with `hub_priority` are sorted to the front of the hub list (lowest number first) before any `auto_sort_hubs` ordering is applied. Requires the collection to be promoted to a hub via `visible_library`, `visible_home`, or `visible_shared` (Plex Pass Required). If omitted, normal hub sorting is used. | Integer greater than 0 |
    | `item_radarr_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Used to append a tag in Radarr for every movie found by the builders that's in Radarr of the key's collection. | **Default:** `item_radarr_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
    | `item_radarr_tag` | Used to append a tag in Radarr for every movie found by the builders that's in Radarr for all collections in a Defaults File. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
    | `item_sonarr_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Used to append a tag in Sonarr for every series found by the builders that's in Sonarr of the key's collection. | **Default:** `item_sonarr_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
    | `item_sonarr_tag` | Used to append a tag in Sonarr for every series found by the builders that's in Sonarr for all collections in a Defaults File. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
    | `language` | Set the language of Collection Names and Summaries | **Default:** `default`<br>`default` (English), `fr` (French), or `de` (German) |
    | `minimum_items_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Set the number of minimum items for a collection to be created for the key's collection. | Any number greater than 0 |
    | `minimum_items` | Set the number of minimum items for a collection to be created for all collections. | Any number greater than 0 |
    | `name_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the name of the key's collection. | New Collection Name |
    | `name_mapping` | Changes the `name_mapping` of all collections. | **Default:** `<<title>>`<br>Any String with `<<key_name>>` in it. |
    | `order_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the sort order of the collections in their collection section. | Any number |
    | `radarr_add_missing` | Override Radarr `add_missing` attribute for all collections in a Defaults File. | `true` or `false` |
    | `radarr_add_missing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `add_missing` attribute of the key's collection. | **Default:** `radarr_add_missing`<br>`true` or `false` |
    | `radarr_folder` | Override Radarr `root_folder_path` attribute for all collections in a Defaults File. | Folder Path |
    | `radarr_folder_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `root_folder_path` attribute of the key's collection. | **Default:** `radarr_folder`<br>Folder Path |
    | `radarr_monitor_existing` | Override Radarr `monitor_existing` attribute for all collections in a Defaults File. | `true` or `false` |
    | `radarr_monitor_existing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `monitor_existing` attribute of the key's collection. | `true` or `false` |
    | `radarr_search` | Override Radarr `search` attribute or all collections in a Defaults File. | `true` or `false` |
    | `radarr_search_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `search` attribute of the key's collection. | **Default:** `radarr_search`<br>`true` or `false` |
    | `radarr_tag` | Override Radarr `tag` attribute for all collections in a Defaults File. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
    | `radarr_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `tag` attribute of the key's collection. | **Default:** `radarr_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
    | `radarr_upgrade_existing` | Override Radarr `upgrade_existing` attribute for all collections in a Defaults File. | `true` or `false` |
    | `radarr_upgrade_existing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `upgrade_existing` attribute of the key's collection. | `true` or `false` |
    | `schedule_<<key>>` | Set the schedule for a specific key's collection. | Any [Scheduling Option](../../config/schedule.md#important) |
    | `schedule` | Set the schedule for all of the collections in a Defaults File. | Any [Scheduling Option](../../config/schedule.md#important) |
    | `sonarr_add_missing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `add_missing` attribute of the key's collection. | **Default:** `sonarr_add_missing`<br>`true` or `false` |
    | `sonarr_add_missing` | Override Sonarr `add_missing` attribute for all collections in a Defaults File. | `true` or `false` |
    | `sonarr_folder_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `root_folder_path` attribute of the key's collection. | **Default:** `sonarr_folder`<br>Folder Path |
    | `sonarr_folder` | Override Sonarr `root_folder_path` attribute for all collections in a Defaults File. | Folder Path |
    | `sonarr_monitor_existing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `monitor_existing` attribute of the key's collection. | `true` or `false` |
    | `sonarr_monitor_existing` | Override Sonarr `monitor_existing` attribute for all collections in a Defaults File. | `true` or `false` |
    | `sonarr_search_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `search` attribute of the key's collection. | **Default:** `sonarr_search`<br>`true` or `false` |
    | `sonarr_search` | Override Sonarr `search` attribute or all collections in a Defaults File. | `true` or `false` |
    | `sonarr_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `tag` attribute of the key's collection. | **Default:** `sonarr_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
    | `sonarr_tag` | Override Sonarr `tag` attribute for all collections in a Defaults File. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
    | `sonarr_upgrade_existing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `upgrade_existing` attribute of the key's collection. | `true` or `false` |
    | `sonarr_upgrade_existing` | Override Sonarr `upgrade_existing` attribute for all collections in a Defaults File. | `true` or `false` |
    | `sort_prefix` | Changes the prefix of the sort title. | **Default:** `!`<br>Any String |
    | `sort_title` | Changes the sort title of all collections. | **Default:** `<<sort_prefix>><<collection_section>><<pre>><<order_<<key>>>><<title>>`<br>Any String |
    | `summary_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the summary of the key's collection. | New Collection Summary |
    | `url_background_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the background url of the key's collection. | URL directly to the Image |
    | `url_background` | Sets the background url for all collections. | URL directly to the Image |
    | `url_logo_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the logo url of the key's collection. | URL directly to the Image |
    | `url_logo` | Sets the logo url for all collections. | URL directly to the Image |
    | `url_poster_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the poster url of the key's collection. | URL directly to the Image |
    | `url_poster` | Changes the poster url for all collections. | URL directly to the Image |
    | `url_square_art_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the square url of the key's collection. | URL directly to the Image |
    | `url_square_art` | Sets the square url for all collections. | URL directly to the Image |
    | `use_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Turns off individual Collections in a Defaults File. | `false` to turn off the collection |
    | `use_all` | Turns off all Collections in a Defaults File. | `false` to turn off the collection |
    | `visible_home_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls visible on Home Tab of the key's collection. (Only works with Plex Pass) | **Default:** `visible_home`<br><table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table> |
    | `visible_home` | Controls visible on Home Tab for all collections in a Defaults File. (Only works with Plex Pass) | <table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table> |
    | `visible_library_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls visible on Library Recommended Tab of the key's collection. (Only works with Plex Pass) | **Default:** `visible_library`<br><table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table> |
    | `visible_library` | Controls visible on Library Recommended Tab for all collections in a Defaults File. (Only works with Plex Pass) | <table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table> |
    | `visible_shared_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls visible on Shared Users' Home Tab of the key's collection. (Only works with Plex Pass) | **Default:** `visible_shared`<br><table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table> |
    | `visible_shared` | Controls visible on Shared Users' Home Tab for all collections in a Defaults File. (Only works with Plex Pass) | <table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table> |

<!--separator-variables-->

=== "Shared Separator Variables"

    | Variable | Description | Values |
    |:---------|:------------|:-------|
    | `collection_mode` | Controls the collection mode of all collections in a Defaults File. | <table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table> |
    | `collection_section` | Changes the sort order of the collection sections against other default collection sections. | Any number |
    | `name_separator` | Changes the name of the key's collection. | New Collection Name |
    | `placeholder_imdb_id` | Add a placeholder Movie/Show to the Separator. Valid for Movie or Show libraries assuming the ID points to an item of the correct type. | IMDb ID |
    | `placeholder_tmdb_movie` | Add a placeholder Movie to the Separator. Only valid for Movie libraries. | TMDb Movie ID |
    | `placeholder_tvdb_show` | Add a placeholder Show to the Separator. Only valid for Show libraries. | TVDb Show ID |
    | `sep_style` | Choose the [Separator Style](../../../../defaults/separators.md#separator-styles). | **Default:** `orig`<br>`amethyst`, `aqua`, `blue`, `forest`, `fuchsia`, `gold`, `gray`, `green`, `navy`, `ocean`, `olive`, `orchid`, `orig`, `pink`, `plum`, `purple`, `red`, `rust`, `salmon`, `sand`, `stb`, or `tan` |
    | `sort_prefix` | Changes the prefix of the sort title. | **Default:** `!`<br>Any String |
    | `sort_title` | Changes the sort title of all collections. | **Default:** `<<sort_prefix>><<collection_section>>_!<<title>>`<br>Any String |
    | `summary_separator` | Changes the summary of the key's collection. | New Collection Summary |
    | `url_poster_separator` | Changes the poster url of the key's collection. | URL directly to the Image |
    | `use_separator` | Turn the [Separator Collection](../../../../defaults/separators.md#use-separators) off. | `false` to turn of the collection |
