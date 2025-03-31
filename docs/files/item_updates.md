---
search:
  boost: 3
hide:
  - tags
  - toc
tags:
  - addon_offset
  - item_label
  - item_label.remove
  - item_label.sync
  - item_genre
  - item_genre.remove
  - item_genre.sync
  - item_edition
  - non_item_remove_label
  - item_lock_poster
  - item_lock_background
  - item_lock_title
  - item_assets
  - item_refresh
  - item_refresh_delay
  - item_tmdb_season_titles
  - item_episode_sorting
  - item_keep_episodes
  - item_delete_episodes
  - item_season_display
  - item_episode_ordering
  - item_metadata_language
  - item_use_original_title
  - item_credits_detection
  - item_audio_language
  - item_subtitle_language
  - item_subtitle_mode
  - item_analyze
---

# Item Metadata Updates

All the following attributes update various details of the metadata for every item in the collection. 

**None of these updates work with Playlists or Overlays.**

<div class="annotate" markdown>

| Attribute                     | Description                                                                                           | Allowed Values (default in **bold**)                                                                                                                                                                                                                                                                                                                                                                         |
|:------------------------------|:------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `item_analyze`                | Runs Plex's Analyze Operation on every movie/show in the collection                                   | `true`, **`false`**                                                                                                                                                                                                                                                                                                                                                                                          |
| `item_assets`                 | Checks your assets folders for assets of every movie/show in the collection                           | `true`, **`false`**                                                                                                                                                                                                                                                                                                                                                                                          |
| `item_audio_language` (1)     | Changes the preferred audio language of every movie/show in the collection                            | `default`, `en`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-TW     |
| `item_credits_detection` (2)  | Changes the enable credits detection of every movie/show in the collection                            | `default` (Library default), `disabled` (Disabled)                                                                                                                                                                                                                                                                                                                                                           |
| `item_delete_episodes` (3)    | Changes the delete episodes setting of every show in the collection                                   | `never` (Never), `day` (After a day), `week` (After a week), `month` (After a month), `refresh` (On next refresh)                                                                                                                                                                                                                                                                                            |
| `item_edition`                | Replaces the edition of every movie in the collection                                                 | Edition name (e.g. `Extended`, `Director's Cut`)                                                                                                                                                                                                                                                                                                                                                             |
| `item_episode_ordering`(4)    | Changes the episode ordering of every show in the collection                                          | `default` (Library default), `tmdb_aired`, `tvdb_aired`, `tvdb_dvd`, `tvdb_absolute`                                                                                                                                                                                                                                                                                                                         |
| `item_episode_sorting`(5)     | Changes the episode sorting of every show in the collection                                           | `default` (Library default), `oldest`, `newest`                                                                                                                                                                                                                                                                                                                                                              |
| `item_genre.remove`           | Removes existing genres from every movie/show in the collection                                       | Comma-separated list of genres to remove                                                                                                                                                                                                                                                                                                                                                                     |
| `item_genre.sync`             | Matches the genres of every movie/show in the collection to the genres provided                       | Comma-separated list of genres to sync                                                                                                                                                                                                                                                                                                                                                                       |
| `item_genre`                  | Appends new genres to every movie/show in the collection                                              | Comma-separated list of genres to append                                                                                                                                                                                                                                                                                                                                                                     |
| `item_keep_episodes`(6)       | Changes the keep episodes setting of every show in the collection                                     | `all`, `5_latest`, `3_latest`, `latest`, `past_3`, `past_7`, `past_30`                                                                                                                                                                                                                                                                                                                                       |
| `item_label.remove`           | Removes existing labels from every movie/show in the collection                                       | Comma-separated list of labels to remove                                                                                                                                                                                                                                                                                                                                                                     |
| `item_label.sync`             | Matches the labels of every movie/show in the collection to the labels provided                       | Comma-separated list of labels to sync                                                                                                                                                                                                                                                                                                                                                                       |
| `item_label`                  | Appends new labels to every movie/show in the collection                                              | Comma-separated list of labels to append                                                                                                                                                                                                                                                                                                                                                                     |
| `item_lock_background`        | Locks or unlocks the background of every movie/show in the collection                                 | `true`, `false`, or leave blank                                                                                                                                                                                                                                                                                                                                                                              |
| `item_lock_poster`            | Locks or unlocks the poster of every movie/show in the collection                                     | `true`, `false`, or leave blank                                                                                                                                                                                                                                                                                                                                                                              |
| `item_lock_title`             | Locks or unlocks the title of every movie/show in the collection                                      | `true`, `false`, or leave blank                                                                                                                                                                                                                                                                                                                                                                              |
| `item_metadata_language`(7)   | Changes the metadata language of every movie/show in the collection                                   | `default`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-T`           |
| `item_refresh_delay`          | Amount of time to wait between each `item_refresh` of every movie/show in the collection              | Number greater than `0`, e.g. **`0`**                                                                                                                                                                                                                                                                                                                                                                        |
| `item_refresh`                | Refreshes the metadata of every movie/show in the collection                                          | `true`, **`false`**                                                                                                                                                                                                                                                                                                                                                                                          |
| `item_season_display`(8)      | Changes the season display of every show in the collection                                            | `default` (Library default), `show`, `hide`                                                                                                                                                                                                                                                                                                                                                                  |
| `item_subtitle_language`(9)   | Changes the preferred subtitle language of every movie/show in the collection                         | `default`, `en`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-TW`    |
| `item_subtitle_mode`(10)      | Changes the auto-select subtitle mode of every movie/show in the collection                           | `default` (Account default), `manual` (Manually selected), `foreign` (Shown with foreign audio), `always` (Always enabled)                                                                                                                                                                                                                                                                                   |
| `item_tmdb_season_titles`     | Changes the season titles of every show in the collection to match TMDb                               | `true`, **`false`**                                                                                                                                                                                                                                                                                                                                                                                          |
| `item_use_original_title`(11) | Changes the use original title of every movie/show in the collection                                  | `default` (Library default), `no`, `yes`                                                                                                                                                                                                                                                                                                                                                                     |
| `non_item_remove_label`       | Matches every movie/show that has the given label and is not in the collection and removes the label  | Comma-separated list of labels to remove                                                                                                                                                                                                                                                                                                                                                                     |

</div>

1.  Must be using the Plex Movie or Plex Series Agent
2.  Must be using the Plex Movie or Plex Series Agent
3.  Only works with Show libraries
4.  Only works with Show libraries
5.  Only works with Show libraries
6.  Only works with Show libraries
7.  Must be using the Plex Movie or Plex Series Agent
8.  Only works with Show libraries
9.  Must be using the Plex Movie or Plex Series Agent
10. Must be using the Plex Movie or Plex Series Agent
11. Must be using the Plex Movie or Plex Series Agent