---
search:
  boost: 4
---
# Library Operations

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

| Attribute                                                             | Description                                                                                                                                                |   Movies   |  Shows   |  Music   |
|:----------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|:----------:|:--------:|:--------:|
| [Assets For All](#assets-for-all)                                     | Search in assets for images for every item in your library.                                                                                                |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| [Delete Collections](#delete-collections)                             | Deletes collections based on a set of given attributes.                                                                                                    |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| [Mass Genre Update](#mass-genre-update)                               | Updates every item's genres in the library to the chosen site's genres.                                                                                    |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| [Mass Content Rating Update](#mass-content-rating-update)             | Updates every item's content rating in the library to the chosen site's content rating.                                                                    |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass Original Title Update](#mass-original-title-update)             | Updates every item's original title in the library to the chosen site's original title.                                                                    |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass Studio Update](#mass-studio-update)                             | Updates every item's studio in the library to the chosen site's studio.                                                                                    |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass Originally Available Update](#mass-originally-available-update) | Updates every item's originally available date in the library to the chosen site's date.                                                                   |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass * Rating Update](#mass-rating-update)                          | Updates every item's audience/critic/user rating in the library to the chosen site's rating.                                                               |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass Episode * Rating Update](#mass-episode-rating-update)          | Updates every item's episode's audience/critic/user rating in the library to the chosen site's rating.                                                     |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass Poster Update](#mass-poster-update)                             | Updates every item's poster to the chosen sites poster. Will fallback to `plex` if the given option fails. Assets will be used over anything else.         |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass Background Update](#mass-background-update)                     | Updates every item's background to the chosen sites background. Will fallback to `plex` if the given option fails. Assets will be used over anything else. |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass IMDb Parental Labels](#mass-imdb-parental-labels)               | Updates every item's labels in the library to match the IMDb Parental Guide.                                                                               |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |
| [Mass Collection Mode](#mass-collection-mode)                         | Updates every Collection in your library to the specified Collection Mode.                                                                                 |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |
| [Update Blank Track Titles](#update-blank-track-titles)               | Search though every track in a music library and replace any blank track titles with the tracks sort title.                                                |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  |
| [Remove Title Parentheses](#remove-title-parentheses)                 | Search through every title and remove all ending parentheses in an items title if the title is not locked.                                                 |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Split Duplicates](#split-duplicates)                                 | Splits all duplicate movies/shows found in this library.                                                                                                   |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Radarr Add All](#radarr-add-all)                                     | Adds every item in the library to Radarr.                                                                                                                  |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |
| [Radarr Remove By Tag](#radarr-remove-by-tag)                         | Removes every item from Radarr with the Tags given.                                                                                                        |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |
| [Sonarr Add All](#sonarr-add-all)                                     | Adds every item in the library to Sonarr.                                                                                                                  |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Sonarr Remove By Tag](#sonarr-remove-by-tag)                         | Removes every item from Sonarr with the Tags given.                                                                                                        |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Genre Mapper](#genre-mapper)                                         | Allows genres to be changed to other genres or be removed from every item in your library.                                                                 |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Content Rating Mapper](#content-rating-mapper)                       | Allows content ratings to be changed to other content ratings or be removed from every item in your library.                                               |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| [Metadata Backup](#metadata-backup)                                   | Creates/Maintains a PMM [Metadata File](../metadata/metadata.md) with a full `metadata` mapping based on the library's items locked attributes.               |  :fontawesome-solid-circle-check:{ .green }   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |

## Assets For All

Search in assets for images for every item in your library.

**Attribute:** `assets_for_all`

**Values:** `true` or `false`

## Delete Collections

Deletes collections based on a set of given attributes. The Collection must match all set attributes to be deleted.

**Attribute:** `delete_collections`

**Values:** There are a few different options to determine how the `delete_collections` works.

| Attribute    | Description                                                                                                                                                                                                                                                                                                                                                                                                 |
|:-------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `managed`    | **Values:**<br>`true`: Collection must be a Managed Collection to be deleted (the collection has the `PMM` label)<br>`false`: Collection must be an Unmanaged Collection to be deleted (the collection does not have the `PMM` label)                                                                                                                                                                       |
| `configured` | **Values:**<br>`true`: Collection must be a Configured Collection to be deleted (collection is in the config file of the specific PMM run)<br>`false`: Collection must be an Unconfigured Collection to be deleted (collection is not in the config file of the specific PMM run).<br>**The collection does not need to be scheduled to be considered configured and only needs to be in the config file.** |
| `less`       | Collection must contain less then the given number of items to be deleted.<br>**Values:** Number greater than 0                                                                                                                                                                                                                                                                                             |

**Example:**

Removes all Managed Collections (Collections with the `PMM` Label) that are not configured in the Current Run.

```yaml
library:
  Movies:
    operations:
      delete_collections:
        configured: false
        managed: true
```

## Mass Genre Update

Updates every item's genres in the library to the chosen site's genres.

**Attribute:** `mass_genre_update`

**Values:**

| Value       | Description                                                    |
|:------------|:---------------------------------------------------------------|
| `tmdb`      | Use TMDb for Genres                                            |
| `tvdb`      | Use TVDb for Genres                                            |
| `imdb`      | Use IMDb for Genres                                            |
| `omdb`      | Use IMDb through OMDb for Genres                               |
| `anidb`     | Use AniDB Main Tags for Genres                                 |
| `anidb_3_0` | Use AniDB Main Tags and All 3 Star Tags and above for Genres   |
| `anidb_2_5` | Use AniDB Main Tags and All 2.5 Star Tags and above for Genres |
| `anidb_2_0` | Use AniDB Main Tags and All 2 Star Tags and above for Genres   |
| `anidb_1_5` | Use AniDB Main Tags and All 1.5 Star Tags and above for Genres |
| `anidb_1_0` | Use AniDB Main Tags and All 1 Star Tags and above for Genres   |
| `anidb_0_5` | Use AniDB Main Tags and All 0.5 Star Tags and above for Genres |
| `mal`       | Use MyAnimeList for Genres                                     |
| `lock`      | Lock Genre Field                                               |
| `unlock`    | Unlock Genre Field                                             |
| `remove`    | Remove all Genres and Lock Field                               |
| `reset`     | Remove all Genres and Unlock Field                             |

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

## Mass Studio Update

Updates every item's studio in the library to the chosen site's studio.

**Attribute:** `mass_studio_update`

**Values:**

| Value    | Description                            |
|:---------|:---------------------------------------|
| `anidb`  | Use AniDB Animation Work for Studio    |
| `mal`    | Use MyAnimeList Studio for Studio      |
| `tmdb`   | Use TMDb Studio for Studio             |
| `lock`   | Lock Original Title Field              |
| `unlock` | Unlock Original Title Field            |
| `remove` | Remove Original Title and Lock Field   |
| `reset`  | Remove Original Title and Unlock Field |

## Mass Originally Available Update

Updates every item's originally available date in the library to the chosen site's date.

**Attribute:** `mass_originally_available_update`

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

???+ warning "Important Note"
    
    This does not affect the icons displayed in the Plex UI.  This will place the number of your choice in the relevant field in the Plex database.  In other words, if Plex is configured to use Rotten Tomatoes ratings, then no matter what happens with this mass rating update operation, the icons in the Plex UI will remain Rotten Tomatoes.  The human who decided to put TMDB ratings in the critic slot and Letterboxd ratings in the audience slot is the only party who knows that the ratings are no longer Rotten Tomatoes.  One primary use of this feature is to put ratings overlays on posters.  More information on what PMM can do with these ratings can be found [here](../pmm/install/guides/ratings.md).

**Attribute:** `mass_audience_rating_update`/`mass_critic_rating_update`/`mass_user_rating_update`

**Values:**

| Value                  | Description                                         |
|:-----------------------|:----------------------------------------------------|
| `tmdb`                 | Use TMDb Rating                                     |
| `imdb`                 | Use IMDb Rating                                     |
| `trakt_user`           | Use Trakt User's Personal Rating                    |
| `omdb`                 | Use IMDbRating through OMDb                         |
| `mdb`                  | Use MdbList Score                                   |
| `mdb_average`          | Use MdbList Average Score                           |
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

???+ warning

    When used in combination with Overlays, this could cause PMM to reset the poster and then reapply all overlays on each run, which will result in [image bloat](../pmm/essentials/scripts/image-cleanup.md).


**Attribute:** `mass_poster_update`

**Values:** There are a few different options to determine how the `mass_poster_update` works.

| Attribute           | Description                                                                                         |
|:--------------------|:----------------------------------------------------------------------------------------------------|
| `source`            | Source of the poster update<br>**Values:** `tmdb`, `plex`, `lock`, or `unlock`                      |
| `seasons`           | Update season posters while updating shows<br>**Default:** `true`<br>**Values:** `true` or `false`  |
| `episodes`          | Update episode posters while updating shows<br>**Default:** `true`<br>**Values:** `true` or `false` |

**Example:**

```yaml
library:
  TV Shows:
    operations:
      mass_poster_update:
        source: tmdb
        seasons: false
        episodes: false
```

## Mass Background Update

Updates every item's background to the chosen sites background. Will fallback to `plex` if the given option fails. Assets will be used over anything else.

???+ warning

    When used in combination with Overlays, this could cause PMM to reset the background and then reapply all overlays on each run, which will result in [image bloat](../pmm/essentials/scripts/image-cleanup.md).

**Attribute:** `mass_background_update`

**Values:** There are a few different options to determine how the `mass_background_update` works.

| Attribute           | Description                                                                                             |
|:--------------------|:--------------------------------------------------------------------------------------------------------|
| `source`            | Source of the background update<br>**Values:** `tmdb`, `plex`, `lock`, or `unlock`                      |
| `seasons`           | Update season backgrounds while updating shows<br>**Default:** `true`<br>**Values:** `true` or `false`  |
| `episodes`          | Update episode backgrounds while updating shows<br>**Default:** `true`<br>**Values:** `true` or `false` |

**Example:**

```yaml
library:
  TV Shows:
    operations:
      mass_background_update:
        source: tmdb
        seasons: false
        episodes: false
```

## Mass IMDb Parental Labels

Updates every item's labels in the library to match the IMDb Parental Guide.

**Attribute:** `mass_imdb_parental_labels`

**Values:**

| Value      | Description                                                                       |
|:-----------|:----------------------------------------------------------------------------------|
| `none`     | Apply all Parental Labels with a value of `None`, `Mild`, `Moderate`, or `Severe` |
| `mild`     | Apply all Parental Labels with a value of `Mild`, `Moderate`, or `Severe`         |
| `moderate` | Apply all Parental Labels with a value of `Moderate` or `Severe`                  |
| `severe`   | Apply all Parental Labels with a value of `Severe`                                |

## Mass Collection Mode

Updates every Collection in your library to the specified Collection Mode.

**Attribute:** `mass_collection_mode`

**Values:**

| Value        | Description                        |
|:-------------|:-----------------------------------|
| `default`    | Library default                    |
| `hide`       | Hide Collection                    |
| `hide_items` | Hide Items in this Collection      |
| `show_items` | Show this Collection and its Items |

## Update Blank Track Titles

Search though every track in a music library and replace any blank track titles with the tracks sort title.

**Attribute:** `update_blank_track_titles`

**Values:** `true` or `false`

## Remove Title Parentheses

Search through every title and remove all ending parentheses in an items title if the title is not locked.

**Attribute:** `remove_title_parentheses`

**Values:** `true` or `false`

## Split Duplicates

Splits all duplicate movies/shows found in this library.

**Attribute:** `split_duplicates`

**Values:** `true` or `false`

## Radarr Add All

Adds every item in the library to Radarr. The existing paths in plex will be used as the root folder of each item, if the paths in Plex are not the same as your Radarr paths you can use the `plex_path` and `radarr_path` [Radarr](radarr.md) details to convert the paths.

**Attribute:** `radarr_add_all`

**Values:** `true` or `false`

## Radarr Remove By Tag

Removes every item from Radarr with the Tags given.

**Attribute:** `radarr_remove_by_tag`

**Values:** List or comma separated string of tags

## Sonarr Add All

Adds every item in the library to Sonarr. The existing paths in plex will be used as the root folder of each item, if the paths in Plex are not the same as your Sonarr paths you can use the `plex_path` and `sonarr_path` [Sonarr](sonarr.md) details to convert the paths.

**Attribute:** `sonarr_add_all`

**Values:** `true` or `false`

## Sonarr Remove By Tag

Removes every item from Sonarr with the Tags given.

**Attribute:** `sonarr_remove_by_tag`

**Values:** List or comma separated string of tags

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

Creates/Maintains a Plex Meta Manager [Metadata File](../metadata/metadata.md) with a full `metadata` mapping based on the library's items locked attributes.

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
