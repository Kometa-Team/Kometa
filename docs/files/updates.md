---
hide:
  - tags
  - toc
tags:
  - tmdb_person
  - tmdb_person_offset
  - sort_title
  - content_rating
  - label
  - label.remove
  - label.sync
  - collection_mode
  - collection_order
  - collection_filtering
  - visible_library
  - visible_home
  - visible_shared
  - url_theme
  - file_theme
  - url_poster
  - tmdb_poster
  - tmdb_list_poster
  - tmdb_profile
  - tvdb_poster
  - tvdb_list_poster
  - file_poster
  - url_background
  - tmdb_background
  - tvdb_background
  - file_background
---

# Collection/Playlist Metadata Updates

All the following attributes update various details of the definition's Metadata. 

**Only `tmdb_person` works with Playlists.**

| Attribute              | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `collection_filtering` | **Description:** Changes the Collection Filtering<br>**Smart Collections Only**<br>**Values:**<table class="clearTable"><tr><td>`admin`</td><td>Always the server admin user</td></tr><tr><td>`user`</td><td>User currently viewing the content</td></tr></table>                                                                                                                                                                                                                                                                                                                                                               |
| `collection_mode`      | **Description:** Changes the Collection Mode<br>**Values:**<table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table>                                                                                                                                                                                                                                                                                   |
| `collection_order`     | **Description:** Changes the Collection Order<br>**Normal Collections Only**<br>When using `custom.asc`/`custom.desc` you can only have a single Builder in the collection.<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom.asc`/`custom.desc`</td><td>Order Collection Via the Builder Order ascending or descending</td></tr><tr><td>[Any `plex_search` Sort Option](builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |
| `content_rating`       | **Description:** Changes the content rating.<br>**Values:** Text to change Content Rating                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `file_theme`           | **Description:** Changes the Collection Theme to the file location provided.<br>**Values:** Path to mp3 file                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `label.remove`         | **Description:** Removes existing labels from the collection.<br>**Values:** Comma-separated string of labels to remove                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `label.sync`           | **Description:** Matches the labels of the collection to the labels provided (Leave blank to remove all labels)<br>**Values:** Comma-separated string of labels to sync                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `label`                | **Description:** Appends new labels.<br>**Values:** Comma-separated string of labels to append                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `sort_title`           | **Description:** Changes the sort title.<br>You can "promote" certain collections to the top of a library by creating a sort title starting with a `+` or "demote" certain collections to the bottom of a library by creating a sort title starting with a `~`.<br>**Values:** Text to change Sort Title                                                                                                                                                                                                                                                                                                                        |
| `tmdb_person_offset`   | **Description:** Offsets which search results are used by `tmdb_person`.<br>**Values:** Any number greater than 0<br>**Default:** 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `tmdb_person`          | **Description:** Changes summary and poster to a TMDb Person's biography and profile to the first specified person as well as allow the people specified to be used in [Plex Searches](builders/plex.md#plex-search).<br>**Values:** TMDb Person ID or Actor Name (Will pull the first ID from the TMDb search results) (List or Comma-separated string)                                                                                                                                                                                                                                                                        |
| `url_theme`            | **Description:** Changes the Collection Theme to the URL provided.<br>**Values:** URL to mp3 file                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `visible_home`         | **Description:** Changes collection visible on Home Tab (Only works with Plex Pass)<br>**Values:**<table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table>                                                                                                                                                                                                                                                                                                        |
| `visible_library`      | **Description:** Changes collection visible on Library Recommended Tab (Only works with Plex Pass)<br>**Values:**<table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table>                                                                                                                                                                                                                                                                                         |
| `visible_shared`       | **Description:** Changes collection visible on Shared Users' Home Tab (Only works with Plex Pass)<br>**Values:**<table class="clearTable"><tr><td>`true`</td><td>Visible</td></tr><tr><td>`false`</td><td>Not Visible</td></tr><tr><td>[Any `schedule` Option](../config/schedule.md)</td><td>Visible When Scheduled</td></tr></table>                                                                                                                                                                                                                                                                                          |

* Here's an example of how the collections can look on the Home Page.

## Summary Collection/Playlist Metadata Updates

All the following attributes update the summary of the collection/playlist from various sources. 

**All of these details work with Playlists.**

| Attribute                | Description & Values                                                                                                                                                               |
| :----------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `letterboxd_description` | **Description:** Changes summary to the Letterboxd List Description<br>**Values:** Letterboxd List URL                                                                             |
| `summary`                | **Description:** Changes summary to the Text Provided<br>**Values:** Text to change Summary                                                                                        |
| `tmdb_biography`         | **Description:** Changes summary to the TMDb Person's biography<br>**Values:** TMDb Person ID                                                                                      |
| `tmdb_description`       | **Description:** Changes summary to the TMDb List Description<br>**Values:** TMDb List ID                                                                                          |
| `tmdb_summary`           | **Description:** Changes summary to the TMDb Movie/Collection summary for a movie library or the TMDb Show summary for a show library<br>**Values:** TMDb Movie/Show/Collection ID |
| `trakt_description`      | **Description:** Changes summary to the Trakt List Description<br>**Values:** Trakt List URL                                                                                       |
| `tvdb_description`       | **Description:** Changes summary to the TVDb List Description<br>**Values:** TVDb List URL                                                                                         |
| `tvdb_summary`           | **Description:** Changes summary to the TVDb Movie summary for a movie library or the TVDb Show summary for a show library<br>**Values:** TVDb Movie/Show ID or URL                |

## Poster Collection/Playlist Metadata Updates

All the following attributes update the poster of the collection/playlist from various sources. 

**All of these details work with Playlists.**

If no poster is specified the script will look in the library's [Image Asset Directories](../kometa/guides/assets.md) for a
folder named either the collection/playlist name or the `name_mapping` if specified and look for a `poster.ext` file in 
that folder (replacing .ext with the image extension).

| Attribute          | Description & Values                                                                                                                                                            |
| :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `file_poster`      | **Description:** Changes poster to the image in the file system<br>**Values:** Path to image in the file system                                                                 |
| `tmdb_list_poster` | **Description:** Changes poster to the TMDb List poster<br>**Values:** TMDb List ID                                                                                             |
| `tmdb_poster`      | **Description:** Changes poster to the TMDb Movie/Collection poster for a movie library or the TMDb Show poster for a show library<br>**Values:** TMDb Movie/Show/Collection ID |
| `tmdb_profile`     | **Description:** Changes poster to the TMDb Person's profile<br>**Values:** TMDb Person ID                                                                                      |
| `tvdb_list_poster` | **Description:** Changes poster to the TVDb List poster<br>**Values:** TVDb List URL                                                                                            |
| `tvdb_poster`      | **Description:** Changes poster to the TVDb Movie poster for a movie library or the TVDb Show poster for a show library<br>**Values:** TVDb Movie/Show ID or URL                |
| `url_poster`       | **Description:** Changes poster to the URL<br>**Values:** URL of image publicly available on the internet                                                                       |

Standard priority is as follows [lower numbers take precedence]:

1. url_poster

2. file_poster

3. tmdb_poster

4. tvdb_poster

5. asset_directory

6. tmdb_person

7. tmdb_collection_details

8+. all other _details methods

You can use the `prioritize_assets` setting to push the asset_directory to the top of this priority list.

## Background Collection/Playlist Metadata Updates

All the following attributes update the background of the collection/playlist from various sources.

**All of these details work with Playlists.**

If no background is specified the script will look in the library's [Image Asset Directories](../kometa/guides/assets.md) 
for a folder named either the collection/playlist name or the `name_mapping` if specified and look for a 
`background.ext` file in that folder (replacing .ext with the image extension).

| Attribute         | Description & Values                                                                                                                                                                        |
| :---------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `file_background` | **Description:** Changes background to the image in the file system<br>**Values:** Path to image in the file system                                                                         |
| `tmdb_background` | **Description:** Changes background to the TMDb Movie/Collection background for a movie library or the TMDb Show background for a show library<br>**Values:** TMDb Movie/Show/Collection ID |
| `tvdb_background` | **Description:** Changes background to the TVDb Movie background for a movie library or the TVDb Show background for a show library<br>**Values:** TVDb Movie/Show ID or URL                |
| `url_background`  | **Description:** Changes background to the URL<br>**Values:** URL of image publicly available on the internet                                                                               |

Standard priority is as follows [lower numbers take precedence]:

1. url_background

2. file_background

3. tmdb_background

4. tvdb_background

5. asset_directory

You can use the `prioritize_assets` setting to push the asset_directory to the top of this priority list.
