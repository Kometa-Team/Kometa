# Playlists

The `playlist` Default Collection File is used to create playlists based on popular Movie/TV Show universes (such as the
Marvel Cinematic Universe or Star Trek).

This Default file requires [Trakt Authentication](../config/trakt.md)

This file assumes that you have libraries named `Movies` and `TV Shows`. If you do not have these libraries or want to 
use alternative/additional libraries, use the `libraries` template variable which is outlined in the 
[Template Variables](#template-variables) table.

![](images/playlist.png)

## Playlists

| Playlist                                     | Key          | Description                                                                       |
|:---------------------------------------------|:-------------|:----------------------------------------------------------------------------------|
| `Arrowverse (Timeline Order)`                | `arrow`      | Playlist of Movies and Episodes in the Arrowverse (Timeline Order)                |
| `DC Animated Universe (Timeline Order)`      | `dcau`       | Playlist of Movies and Episodes in the DC Animated Universe (Timeline Order)      |
| `Dragon Ball (Timeline Order)`               | `dragonball` | Playlist of Movies and Episodes in the Dragon Ball (Timeline Order)               |
| `Marvel Cinematic Universe (Timeline Order)` | `mcu`        | Playlist of Movies and Episodes in the Marvel Cinematic Universe (Timeline Order) |
| `Pokémon (Timeline Order)`                   | `pokemon`    | Playlist of Movies and Episodes in the Pokémon (Timeline Order)                   |
| `Star Trek (Timeline Order)`                 | `startrek`   | Playlist of Movies and Episodes in the Star Trek (Timeline Order)                 |
| `Star Wars (Timeline Order)`                 | `starwars`   | Playlist of Movies and Episodes in the Star Wars (Timeline Order)                 |
| `Star Wars The Clone Wars (Timeline Order)`  | `clonewars`  | Playlist of Movies and Episodes in the Star Wars The Clone Wars (Timeline Order)  |
| `X-Men (Timeline Order)`                     | `xmen`       | Playlist of Movies and Episodes in the X-Men (Timeline Order)                     |

## Config

The below YAML in your config.yml will create the collections:

```yaml
playlist_files:
  - default: playlist
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this Kometa Defaults file.

    ???+ warning

        [Shared Collection Variables](collection_variables.md) are NOT available to this default file.

    === "File-Specific Template Variables"

    | Variable                                 | Description & Values                                                                                                                                                                                                                                                                      |
    |:-----------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | `use_<<key>>`<sup>1</sup>                | **Description:** Turns off individual Playlists in a Defaults file.<br>**Values:** `false` to turn off the playlist                                                                                                                                                                       |
    | `name_<<key>>`<sup>1</sup>               | **Description:** Changes the name of the specified key's playlist.<br>**Values:** New Playlist Name                                                                                                                                                                                       |
    | `summary_<<key>>`<sup>1</sup>            | **Description:** Changes the summary of the specified key's playlist.<br>**Values:** New Playlist Summary                                                                                                                                                                                 |
    | `libraries`                              | **Description:** Sets the names of the libraries to use for the Playlists.<br>**Default:** `Movies, TV Shows`<br>**Values:** Comma-separated string or list of library mapping names defined in the `libraries` attribute in the base of your [Configuration File](../config/overview.md. |
    | `sync_to_users`                           | **Description:** Sets the users to sync all playlists to.<br>**Default:** `playlist_sync_to_users` Global Setting Value<br>**Values:** Comma-separated string or list of user names.                                                                                                      |
    | `sync_to_users_<<key>>`<sup>1</sup>       | **Description:** Sets the users to sync the specified key's playlist to.<br>**Default:** `sync_to_user` Value<br>**Values:** Comma-separated string or list of user names.                                                                                                                |
    | `exclude_user`                           | **Description:** Sets the users to exclude from sync for all playlists.<br>**Default:** `playlist_sync_to_users` Global Setting Value<br>**Values:** Comma-separated string or list of user names.                                                                                        |
    | `exclude_user_<<key>>`<sup>1</sup>       | **Description:** Sets the users to exclude from sync the specified key's playlist.<br>**Default:** `sync_to_users` Value<br>**Values:** Comma-separated string or list of user names.                                                                                                      |
    | `trakt_list_<<key>>`<sup>1</sup>         | **Description:** Adds the Movies in the Trakt List to the specified key's playlist. Overrides the [default trakt_list] for that playlist if used.<br>**Values:** List of Trakt List URLs                                                                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
    | `delete_playlist`                        | **Description:** Will delete all playlists for the users defined by sync_to_users.<br>**Values:** `true` or `false`                                                                                                                                                                       |
    | `delete_playlist_<<key>>`<sup>1</sup>    | **Description:** Will delete the specified key's playlists for the users defined by sync_to_users.<br>**Values:** `true` or `false`                                                                                                                                                       |
    | `ignore_ids`                             | **Description:** Set a list or comma-separated string of TMDb/TVDb IDs to ignore in all playlists.<br>**Values:** List or comma-separated string of TMDb/TVDb IDs                                                                                                                         |
    | `ignore_imdb_ids`                        | **Description:** Set a list or comma-separated string of IMDb IDs to ignore in all playlists.<br>**Values:** List or comma-separated string of IMDb IDs                                                                                                                                   |
    | `url_poster_<<key>>`<sup>1</sup>         | **Description:** Changes the poster url of the specified key's playlist.<br>**Values:** URL directly to the Image                                                                                                                                                                         |
    | `radarr_add_missing`                     | **Description:** Override Radarr `add_missing` attribute for all playlists in a Defaults file.<br>**Values:** `true` or `false`                                                                                                                                                           |
    | `radarr_add_missing_<<key>>`<sup>1</sup> | **Description:** Override Radarr `add_missing` attribute of the specified key's playlist.<br>**Default:** `radarr_add_missing`<br>**Values:** `true` or `false`                                                                                                                           |
    | `radarr_folder`                          | **Description:** Override Radarr `root_folder_path` attribute for all playlists in a Defaults file.<br>**Values:** Folder Path                                                                                                                                                            |
    | `radarr_folder_<<key>>`<sup>1</sup>      | **Description:** Override Radarr `root_folder_path` attribute of the specified key's playlist.<br>**Default:** `radarr_folder`<br>**Values:** Folder Path                                                                                                                                 |
    | `radarr_tag`                             | **Description:** Override Radarr `tag` attribute for all playlists in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                              |
    | `radarr_tag_<<key>>`<sup>1</sup>         | **Description:** Override Radarr `tag` attribute of the specified key's playlist.<br>**Default:** `radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                      |
    | `item_radarr_tag`                        | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr for all playlists in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                        |
    | `item_radarr_tag_<<key>>`<sup>1</sup>    | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr of the specified key's playlist.<br>**Default:** `item_radarr_tag`<br>**Values:** List or comma-separated string of tags                                                           |
    | `sonarr_add_missing`                     | **Description:** Override Sonarr `add_missing` attribute for all playlists in a Defaults file.<br>**Values:** `true` or `false`                                                                                                                                                           |
    | `sonarr_add_missing_<<key>>`<sup>1</sup> | **Description:** Override Sonarr `add_missing` attribute of the specified key's playlist.<br>**Default:** `sonarr_add_missing`<br>**Values:** `true` or `false`                                                                                                                           |
    | `sonarr_folder`                          | **Description:** Override Sonarr `root_folder_path` attribute for all playlists in a Defaults file.<br>**Values:** Folder Path                                                                                                                                                            |
    | `sonarr_folder_<<key>>`<sup>1</sup>      | **Description:** Override Sonarr `root_folder_path` attribute of the specified key's playlist.<br>**Default:** `sonarr_folder`<br>**Values:** Folder Path                                                                                                                                 |
    | `sonarr_tag`                             | **Description:** Override Sonarr `tag` attribute for all playlists in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                              |
    | `sonarr_tag_<<key>>`<sup>1</sup>         | **Description:** Override Sonarr `tag` attribute of the specified key's playlist.<br>**Default:** `sonarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                      |
    | `item_sonarr_tag`                        | **Description:** Used to append a tag in Sonarr for every series found by the builders that's in Sonarr for all playlists in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                       |
    | `item_sonarr_tag_<<key>>`<sup>1</sup>    | **Description:** Used to append a tag in Sonarr for every series found by the builders that's in Sonarr of the specified key's playlist.<br>**Default:** `item_sonarr_tag`<br>**Values:** List or comma-separated string of tags                                                          |
    
    1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    Click the :fontawesome-solid-circle-plus: icon to learn more
    
    ```yaml
    playlist_files:
      - default: playlist
        template_variables:
          radarr_add_missing: true #(1)!
    ```

    1.  Adds items from the source list which are not in Plex to Radarr

## Default Values

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not 
show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default Template Variable `trakt_list` (click to expand) <a class="headerlink" href="#trakt-list" title="Permanent link">¶</a>"

    <div id="trakt-list" />

    ???+ tip 
    
        Pass `trakt_list_<<key>>` to the file as template variables to change this value per playlist.

    ```yaml
    {%
      include-markdown "../../defaults/playlist.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="conditions:"
      end="default:"
    %}
    ```