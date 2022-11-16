# Config File

Plex Meta Manager uses a YAML configuration file; this file contains settings that determine how Plex Meta Manager behaves, and the required connection details needed to connect to Plex Media Server, Radarr, Sonarr, and other third-party services via API.

By default, and unless otherwise stated, Plex Meta Manager looks for the configuration file at `/config/config.yml`.

A template Configuration File can be found in the [GitHub Repo](https://github.com/meisnate12/Plex-Meta-Manager/blob/master/config/config.yml.template).

This table outlines the third-party services that Plex Meta Manager can make use of. Each service has specific requirements for setup that can be found by clicking the links within the table.

| Attribute                     | Required                                |
|:------------------------------|:----------------------------------------|
| [`libraries`](libraries)      | &#9989;                                 |
| [`playlist_files`](playlists) | &#10060;                                |
| [`settings`](settings)        | &#10060;                                |
| [`webhooks`](webhooks)        | &#10060;                                |
| [`plex`](plex)                | &#9989; <br/>Either here or per library |
| [`tmdb`](tmdb)                | &#9989;                                 |
| [`tautulli`](tautulli)        | &#10060;                                |
| [`omdb`](omdb)                | &#10060;                                |
| [`notifiarr`](notifiarr)      | &#10060;                                |
| [`anidb`](anidb)              | &#10060;                                |
| [`radarr`](radarr)            | &#10060;                                |
| [`sonarr`](sonarr)            | &#10060;                                |
| [`trakt`](trakt)              | &#10060;                                |
| [`mal`](myanimelist)          | &#10060;                                |

## Configuration File Example

This example outlines what a "standard" config.yml file might look like when in use.

<details>
  <summary>Example config.yml file</summary>
  <br />

```yaml
libraries:                          # This is called out once within the config.yml file                                       
  Movies:                           # Each library must match the Plex library name
    metadata_path:
      - file: config/Movies.yml     # This is a local file on the system
      - folder: config/Movies/      # This is a local directory on the system
      - pmm: basic                  # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
      - pmm: imdb                   # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
    overlay_path:
      - remove_overlays: false      # Set this to true to remove all overlays
      - file: config/Overlays.yml   # This is a local file on the system
      - pmm: ribbon                 # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
  TV Shows:                           
    metadata_path:
      - file: config/TVShows.yml
      - folder: config/TV Shows/
      - pmm: basic                  # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
      - pmm: imdb                   # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
    overlay_path:
      - remove_overlays: false      # Set this to true to remove all overlays
      - file: config/Overlays.yml   # This is a local file on the system
      - pmm: ribbon                 # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
  Anime:
    metadata_path:
      - file: config/Anime.yml
      - pmm: basic                  # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
      - pmm: anilist                # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
  Music:
    metadata_path:
      - file: config/Music.yml
playlist_files:
  - file: config/playlists.yml       
  - pmm: playlist                   # This is a local PMM Default file. Usage Guide: https://metamanager.wiki/en/nightly/defaults/guide.html
settings:
  cache: true
  cache_expiration: 60
  asset_directory: config/assets
  asset_folders: true
  asset_depth: 0
  create_asset_folders: false
  dimensional_asset_rename: false
  download_url_assets: false
  show_missing_season_assets: false
  show_missing_episode_assets: false
  show_asset_not_needed: true
  sync_mode: append
  minimum_items: 1
  default_collection_order:
  delete_below_minimum: true
  delete_not_scheduled: false
  run_again_delay: 2
  missing_only_released: false
  only_filter_missing: false
  show_unmanaged: true
  show_filtered: false
  show_options: false
  show_missing: true
  show_missing_assets: true
  save_report: true
  tvdb_language: eng
  ignore_ids:
  ignore_imdb_ids:
  item_refresh_delay: 0
  playlist_sync_to_users: all
  verify_ssl: true
webhooks:
  error:
  run_start:
  run_end:
  changes:
    version:
plex:
  url: http://192.168.1.12:32400
  token: ####################
  timeout: 60
  clean_bundles: false
  empty_trash: false
  optimize: false
tmdb:
  apikey: ################################
  language: en
tautulli:
  url: http://192.168.1.12:8181
  apikey: ################################
omdb:
  apikey: ########
notifiarr:
  apikey: ####################################
anidb:
  username: ######
  password: ######
radarr:
  url: http://192.168.1.12:7878
  token: ################################
  add_missing: false
  add_existing: false
  root_folder_path: S:/Movies
  monitor: true
  availability: announced
  quality_profile: HD-1080p
  tag:
  search: false
  radarr_path:
  plex_path:
sonarr:
  url: http://192.168.1.12:8989
  token: ################################
  add_missing: false
  add_existing: false
  root_folder_path: "S:/TV Shows"
  monitor: all
  quality_profile: HD-1080p
  language_profile: English
  series_type: standard
  season_folder: true
  tag:
  search: false
  cutoff_search: false
  sonarr_path:
  plex_path:
trakt:
  client_id: ################################################################
  client_secret: ################################################################
  authorization:
    # everything below is autofilled by the script
    access_token:
    token_type:
    expires_in:
    refresh_token:
    scope: public
    created_at:
mal:
  client_id: ################################
  client_secret: ################################################################
  authorization:
    # everything below is autofilled by the script
    access_token:
    token_type:
    expires_in:
    refresh_token:
```
</details>

**Expand the above to see the full config.yml file before continuing.**
<br/>
