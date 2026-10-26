<!--aspect-overlay-->
| `text_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Choose the text for the Overlay. | Any String<br><table class="clearTable" style="text-align:left;"><tr><th>Key</th><th>Default Text</th></tr><tr><td>`1.33`</td><td>`1.33`</td></tr><tr><td>`1.65`</td><td>`1.65`</td></tr><tr><td>`1.66`</td><td>`1.66`</td></tr><tr><td>`1.78`</td><td>`1.78`</td></tr><tr><td>`1.85`</td><td>`1.85`</td></tr><tr><td>`2.2`</td><td>`2.2`</td></tr><tr><td>`2.35`</td><td>`2.35`</td></tr><tr><td>`2.77`</td><td>`2.77`</td></tr></table> |
<!--aspect-overlay-->
<!--commonsense-overlay-->
| `pre_text` | Choose the text before the key for the Overlay. | Any String |
| `post_text` | Choose the text after the key for the Overlay. | **Default:** `+`<br>Any String |
| `pre_nr_text` | Choose the text before the `nr` key for the Overlay. | Any String |
| `post_nr_text` | Choose the text after the `nr` key for the Overlay. | Any String |
<!--commonsense-overlay-->
<!--language_count-overlay-->
| `minimum` | Choose the minimum for the `multi` Overlay. | **Default:** `2`<br>Any Number |
| `use_subtitles` | Controls if the overlay is based on subtitle language instead of audio language. | `true` to look at subtitle language instead of audio language |
<!--language_count-overlay-->
<!--languages-overlay-->
| `country_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the country image for the Overlay. | **Default:** Listed in the [Table](#supported-audiosubtitle-language-flags) above<br>[ISO 3166-1 Country Code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) for the flag desired |
| `flag_alignment` | Controls the flag alignment in the backdrop. | **Default:** `left`<br>`left` or `right` |
| `group_alignment` | Choose the display alignment for the flag group. | **Default:** `vertical`<br>`horizontal`, or `vertical` |
| `hide_text` | Disables the country code text, showing only the flag. | **Default:** `false`<br>`true` to hide the country text |
| `horizontal_position` | Choose the horizontal position for the flag group. | **Default:** `left`<br>`left`, `left2`, `center`, `center_left`, `center_right`, `right` or `right2` |
| `horizontal_spacing` | Controls the vertical spacing from one overlay in the queue to the next. | Any Integer |
| `initial_horizontal_align` | Controls the initial horizontal align the queue starts from. | `left`, `center`, or `right` |
| `initial_horizontal_offset` | Controls the initial horizontal offset the queue starts from. | Any Integer |
| `initial_vertical_align` | Controls the initial vertical align the queue starts from. | `top`, `center`, or `bottom` |
| `initial_vertical_offset` | Controls the initial vertical offset the queue starts from. | Any Integer |
| `languages` | Controls which Languages will be active. | **Default:** `["en", "de", "fr", "es", "pt", "ja"]`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of [ISO 639-1 Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) for the Languages desired |
| `offset` | Controls the offset between the flag and the text. | **Default:** `10`<br>Any Integer 0 or greater |
| `overlay_limit` | Choose the number of overlay this queue displays. | **Default:** `3`<br>`1`, `2`, `3`, `4`, or `5` |
| `position` | Use the Custom Given Queue instead of the the provided Queues. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of Coordinates |
| `size` | Controls the size of the overlay. | **Default:** `small`<br>`small` or `big` |
| `style` | Controls the visual theme of the overlays created. | <table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>round</code></td><td>Round Theme</td></tr><tr><td><code>square</code></td><td>Square Theme</td></tr><tr><td><code>half</code></td><td>Square Flag with Round Background</td></tr></table> |
| `use_lowercase` | Controls if the overlay display is in lowercase. | `true` to use lowercase text |
| `use_subtitles` | Controls if the overlay is based on subtitle language instead of audio language. | `true` to look at subtitle language instead of audio language |
| `vertical_position` | Choose the vertical position for the flag group. | **Default:** `top`<br>`top`, `top2`, `top3`, `center`, `center_top`, `center_bottom`, `bottom`, `bottom2` or `bottom3` |
| `vertical_spacing` | Controls the vertical spacing from one overlay in the queue to the next. | Any Integer |
<!--languages-overlay-->

<!--ratings-overlay-->
| `fresh_rating` | Threshold used by Fresh/Rotten image levels. Ratings at or above this value are Fresh; below it are Rotten. Uses the normalised 0–10 scale (e.g. `6.0` = 60% on Rotten Tomatoes). | **Default:** `6.0`<br>Any Number |
| `horizontal_position` | Choose the horizontal position for the rating group. | **Default:** `left`<br>`left`, `right`, or `center` |
| `vertical_position` | Choose the vertical position for the rating group. | **Default:** `center`<br>`top`, `bottom`, or `center` |
| `maximum_rating` | Maximum Rating to display | **Default:** 10.0<br>Any Number |
| `minimum_rating` | Minimum Rating to display | **Default:** 0.0<br>Any Number |
| `rating1` | Choose the rating source to display in rating1. `critic`, `audience`, and `user` read from Plex's own rating slots (require a Mass Metadata Update operation to populate). All other sources are fetched directly from external services during the overlay run — no operation required. | `critic`, `audience`, `user`, `serializd` (shows and episodes only), or any source key from the [Mass Metadata Update](../../config/operations.md#mass-metadata-update) ratings table (e.g. `imdb`, `tmdb`, `mdb_tomatoes`) |
| `rating_alignment` | Choose the display alignment for the rating group. | **Default:** `vertical`<br>`horizontal`, or `vertical` |
| `rating1_addon_offset` | Text Addon Image Offset from the text. | **Default:** `15`<br>Any number greater than 0 |
| `rating1_addon_position` | Text Addon Image Alignment in relation to the text. | **Default:** `top`<br>`left`, `right`, `top`, `bottom` |
| `rating1_extra` | Extra text after rating1. | **Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`.<br>Any Value |
| `rating1_image` | Choose the rating image to display in rating1. Optional — when omitted the image is auto-picked based on the `rating1` value. | `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `omdb`, `rt_popcorn`, `rt_tomato`, `mal`, `mdb`, `critic`, `audience`, or `star` |
| `rating1_style` | Choose the rating number style for rating1. Please refer to the detailed style guide. | — |
| `rating2` | Choose the rating source to display in rating2. See `rating1` for details on Plex-native vs. fetched sources. | `critic`, `audience`, `user`, or any source key from the [Mass Metadata Update](../../config/operations.md#mass-metadata-update) ratings table |
| `rating2_addon_offset` | Text Addon Image Offset from the text. | **Default:** `15`<br>Any number greater than 0 |
| `rating2_addon_position` | Text Addon Image Alignment in relation to the text. | **Default:** `top`<br>`left`, `right`, `top`, `bottom` |
| `rating2_extra` | Extra text after rating2. | **Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`.<br>Any Value |
| `rating2_image` | Choose the rating image to display in rating2. Optional — when omitted the image is auto-picked based on the `rating2` value. | `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `omdb`, `rt_popcorn`, `rt_tomato`, `mal`, `mdb`, `critic`, `audience`, or `star` |
| `rating2_style` | Choose the rating number style for rating2. Please refer to the detailed style guide. | — |
| `rating3` | Choose the rating source to display in rating3. See `rating1` for details on Plex-native vs. fetched sources. | `critic`, `audience`, `user`, or any source key from the [Mass Metadata Update](../../config/operations.md#mass-metadata-update) ratings table |
| `rating3_addon_offset` | Text Addon Image Offset from the text. | **Default:** `15`<br>Any number greater than 0 |
| `rating3_addon_position` | Text Addon Image Alignment in relation to the text. | **Default:** `top`<br>`left`, `right`, `top`, `bottom` |
| `rating3_extra` | Extra text after rating3. | **Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`.<br>Any Value |
| `rating3_image` | Choose the rating image to display in rating3. Optional — when omitted the image is auto-picked based on the `rating3` value. | `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `omdb`, `rt_popcorn`, `rt_tomato`, `mal`, `mdb`, `critic`, `audience`, or `star` |
| `rating3_style` | Choose the rating number style for rating3. Please refer to the detailed style guide. | — |
<!--ratings-overlay-->
<!--resolution-overlay-->
| `use_edition` | Turns off all Edition Overlays in the Defaults File. | `false` to turn off the overlays |
| `use_resolution` | Turns off all Resolution Overlays in the Defaults File. | `false` to turn off the overlays |
<!--resolution-overlay-->
<!--ribbon-overlay-->
| `style` | Controls the color of the ribbon. | **Default:** `yellow`<br>`yellow`, `gray`, `black`, `red` |
| `use_all` | Used to turn on/off all keys. | **Default:** `true`<br>`true` or `false` |
<!--ribbon-overlay-->
<!--runtimes-overlay-->
| `format` | Choose the format of the displayed runtime. | **Default:** `<<runtimeH>>h <<runtimeM>>m`<br>Any String |
| `text` | Choose the text that appears prior to the runtime on the Overlay. | **Default:** `Runtime:`<br>Any String |
<!--runtimes-overlay-->
<!--status-overlay-->
| `last` | Episode Air Date in the last number of days for the AIRING Overlay. | **Default:** `14`<br>Any number greater than 0 |
| `text_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Choose the text for the Overlay. | Any String<br><table class="clearTable" style="text-align:left;"><tr><th>Key</th><th>Default Text</th></tr><tr><td>`airing`</td><td>`AIRING`</td></tr><tr><td>`returning`</td><td>`RETURNING`</td></tr><tr><td>`canceled`</td><td>`CANCELED`</td></tr><tr><td>`ended`</td><td>`ENDED`</td></tr></table> |
<!--status-overlay-->
<!--streaming-overlay-->
| `discover_with_<<key>>` | Overrides the TMDb Watch Provider used for the specified key. This is only needed if a specific `region` has a different ID for the watch provider. | **Default:** `<<discover_with>>`<br>Any TMDb Watch Provider ID for [Movies](https://developer.themoviedb.org/reference/watch-providers-movie-list) / [Shows](https://developer.themoviedb.org/reference/watch-provider-tv-list) based on the user's region |
| `originals_only` | Changes Streaming Service overlays to only apply to original content produced by the service.<br>**Note**: Cannot be used with `region`, and only produces overlays for `amazon`, `appletv`, `disney`, `max`, `hulu`, `netflix`, `paramount`, `peacock` | **Default:** `false`<br>`true`, `false` |
| `region` | Changes some Streaming Service lists to regional variants (see below table for more information. | **Default:** `US`<br>Any [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) of the region where the streaming information should be based on. |
<!--streaming-overlay-->
<!--studio-overlay-->
| `style` | Choose between the standard size or the **bigger** one. | `bigger` |
<!--studio-overlay-->
<!--video_format-overlay-->
| `text_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Choose the text for the Overlay. | Any String<br><table class="clearTable" style="text-align:left;"><tr><th>Key</th><th>Default Text</th></tr><tr><td>`remux`</td><td>`REMUX`</td></tr><tr><td>`bluray`</td><td>`BLU-RAY`</td></tr><tr><td>`web`</td><td>`WEB`</td></tr><tr><td>`hdtv`</td><td>`HDTV`</td></tr><tr><td>`dvd`</td><td>`DVD`</td></tr><tr><td>`sdtv`</td><td>`SDTV`</td></tr></table> |
<!--video_format-overlay-->

<!--playlists-->
| `delete_playlist_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Will delete the key's playlists for the users defined by sync_to_users. | `true` or `false` |
| `delete_playlist` | Will delete all playlists for the users defined by sync_to_users. | `true` or `false` |
| `exclude_user_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the users to exclude from sync the key's playlist. | **Default:** `sync_to_users` Value<br>Comma-separated string or list of user names. |
| `exclude_user` | Sets the users to exclude from sync for all playlists. | **Default:** `playlist_sync_to_users` Global Setting Value<br>Comma-separated string or list of user names. |
| `ignore_ids` | Set a List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of TMDb/TVDb IDs to ignore in all playlists. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of TMDb/TVDb IDs |
| `ignore_imdb_ids` | Set a List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of IMDb IDs to ignore in all playlists. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of IMDb IDs |
| `imdb_list_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the Movies in the IMDb List to the key's playlist. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of IMDb List URLs |
| `item_radarr_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Used to append a tag in Radarr for every movie found by the builders that's in Radarr of the key's playlist. | **Default:** `item_radarr_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `item_radarr_tag` | Used to append a tag in Radarr for every movie found by the builders that's in Radarr for all playlists in a Defaults file. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `item_sonarr_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Used to append a tag in Sonarr for every series found by the builders that's in Sonarr of the key's playlist. | **Default:** `item_sonarr_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `item_sonarr_tag` | Used to append a tag in Sonarr for every series found by the builders that's in Sonarr for all playlists in a Defaults file. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `libraries` | Sets the names of the libraries to use for the Playlists. | **Default:** All libraries processed as part of the run.<br>Comma-separated string or list of library mapping names defined in the `libraries` attribute in the base of your [Configuration File](../config/overview.md. |
| `mdblist_list_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the Movies in the MDBList List to the key's playlist. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of MDBList List URLs |
| `name_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the name of the key's playlist. | New Playlist Name |
| `radarr_add_missing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `add_missing` attribute of the key's playlist. | **Default:** `radarr_add_missing`<br>`true` or `false` |
| `radarr_add_missing` | Override Radarr `add_missing` attribute for all playlists in a Defaults file. | `true` or `false` |
| `radarr_folder_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `root_folder_path` attribute of the key's playlist. | **Default:** `radarr_folder`<br>Folder Path |
| `radarr_folder` | Override Radarr `root_folder_path` attribute for all playlists in a Defaults file. | Folder Path |
| `radarr_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Radarr `tag` attribute of the key's playlist. | **Default:** `radarr_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `radarr_tag` | Override Radarr `tag` attribute for all playlists in a Defaults file. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `sonarr_add_missing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `add_missing` attribute of the key's playlist. | **Default:** `sonarr_add_missing`<br>`true` or `false` |
| `sonarr_add_missing` | Override Sonarr `add_missing` attribute for all playlists in a Defaults file. | `true` or `false` |
| `sonarr_folder_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `root_folder_path` attribute of the key's playlist. | **Default:** `sonarr_folder`<br>Folder Path |
| `sonarr_folder` | Override Sonarr `root_folder_path` attribute for all playlists in a Defaults file. | Folder Path |
| `sonarr_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override Sonarr `tag` attribute of the key's playlist. | **Default:** `sonarr_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `sonarr_tag` | Override Sonarr `tag` attribute for all playlists in a Defaults file. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `summary_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the summary of the key's playlist. | New Playlist Summary |
| `sync_to_users_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the users to sync the key's playlist to. | **Default:** `sync_to_user` Value<br>Comma-separated string or list of user names. |
| `sync_to_users` | Sets the users to sync all playlists to. | **Default:** `playlist_sync_to_users` Global Setting Value<br>Comma-separated string or list of user names. |
| `url_poster_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the poster url of the key's playlist. | URL directly to the Image |
| `use_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Turns off individual Playlists in a Defaults file. | `false` to turn off the playlist |
<!--playlists-->

<!--addon_image-->
| `addon_offset` | Text Addon Image Offset from the text. | **Default:** `15`<br>Any number greater than 0 |
| `addon_position` | Text Addon Image Alignment in relation to the text. | **Default:** `left`<br>`left`, `right`, `top`, `bottom` |
<!--addon_image-->
<!--builder_level-->
| `builder_level` | Choose the Overlay Level. | `season` or `episode` |
<!--builder_level-->
<!--color-->
| `color` | Color version of the content rating images | **Default:** Set to `false` if you want b&w version. |
<!--color-->

<!--regex-->
| `regex_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the regex of the Overlay Search. | Any Proper Regex |
<!--regex-->
<!--style-->
| `style` | Choose the Overlay Style. | **Default:** `compact`<br>`compact` or `standard` |
<!--style-->
<!--weight-->
| `weight_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the weight of the Overlay. Higher numbers have priority. | Any Number |
<!--weight-->
<!--overlay-white-style-->
| `style` | Choose between the default color version or the **white** one. | `color` or `white` |
<!--overlay-white-style-->








<!--award-->
| `use_year_collections` | Turn the individual year collections off. | `false` to turn of the collections |
| `year_collection_section` | Change the collection section for year collections only. (Use quotes to not lose leading zeros `"05"`) | Any number |
<!--award-->
<!--seasonal-->
| `emoji` | Prefix an emoji to the title of Collections. | Any emoji followed by a space, all wrapped in quotes (i.e. "🎅 ") |
| `emoji_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Prefix an emoji to the title of the specified [key's](#collection_section) collection. Overrides the [default emoji](#default-value-source) for that collection if used. | Any emoji followed by a space, all wrapped in quotes (i.e. "🔥 ") |
| `imdb_list_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the Movies in the IMDb List to the specified [key's](#collection_section) collection. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of IMDb List URLs |
| `imdb_search_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the Movies in the IMDb Search to the specified [key's](#collection_section) collection. Overrides the [default imdb_search](#default-value-source) for that collection if used. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of IMDb List URLs |
| `letterboxd_list_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the Movies in the Letterboxd List to the specified [key's](#collection_section) collection. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of Letterboxd List URLs |
| `mdblist_list_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the Movies in the MDb List to the specified [key's](#collection_section) collection. Overrides the [default mdblist_list](#default-value-source) for that collection if used. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of MDBList URLs |
| `tmdb_collection_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the TMDb Collection IDs given to the specified [key's](#collection_section) collection. Overrides the [default tmdb_collection](#default-value-source) for that collection if used. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Collection IDs |
| `tmdb_movie_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the TMDb Movie IDs given to the specified [key's](#collection_section) collection. Overrides the [default tmdb_movie](#default-value-source) for that collection if used. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Movie IDs |
| `schedule` | Changes the Schedule for all collections in this file. Use `daily` to have all collections show. | [Any Schedule Option](../../config/schedule.md) |
| `schedule_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the Schedule of the specified [key's](#collection_section) collection. Overrides the [default schedule](#default-value-source) for that collection if used. | [Any Schedule Option](../../config/schedule.md) |
<!--seasonal-->
<!--show-franchise-->
| `addons` | Overrides the [default addons dictionary](#default-value-source). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Show IDs |
| `append_addons` | Appends to the [default addons dictionary](#default-value-source). | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Show IDs |
| `append_data` | Appends to the [default data dictionary](#default-value-source). | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Main Show ID |
| `build_collection` | Controls if you want the collection to actually be built. i.e. you may just want these shows sent to Sonarr. | `false` to not build the collection |
| `collection_section` | Adds a sort title with this collection sections. | Any number |
| `data` | Overrides the [default data dictionary](#default-value-source). Defines the data that the custom dynamic collection processes. | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Main Show ID |
| `exclude` | Exclude these Collections from creating a Dynamic Collection. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of Collection IDs |
| `minimum_items` | Controls the minimum items that the collection must have to be created. | **Default:** `2`<br>Any number |
| `name_mapping_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the name mapping value for using assets of the [key's](#collection_section) collection. | Any String |
| `order_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the sort order of the collections in their collection section. | Any number |
| `remove_addons` | Removes from the [default addons dictionary](#default-value-source). | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Show IDs |
| `remove_data` | Removes from the [default data dictionary](#default-value-source). | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Main Show IDs to remove |
| `sort_title_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the sort title of the [key's](#collection_section) collection. | **Default:** `sort_title`<br>Any String |
| `sort_title` | Sets the sort title for all collections. Use `<<collection_name>>` to use the collection name. **Example:** `"!02_<<collection_name>>"` | Any String with `<<collection_name>>` |
| `summary_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the summary of the [key's](#collection_section) collection. | New Collection Summary |
<!--show-franchise-->
<!--franchise-->
| `build_collection` | Controls if you want the collection to actually be built. i.e. you may just want these movies sent to Radarr. | `false` to not build the collection |
| `collection_section` | Adds a sort title with this collection sections. | Any number |
| `minimum_items` | Controls the minimum items that the collection must have to be created. | **Default:** `2`<br>Any number |
| `movie_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the TMDb Movie IDs given to the [key's](#collection_section) collection. Overrides the [default movie](#default-value-source) for that collection if used. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } of TMDb Movie IDs |
| `name_mapping_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the name mapping value for using assets of the [key's](#collection_section) collection.Overrides the [default name_mapping](#default-value-source) for that collection if used. | Any String |
| `order_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Controls the sort order of the collections in their collection section. | Any number |
| `sort_title_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the sort title of the [key's](#collection_section) collection. | **Default:** `sort_title`<br>Any String |
| `sort_title` | Sets the sort title for all collections. Use `<<collection_name>>` to use the collection name. **Example:** `"!02_<<collection_name>>"` | Any String with `<<collection_name>>` |
| `summary_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the summary of the [key's](#collection_section) collection. | New Collection Summary |
| `title_override` | Overrides the [default title_override dictionary](#default-value-source). | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } with `key: new_title` entries |
| `file_background_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the background filepath of the [key's](#collection_section) collection. | Filepath directly to the Image |
| `file_logo_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the logo filepath of the [key's](#collection_section) collection. | Filepath directly to the Image |
| `file_poster_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the poster filepath of the [key's](#collection_section) collection. | Filepath directly to the Image |
| `file_square_art_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the square art filepath of the [key's](#collection_section) collection. | Filepath directly to the Image |
| `url_background_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the background URL of the [key's](#collection_section) collection. | URL directly to the Image |
| `url_logo_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the logo URL of the [key's](#collection_section) collection. | URL directly to the Image |
| `url_poster_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the poster URL of the [key's](#collection_section) collection. | URL directly to the Image |
| `url_square_art_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the square art URL of the [key's](#collection_section) collection. | URL directly to the Image |
<!--franchise-->
<!--arr-->
| `ARR_CODE_add_missing_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override ARR_NAME `add_missing` attribute of the [key's](#collection_section) collection. | **Default:** `ARR_CODE_add_missing`<br>`true` or `false` |
| `ARR_CODE_add_missing` | Override ARR_NAME `add_missing` attribute for all collections in a Defaults File. | `true` or `false` |
| `ARR_CODE_folder_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override ARR_NAME `root_folder_path` attribute of the [key's](#collection_section) collection. | **Default:** `ARR_CODE_folder`<br>Folder Path |
| `ARR_CODE_folder` | Override ARR_NAME `root_folder_path` attribute for all collections in a Defaults File. | Folder Path |
| `ARR_CODE_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Override ARR_NAME `tag` attribute of the [key's](#collection_section) collection. | **Default:** `ARR_CODE_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `ARR_CODE_tag` | Override ARR_NAME `tag` attribute for all collections in a Defaults File. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `item_ARR_CODE_tag_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Used to append a tag in ARR_NAME for every ARR_TYPE found by the builders that's in ARR_NAME of the [key's](#collection_section) collection. | **Default:** `item_ARR_CODE_tag`<br>List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
| `item_ARR_CODE_tag` | Used to append a tag in ARR_NAME for every ARR_TYPE found by the builders that's in ARR_NAME for all collections in a Defaults File. | List :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or comma-separated string of tags |
<!--arr-->
<!--basic-->
| `in_the_last_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes how far back the Smart Filter looks. | **Default:** <table class="clearTable"><tr><td>Key</td><td>Value</td></tr><tr><td>`released`</td><td>`90`</td></tr><tr><td>`episodes`</td><td>`7`</td></tr></table><br>Number greater than 0 |
<!--basic-->
<!--myanimelist-->
| `starting_only` | Changes the season collection to only use anime listed under the new section on [MAL Seasons](https://myanimelist.net/anime/season) | **Default:** `False`<br>`True` or `False` |
<!--myanimelist-->
<!--tautulli-->
| `list_days` | Changes the `list_days` attribute of the Builder for all collections in a Defaults File. | Number greater than 0 |
| `list_days_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the `list_days` attribute of the Builder of the [key's](#collection_section) collection. | Number greater than 0 |
| `list_size` | Changes the `list_size` attribute of the Builder for all collections in a Defaults File. | Number greater than 0 |
| `list_size_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the `list_size` attribute of the Builder of the [key's](#collection_section) collection. | Number greater than 0 |
<!--tautulli-->
<!--tracearr-->
| `list_days` | Changes how many days of Tracearr history are used for all collections in the Defaults File. | **Default:** `30`<br>Number greater than 0 |
| `list_days_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes how many days of Tracearr history are used for the [key's](#collection_section) collection. | **Default:** `30`; `list_days_trending` defaults to `7`<br>Number greater than 0 |
| `list_minimum` | Changes the minimum activity count required for all collections in the Defaults File. | **Default:** `0`<br>Number 0 or greater |
| `list_minimum_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the minimum activity count required for the [key's](#collection_section) collection. | **Default:** `0`<br>Number 0 or greater |
| `list_size` | Changes the maximum number of items in all collections in the Defaults File. | **Default:** `20`<br>Number greater than 0 |
| `list_size_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the maximum number of items in the [key's](#collection_section) collection. | **Default:** `20`<br>Number greater than 0 |
<!--tracearr-->
<!--universe-->
| `name_mapping_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Sets the name mapping value for using assets of the [key's](#collection_section) collection. | Any String |
| `minimum_items` | Controls the minimum items that the collection must have to be created. | **Default:** `2`<br>Any number |
| `imdb_list_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the Movies in the IMDb List to the [key's](#collection_section) collection. | List of IMDb List URLs |
| `mdblist_list_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Adds the Movies in the MDBList List to the [key's](#collection_section) collection. Overrides the [default mdblist_url](#default-value-source) for that collection if used. | List of MDBList List URLs |
<!--universe-->
<!--streaming-->
| `discover_with_<<key>>` | Overrides the TMDb Watch Provider used for the specified key. This is only needed if a specific `region` has a different ID for the watch provider. | **Default:** `<<discover_with>>`<br>Any TMDb Watch Provider ID for [Movies](https://developer.themoviedb.org/reference/watch-providers-movie-list) / [Shows](https://developer.themoviedb.org/reference/watch-provider-tv-list) based on the user's region |
| `originals_only` | Changes Streaming Service lists to only show original content produced by the service.<br>**Note**: Cannot be used with `region`, and only produces collections for `amazon`, `appletv`, `disney`, `max`, `hulu`, `netflix`, `paramount`, `peacock` | **Default:** `false`<br>`true`, `false` |
| `region` | Changes some Streaming Service lists to regional variants (see below table for more information. | **Default:** `us`<br>Any [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) of the region where the streaming information should be based on. |
<!--streaming-->
<!--collectionless-->
| `collection_order` | Changes the Collection Order for all collections in a Defaults File. | **Default:** `alpha`<br>{% include-markdown "./tables/collection_order.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
| `sort_title` | Sets the sort title for the collection. | **Default:** `~_Collectionless`<br>Any String |
| `url_poster` | Changes the poster url of the collection. | URL directly to the Image |
| `exclude` | Exclude these Collections from being considered for collectionless. | List of Collections |
| `exclude_prefix` | Overrides the default exclude_prefix list. Exclude Collections with one of these prefixes from being considered for collectionless. | **Default:** default exclude_prefix list<br>List of Prefixes |
| `name_collectionless` | Changes the name of the collection. | New Collection Name |
| `summary_collectionless` | Changes the summary of the collection. | New Collection Summary |
<!--collectionless-->
<!--people-data-->
| `data` | Replaces the `data` dynamic collection value. | <table class="clearTable"><tr><th>Attribute</th><th>Description</th><th>Values</th></tr><tr><td><code>depth</code></td><td>Controls the depth within the casting credits to search for common actors</td><td><strong>Default:</strong> 5<br>Number greater than 0</td></tr><tr><td><code>limit</code></td><td>Controls the maximum number of collections to create</td><td><strong>Default:</strong> 25<br>Number greater than 0</td></tr></table> |
| `style` | Controls the visual theme of the collections created. | **Default:** `bw`<br>`bw`, `rainier`, `signature`, `diiivoy`, or `diiivoycolor` |
<!--people-data-->
<!--award-data-->
| `data` | Replaces the `data` dynamic collection value. | <table class="clearTable"><tr><th>Attribute</th><th>Description</th><th>Values</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections</td><td><strong>Default:</strong> latest-5<br>Number greater than 0</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections</td><td><strong>Default:</strong> latest<br>Number greater than 1</td></tr><tr><td><code>increment</code></td><td>Controls the increment (i.e. every 5th year)</td><td><strong>Default:</strong> 1<br>Number greater than 0</td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>latest</code></strong></li><li><strong>You can also use a value relative to the <code>latest</code> by doing <code>latest-5</code></strong></li></ul> |
<!--award-data-->
<!--year-data-->
| `data` | Replaces the `data` dynamic collection value. | <table class="clearTable"><tr><th>Attribute</th><th>Description</th><th>Values</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections</td><td><strong>Default:</strong> current_year-10<br>Number greater than 0</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections</td><td><strong>Default:</strong> current_year<br>Number greater than 1</td></tr><tr><td><code>increment</code></td><td>Controls the increment (i.e. every 5th year)</td><td><strong>Default:</strong> 1<br>Number greater than 0</td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>current_year</code></strong></li><li><strong>You can also use a value relative to the <code>current_year</code> by doing <code>current_year-5</code></strong></li></ul> |
<!--year-data-->
<!--data-->
| `data` | Overrides the [default data dictionary](#default-value-source). Defines the data that the custom dynamic collection processes. | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List of keys/names |
| `append_data` | Appends to the [default data dictionary](#default-value-source). | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List of keys/names; if the name contains commas, wrap it in quotes. |
| `remove_data` | Removes from the [default data dictionary](#default-value-source). | List of keys to remove |
<!--data-->
<!--addons-->
| `addons` | Overrides the [default addons dictionary](#default-value-source). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List of DYNAMIC_VALUE |
<!--addons-->
<!--addons-extra-->
| `append_addons` | Appends to the [default addons dictionary](#default-value-source). | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List of DYNAMIC_VALUE |
| `remove_addons` | Removes from the [default addons dictionary](#default-value-source). | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } List of DYNAMIC_VALUE |
<!--addons-extra-->
<!--exclude-->
| `exclude` | Exclude these DYNAMIC_NAME from creating a Dynamic Collection. | List of DYNAMIC_VALUE |
<!--exclude-->
<!--include-->
| `include` | Force these NAME to be included to create a Dynamic Collection. | List of DYNAMIC_VALUE |
<!--include-->
<!--include-extra-->
| `append_include` | Appends to the [default include list](#default-value-source) | List of DYNAMIC_VALUE |
| `remove_include` | Removes from the [default include list](#default-value-source) | List of DYNAMIC_VALUE |
<!--include-extra-->
<!--key_name_override-->
| `key_name_override` | Overrides the [default key_name_override dictionary](#default-value-source). | Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } with `key: new_key_name` entries |
<!--key_name_override-->
<!--cache_builders-->
| `cache_builders` | Changes the Builder Cache for all collections in a Defaults File. | **Default:** `1`<br>number 0 or greater |
| `cache_builders_<<key>>` | Changes the Builder Cache of the [key's](#collection_section) collection. | **Default:** `1`<br>number 0 or greater |
<!--cache_builders-->
<!--collection_mode-->
| `collection_mode` | Controls the collection mode of all collections in this file. | {% include-markdown "./tables/collection_mode.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
<!--collection_mode-->
<!--collection_order-->
| `collection_order` | Changes the Collection Order for all collections in a Defaults File. | **Default:** COLLECTION_ORDER<br>{% include-markdown "./tables/collection_order.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
| `collection_order_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the Collection Order of the [key's](#collection_section) collection. | **Default:** `collection_order`<br>{% include-markdown "./tables/collection_order.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
<!--collection_order-->
<!--limit-->
| `limit` | Changes the Builder Limit for all collections in a Defaults File. | <!--limit-extra-->Number Greater than 0 |
| `limit_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the Builder Limit of the [key's](#collection_section) collection. | **Default:** `limit`<br>Number Greater than 0 |
<!--limit-->
<!--limit_anidb-->
| `limit_anidb` | Changes the Builder Limit of the AniDB Popular Collection. | **Default:** `30`<br>Number greater than 0 |
<!--limit_anidb-->
<!--sort_by-->
| `sort_by` | Changes the Smart Filter Sort for all collections in a Defaults File. | **Default:** `release.desc`<br>[Any `smart_filter` Sort Option](../../files/builders/plex/sort-options.md) |
| `sort_by_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the Smart Filter Sort of the [key's](#collection_section) collection. | **Default:** `sort_by`<br>[Any `smart_filter` Sort Option](../../files/builders/plex/sort-options.md) |
<!--sort_by-->
<!--resolution-style-->
| `style` | Controls the visual theme of the collections created. | **Default:** `default`<br>`default` or `standards` |
<!--resolution-style-->
<!--white-style-->
| `style` | Controls the visual theme of the collections created. | **Default:** `color`<br>`color` or `white` |
<!--white-style-->
<!--color-style-->
| `style` | Controls the visual theme of the collections created. | **Default:** `white`<br>`color` or `white` |
<!--color-style-->
<!--sync_mode-->
| `sync_mode` | Changes the Sync Mode for all collections in a Defaults File. | **Default:** `sync`<br>{% include-markdown "./tables/sync_mode.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
| `sync_mode_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the Sync Mode of the [key's](#collection_section) collection. | **Default:** `sync_mode`<br>{% include-markdown "./tables/sync_mode.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
<!--sync_mode-->
<!--format-->
| `name_format` | Changes the title format of the Dynamic Collections. | **Default:** `NAME_FORMAT`<br>Any string with `<<key_name>>` in it. |
| `summary_format` | Changes the summary format of the Dynamic Collections. | **Default:** `SUMMARY_FORMAT`<br>Any string with `<<key_name>>` in it. |
<!--format-->
<!--tmdb_birthday-->
| `tmdb_birthday` | Controls if the Definition is run based on `tmdb_person`'s Birthday. Has 3 possible attributes `this_month`, `before` and `after`. | <table class="clearTable"><tr><td>`this_month`</td><td>Run's if Birthday is in current Month</td><td>`true`/`false`</td></tr><tr><td>`before`</td><td>Run if X Number of Days before the Birthday</td><td>Number 0 or greater</td></tr><tr><td>`after`</td><td>Run if X Number of Days after the Birthday</td><td>Number 0 or greater</td></tr></table> |
| `tmdb_deathday` | Controls if the Definition is run based on `tmdb_person`'s Deathday. Has 3 possible attributes `this_month`, `before` and `after`. | <table class="clearTable"><tr><td>`this_month`</td><td>Run's if Deathday is in current Month</td><td>`true`/`false`</td></tr><tr><td>`before`</td><td>Run if X Number of Days before the Deathday</td><td>Number 0 or greater</td></tr><tr><td>`after`</td><td>Run if X Number of Days after the Deathday</td><td>Number 0 or greater</td></tr></table> |
<!--tmdb_birthday-->
<!--tmdb_person_offset-->
| `tmdb_person_offset_<<key>>` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-defaults-key" } | Changes the summary tmdb_person_offset for the specific key. | **Default:** `0`<br>Dictionary :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-dictionaries" } of Actor Name as the keys and the tmdb_person_offset as the value. |
<!--tmdb_person_offset-->

<!--sup1-->
1. Each default collection has a [`key`](#collection_section) that you must replace `<<key>>` with when using this Template Variable. These keys are found in the table at the top of this page.
<!--sup1-->
