# Operations

There are a variety of Library Operations that can be utilized in a library.

Within each library, operations can be defined by using the `operations` attribute, as demonstrated below.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: imdb
    operations:
      mass_critic_rating_update: tmdb
      split_duplicates: true
```

The available attributes for the operations attribute are as follows

| Attribute                                                             | Description                                                                                                                                                |
|:----------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Assets For All](#assets-for-all)                                     | Search in assets for images for every item in your library.                                                                                                |
| [Delete Collections With Less](#delete-collections-with-less)         | Deletes every collection with less than the given number of items.                                                                                         |
| [Delete Unmanaged Collections](#delete-unmanaged-collections)         | Deletes every unmanaged collection.                                                                                                                        |
| [Mass Genre Update](#mass-genre-update)                               | Updates every item's genres in the library to the chosen site's genres.                                                                                    |
| [Mass Content Rating Update](#mass-content-rating-update)             | Updates every item's content rating in the library to the chosen site's content rating.                                                                    |
| [Mass Original Title Update](#mass-original-title-update)             | Updates every item's original title in the library to the chosen site's original title.                                                                    |
| [Mass Originally Available Update](#mass-originally-available-update) | Updates every item's originally available date in the library to the chosen site's date.                                                                   |
| [Mass * Rating Update](#mass--rating-update)                          | Updates every item's audience/critic/user rating in the library to the chosen site's rating.                                                               |
| [Mass Episode * Rating Update](#mass-episode--rating-update)          | Updates every item's episode's audience/critic/user rating in the library to the chosen site's rating.                                                     |
| [Mass Poster Update](#mass-poster-update)                             | Updates every item's poster to the chosen sites poster. Will fallback to `plex` if the given option fails. Assets will be used over anything else.         |
| [Mass Background Update](#mass-background-update)                     | Updates every item's background to the chosen sites background. Will fallback to `plex` if the given option fails. Assets will be used over anything else. |
| [Mass IMDb Parental Labels](#mass-imdb-parental-labels)               | Updates every item's labels in the library to match the IMDb Parental Guide.                                                                               |
| [Mass Collection Mode](#mass-collection-mode)                         | Updates every Collection in your library to the specified Collection Mode.                                                                                 |
| [Update Blank Track Titles](#update-blank-track-titles)               | Search though every track in a music library and replace any blank track titles with the tracks sort title.                                                |
| [Remove Title Parentheses](#remove-title-parentheses)                 | Search through every title and remove all ending parentheses in an items title if the title isn not locked.                                                |
| [Split Duplicates](#split-duplicates)                                 | Splits all duplicate movies/shows found in this library.                                                                                                   |
| [Radarr Add All](#radarr-add-all)                                     | Adds every item in the library to Radarr.                                                                                                                  |
| [Radarr Remove By Tag](#radarr-remove-by-tag)                         | Removes every item from Radarr with the Tags given.                                                                                                        |
| [Sonarr Add All](#sonarr-add-all)                                     | Adds every item in the library to Sonarr.                                                                                                                  |
| [Sonarr Remove By Tag](#sonarr-remove-by-tag)                         | Removes every item from Sonarr with the Tags given.                                                                                                        |
| [Genre Mapper](#genre-mapper)                                         | Allows genres to be changed to other genres or be removed from every item in your library.                                                                 |
| [Content Rating Mapper](#content-rating-mapper)                       | Allows content ratings to be changed to other content ratings or be removed from every item in your library.                                               |
| [Metadata Backup](#metadata-backup)                                   | Creates/Maintains a PMM [Metadata File](../metadata/metadata) with a full `metadata` mapping based on the library's items locked attributes.               |

## Assets For All

Search in assets for images for every item in your library.

**Attribute:** `assets_for_all`

**Values:** `true` or `false`

## Delete Collections With Less

Deletes every collection with less than the given number of items.

**Attribute:** `delete_collections_with_less`

**Values:** number greater than 0  

## Delete Unmanaged Collections

Deletes every collection that doesn't have the PMM label.

**Attribute:** `delete_unmanaged_collections`

**Values:** `true` or `false`

## Mass Genre Update

Updates every item's genres in the library to the chosen site's genres.

**Attribute:** `mass_genre_update`

**Values:**

| Value    | Description                        |
|:---------|:-----------------------------------|
| `tmdb`   | Use TMDb for Genres                |
| `tvdb`   | Use TVDb for Genres                |
| `imdb`   | Use IMDb for Genres                |
| `omdb`   | Use IMDb through OMDb for Genres   |
| `anidb`  | Use AniDB Tags for Genres          |
| `mal`    | Use MyAnimeList for Genres         |
| `lock`   | Lock Genre Field                   |
| `unlock` | Unlock Genre Field                 |
| `remove` | Remove all Genres and Lock Field   |
| `reset`  | Remove all Genres and Unlock Field |

## Mass Content Rating Update

Updates every item's content rating in the library to the chosen site's content rating.

**Attribute:** `mass_content_rating_update`

**Values:**

| Value              | Description                                                                  |
|:-------------------|:-----------------------------------------------------------------------------|
| `mdb`              | Use MdbList for Content Ratings                                              |
| `mdb_commonsense`  | Use Commonsense Rating through MDbList for Content Ratings                   |
| `mdb_commonsense0` | Use Commonsense Rating with Zero Padding through MDbList for Content Ratings |
| `omdb`             | Use IMDb through OMDb for Content Ratings                                    |
| `mal`              | Use MyAnimeList for Content Ratings                                          |
| `lock`             | Lock Content Rating Field                                                    |
| `unlock`           | Unlock Content Rating Field                                                  |
| `remove`           | Remove Content Rating and Lock Field                                         |
| `reset`            | Remove Content Rating and Unlock Field                                       |

## Mass Original Title Update 

Updates every item's original title in the library to the chosen site's original title.

**Attribute:** `mass_original_title_update`

**Values:**

| Value            | Description                                                                                     |
|:-----------------|:------------------------------------------------------------------------------------------------|
| `anidb`          | Use AniDB Main Title for Original Titles                                                        |
| `anidb_official` | Use AniDB Official Title based on the language attribute in the config file for Original Titles |
| `mal`            | Use MyAnimeList Main Title for Original Titles                                                  |
| `mal_english`    | Use MyAnimeList English Title for Original Titles                                               |
| `mal_japanese`   | Use MyAnimeList Japanese Title for Original Titles                                              |
| `lock`           | Lock Original Title Field                                                                       |
| `unlock`         | Unlock Original Title Field                                                                     |
| `remove`         | Remove Original Title and Lock Field                                                            |
| `reset`          | Remove Original Title and Unlock Field                                                          |

## Mass Originally Available Update 

Updates every item's originally available date in the library to the chosen site's date.

**Attribute:** `mass_original_title_update`

**Values:**

| Value    | Description                                  |
|:---------|:---------------------------------------------|
| `tmdb`   | Use TMDb Release Date                        |
| `tvdb`   | Use TVDb Release Date                        |
| `omdb`   | Use IMDb Release Date through OMDb           |
| `mdb`    | Use MdbList Release Date                     |
| `anidb`  | Use AniDB Release Date                       |
| `mal`    | Use MyAnimeList Release Date                 |
| `lock`   | Lock Originally Available Field              |
| `unlock` | Unlock Originally Available Field            |
| `remove` | Remove Originally Available and Lock Field   |
| `reset`  | Remove Originally Available and Unlock Field |

## Mass * Rating Update 

Updates every item's audience/critic/user rating in the library to the chosen site's rating.

**Attribute:** `mass_audience_rating_update`/`mass_critic_rating_update`/`mass_user_rating_update`

**Values:**

| Value                  | Description                                         |
|:-----------------------|:----------------------------------------------------|
| `tmdb`                 | Use TMDb Rating                                     |
| `imdb`                 | Use IMDb Rating                                     |
| `trakt_user`           | Use Trakt User's Personal Rating                    |
| `omdb`                 | Use IMDbRating through OMDb                         |
| `mdb`                  | Use MdbList Score                                   |
| `mdb_imdb`             | Use IMDb Rating through MDbList                     |
| `mdb_metacritic`       | Use Metacritic Rating through MDbList               |
| `mdb_metacriticuser`   | Use Metacritic User Rating through MDbList          |
| `mdb_trakt`            | Use Trakt Rating through MDbList                    |
| `mdb_tomatoes`         | Use Rotten Tomatoes Rating through MDbList          |
| `mdb_tomatoesaudience` | Use Rotten Tomatoes Audience Rating through MDbList |
| `mdb_tmdb`             | Use TMDb Rating through MDbList                     |
| `mdb_letterboxd`       | Use Letterboxd Rating through MDbList               |
| `mdb_myanimelist`      | Use MyAnimeList Rating through MDbList              |
| `anidb_rating`         | Use AniDB Rating                                    |
| `anidb_average`        | Use AniDB Average                                   |
| `anidb_score`          | Use AniDB Review Score                              |
| `mal`                  | Use MyAnimeList Score                               |
| `lock`                 | Lock Rating Field                                   |
| `unlock`               | Unlock Rating Field                                 |
| `remove`               | Remove Rating and Lock Field                        |
| `reset`                | Remove Rating and Unlock Field                      |

## Mass Episode * Rating Update

Updates every item's episode's audience/critic/user rating in the library to the chosen site's rating.

**Attribute:** `mass_episode_audience_rating_update`/`mass_episode_critic_rating_update`/`mass_episode_user_rating_update`

**Values:**

| Value    | Description                    |
|:---------|:-------------------------------|
| `tmdb`   | Use TMDb Rating                |
| `imdb`   | Use IMDb Rating                |
| `lock`   | Lock Rating Field              |
| `unlock` | Unlock Rating Field            |
| `remove` | Remove Rating and Lock Field   |
| `reset`  | Remove Rating and Unlock Field |

## Mass Poster Update

Updates every item's poster to the chosen sites poster. Will fallback to `plex` if the given option fails. Assets will be used over anything else.

**Attribute:** `mass_poster_update`

**Values:**

| Value    | Description     |
|:---------|:----------------|
| `tmdb`   | Use TMDb Poster |
| `plex`   | Use Plex Poster |
| `lock`   | Lock Poster     |
| `unlock` | Unlock Poster   |

## Mass Background Update

Updates every item's background to the chosen sites background. Will fallback to `plex` if the given option fails. Assets will be used over anything else.

**Attribute:** `mass_background_update`

**Values:**

| Value    | Description         |
|:---------|:--------------------|
| `tmdb`   | Use TMDb Background |
| `plex`   | Use Plex Background |
| `lock`   | Lock Background     |
| `unlock` | Unlock Background   |

## Mass IMDb Parental Labels

Updates every item's labels in the library to match the IMDb Parental Guide

**Attribute:** `mass_imdb_parental_labels`

**Values** `with_none` or `without_none`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

## Mass Collection Mode

Updates every Collection in your library to the specified Collection Mode.

**Attribute:** `mass_collection_mode`

**Values:** `default`: Library default<br>`hide`: Hide Collection<br>`hide_items`: Hide Items in this Collection<br>`show_items`: Show this Collection and its Items<table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

## Update Blank Track Titles`

Search though every track in a music library and replace any blank track titles with the tracks sort title.

**Attribute:** `update_blank_track_titles`

**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

## Remove Title Parentheses

Search through every title and remove all ending parentheses in an items title if the title isn not locked.

**Attribute:** `remove_title_parentheses`

**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

## Split Duplicates

Splits all duplicate movies/shows found in this library.

**Attribute:** `split_duplicates`

**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

## Radarr Add All

Adds every item in the library to Radarr. The existing paths in plex will be used as the root folder of each item, if the paths in Plex are not the same as your Radarr paths you can use the `plex_path` and `radarr_path` [Radarr](radarr) details to convert the paths.

**Attribute:** `radarr_add_all`

**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

## Radarr Remove By Tag`

Removes every item from Radarr with the Tags given.

**Attribute:** `radarr_remove_by_tag`

**Values:** List or comma separated string of tags                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

## Sonarr Add All

Adds every item in the library to Sonarr. The existing paths in plex will be used as the root folder of each item, if the paths in Plex are not the same as your Sonarr paths you can use the `plex_path` and `sonarr_path` [Sonarr](sonarr) details to convert the paths.

**Attribute:** `sonarr_add_all`

**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

## Sonarr Remove By Tag

Removes every item from Sonarr with the Tags given.

**Attribute:** `sonarr_remove_by_tag`

**Values:** List or comma separated string of tags                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

## Genre Mapper

Maps genres in your library to be changed to other genres.

**Attribute:** `genre_mapper`

**Values:** Each attribute under `genre_mapper` is a separate mapping and has two parts.
* The key (`Action/Adventure, Action & Adventure` in the example below) is what genres you want mapped to the value.
* The value (`Action` in the example below) is what the genres will end up as.

So this example will change go through every item in your library and change the genre `Action/Adventure` or `Action & Adventure` to `Action` and `Romantic Comedy` to `Comedy`.

```yaml
library:
  Movies:
    operations:
      genre_mapper:
        "Action/Adventure": Action 
        "Action & Adventure": Action
        Romantic Comedy: Comedy
```

To just Remove a Genre without replacing it just set the Genre to nothing like this.

```yaml
library:
  Movies:
    operations:
      genre_mapper:
        "Action/Adventure": Action 
        "Action & Adventure": Action
        Romantic Comedy:
```

This example will change go through every item in your library and change the genre `Action/Adventure` or `Action & Adventure` to `Action` and remove every instance of the Genre `Romantic Comedy`.

## Content Rating Mapper

Maps content ratings in your library to be changed to other content ratings.

**Attribute:** `content_rating_mapper`

**Values:** Each attribute under `content_rating_mapper` is a separate mapping and has two parts.
* The key (`PG`, `PG-13` in the example below) is what content ratings you want mapped to the value.
* The value (`Y-10` in the example below) is what the content ratings will end up as.

So this example will change go through every item in your library and change the content rating `PG` or `PG-13` to `Y-10` and `R` to `Y-17`.

```yaml
library:
  Movies:
    operations:
      content_rating_mapper:
        PG: Y-10 
        "PG-13": Y-10
        R: Y-17
```

To just Remove a content rating without replacing it just set the content rating to nothing like this.

```yaml
library:
  Movies:
    operations:
      content_rating_mapper:
        PG: Y-10 
        "PG-13": Y-10
        R:
```

This example will change go through every item in your library and change the content rating `PG` or `PG-13` to `Y-10` and remove every instance of the content rating `R`.

## Metadata Backup 

Creates/Maintains a Plex Meta Manager [Metadata File](../metadata/metadata) with a full `metadata` mapping based on the library's items locked attributes.

If you point to an existing Metadata File then PMM will Sync the changes to the file, so you won't lose non plex changes in the file.

**Attribute:** `metadata_backup`

**Values:** There are a few different options to determine how the `metadata_backup` works.

| Attribute           | Description                                                                                                                                                         |
|:--------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `path`              | Path to where the metadata will be saved/maintained<br>**Default:** <<library_name>>_Metadata_Backup.yml in your config folder<br>**Values:** Path to Metadata File |
| `exclude`           | Exclude all listed attributes from being saved in the metadata file<br>**Values:** Comma-separated string or list of attributes                                     |
| `sync_tags`         | All Tag Attributes will have the `.sync` option and blank attribute will be added to sync to as well<br>**Default:** `false`<br>**Values:** `true` or `false`       |
| `add_blank_entries` | Will add a line for entries that have no metadata changes<br>**Default:** `true`<br>**Values:** `true` or `false`                                                   |

**Example:**

```yaml
library:
  Movies:
    operations:
      metadata_backup:
        path: config/Movie_Backup.yml
        sync_tags: true
        add_blank_entries: false
```
