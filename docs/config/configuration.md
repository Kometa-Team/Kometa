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

```yaml
## This file is a template remove the .template to use the file

libraries:                       # This is called out once within the config.yml file
  Movies:                        # These are names of libraries in your Plex
    metadata_path:
      - pmm: basic               # This is a file within PMM's defaults folder
      - pmm: imdb                # This is a file within PMM's defaults folder
      # see the wiki for how to use local files, folders, URLs, or files from git
    overlay_path:
      - remove_overlays: false   # Set this to true to remove all overlays
      - pmm: ribbon              # This is a file within PMM's defaults folder
      # see the wiki for how to use local files, folders, URLs, or files from git
  TV Shows:
    metadata_path:
      - pmm: basic               # This is a file within PMM's defaults folder
      - pmm: imdb                # This is a file within PMM's defaults folder
      # see the wiki for how to use local files, folders, URLs, or files from git
    overlay_path:
      - remove_overlays: false   # Set this to true to remove all overlays
      - pmm: ribbon              # This is a file within PMM's defaults folder
      # see the wiki for how to use local files, folders, URLs, or files from git
  Anime:
    metadata_path:
      - pmm: basic               # This is a file within PMM's defaults folder
      - pmm: anilist             # This is a file within PMM's defaults folder
      # see the wiki for how to use local files, folders, URLs, or files from git
  Music:
    metadata_path:
      - file: config/Music.yml   # This is a local file THAT YOU MIGHT CREATE
playlist_files:
  - pmm: playlist                # This is a file within PMM's defaults folder
  # see the wiki for how to use local files, folders, URLs, or files from git
settings:
  cache: true
  cache_expiration: 60
  asset_directory: config/assets
  asset_folders: true
  asset_depth: 0
  create_asset_folders: false
  prioritize_assets: false
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
  save_report: false
  tvdb_language: eng
  ignore_ids:
  ignore_imdb_ids:
  item_refresh_delay: 0
  playlist_sync_to_user: all
  playlist_exclude_user: 
  playlist_report: false
  verify_ssl: true
  custom_repo:
  check_nightly: false
webhooks:                        # Can be individually specified per library as well
  error:
  version:
  run_start:
  run_end:
  changes:
plex:                            # Can be individually specified per library as well; REQUIRED for the script to run
  url: http://192.168.1.12:32400
  token: ####################
  timeout: 60
  clean_bundles: false
  empty_trash: false
  optimize: false
tmdb:                            # REQUIRED for the script to run
  apikey: ################################
  language: en
tautulli:                        # Can be individually specified per library as well
  url: http://192.168.1.12:8181
  apikey: ################################
omdb:
  apikey: ########
  cache_expiration: 60
mdblist:
  apikey: #########################
  cache_expiration: 60
notifiarr:
  apikey: ####################################
anidb:                           # Not required for AniDB builders unless you want mature content
  username: ######
  password: ######
radarr:                          # Can be individually specified per library as well
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
sonarr:                          # Can be individually specified per library as well
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
  client_id: ####################
  client_secret: ####################
  pin:
  authorization:
    # everything below is autofilled by the script
    access_token:
    token_type:
    expires_in:
    refresh_token:
    scope: public
    created_at:
mal:
  client_id: ####################
  client_secret: ####################
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
