<!--aspect-overlay-->
| `text_<<key>>`<sup>**1**</sup> | **Description:** Choose the text for the Overlay.<br><br>**Values:** Any String<br><table class="clearTable" style="text-align:left;"><tr><th>Key</th><th>Default Text</th></tr><tr><td>`1.33`</td><td>`1.33`</td></tr><tr><td>`1.65`</td><td>`1.65`</td></tr><tr><td>`1.66`</td><td>`1.66`</td></tr><tr><td>`1.78`</td><td>`1.78`</td></tr><tr><td>`1.85`</td><td>`1.85`</td></tr><tr><td>`2.2`</td><td>`2.2`</td></tr><tr><td>`2.35`</td><td>`2.35`</td></tr><tr><td>`2.77`</td><td>`2.77`</td></tr></table> |
<!--aspect-overlay-->
<!--commonsense-overlay-->
| `pre_text`       | **Description:** Choose the text before the key for the Overlay.<br>**Values:** Any String                    |
| `post_text`      | **Description:** Choose the text after the key for the Overlay.<br>**Default:** `+`<br>**Values:** Any String |
| `pre_nr_text`    | **Description:** Choose the text before the `nr` key for the Overlay.<br>**Values:** Any String               |
| `post_nr_text`   | **Description:** Choose the text after the `nr` key for the Overlay.<br>**Values:** Any String                |
<!--commonsense-overlay-->
<!--language_count-overlay-->
| `minimum`       | **Description:** Choose the minimum for the `multi` Overlay.<br>**Default:** `2` <br>**Values:** Any Number                                                                    |
| `use_subtitles` | **Description:** Controls if the overlay is based on subtitle language instead of audio language.<br>**Values:** `true` to look at subtitle language instead of audio language |
<!--language_count-overlay-->
<!--languages-overlay-->
| `country_<<key>>`<sup>**1**</sup> | **Description:** Controls the country image for the Overlay.<br>**Default:** Listed in the [Table](#supported-audiosubtitle-language-flags) above<br>**Values:** [ISO 3166-1 Country Code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) for the flag desired                                                 |
| `flag_alignment`              | **Description:** Controls the flag alignment in the backdrop.<br>**Default:** `left`<br>**Values:** `left` or `right`                                                                                                                                                                                                         |
| `group_alignment`             | **Description:** Choose the display alignment for the flag group.<br>**Default:** `vertical`<br>**Values:** `horizontal`, or `vertical`                                                                                                                                                                                       |
| `hide_text`                   | **Description:** Disables the country code text, showing only the flag.<br>**Default: `false` <br>**Values:\*\* `true` to hide the country text                                                                                                                                                                               |
| `horizontal_position`         | **Description:** Choose the horizontal position for the flag group.<br>**Default:** `left`<br>**Values:** `left`, `left2`, `center`, `center_left`, `center_right`, `right` or `right2`                                                                                                                                       |
| `horizontal_spacing`          | **Description:** Controls the vertical spacing from one overlay in the queue to the next.<br>**Values:** Any Integer                                                                                                                                                                                                          |
| `initial_horizontal_align`    | **Description:** Controls the initial horizontal align the queue starts from.<br>**Values:** `left`, `center`, or `right`                                                                                                                                                                                                     |
| `initial_horizontal_offset`   | **Description:** Controls the initial horizontal offset the queue starts from.<br>**Values:** Any Integer                                                                                                                                                                                                                     |
| `initial_vertical_align`      | **Description:** Controls the initial vertical align the queue starts from.<br>**Values:** `top`, `center`, or `bottom`                                                                                                                                                                                                       |
| `initial_vertical_offset`     | **Description:** Controls the initial vertical offset the queue starts from.<br>**Values:** Any Integer                                                                                                                                                                                                                       |
| `languages`                   | **Description:** Controls which Languages will be active.<br>**Default:** `["en", "de", "fr", "es", "pt", "ja"]` <br>**Values:** List of [ISO 639-1 Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) for the Languages desired                                                                                   |
| `offset`                      | **Description:** Controls the offset between the flag and the text.<br>**Default:** `10`<br>**Values:** Any Integer 0 or greater                                                                                                                                                                                              |
| `overlay_limit`               | **Description:** Choose the number of overlay this queue displays.<br>**Default:** `3`<br>**Values:** `1`, `2`, `3`, `4`, or `5`                                                                                                                                                                                              |
| `position`                    | **Description:** Use the Custom Given Queue instead of the the provided Queues.<br>**Values:** List of Coordinates                                                                                                                                                                                                            |
| `size`                        | **Description:** Controls the size of the overlay.<br>**Default: small** <br>**Values:** `small` or `big`                                                                                                                                                                                                                     |
| `style`                       | **Description:** Controls the visual theme of the overlays created.<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>round</code></td><td>Round Theme</td></tr><tr><td><code>square</code></td><td>Square Theme</td></tr><tr><td><code>half</code></td><td>Square Flag with Round Background</td></tr></table> |
| `use_lowercase`               | **Description:** Controls if the overlay display is in lowercase.<br>**Values:** `true` to use lowercase text                                                                                                                                                                                                                 |
| `use_subtitles`               | **Description:** Controls if the overlay is based on subtitle language instead of audio language.<br>**Values:** `true` to look at subtitle language instead of audio language                                                                                                                                                |
| `vertical_position`           | **Description:** Choose the vertical position for the flag group.<br>**Default:** `top`<br>**Values:** `top`, `top2`, `top3`, `center`, `center_top`, `center_bottom`, `bottom`, `bottom2` or `bottom3`                                                                                                                       |
| `vertical_spacing`            | **Description:** Controls the vertical spacing from one overlay in the queue to the next.<br>**Values:** Any Integer                                                                                                                                                                                                          |
<!--languages-overlay-->

<!--ratings-overlay-->
| `fresh_rating`           | **Description:** Determines when ratings are considered Fresh<br>**Default:** 6.0<br>**Values:** Any Number                                                                                                                                |
| `horizontal_position`    | **Description:** Choose the horizontal position for the rating group.<br>**Default:** `left`<br>**Values:** `left`, `right`, or `center`                                                                                                   |
| `vertical_position`      | **Description:** Choose the vertical position for the rating group.<br>**Default:** `center`<br>**Values:** `top`, `bottom`, or `center`                                                                                                   |
| `maximum_rating`         | **Description:** Maximum Rating to display<br>**Default:** 10.0<br>**Values:** Any Number                                                                                                                                                 |
| `minimum_rating`         | **Description:** Minimum Rating to display<br>**Default:** 0.0<br>**Values:** Any Number                                                                                                                                                  |
| `rating1`                | **Description:** Choose the rating to display in rating1.<br>**Values:** `critic`, `audience`, or `user`                                                                                                                                   |
| `rating_alignment`       | **Description:** Choose the display alignment for the rating group.<br>**Default:** `vertical`<br>**Values:** `horizontal`, or `vertical`                                                                                                 |
| `rating1_addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                                                                                                                     |
| `rating1_addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `top`<br>**Values:** `left`, `right`, `top`, `bottom`                                                                                                |
| `rating1_extra`          | **Description:** Extra text after rating1.<br>**Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`. <br>**Values:** Any Value                                                                                                            |
| `rating1_image`          | **Description:** Choose the rating image to display in rating1.<br>**Values:** `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, or `star`                                            |
| `rating1_style`          | **Description:** Choose the rating number style for rating1. Please refer to the detailed style guide.                                                                                                                                     |
| `rating2`                | **Description:** Choose the rating to display in rating2.<br>**Values:** `critic`, `audience`, or `user`                                                                                                                                   |
| `rating2_addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                                                                                                                     |
| `rating2_addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `top`<br>**Values:** `left`, `right`, `top`, `bottom`                                                                                                |
| `rating2_extra`          | **Description:** Extra text after rating2.<br>**Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`. <br>**Values:** Any Value                                                                                                            |
| `rating2_image`          | **Description:** Choose the rating image to display in rating2.<br>**Values:** `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, or `star`                                            |
| `rating2_style`          | **Description:** Choose the rating number style for rating2. Please refer to the detailed style guide.                                                                                                                                     |
| `rating3`                | **Description:** Choose the rating to display in rating3.<br>**Values:** `critic`, `audience`, or `user`                                                                                                                                   |
| `rating3_addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                                                                                                                     |
| `rating3_addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `top`<br>**Values:** `left`, `right`, `top`, `bottom`                                                                                                |
| `rating3_extra`          | **Description:** Extra text after rating3.<br>**Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`. <br>**Values:** Any Value                                                                                                            |
| `rating3_image`          | **Description:** Choose the rating image to display in rating3.<br>**Values:** `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, or `star`                                            |
| `rating3_style`          | **Description:** Choose the rating number style for rating3. Please refer to the detailed style guide.                                                                                                                                     |
<!--ratings-overlay-->
<!--resolution-overlay-->
| `use_edition`    | **Description:** Turns off all Edition Overlays in the Defaults File.<br>**Values:** `false` to turn off the overlays    |
| `use_resolution` | **Description:** Turns off all Resolution Overlays in the Defaults File.<br>**Values:** `false` to turn off the overlays |
<!--resolution-overlay-->
<!--ribbon-overlay-->
| `style`   | **Description:** Controls the color of the ribbon. <br>**Default:** `yellow` <br>**Values:** `yellow`, `gray`, `black`, `red` |
| `use_all` | **Description:** Used to turn on/off all keys. <br>**Default:** `true` <br>**Values:** `true` or `false`                |
<!--ribbon-overlay-->
<!--runtimes-overlay-->
| `format` | **Description:** Choose the format of the displayed runtime.<br>**Default:** `<<runtimeH>>h <<runtimeM>>m`<br>**Values:** Any String |
| `text`   | **Description:** Choose the text that appears prior to the runtime on the Overlay.<br>**Default:** `Runtime:`<br>**Values:** Any String  |
<!--runtimes-overlay-->
<!--status-overlay-->
| `last`                     | **Description:** Episode Air Date in the last number of days for the AIRING Overlay.<br>**Default:** `14`<br>**Values:** Any number greater than 0                                                                                                                                                                                                  |
| `text_<<key>>`<sup>**1**</sup> | **Description:** Choose the text for the Overlay.<br><br>**Values:** Any String<br><table class="clearTable" style="text-align:left;"><tr><th>Key</th><th>Default Text</th></tr><tr><td>`airing`</td><td>`AIRING`</td></tr><tr><td>`returning`</td><td>`RETURNING`</td></tr><tr><td>`canceled`</td><td>`CANCELED`</td></tr><tr><td>`ended`</td><td>`ENDED`</td></tr></table> |
<!--status-overlay-->
<!--streaming-overlay-->
| `discover_with_<<key>>` | **Description:** Overrides the TMDb Watch Provider used for the specified key. This is only needed if a specific `region` has a different ID for the watch provider.<br>**Default:** `<<discover_with>>`<br>**Values:** Any TMDb Watch Provider ID for [Movies](https://developer.themoviedb.org/reference/watch-providers-movie-list) / [Shows](https://developer.themoviedb.org/reference/watch-provider-tv-list) based on the user's region |
| `originals_only`        | **Description:** Changes Streaming Service overlays to only apply to original content produced by the service.<br>**Note**: Cannot be used with `region`, and only produces overlays for `amazon`, `appletv`, `disney`, `max`, `hulu`, `netflix`, `paramount`, `peacock`<br>**Default:** `false`<br>**Values:** `true`, `false`                                                                                                                |
| `region`                | **Description:** Changes some Streaming Service lists to regional variants (see below table for more information.<br>**Default:** `US`<br>**Values:** Any [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) of the region where the streaming information should be based on.                                                                                                                                          |
<!--streaming-overlay-->
<!--studio-overlay-->
| `style` | **Description:** Choose between the standard size or the **bigger** one.<br>**Values:** `bigger` |
<!--studio-overlay-->
<!--video_format-overlay-->
| `text_<<key>>`<sup>**1**</sup> | **Description:** Choose the text for the Overlay.<br><br>**Values:** Any String<br><table class="clearTable" style="text-align:left;"><tr><th>Key</th><th>Default Text</th></tr><tr><td>`remux`</td><td>`REMUX`</td></tr><tr><td>`bluray`</td><td>`BLU-RAY`</td></tr><tr><td>`web`</td><td>`WEB`</td></tr><tr><td>`hdtv`</td><td>`HDTV`</td></tr><tr><td>`dvd`</td><td>`DVD`</td></tr><tr><td>`sdtv`</td><td>`SDTV`</td></tr></table> |
<!--video_format-overlay-->

<!--playlists-->
| `delete_playlist_<<key>>`<sup>**1**</sup>    | **Description:** Will delete the key's playlists for the users defined by sync_to_users.<br>**Values:** `true` or `false`                                                                                                                                                                 |
| `delete_playlist`                        | **Description:** Will delete all playlists for the users defined by sync_to_users.<br>**Values:** `true` or `false`                                                                                                                                                                       |
| `exclude_user_<<key>>`<sup>**1**</sup>       | **Description:** Sets the users to exclude from sync the key's playlist.<br>**Default:** `sync_to_users` Value<br>**Values:** Comma-separated string or list of user names.                                                                                                               |
| `exclude_user`                           | **Description:** Sets the users to exclude from sync for all playlists.<br>**Default:** `playlist_sync_to_users` Global Setting Value<br>**Values:** Comma-separated string or list of user names.                                                                                        |
| `ignore_ids`                             | **Description:** Set a list or comma-separated string of TMDb/TVDb IDs to ignore in all playlists.<br>**Values:** List or comma-separated string of TMDb/TVDb IDs                                                                                                                         |
| `ignore_imdb_ids`                        | **Description:** Set a list or comma-separated string of IMDb IDs to ignore in all playlists.<br>**Values:** List or comma-separated string of IMDb IDs                                                                                                                                   |
| `imdb_list_<<key>>`<sup>**1**</sup>          | **Description:** Adds the Movies in the IMDb List to the key's playlist. Overrides the [default trakt_list] for that playlist if used.<br>**Values:** List of Trakt List URLs                                                                                                             |
| `item_radarr_tag_<<key>>`<sup>**1**</sup>    | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr of the key's playlist.<br>**Default:** `item_radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                     |
| `item_radarr_tag`                        | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr for all playlists in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                        |
| `item_sonarr_tag_<<key>>`<sup>**1**</sup>    | **Description:** Used to append a tag in Sonarr for every series found by the builders that's in Sonarr of the key's playlist.<br>**Default:** `item_sonarr_tag`<br>**Values:** List or comma-separated string of tags                                                                    |
| `item_sonarr_tag`                        | **Description:** Used to append a tag in Sonarr for every series found by the builders that's in Sonarr for all playlists in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                       |
| `libraries`                              | **Description:** Sets the names of the libraries to use for the Playlists.<br>**Default:** `Movies, TV Shows`<br>**Values:** Comma-separated string or list of library mapping names defined in the `libraries` attribute in the base of your [Configuration File](../config/overview.md. |
| `mdblist_list_<<key>>`<sup>**1**</sup>       | **Description:** Adds the Movies in the MDBList List to the key's playlist. Overrides the [default trakt_list] for that playlist if used.<br>**Values:** List of Trakt List URLs                                                                                                          | 
| `name_<<key>>`<sup>**1**</sup>               | **Description:** Changes the name of the key's playlist.<br>**Values:** New Playlist Name                                                                                                                                                                                                 |
| `radarr_add_missing_<<key>>`<sup>**1**</sup> | **Description:** Override Radarr `add_missing` attribute of the key's playlist.<br>**Default:** `radarr_add_missing`<br>**Values:** `true` or `false`                                                                                                                                     |
| `radarr_add_missing`                     | **Description:** Override Radarr `add_missing` attribute for all playlists in a Defaults file.<br>**Values:** `true` or `false`                                                                                                                                                           |
| `radarr_folder_<<key>>`<sup>**1**</sup>      | **Description:** Override Radarr `root_folder_path` attribute of the key's playlist.<br>**Default:** `radarr_folder`<br>**Values:** Folder Path                                                                                                                                           |
| `radarr_folder`                          | **Description:** Override Radarr `root_folder_path` attribute for all playlists in a Defaults file.<br>**Values:** Folder Path                                                                                                                                                            |
| `radarr_tag_<<key>>`<sup>**1**</sup>         | **Description:** Override Radarr `tag` attribute of the key's playlist.<br>**Default:** `radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                |
| `radarr_tag`                             | **Description:** Override Radarr `tag` attribute for all playlists in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                              |
| `sonarr_add_missing_<<key>>`<sup>**1**</sup> | **Description:** Override Sonarr `add_missing` attribute of the key's playlist.<br>**Default:** `sonarr_add_missing`<br>**Values:** `true` or `false`                                                                                                                                     |
| `sonarr_add_missing`                     | **Description:** Override Sonarr `add_missing` attribute for all playlists in a Defaults file.<br>**Values:** `true` or `false`                                                                                                                                                           |
| `sonarr_folder_<<key>>`<sup>**1**</sup>      | **Description:** Override Sonarr `root_folder_path` attribute of the key's playlist.<br>**Default:** `sonarr_folder`<br>**Values:** Folder Path                                                                                                                                           |
| `sonarr_folder`                          | **Description:** Override Sonarr `root_folder_path` attribute for all playlists in a Defaults file.<br>**Values:** Folder Path                                                                                                                                                            |
| `sonarr_tag_<<key>>`<sup>**1**</sup>         | **Description:** Override Sonarr `tag` attribute of the key's playlist.<br>**Default:** `sonarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                |
| `sonarr_tag`                             | **Description:** Override Sonarr `tag` attribute for all playlists in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                              |
| `summary_<<key>>`<sup>**1**</sup>            | **Description:** Changes the summary of the key's playlist.<br>**Values:** New Playlist Summary                                                                                                                                                                                           |
| `sync_to_users_<<key>>`<sup>**1**</sup>      | **Description:** Sets the users to sync the key's playlist to.<br>**Default:** `sync_to_user` Value<br>**Values:** Comma-separated string or list of user names.                                                                                                                          |
| `sync_to_users`                          | **Description:** Sets the users to sync all playlists to.<br>**Default:** `playlist_sync_to_users` Global Setting Value<br>**Values:** Comma-separated string or list of user names.                                                                                                      |
| `trakt_list_<<key>>`<sup>**1**</sup>         | **Description:** Adds the Movies in the Trakt List to the key's playlist. Overrides the [default trakt_list] for that playlist if used.<br>**Values:** List of Trakt List URLs                                                                                                            |
| `url_poster_<<key>>`<sup>**1**</sup>         | **Description:** Changes the poster url of the key's playlist.<br>**Values:** URL directly to the Image                                                                                                                                                                                   |
| `use_<<key>>`<sup>**1**</sup>                | **Description:** Turns off individual Playlists in a Defaults file.<br>**Values:** `false` to turn off the playlist                                                                                                                                                                       |
<!--playlists-->

<!--addon_image-->
| `addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                       |
| `addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `left`<br>**Values:** `left`, `right`, `top`, `bottom` |
<!--addon_image-->
<!--builder_level-->
| `builder_level` | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode` |
<!--builder_level-->
<!--color-->
| `color` | **Description:** Color version of the content rating images<br>**Default:** Set to `false` if you want b&w version. |
<!--color-->

<!--regex-->
| `regex_<<key>>`<sup>**1**</sup> | **Description:** Controls the regex of the Overlay Search.<br>**Values:** Any Proper Regex |
<!--regex-->
<!--style-->
| `style` | **Description:** Choose the Overlay Style.<br>**Default:** `compact`<br>**Values:** `compact` or `standard` |
<!--style-->
<!--weight-->
| `weight_<<key>>`<sup>**1**</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number |
<!--weight-->
<!--overlay-white-style-->
| `style`  | **Description:** Choose between the default color version or the **white** one.<br>**Values:** `color` or `white` |
<!--overlay-white-style-->








<!--award-->
| `use_year_collections`    | **Description:** Turn the individual year collections off.<br>**Values:** `false` to turn of the collections                                      |
| `year_collection_section` | **Description:** Change the collection section for year collections only. (Use quotes to not lose leading zeros `"05"`)<br>**Values:** Any number |
<!--award-->
<!--seasonal-->
| `emoji`                               | **Description:** Prefix an emoji to the title of Collections. <br>**Values:** Any emoji followed by a space, all wrapped in quotes (i.e. "🎅 ")                                                                                                                    |
| `emoji_<<key>>`<sup>**1**</sup>           | **Description:** Prefix an emoji to the title of the specified [key's](#collection_section) collection. Overrides the [default emoji](#default-values) for that collection if used.<br>**Values:** Any emoji followed by a space, all wrapped in quotes (i.e. "🔥 ")                                     |
| `imdb_list_<<key>>`<sup>**1**</sup>       | **Description:** Adds the Movies in the IMDb List to the specified [key's](#collection_section) collection.<br>**Values:** List of IMDb List URLs                                                                                              |
| `imdb_search_<<key>>`<sup>**1**</sup>     | **Description:** Adds the Movies in the IMDb Search to the specified [key's](#collection_section) collection. Overrides the [default imdb_search](#default-values) for that collection if used.<br>**Values:** List of IMDb List URLs          |
| `letterboxd_list_<<key>>`<sup>**1**</sup> | **Description:** Adds the Movies in the Letterboxd List to the specified [key's](#collection_section) collection.<br>**Values:** List of Letterboxd List URLs                                                                                  |
| `mdblist_list_<<key>>`<sup>**1**</sup>    | **Description:** Adds the Movies in the MDb List to the specified [key's](#collection_section) collection. Overrides the [default mdblist_list](#default-values) for that collection if used.<br>**Values:** List of MDBList URLs              |
| `tmdb_collection_<<key>>`<sup>**1**</sup> | **Description:** Adds the TMDb Collection IDs given to the specified [key's](#collection_section) collection. Overrides the [default tmdb_collection](#default-values) for that collection if used.<br>**Values:** List of TMDb Collection IDs |
| `tmdb_movie_<<key>>`<sup>**1**</sup>      | **Description:** Adds the TMDb Movie IDs given to the specified [key's](#collection_section) collection. Overrides the [default tmdb_movie](#default-values) for that collection if used.<br>**Values:** List of TMDb Movie IDs                |
| `trakt_list_<<key>>`<sup>**1**</sup>      | **Description:** Adds the Movies in the Trakt List to the specified [key's](#collection_section) collection. Overrides the [default trakt_list](#default-values) for that collection if used.<br>**Values:** List of Trakt List URLs           |
| `schedule`                            | **Description:** Changes the Schedule for all collections in this file. Use `daily` to have all collections show.<br>**Values:** [Any Schedule Option](../../config/schedule.md)                                                               |
| `schedule_<<key>>`<sup>**1**</sup>        | **Description:** Changes the Schedule of the specified [key's](#collection_section) collection. Overrides the [default schedule](#default-values) for that collection if used.<br>**Values:** [Any Schedule Option](../../config/schedule.md)  |
<!--seasonal-->
<!--show-franchise-->
| `addons`                                 | **Description:** Overrides the [default addons dictionary](#default-values). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of TMDb Show IDs |
| `append_addons`                          | **Description:** Appends to the [default addons dictionary](#default-values).<br>**Values:** Dictionary List of TMDb Show IDs                                                                                                                   |
| `append_data`                            | **Description:** Appends to the [default data dictionary](#default-values).<br>**Values:** Dictionary List of TMDb Main Show ID                                                                                                                 |
| `build_collection`                       | **Description:** Controls if you want the collection to actually be built. i.e. you may just want these shows sent to Sonarr.<br>**Values:** `false` to not build the collection                                                                |
| `collection_section`                     | **Description:** Adds a sort title with this collection sections.<br>**Values:** Any number                                                                                                                                                     |
| `data`                                   | **Description:** Overrides the [default data dictionary](#default-values). Defines the data that the custom dynamic collection processes.<br>**Values:** Dictionary List of TMDb Main Show ID                                                   |
| `exclude`                                | **Description:** Exclude these Collections from creating a Dynamic Collection.<br>**Values:** List of Collection IDs                                                                                                                            |
| `minimum_items`                          | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                                          |
| `name_mapping_<<key>>`<sup>**1**</sup>       | **Description:** Sets the name mapping value for using assets of the [key's](#collection_section) collection.<br>**Values:** Any String                                                                                                         |
| `order_<<key>>`<sup>**1**</sup>              | **Description:** Controls the sort order of the collections in their collection section.<br>**Values:** Any number                                                                                                                              |
| `remove_addons`                          | **Description:** Removes from the [default addons dictionary](#default-values).<br>**Values:** Dictionary List of TMDb Show IDs                                                                                                                 |
| `remove_data`                            | **Description:** Removes from the [default data dictionary](#default-values).<br>**Values:** List of TMDb Main Show IDs to remove                                                                                                               |
| `sort_title_<<key>>`<sup>**1**</sup>         | **Description:** Sets the sort title of the [key's](#collection_section) collection.<br>**Default:** `sort_title`<br>**Values:** Any String                                                                                                     |
| `sort_title`                             | **Description:** Sets the sort title for all collections. Use `<<collection_name>>` to use the collection name. **Example:** `"!02_<<collection_name>>"`<br>**Values:** Any String with `<<collection_name>>`                                   |
| `summary_<<key>>`<sup>**1**</sup>            | **Description:** Changes the summary of the [key's](#collection_section) collection.<br>**Values:** New Collection Summary                                                                                                                      |
<!--show-franchise-->
<!--franchise-->
| `build_collection`                       | **Description:** Controls if you want the collection to actually be built. i.e. you may just want these movies sent to Radarr.<br>**Values:** `false` to not build the collection                                                              |
| `collection_section`                     | **Description:** Adds a sort title with this collection sections.<br>**Values:** Any number                                                                                                                                                    |
| `minimum_items`                          | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                                         |
| `movie_<<key>>`<sup>**1**</sup>              | **Description:** Adds the TMDb Movie IDs given to the [key's](#collection_section) collection. Overrides the [default movie](#default-values) for that collection if used.<br>**Values:** List of TMDb Movie IDs                               |
| `name_mapping_<<key>>`<sup>**1**</sup>       | **Description:** Sets the name mapping value for using assets of the [key's](#collection_section) collection.Overrides the [default name_mapping](#default-values) for that collection if used.<br>**Values:** Any String                      |
| `order_<<key>>`<sup>**1**</sup>              | **Description:** Controls the sort order of the collections in their collection section.<br>**Values:** Any number                                                                                                                             |
| `sort_title_<<key>>`<sup>**1**</sup>         | **Description:** Sets the sort title of the [key's](#collection_section) collection.<br>**Default:** `sort_title`<br>**Values:** Any String                                                                                                    |
| `sort_title`                             | **Description:** Sets the sort title for all collections. Use `<<collection_name>>` to use the collection name. **Example:** `"!02_<<collection_name>>"`<br>**Values:** Any String with `<<collection_name>>`                                  |
| `summary_<<key>>`<sup>**1**</sup>            | **Description:** Changes the summary of the [key's](#collection_section) collection.<br>**Values:** New Collection Summary                                                                                                                     |
| `title_override`                         | **Description:** Overrides the [default title_override dictionary](#default-values).<br>**Values:** Dictionary with `key: new_title` entries                                                                                                   |
<!--franchise-->
<!--arr-->
| `ARR_CODE_add_missing_<<key>>`<sup>**1**</sup> | **Description:** Override ARR_NAME `add_missing` attribute of the [key's](#collection_section) collection.<br>**Default:** `ARR_CODE_add_missing`<br>**Values:** `true` or `false`                                                                      |
| `ARR_CODE_add_missing`                     | **Description:** Override ARR_NAME `add_missing` attribute for all collections in a Defaults File.<br>**Values:** `true` or `false`                                                                                                                     |
| `ARR_CODE_folder_<<key>>`<sup>**1**</sup>      | **Description:** Override ARR_NAME `root_folder_path` attribute of the [key's](#collection_section) collection.<br>**Default:** `ARR_CODE_folder`<br>**Values:** Folder Path                                                                            |
| `ARR_CODE_folder`                          | **Description:** Override ARR_NAME `root_folder_path` attribute for all collections in a Defaults File.<br>**Values:** Folder Path                                                                                                                      |
| `ARR_CODE_tag_<<key>>`<sup>**1**</sup>         | **Description:** Override ARR_NAME `tag` attribute of the [key's](#collection_section) collection.<br>**Default:** `ARR_CODE_tag`<br>**Values:** List or comma-separated string of tags                                                                 |
| `ARR_CODE_tag`                             | **Description:** Override ARR_NAME `tag` attribute for all collections in a Defaults File.<br>**Values:** List or comma-separated string of tags                                                                                                        |
| `item_ARR_CODE_tag_<<key>>`<sup>**1**</sup>    | **Description:** Used to append a tag in ARR_NAME for every ARR_TYPE found by the builders that's in ARR_NAME of the [key's](#collection_section) collection.<br>**Default:** `item_ARR_CODE_tag`<br>**Values:** List or comma-separated string of tags |
| `item_ARR_CODE_tag`                        | **Description:** Used to append a tag in ARR_NAME for every ARR_TYPE found by the builders that's in ARR_NAME for all collections in a Defaults File.<br>**Values:** List or comma-separated string of tags                                             |
<!--arr-->
<!--basic-->
| `in_the_last_<<key>>`<sup>**1**</sup> | **Description:** Changes how far back the Smart Filter looks.<br>**Default:**<table class="clearTable"><tr><td>Key</td><td>Value</td></tr><tr><td>`released`</td><td>`90`</td></tr><tr><td>`episodes`</td><td>`7`</td></tr></table><br>**Values:** Number greater than 0 |
<!--basic-->
<!--myanimelist-->
| `starting_only` | **Description:** Changes the season collection to only use anime listed under the new section on [MAL Seasons](https://myanimelist.net/anime/season/)<br>**Default:** `False`<br>**Values:** `True` or `False` |
<!--myanimelist-->
<!--tautulli-->
| `list_days`                     | **Description:** Changes the `list_days` attribute of the Builder for all collections in a Defaults File.<br>**Values:** Number greater than 0         |
| `list_days_<<key>>`<sup>**1**</sup> | **Description:** Changes the `list_days` attribute of the Builder of the [key's](#collection_section) collection.<br>**Values:** Number greater than 0 |
| `list_size`                     | **Description:** Changes the `list_size` attribute of the Builder for all collections in a Defaults File.<br>**Values:** Number greater than 0         |
| `list_size_<<key>>`<sup>**1**</sup> | **Description:** Changes the `list_size` attribute of the Builder of the [key's](#collection_section) collection.<br>**Values:** Number greater than 0 |
<!--tautulli-->
<!--universe-->
| `name_mapping_<<key>>`<sup>**1**</sup>     | **Description:** Sets the name mapping value for using assets of the [key's](#collection_section) collection. <br>**Values:** Any String                                                                                        |
| `minimum_items`                        | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                          |
| `trakt_list_<<key>>`<sup>**1**</sup>       | **Description:** Adds the Movies in the Trakt List to the [key's](#collection_section) collection. Overrides the [default trakt_url](#default-values) for that collection if used.<br>**Values:** List of Trakt List URLs       |
| `imdb_list_<<key>>`<sup>**1**</sup>        | **Description:** Adds the Movies in the IMDb List to the [key's](#collection_section) collection.<br>**Values:** List of IMDb List URLs                                                                                         |
| `mdblist_list_<<key>>`<sup>**1**</sup>     | **Description:** Adds the Movies in the MDBList List to the [key's](#collection_section) collection. Overrides the [default mdblist_url](#default-values) for that collection if used.<br>**Values:** List of MDBList List URLs |
<!--universe-->
<!--streaming-->
| `discover_with_<<key>>` | **Description:** Overrides the TMDb Watch Provider used for the specified key. This is only needed if a specific `region` has a different ID for the watch provider.<br>**Default:** `<<discover_with>>`<br>**Values:** Any TMDb Watch Provider ID for [Movies](https://developer.themoviedb.org/reference/watch-providers-movie-list) / [Shows](https://developer.themoviedb.org/reference/watch-provider-tv-list) based on the user's region |
| `originals_only`        | **Description:** Changes Streaming Service lists to only show original content produced by the service.<br>**Note**: Cannot be used with `region`, and only produces collections for `amazon`, `appletv`, `disney`, `max`, `hulu`, `netflix`, `paramount`, `peacock`<br>**Default:** `false`<br>**Values:** `true`, `false`                                                                                                                    |
| `region`                | **Description:** Changes some Streaming Service lists to regional variants (see below table for more information.<br>**Default:** `us`<br>**Values:** Any [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) of the region where the streaming information should be based on.                                                                                                                                          |
<!--streaming-->
<!--collectionless-->
| `collection_order`       | **Description:** Changes the Collection Order for all collections in a Defaults File.<br>**Default:** `alpha`<br>**Values:**{% include-markdown "./tables/collection_order.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
| `sort_title`             | **Description:** Sets the sort title for the collection.<br>**Default:** `~_Collectionless`<br>**Values:** Any String                                                                                                                        |
| `url_poster`             | **Description:** Changes the poster url of the collection.<br>**Values:** URL directly to the Image                                                                                                                                          |
| `exclude`                | **Description:** Exclude these Collections from being considered for collectionless.<br>**Values:** List of Collections                                                                                                                      |
| `exclude_prefix`         | **Description:** Overrides the default exclude_prefix list. Exclude Collections with one of these prefixes from being considered for collectionless.<br>**Default:** default exclude_prefix list<br>**Values:** List of Prefixes             |
| `name_collectionless`    | **Description:** Changes the name of the collection.<br>**Values:** New Collection Name                                                                                                                                                      |
| `summary_collectionless` | **Description:** Changes the summary of the collection.<br>**Values:** New Collection Summary                                                                                                                                                |
<!--collectionless-->
<!--people-data-->
| `data` | **Description:** Replaces the `data` dynamic collection value.<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>depth</code></td><td>Controls the depth within the casting credits to search for common actors<br><strong>Default:</strong> 5<br><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>limit</code></td><td>Controls the maximum number of collections to create<br><strong>Default:</strong> 25<br><strong>Values:</strong> Number greater than 0</td></tr></table> |
<!--people-data-->
<!--award-data-->
| `data` | **Description:** Replaces the `data` dynamic collection value.<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections<br><strong>Default:</strong> latest-5<br><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections<br><strong>Default:</strong> latest<br><strong>Values:</strong> Number greater than 1</td></tr><tr><td><code>increment</code></td><td>Controls the increment (i.e. every 5th year)<br><strong>Default:</strong> 1<br><strong>Values:</strong> Number greater than 0</td><td></td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>latest</code></strong></li><li><strong>You can also use a value relative to the <code>latest</code> by doing <code>latest-5</code></strong></li></ul> |
<!--award-data-->
<!--year-data-->
| `data` | **Description:** Replaces the `data` dynamic collection value.<br><table class="clearTable"><tr><th>Attribute</th><th>Description & Values</th></tr><tr><td><code>starting</code></td><td>Controls the starting year for collections<br><strong>Default:</strong> current_year-10<br><strong>Values:</strong> Number greater than 0</td></tr><tr><td><code>ending</code></td><td>Controls the ending year for collections<br><strong>Default:</strong> current_year<br><strong>Values:</strong> Number greater than 1</td></tr><tr><td><code>increment</code></td><td>Controls the increment (i.e. every 5th year)<br><strong>Default:</strong> 1<br><strong>Values:</strong> Number greater than 0</td><td></td></tr></table><ul><li><strong><code>starting</code> and <code>ending</code> can also have the value <code>current_year</code></strong></li><li><strong>You can also use a value relative to the <code>current_year</code> by doing <code>current_year-5</code></strong></li></ul> |
<!--year-data-->
<!--data-->
| `data`        | **Description:** Overrides the [default data dictionary](#default-values). Defines the data that the custom dynamic collection processes.<br>**Values:** Dictionary List of keys/names |
| `append_data` | **Description:** Appends to the [default data dictionary](#default-values).<br>**Values:** Dictionary List of keys/names                                                               |
| `remove_data` | **Description:** Removes from the [default data dictionary](#default-values).<br>**Values:** List of keys to remove                                                                    |
<!--data-->
<!--addons-->
| `addons` | **Description:** Overrides the [default addons dictionary](#default-values). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of DYNAMIC_VALUE |
<!--addons-->
<!--addons-extra-->
| `append_addons` | **Description:** Appends to the [default addons dictionary](#default-values).<br>**Values:** Dictionary List of DYNAMIC_VALUE   |
| `remove_addons` | **Description:** Removes from the [default addons dictionary](#default-values).<br>**Values:** Dictionary List of DYNAMIC_VALUE |
<!--addons-extra-->
<!--exclude-->
| `exclude` | **Description:** Exclude these DYNAMIC_NAME from creating a Dynamic Collection.<br>**Values:** List of DYNAMIC_VALUE |
<!--exclude-->
<!--include-->
| `include` | **Description:** Force these NAME to be included to create a Dynamic Collection.<br>**Values:** List of DYNAMIC_VALUE |
<!--include-->
<!--include-extra-->
| `append_include` | **Description:** Appends to the [default include list](#default-values)<br>**Values:** List of DYNAMIC_VALUE |
| `remove_include` | **Description:** Removes from the [default include list](#default-values)<br>**Values:** List of DYNAMIC_VALUE |
<!--include-extra-->
<!--key_name_override-->
| `key_name_override` | **Description:** Overrides the [default key_name_override dictionary](#default-values).<br>**Values:** Dictionary with `key: new_key_name` entries |
<!--key_name_override-->
<!--cache_builders-->
| `cache_builders`         | **Description:** Changes the Builder Cache for all collections in a Defaults File.<br>**Default:** `1`<br>**Values:** number 0 or greater         |
| `cache_builders_<<key>>` | **Description:** Changes the Builder Cache of the [key's](#collection_section) collection.<br>**Default:** `1`<br>**Values:** number 0 or greater |
<!--cache_builders-->
<!--collection_mode-->
| `collection_mode` | **Description:** Controls the collection mode of all collections in this file.<br>**Values:**{% include-markdown "./tables/collection_mode.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
<!--collection_mode-->
<!--collection_order-->
| `collection_order`                     | **Description:** Changes the Collection Order for all collections in a Defaults File.<br>**Default:** COLLECTION_ORDER<br>**Values:**{% include-markdown "./tables/collection_order.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %}           |
| `collection_order_<<key>>`<sup>**1**</sup> | **Description:** Changes the Collection Order of the [key's](#collection_section) collection.<br>**Default:** `collection_order`<br>**Values:**{% include-markdown "./tables/collection_order.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
<!--collection_order-->
<!--limit-->
| `limit`                     | **Description:** Changes the Builder Limit for all collections in a Defaults File.<!--limit-extra--><br>**Values:** Number Greater than 0               |
| `limit_<<key>>`<sup>**1**</sup> | **Description:** Changes the Builder Limit of the [key's](#collection_section) collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0 |
<!--limit-->
<!--limit_anidb-->
| `limit_anidb` | **Description:** Changes the Builder Limit of the AniDB Popular Collection.<br>**Default:** `30`<br>**Values:** Number greater than 0 |
<!--limit_anidb-->
<!--sort_by-->
| `sort_by` | **Description:** Changes the Smart Filter Sort for all collections in a Defaults File.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/plex.md#sort-options) |
| `sort_by_<<key>>`<sup>**1**</sup> | **Description:** Changes the Smart Filter Sort of the [key's](#collection_section) collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/plex.md#sort-options) |
<!--sort_by-->
<!--style-->
| `style` | **Description:** Controls the visual theme of the collections created.<br>**Default:** `bw`<br>**Values:** `bw`, `rainier`, `signature`, `diiivoy`, or `diiivoycolor` |
<!--style-->
<!--resolution-style-->
| `style` | **Description:** Controls the visual theme of the collections created.<br>**Default:** `default`<br>**Values:** `default` or `standards` |
<!--resolution-style-->
<!--white-style-->
| `style` | **Description:** Controls the visual theme of the collections created.<br>**Default:** `color`<br>**Values:** `color` or `white` |
<!--white-style-->
<!--color-style-->
| `style` | **Description:** Controls the visual theme of the collections created.<br>**Default:** `white`<br>**Values:** `color` or `white` |
<!--color-style-->
<!--sync_mode-->
| `sync_mode`                     | **Description:** Changes the Sync Mode for all collections in a Defaults File.<br>**Default:** `sync`<br>**Values:**{% include-markdown "./tables/sync_mode.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
| `sync_mode_<<key>>`<sup>**1**</sup> | **Description:** Changes the Sync Mode of the [key's](#collection_section) collection.<br>**Default:** `sync_mode`<br>**Values:**{% include-markdown "./tables/sync_mode.md" replace='{"\n": "", "\t": ""}' rewrite-relative-urls=false %} |
<!--sync_mode-->
<!--format-->
| `name_format` | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `NAME_FORMAT`<br>**Values:** Any string with `<<key_name>>` in it. |
| `summary_format` | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `SUMMARY_FORMAT`<br>**Values:** Any string with `<<key_name>>` in it. |
<!--format-->
<!--tmdb_birthday-->
| `tmdb_birthday` | **Description:** Controls if the Definition is run based on `tmdb_person`'s Birthday. Has 3 possible attributes `this_month`, `before` and `after`.<br>**Values:**<table class="clearTable"><tr><td>`this_month`</td><td>Run's if Birthday is in current Month</td><td>`true`/`false`</td></tr><tr><td>`before`</td><td>Run if X Number of Days before the Birthday</td><td>Number 0 or greater</td></tr><tr><td>`after`</td><td>Run if X Number of Days after the Birthday</td><td>Number 0 or greater</td></tr></table> |
| `tmdb_deathday` | **Description:** Controls if the Definition is run based on `tmdb_person`'s Deathday. Has 3 possible attributes `this_month`, `before` and `after`.<br>**Values:**<table class="clearTable"><tr><td>`this_month`</td><td>Run's if Deathday is in current Month</td><td>`true`/`false`</td></tr><tr><td>`before`</td><td>Run if X Number of Days before the Deathday</td><td>Number 0 or greater</td></tr><tr><td>`after`</td><td>Run if X Number of Days after the Deathday</td><td>Number 0 or greater</td></tr></table> |
<!--tmdb_birthday-->
<!--tmdb_person_offset-->
| `tmdb_person_offset_<<key>>`<sup>**1**</sup> | **Description:** Changes the summary tmdb_person_offset for the specific key.<br>**Default:** `0`<br>**Values:** Dictionary of Actor Name as the keys and the tmdb_person_offset as the value. |
<!--tmdb_person_offset-->

<!--sup1-->
1. Each default collection has a [`key`](#collection_section) that you must replace `<<key>>` with when using this Template Variable. These keys are found in the table at the top of this page.
<!--sup1-->