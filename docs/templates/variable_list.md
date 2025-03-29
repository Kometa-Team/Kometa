<!--aspect-overlay-->
| `text_<<key>>`<sup>**1**</sup> | Choose the text for the Overlay.                                                                                   | Any string<br><br>Key → Default Text:<br>`1.33` = `1.33`<br>`1.65` = `1.65`<br>`1.66` = `1.66`<br>`1.78` = `1.78`<br>`1.85` = `1.85`<br>`2.2` = `2.2`<br>`2.35` = `2.35`<br>`2.77` = `2.77`         |
<!--aspect-overlay-->
<!--commonsense-overlay-->
| `pre_text`          | Choose the text before the key for the Overlay.                                                             | Any string                                                                                                             |
| `post_text`         | Choose the text after the key for the Overlay.                                                              | Any string<br>**`+`**                                                                                                  |
| `pre_nr_text`       | Choose the text before the `nr` key for the Overlay.                                                        | Any string                                                                                                             |
| `post_nr_text`      | Choose the text after the `nr` key for the Overlay.                                                         | Any string                                                                                                             |
<!--commonsense-overlay-->
<!--language_count-overlay-->
| `minimum`                  | Choose the minimum for the `multi` Overlay.                                                                             | Any number<br>**`2`**                                                                                                  |
| `use_subtitles`            | Controls if the overlay is based on subtitle language instead of audio language.                                       | `true` = use subtitle language<br>`**false`** = use audio language                                                         |
<!--language_count-overlay-->
<!--languages-overlay-->
| `country_<<key>>`<sup>**1**</sup>        | Controls the country image for the Overlay.                                                             | [ISO 3166-1 Country Code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)<br>Default listed in [table](#supported-audiosubtitle-language-flags) |
| `flag_alignment`                       | Controls the flag alignment in the backdrop.                                                            | **`left`**, `right`                                                                                                    |
| `group_alignment`                      | Choose the display alignment for the flag group.                                                        | **`vertical`**, `horizontal`                                                                                           |
| `hide_text`                            | Disables the country code text, showing only the flag.                                                  | `true`, **`false`**                                                                          |
| `horizontal_position`                  | Choose the horizontal position for the flag group.                                                      | **`left`**, `left2`, `center`, `center_left`, `center_right`, `right`, `right2`                                       |
| `horizontal_spacing`                   | Controls the horizontal spacing from one overlay to the next.                                           | Any integer                                                                                                            |
| `initial_horizontal_align`            | Controls the initial horizontal alignment the queue starts from.                                        | `left`, `center`, `right`                                                                                              |
| `initial_horizontal_offset`           | Controls the initial horizontal offset the queue starts from.                                           | Any integer                                                                                                            |
| `initial_vertical_align`              | Controls the initial vertical alignment the queue starts from.                                          | `top`, `center`, `bottom`                                                                                              |
| `initial_vertical_offset`             | Controls the initial vertical offset the queue starts from.                                             | Any integer                                                                                                            |
| `languages`                            | Controls which languages will be active.                                                                | List of [ISO 639-1 Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)<br>**`["en", "de", "fr", "es", "pt", "ja"]`** |
| `offset`                               | Controls the offset between the flag and the text.                                                      | Any integer ≥ 0<br>**`10`**                                                                                             |
| `overlay_limit`                        | Number of overlays this queue displays.                                                                 | **`3`**, `1`, `2`, `4`, `5`                                                                                             |
| `position`                             | Use the custom given queue instead of the provided queues.                                              | List of coordinates                                                                                                     |
| `size`                                 | Controls the size of the overlay.                                                                       | **`small`**, `big`                                                                                                      |
| `style`                                | Controls the visual theme of the overlays created.                                                      | `round` = Round Theme<br>`square` = Square Theme<br>`half` = Square Flag with Round Background                         |
| `use_lowercase`                        | Controls if the overlay display is in lowercase.                                                        | `true`, **false**                                                                                           |
| `use_subtitles`                        | Controls if the overlay is based on subtitle language instead of audio language.                        | `true`, **false**                                                           |
| `vertical_position`                    | Choose the vertical position for the flag group.                                                        | **`top`**, `top2`, `top3`, `center`, `center_top`, `center_bottom`, `bottom`, `bottom2`, `bottom3`                    |
| `vertical_spacing`                     | Controls the vertical spacing from one overlay to the next.                                             | Any integer                                                                                                            |
<!--languages-overlay-->
<!--ratings-overlay-->
<!--ratings-overlay-->
| `fresh_rating`            | Determines when ratings are considered Fresh                                                                  | Any number<br>**`6.0`**                                                                                                                |
| `horizontal_position`     | Choose the horizontal position for the rating group.                                                          | **`left`**, `right`, `center`                                                                                                          |
| `vertical_position`       | Choose the vertical position for the rating group.                                                            | **`center`**, `top`, `bottom`                                                                                                          |
| `maximum_rating`          | Maximum rating to display                                                                                     | Any number<br>**`10.0`**                                                                                                               |
| `minimum_rating`          | Minimum rating to display                                                                                     | Any number<br>**`0.0`**                                                                                                                |
| `rating1`                 | Choose the rating to display in `rating1`.                                                                    | `critic`, `audience`, `user`                                                                                                           |
| `rating_alignment`        | Choose the display alignment for the rating group.                                                            | **`vertical`**, `horizontal`                                                                                                           |
| `rating1_addon_offset`    | Text addon image offset from the text.                                                                        | Any number > 0<br>**`15`**                                                                                                             |
| `rating1_addon_position`  | Text addon image alignment in relation to the text.                                                           | **`top`**, `left`, `right`, `bottom`                                                                                                   |
| `rating1_extra`           | Extra text after `rating1`.                                                                                   | Any value<br>Default: **`%`** for `rt_popcorn`, `rt_tomato`, `tmdb`                                                                   |
| `rating1_image`           | Rating image to display in `rating1`.                                                                         | `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, `star`                        |
| `rating1_style`           | Rating number style for `rating1`. See style guide.                                                           | —                                                                                                                                      |
| `rating2`                 | Choose the rating to display in `rating2`.                                                                    | `critic`, `audience`, `user`                                                                                                           |
| `rating2_addon_offset`    | Text addon image offset from the text.                                                                        | Any number > 0<br>**`15`**                                                                                                             |
| `rating2_addon_position`  | Text addon image alignment in relation to the text.                                                           | **`top`**, `left`, `right`, `bottom`                                                                                                   |
| `rating2_extra`           | Extra text after `rating2`.                                                                                   | Any value<br>Default: **`%`** for `rt_popcorn`, `rt_tomato`, `tmdb`                                                                   |
| `rating2_image`           | Rating image to display in `rating2`.                                                                         | `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, `star`                        |
| `rating2_style`           | Rating number style for `rating2`. See style guide.                                                           | —                                                                                                                                      |
| `rating3`                 | Choose the rating to display in `rating3`.                                                                    | `critic`, `audience`, `user`                                                                                                           |
| `rating3_addon_offset`    | Text addon image offset from the text.                                                                        | Any number > 0<br>**`15`**                                                                                                             |
| `rating3_addon_position`  | Text addon image alignment in relation to the text.                                                           | **`top`**, `left`, `right`, `bottom`                                                                                                   |
| `rating3_extra`           | Extra text after `rating3`.                                                                                   | Any value<br>Default: **`%`** for `rt_popcorn`, `rt_tomato`, `tmdb`                                                                   |
| `rating3_image`           | Rating image to display in `rating3`.                                                                         | `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, `star`                        |
| `rating3_style`           | Rating number style for `rating3`. See style guide.                                                           | —                                                                                                                                      |
<!--ratings-overlay-->
<!--resolution-overlay-->
| `use_edition`             | Turns off all Edition Overlays in the Defaults File.                                                          | `false` to turn off the overlays                                                                                                       |
| `use_resolution`          | Turns off all Resolution Overlays in the Defaults File.                                                       | `false` to turn off the overlays                                                                                                       |
<!--resolution-overlay-->
<!--ribbon-overlay-->
| `style`                | Controls the color of the ribbon.                                                             | **`yellow`**, `gray`, `black`, `red`                                                                                                  |
| `use_all`              | Used to turn on/off all keys.                                                                 | **`true`**, `false`                                                                                                                    |
<!--ribbon-overlay-->
<!--runtimes-overlay-->
| `format`               | Choose the format of the displayed runtime.                                                   | Any string<br>**`<<runtimeH>>h <<runtimeM>>m`**                                                                                        |
| `text`                 | Choose the text that appears prior to the runtime on the overlay.                             | Any string<br>**`Runtime:`**                                                                                                           |
<!--runtimes-overlay-->
<!--status-overlay-->
| `last`                 | Episode air date in the last number of days for the AIRING overlay.                           | Any number > 0<br>**`14`**                                                                                                             |
| `text_<<key>>`<sup>**1**</sup> | Choose the text for the Overlay.                                                                       | Any string<br><br>Key → Default Text:<br>`airing` = `AIRING`<br>`returning` = `RETURNING`<br>`canceled` = `CANCELED`<br>`ended` = `ENDED` |
<!--status-overlay-->
<!--streaming-overlay-->
| `discover_with_<<key>>` | Overrides the TMDb Watch Provider used for the specified key.                                | Any TMDb Watch Provider ID for [Movies](https://developer.themoviedb.org/reference/watch-providers-movie-list)<br>or [Shows](https://developer.themoviedb.org/reference/watch-provider-tv-list)<br>Default: **`<<discover_with>>`**                         |
| `originals_only`        | Changes overlays to only apply to original content from the service.                         | **`false`**, `true`<br>Note: Cannot be used with `region`. Only applies to `amazon`, `appletv`, `disney`, `max`, `hulu`, `netflix`, `paramount`, `peacock` |
| `region`                | Regional variant support for streaming info.                                                  | Any [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes)<br>**`US`**                                              |
<!--streaming-overlay-->
<!--studio-overlay-->
| `style`                | Choose between the standard size or the **bigger** one.                                       | `bigger`                                                                                                                              |
<!--studio-overlay-->
<!--video_format-overlay-->
| `text_<<key>>`<sup>**1**</sup> | Choose the text for the Overlay.                                                                       | Any string<br><br>Key → Default Text:<br>`remux` = `REMUX`<br>`bluray` = `BLU-RAY`<br>`web` = `WEB`<br>`hdtv` = `HDTV`<br>`dvd` = `DVD`<br>`sdtv` = `SDTV`                     |
<!--video_format-overlay-->

<!--playlists-->
| `delete_playlist_<<key>>`<sup>**1**</sup> | Will delete the key's playlists for the users defined by `sync_to_users`.                       | `true`, `false`                                                                                                                       |
| `delete_playlist`                | Will delete all playlists for the users defined by `sync_to_users`.                            | `true`, `false`                                                                                                                       |
| `exclude_user_<<key>>`<sup>**1**</sup>    | Sets the users to exclude from syncing the key's playlist.                                    | Comma-separated string or list of user names<br>Default: **`sync_to_users`**                                                          |
| `exclude_user`                   | Sets the users to exclude from syncing all playlists.                                          | Comma-separated string or list of user names<br>Default: **`playlist_sync_to_users`**                                                 |
| `ignore_ids`                     | TMDb/TVDb IDs to ignore in all playlists.                                                      | List or comma-separated string of TMDb/TVDb IDs                                                                                       |
| `ignore_imdb_ids`                | IMDb IDs to ignore in all playlists.                                                           | List or comma-separated string of IMDb IDs                                                                                            |
| `imdb_list_<<key>>`<sup>**1**</sup>       | Adds IMDb list movies to the key's playlist.<br>Overrides the default `trakt_list`.           | List of IMDb List URLs                                                                                                                |
| `item_radarr_tag_<<key>>`<sup>**1**</sup> | Append a tag in Radarr for all movies in the key's playlist found in Radarr.                 | List or comma-separated string of tags<br>Default: **`item_radarr_tag`**                                                              |
| `item_radarr_tag`               | Append a tag in Radarr for all playlists.                                                      | List or comma-separated string of tags                                                                                               |
| `item_sonarr_tag_<<key>>`<sup>**1**</sup> | Append a tag in Sonarr for all series in the key's playlist found in Sonarr.                 | List or comma-separated string of tags<br>Default: **`item_sonarr_tag`**                                                              |
| `item_sonarr_tag`               | Append a tag in Sonarr for all playlists.                                                      | List or comma-separated string of tags                                                                                               |
| `libraries`                     | Names of libraries to use for playlists.                                                       | Comma-separated string or list of library mapping names<br>Default: **`Movies, TV Shows`**                                            |
| `mdblist_list_<<key>>`<sup>**1**</sup>    | Adds MDBList movies to the key's playlist.<br>Overrides the default `trakt_list`.            | List of MDBList List URLs                                                                                                             |
| `name_<<key>>`<sup>**1**</sup>            | Changes the name of the key's playlist.                                                      | New playlist name                                                                                                                     |
| `radarr_add_missing_<<key>>`<sup>**1**</sup> | Override Radarr `add_missing` for the key's playlist.                                     | `true`, `false`<br>Default: **`radarr_add_missing`**                                                                                  |
| `radarr_add_missing`           | Override Radarr `add_missing` for all playlists.                                               | `true`, `false`                                                                                                                       |
| `radarr_folder_<<key>>`<sup>**1**</sup>   | Override Radarr `root_folder_path` for the key's playlist.                                  | Folder path<br>Default: **`radarr_folder`**                                                                                           |
| `radarr_folder`                | Override Radarr `root_folder_path` for all playlists.                                          | Folder path                                                                                                                           |
| `radarr_tag_<<key>>`<sup>**1**</sup>      | Override Radarr `tag` for the key's playlist.                                               | List or comma-separated string of tags<br>Default: **`radarr_tag`**                                                                   |
| `radarr_tag`                   | Override Radarr `tag` for all playlists.                                                       | List or comma-separated string of tags                                                                                               |
| `sonarr_add_missing_<<key>>`<sup>**1**</sup> | Override Sonarr `add_missing` for the key's playlist.                                   | `true`, `false`<br>Default: **`sonarr_add_missing`**                                                                                  |
| `sonarr_add_missing`           | Override Sonarr `add_missing` for all playlists.                                               | `true`, `false`                                                                                                                       |
| `sonarr_folder_<<key>>`<sup>**1**</sup>   | Override Sonarr `root_folder_path` for the key's playlist.                                  | Folder path<br>Default: **`sonarr_folder`**                                                                                           |
| `sonarr_folder`                | Override Sonarr `root_folder_path` for all playlists.                                          | Folder path                                                                                                                           |
| `sonarr_tag_<<key>>`<sup>**1**</sup>      | Override Sonarr `tag` for the key's playlist.                                               | List or comma-separated string of tags<br>Default: **`sonarr_tag`**                                                                   |
| `sonarr_tag`                   | Override Sonarr `tag` for all playlists.                                                       | List or comma-separated string of tags                                                                                               |
| `summary_<<key>>`<sup>**1**</sup>         | Changes the summary of the key's playlist.                                                  | New playlist summary                                                                                                                  |
| `sync_to_users_<<key>>`<sup>**1**</sup>   | Sets the users to sync the key's playlist to.                                               | Comma-separated string or list of user names<br>Default: **`sync_to_users`**                                                          |
| `sync_to_users`               | Sets the users to sync all playlists to.                                                       | Comma-separated string or list of user names<br>Default: **`playlist_sync_to_users`**                                                 |
| `trakt_list_<<key>>`<sup>**1**</sup>      | Adds Trakt list movies to the key's playlist.<br>Overrides the default `trakt_list`.        | List of Trakt List URLs                                                                                                               |
| `url_poster_<<key>>`<sup>**1**</sup>      | Changes the poster URL of the key's playlist.                                               | URL directly to the image                                                                                                             |
| `use_<<key>>`<sup>**1**</sup>             | Turns off an individual playlist in the Defaults file.                                      | `false` to turn off the playlist                                                                                                      |
<!--playlists-->
<!--addon_image-->
| `addon_offset`         | Text addon image offset from the text.                                                        | Any number > 0<br>**`15`**                                                                                                             |
| `addon_position`       | Text addon image alignment in relation to the text.                                           | **`left`**, `right`, `top`, `bottom`                                                                                                  |
<!--addon_image-->
<!--builder_level-->
| `builder_level`        | Choose the overlay level.                                                                     | `season`, `episode`                                                                                                                   |
<!--builder_level-->
<!--color-->
| `color`                | Use color version of content rating images.                                                   | `true`, **`false`** = black & white                                                                                                   |
<!--color-->
<!--regex-->
| `regex_<<key>>`<sup>**1**</sup> | Controls the regex of the Overlay search.                                                   | Any valid regex                                                                                                                       |
<!--regex-->
<!--style-->
| `style`                | Choose the overlay style.                                                                     | **`compact`**, `standard`                                                                                                              |
<!--style-->
<!--weight-->
| `weight_<<key>>`<sup>**1**</sup> | Controls the weight of the overlay. Higher values have priority.                          | Any number                                                                                                                            |
<!--weight-->
<!--overlay-white-style-->
| `style`                | Choose between the default color version or the **white** one.                                | `color`, `white`                                                                                                                      |
<!--overlay-white-style-->



<!--award-->
| `use_year_collections`           | Turn the individual year collections off.                                                                     | `false` to turn off the collections                                                                                                   |
| `year_collection_section`        | Change the collection section for year collections only. Use quotes to preserve leading zeros.               | Any number (e.g. `"05"`)                                                                                                               |
<!--award-->
<!--seasonal-->
| `emoji`                          | Prefix an emoji to the title of collections.                                                                  | Any emoji followed by a space, wrapped in quotes (e.g. `"🎅 "`)                                                                       |
| `emoji_<<key>>`<sup>**1**</sup>  | Prefix an emoji to the specified key’s collection. Overrides the default emoji.                              | Any emoji followed by a space, wrapped in quotes (e.g. `"🔥 "`)                                                                       |
| `imdb_list_<<key>>`<sup>**1**</sup>       | Adds IMDb list movies to the key’s collection.                                                               | List of IMDb List URLs                                                                                                                |
| `imdb_search_<<key>>`<sup>**1**</sup>     | Adds IMDb search results to the key’s collection. Overrides default `imdb_search`.                           | List of IMDb List URLs                                                                                                                |
| `letterboxd_list_<<key>>`<sup>**1**</sup> | Adds Letterboxd list movies to the key’s collection.                                                         | List of Letterboxd List URLs                                                                                                          |
| `mdblist_list_<<key>>`<sup>**1**</sup>    | Adds MDBList list movies to the key’s collection. Overrides default `mdblist_list`.                          | List of MDBList URLs                                                                                                                  |
| `tmdb_collection_<<key>>`<sup>**1**</sup> | Adds TMDb collection IDs to the key’s collection. Overrides default `tmdb_collection`.                       | List of TMDb Collection IDs                                                                                                            |
| `tmdb_movie_<<key>>`<sup>**1**</sup>      | Adds TMDb movie IDs to the key’s collection. Overrides default `tmdb_movie`.                                 | List of TMDb Movie IDs                                                                                                                 |
| `trakt_list_<<key>>`<sup>**1**</sup>      | Adds Trakt list movies to the key’s collection. Overrides default `trakt_list`.                              | List of Trakt List URLs                                                                                                                |
| `schedule`                      | Changes the schedule for all collections in the file. Use `daily` to show all.                                | [Any Schedule Option](../../config/schedule.md)                                                                                       |
| `schedule_<<key>>`<sup>**1**</sup>        | Changes the schedule of the key’s collection. Overrides default `schedule`.                                  | [Any Schedule Option](../../config/schedule.md)                                                                                       |
<!--seasonal-->
<!--show-franchise-->
| `addons`                        | Overrides the default addons dictionary. Allows grouping keys under a new parent key.                         | Dictionary list of TMDb Show IDs                                                                                                       |
| `append_addons`                 | Appends to the default addons dictionary.                                                                      | Dictionary list of TMDb Show IDs                                                                                                       |
| `append_data`                   | Appends to the default data dictionary.                                                                        | Dictionary list of TMDb Main Show IDs                                                                                                  |
| `build_collection`             | Controls whether to build the collection (e.g., for Sonarr-only cases).                                        | `false` to skip building                                                                                                               |
| `collection_section`           | Adds a sort title with this collection section.                                                                | Any number                                                                                                                             |
| `data`                         | Overrides the default data dictionary. Defines how the dynamic collection processes.                           | Dictionary list of TMDb Main Show IDs                                                                                                  |
| `exclude`                      | Exclude these collections from creating a dynamic collection.                                                   | List of collection IDs                                                                                                                 |
| `minimum_items`                | Minimum items required to create the collection.                                                                | Any number<br>**`2`**                                                                                                                  |
| `name_mapping_<<key>>`<sup>**1**</sup>    | Name mapping for using assets of the key’s collection.                                                       | Any string                                                                                                                             |
| `order_<<key>>`<sup>**1**</sup>           | Sort order of the key’s collection in its section.                                                           | Any number                                                                                                                             |
| `remove_addons`                | Removes entries from the default addons dictionary.                                                             | Dictionary list of TMDb Show IDs                                                                                                       |
| `remove_data`                  | Removes entries from the default data dictionary.                                                               | List of TMDb Main Show IDs to remove                                                                                                   |
| `sort_title_<<key>>`<sup>**1**</sup>      | Sort title for the key’s collection.                                                                          | Any string<br>Default: **`sort_title`**                                                                                                |
| `sort_title`                   | Sort title for all collections. Use `<<collection_name>>` in formatting.                                       | Any string (e.g. `"!02_<<collection_name>>"`)<br>Uses `<<collection_name>>` as placeholder                                             |
| `summary_<<key>>`<sup>**1**</sup>         | Changes the summary of the key’s collection.                                                                  | New collection summary                                                                                                                 |
<!--show-franchise-->
<!--franchise-->
| `build_collection`              | Controls whether to build the collection (e.g. just send to Radarr).                            | `false` to skip building                                                                                                               |
| `collection_section`           | Adds a sort title using this collection section.                                               | Any number                                                                                                                             |
| `minimum_items`                | Minimum items required to create the collection.                                                | Any number<br>**`2`**                                                                                                                  |
| `movie_<<key>>`<sup>**1**</sup>         | Adds TMDb Movie IDs to the key’s collection. Overrides default `movie`.                       | List of TMDb Movie IDs                                                                                                                 |
| `name_mapping_<<key>>`<sup>**1**</sup> | Name mapping value for using assets of the key’s collection. Overrides default `name_mapping`. | Any string                                                                                                                             |
| `order_<<key>>`<sup>**1**</sup>        | Sort order of the key’s collection in its section.                                             | Any number                                                                                                                             |
| `sort_title_<<key>>`<sup>**1**</sup>   | Sort title for the key’s collection.                                                           | Any string<br>Default: **`sort_title`**                                                                                                |
| `sort_title`                   | Sort title for all collections. Use `<<collection_name>>`.                                     | Any string (e.g. `"!02_<<collection_name>>"`), must include `<<collection_name>>`                                                     |
| `summary_<<key>>`<sup>**1**</sup>      | Summary for the key’s collection.                                                              | New collection summary                                                                                                                 |
| `title_override`              | Overrides default title mappings.                                                               | Dictionary with `key: new_title` entries                                                                                               |
<!--franchise-->
<!--arr-->
| `ARR_CODE_add_missing_<<key>>`<sup>**1**</sup> | Override `ARR_NAME` `add_missing` for the key’s collection.                    | `true`, `false`<br>Default: **`ARR_CODE_add_missing`**                                                                                 |
| `ARR_CODE_add_missing`        | Override `ARR_NAME` `add_missing` for all collections.                                          | `true`, `false`                                                                                                                       |
| `ARR_CODE_folder_<<key>>`<sup>**1**</sup>      | Override `ARR_NAME` `root_folder_path` for the key’s collection.          | Folder path<br>Default: **`ARR_CODE_folder`**                                                                                          |
| `ARR_CODE_folder`             | Override `ARR_NAME` `root_folder_path` for all collections.                                    | Folder path                                                                                                                           |
| `ARR_CODE_tag_<<key>>`<sup>**1**</sup>         | Override `ARR_NAME` `tag` for the key’s collection.                       | List or comma-separated string of tags<br>Default: **`ARR_CODE_tag`**                                                                  |
| `ARR_CODE_tag`                | Override `ARR_NAME` `tag` for all collections.                                                  | List or comma-separated string of tags                                                                                                |
| `item_ARR_CODE_tag_<<key>>`<sup>**1**</sup>    | Append tag in `ARR_NAME` for all `ARR_TYPE` found in key’s collection.     | List or comma-separated string of tags<br>Default: **`item_ARR_CODE_tag`**                                                             |
| `item_ARR_CODE_tag`           | Append tag in `ARR_NAME` for all `ARR_TYPE` found in all collections.                          | List or comma-separated string of tags                                                                                                |
<!--arr-->
<!--basic-->
| `in_the_last_<<key>>`<sup>**1**</sup>  | Changes how far back the Smart Filter looks.                                                  | Any number > 0<br>Default:<br>`released` = **`90`**<br>`episodes` = **`7`**                                                            |
<!--basic-->
<!--myanimelist-->
| `starting_only`              | Only include anime listed under the “New” section on [MAL Seasons](https://myanimelist.net/anime/season/). | `true`, `false`<br>Default: **`false`**                                                                                                |
<!--myanimelist-->
<!--tautulli-->
| `list_days`                  | Changes the `list_days` value for all collections.                                               | Any number > 0                                                                                                                         |
| `list_days_<<key>>`<sup>**1**</sup>    | Changes the `list_days` for the key’s collection.                                             | Any number > 0                                                                                                                         |
| `list_size`                  | Changes the `list_size` value for all collections.                                               | Any number > 0                                                                                                                         |
| `list_size_<<key>>`<sup>**1**</sup>    | Changes the `list_size` for the key’s collection.                                             | Any number > 0                                                                                                                         |
<!--tautulli-->
<!--universe-->
| `name_mapping_<<key>>`<sup>**1**</sup> | Name mapping value for using assets of the key’s collection.                                 | Any string                                                                                                                             |
| `minimum_items`              | Minimum items required to create the collection.                                                | Any number<br>**`2`**                                                                                                                  |
| `trakt_list_<<key>>`<sup>**1**</sup>   | Adds Trakt list movies to the key’s collection. Overrides default `trakt_url`.               | List of Trakt List URLs                                                                                                                |
| `imdb_list_<<key>>`<sup>**1**</sup>    | Adds IMDb list movies to the key’s collection.                                               | List of IMDb List URLs                                                                                                                 |
| `mdblist_list_<<key>>`<sup>**1**</sup> | Adds MDBList movies to the key’s collection. Overrides default `mdblist_url`.                | List of MDBList List URLs                                                                                                              |
<!--universe-->
<!--streaming-->
| `discover_with_<<key>>`      | Overrides the TMDb Watch Provider used for the key. Only needed if a different ID is used in a given region. | Any TMDb Watch Provider ID for [Movies](https://developer.themoviedb.org/reference/watch-providers-movie-list) / [Shows](https://developer.themoviedb.org/reference/watch-provider-tv-list)<br>Default: **`<<discover_with>>`** |
| `originals_only`             | Only show original content from the streaming service.                                          | `true`, **`false`**<br>Note: Cannot be used with `region`                                                                             |
| `region`                     | Regional variant of the streaming service lists.                                                | Any [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes)<br>**`us`**                                              |
<!--streaming-->
<!--collectionless-->
| `collection_order`               | Changes the collection order for all collections.                                                             | **`alpha`**<br>Other options from `collection_order.md` (inline include)                                                              |
| `sort_title`                     | Sets the sort title for the collection.                                                                       | Any string<br>**`~_Collectionless`**                                                                                                   |
| `url_poster`                     | Changes the poster URL of the collection.                                                                      | URL directly to the image                                                                                                              |
| `exclude`                        | Exclude these collections from being considered for collectionless.                                           | List of collection names                                                                                                               |
| `exclude_prefix`                | Overrides the default prefix list for exclusions.                                                             | List of prefixes<br>Default: **default exclude_prefix list**                                                                          |
| `name_collectionless`           | Changes the name of the collection.                                                                            | New collection name                                                                                                                    |
| `summary_collectionless`        | Changes the summary of the collection.                                                                         | New collection summary                                                                                                                 |
<!--collectionless-->
<!--people-data-->
| `data`                           | Replaces the `data` dynamic collection value.                                                                 | Table:<br>• `depth`: Number > 0, **`5`**<br>• `limit`: Number > 0, **`25`**                                                             |
<!--people-data-->
<!--award-data-->
| `data`                           | Replaces the `data` dynamic collection value.                                                                 | Table:<br>• `starting`: Number > 0, **`latest-5`**<br>• `ending`: Number > 1, **`latest`**<br>• `increment`: Number > 0, **`1`**<br><br>Notes:<br>• `starting` and `ending` can be `latest`<br>• Relative values like `latest-5` are supported                   |
<!--award-data-->
<!--year-data-->
| `data`                           | Replaces the `data` dynamic collection value.                                                                 | Table:<br>• `starting`: Number > 0, **`current_year-10`**<br>• `ending`: Number > 1, **`current_year`**<br>• `increment`: Number > 0, **`1`**<br><br>Notes:<br>• `starting` and `ending` can be `current_year`<br>• Relative values like `current_year-5` are supported |
<!--year-data-->
<!--data-->
| `data`                           | Overrides the [default data dictionary](#default-values).                                                     | Dictionary list of keys/names                                                                                                          |
| `append_data`                    | Appends to the [default data dictionary](#default-values).                                                    | Dictionary list of keys/names                                                                                                          |
| `remove_data`                    | Removes from the [default data dictionary](#default-values).                                                  | List of keys to remove                                                                                                                 |
<!--data-->
<!--addons-->
| `addons`                         | Overrides the [default addons dictionary](#default-values).                                                   | Dictionary list of dynamic values                                                                                                      |
<!--addons-->
<!--addons-extra-->
| `append_addons`                 | Appends to the [default addons dictionary](#default-values).                                                  | Dictionary list of dynamic values                                                                                                      |
| `remove_addons`                 | Removes from the [default addons dictionary](#default-values).                                                | Dictionary list of dynamic values                                                                                                      |
<!--addons-extra-->
<!--exclude-->
| `exclude`                        | Exclude these dynamic names from creating a Dynamic Collection.                                               | List of dynamic values                                                                                                                 |
<!--exclude-->
<!--include-->
| `include`                        | Force these names to be included for a Dynamic Collection.                                                    | List of dynamic values                                                                                                                 |
<!--include-->
<!--include-extra-->
| `append_include`                | Appends to the [default include list](#default-values).                                                        | List of dynamic values                                                                                                                 |
| `remove_include`                | Removes from the [default include list](#default-values).                                                      | List of dynamic values                                                                                                                 |
<!--include-extra-->
<!--key_name_override-->
| `key_name_override`             | Overrides the [default key_name_override dictionary](#default-values).                                         | Dictionary with `key: new_key_name` entries                                                                                            |
<!--key_name_override-->
<!--cache_builders-->
| `cache_builders`               | Changes the builder cache value for all collections.                                                           | Number ≥ 0<br>**`1`**                                                                                                                  |
| `cache_builders_<<key>>`       | Changes the builder cache value for the key’s collection.                                                      | Number ≥ 0<br>**`1`**                                                                                                                  |
<!--cache_builders-->
<!--collection_mode-->
| `collection_mode`               | Controls the collection mode for all collections in this file.                                                 | Values from `collection_mode.md` (inline include)                                                                                      |
<!--collection_mode-->
<!--collection_order-->
| `collection_order`               | Changes the collection order for all collections.                                                             | Options from `collection_order.md`<br>**`COLLECTION_ORDER`**                                                                          |
| `collection_order_<<key>>`<sup>**1**</sup> | Changes the collection order for the key’s collection.                                               | Options from `collection_order.md`<br>Default: **`collection_order`**                                                                 |
<!--collection_order-->
<!--limit-->
| `limit`                          | Changes the builder limit for all collections.                                                                | Any number > 0                                                                                                                         |
| `limit_<<key>>`<sup>**1**</sup>   | Changes the builder limit for the key’s collection.                                                           | Any number > 0<br>Default: **`limit`**                                                                                                 |
<!--limit-->
<!--limit_anidb-->
| `limit_anidb`                    | Changes the builder limit for the AniDB Popular Collection.                                                   | Any number > 0<br>**`30`**                                                                                                              |
<!--limit_anidb-->
<!--sort_by-->
| `sort_by`                        | Changes the Smart Filter sort for all collections.                                                            | [Any `smart_filter` Sort Option](../../files/builders/plex.md#sort-options)<br>**`release.desc`**                                     |
| `sort_by_<<key>>`<sup>**1**</sup> | Changes the Smart Filter sort for the key’s collection.                                                       | [Any `smart_filter` Sort Option](../../files/builders/plex.md#sort-options)<br>Default: **`sort_by`**                                 |
<!--sort_by-->
<!--style-->
| `style`                          | Controls the visual theme of the collections.                                                                 | **`bw`**, `rainier`, `signature`, `diiivoy`, `diiivoycolor`                                                                           |
<!--style-->
<!--resolution-style-->
| `style`                          | Controls the visual theme of the collections.                                                                 | **`default`**, `standards`                                                                                                              |
<!--resolution-style-->
<!--white-style-->
| `style`                          | Controls the visual theme of the collections.                                                                 | **`color`**, `white`                                                                                                                    |
<!--white-style-->
<!--color-style-->
| `style`                          | Controls the visual theme of the collections.                                                                 | **`white`**, `color`                                                                                                                    |
<!--color-style-->
<!--sync_mode-->
| `sync_mode`                      | Changes the sync mode for all collections.                                                                    | Options from `sync_mode.md`<br>**`sync`**                                                                                               |
| `sync_mode_<<key>>`<sup>**1**</sup> | Changes the sync mode for the key’s collection.                                                       | Options from `sync_mode.md`<br>Default: **`sync_mode`**                                                                                |
<!--sync_mode-->
<!--format-->
| `name_format`                   | Changes the title format of dynamic collections.                                                              | Any string containing `<<key_name>>`<br>Default: **`NAME_FORMAT`**                                                                     |
| `summary_format`                | Changes the summary format of dynamic collections.                                                            | Any string containing `<<key_name>>`<br>Default: **`SUMMARY_FORMAT`**                                                                  |
<!--format-->
<!--tmdb_birthday-->
| `tmdb_birthday`                 | Controls execution based on TMDb person’s birthday.                                                           | Table:<br>• `this_month`: `true`, `false`<br>• `before`: Number ≥ 0<br>• `after`: Number ≥ 0                                           |
<!--tmdb_birthday-->
<!--tmdb_person_offset-->
| `tmdb_person_offset_<<key>>`<sup>**1**</sup> | Changes the `tmdb_person_offset` used in the summary for the key.                                 | Dictionary of `Actor Name: offset`<br>Default: **`0`**                                                                                  |
<!--tmdb_person_offset-->

<!--sup1-->
<sup>**1**</sup> Each default collection has a [`key`](#collection_section) that you must replace `<<key>>` with when using this Template Variable. These keys are found in the table at the top of this page.
<!--sup1-->