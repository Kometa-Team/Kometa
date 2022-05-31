# Configuration File

Plex Meta Manager uses a YAML configuration file; this file contains settings that determine how Plex Meta Manager behaves, and the required connection details needed to connect to Plex Media Server, Radarr, Sonarr, and other third-party services via API.

By default, and unless otherwise stated, Plex Meta Manager looks for the configuration file within `/config/config.yml`

A template Configuration File can be found in the [GitHub Repo](https://github.com/meisnate12/Plex-Meta-Manager/blob/master/config/config.yml.template).

This table outlines the third-party services that Plex Meta Manager can make use of. Each service has specific requirements for setup that can be found by clicking the links within the table.

| Attribute                                                 |                Required                 |
|:----------------------------------------------------------|:---------------------------------------:|
| [`libraries`](libraries)                                  |                 &#9989;                 |
| [`playlist_files`](libraries.md#playlist-files-attribute) |                &#10060;                 |
| [`settings`](settings)                                    |                &#10060;                 |
| [`webhooks`](webhooks)                                    |                &#10060;                 |
| [`plex`](plex)                                            | &#9989; <br/>Either here or per library |
| [`tmdb`](tmdb)                                            |                 &#9989;                 |
| [`tautulli`](tautulli)                                    |                &#10060;                 |
| [`omdb`](omdb)                                            |                &#10060;                 |
| [`notifiarr`](notifiarr)                                  |                &#10060;                 |
| [`anidb`](anidb)                                          |                &#10060;                 |
| [`radarr`](radarr)                                        |                &#10060;                 |
| [`sonarr`](sonarr)                                        |                &#10060;                 |
| [`trakt`](trakt)                                          |                &#10060;                 |
| [`mal`](myanimelist)                                      |                &#10060;                 |

# Configuration File Walkthrough

This example outlines what a "standard" config.yml file might look like when in use.

<details>
  <summary>Example config.yml file</summary>
  <br />

```yaml
libraries:                                      # This is called out once within the config.yml file                                       
  Movies:                                       # Each library must match the Plex library name
    metadata_path:
      - file: config/Movies.yml                 # This is a local file on the system
      - folder: config/Movies/                  # This is a local directory on the system
      - git: PMM/chart/basic                    # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
      - git: PMM/chart/imdb                     # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
    overlay_path:
      - remove_overlays: false                  # Set this to true to remove all overlays
      - file: config/Overlays.yml               # This is a local file on the system
      - git: PMM/overlays/imdb_top_250          # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
  TV Shows:                           
    metadata_path:
      - file: config/TVShows.yml
      - folder: config/TV Shows/
      - git: PMM/chart/basic                    # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
      - git: PMM/chart/imdb                     # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
    overlay_path:
      - remove_overlays: false                  # Set this to true to remove all overlays
      - file: config/Overlays.yml               # This is a local file on the system
      - git: PMM/overlays/imdb_top_250          # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
  Anime:
    metadata_path:
      - file: config/Anime.yml
      - git: PMM/chart/basic                    # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
      - git: PMM/chart/anilist                  # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
  Music:
    metadata_path:
      - file: config/Music.yml
playlist_files:
  - file: config/playlists.yml       
  - git: PMM/playlist                           # This is a file within the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
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

## Library Mappings (`libraries:`)

`libraries:` is used to tell PMM that the following code relates to Plex libraries. `libraries:` should only be seen once within the configuration file.

In this specific example there are four Plex libraries that are being connected to: `Movies - 4K`, `TV Shows`, `Animé` and `Music`. These names **must**  match the name of the library as it appears within Plex, including any special characters such as the é within `Animé`.

Using `Movies - 4K:` as an example, `metadata_path:` instructs PMM that the next piece of code is where to look for the [Metadata Files](../../metadata/metadata) which will be covered in the next section.
<br/>
<br/>

## Metadata/YAML files (`metadata_path:` mappings)
As can be seen in the original config.yml example, there are three metadata_paths being pointed to for the TV Shows library:
```yaml
  TV Shows:
    metadata_path:
      - file: config/TVShows.yml
      - folder: config/TV Shows/
      - git: PMM/chart/basic
      - git: PMM/chart/imdb
```

These path types are outlined as follows:
* `- file:` refers to a YAML file which is located within the system that PMM is being run from. 

* `- folder:` refers to a directory containing YAML files which is located within the system that PMM is being run from. 

* `- git:` refers to a YAML file which is hosted on the [GitHub Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs) unless the user has specified a custom repository within the settings section of the config.yml file.

Within the above example, PMM will:
* First, look within the root of the PMM directory (also known as `config/`) for a metadata file named `TVShows.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.

* Then, look within the root of the PMM directory (also known as `config/`) for a directory called `TV Shows`, and then load any metadata/YAML files within that directory.

* After that, look at the [PMM/chart folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM/chart) within the GitHub Configs Repo for a file called `basic.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/PMM/chart/basic.yml).

* Finally, look at the [PMM/chart folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM/chart) within the GitHub Configs Repo for a file called `imdb.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/PMM/chart/imdb.yml).

It should be noted that whilst the user should be able to edit any metadata files which are `- file:` or `- folder:` based, they have little to no control over `- git:` metadata files **unless a copy of the YAML file is downloaded and ran locally**. In the above example, if the user downloaded the [basic.yml file](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/PMM/chart/basic.yml) from the [GitHub Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs) and placed it in the root directory of PMM (`config/`), then the metadata_path mapping would be updated to reflect this as follows:
```yaml
  TV Shows:
    metadata_path:
      - file: config/TVShows.yml
      - folder: config/TV Shows/
      - file: PMM/chart/basic        # <------ HERE
      - git: PMM/chart/imdb
```

## Playlists (`playlist_files:` mappings)

Playlists can be seen as an extension of Libraries in that they are both handled very similarly within PMM:
```yaml
playlist_files:
  - file: config/playlists.yml
  - git: PMM/playlists
```  

As with `libraries:`, YAML files are defined to create the Playlists. It should be noted that whilst in `libraries:` when working with `playlist_files:` you call out the libraries being connected to within the Metadata/YAML file as Playlists can combine media from multiple libraries. You can view an example playlists.yml file as follows:

<details>
  <summary>Example playlists.yml file</summary>
  <br />

```yaml
playlists:
  Marvel Cinematic Universe:
    sync_to_users: all
    sync_mode: sync
    libraries: Movies, TV Shows
    trakt_list: https://trakt.tv/users/donxy/lists/marvel-cinematic-universe?sort=rank,asc
    summary: Marvel Cinematic Universe In Order
  Star Wars Clone Wars Chronological Order:
    sync_to_users: all
    sync_mode: sync
    libraries: Movies, TV Shows
    trakt_list: https://trakt.tv/users/tomfin46/lists/star-wars-the-clone-wars-chronological-episode-order
```
</details>

As can be seen in the above examples, multiple libraries are being used to combine different types of media (movies and tv shows in this case) into one playlist.