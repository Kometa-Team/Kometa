# Radarr Attributes

Configuring [Radarr](https://radarr.video/) is optional but will allow you to send movies to a Radarr instance when they're found missing while updating a library's collections.

Radarr V2 may work, but it is not supported please upgrade to V3 if you can.

Items in your List Exclusions will be ignored by PMM.

A `radarr` mapping can be either in the root of the config file as global mapping for all libraries, or you can specify the `radarr` mapping individually per library.

At the library level, only those settings which are different to the global settings need to be specified; there is an example of this at the end of the page.

Below is a `radarr` mapping example and the full set of attributes:
```yaml
radarr:
  url: http://192.168.1.12:32788
  token: ################################
  add_missing: false
  add_existing: false
  upgrade_existing: false
  root_folder_path: S:/Movies
  monitor: movie
  availability: announced
  quality_profile: HD-1080p
  tag: pmm
  search: false
  radarr_path: /media
  plex_path: /share/CACHEDEV1_DATA/Multimedia
```

| Attribute          | Allowed Values                                                                                                                                                                                                                                                                                                     | Default     | Required |
|:-------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------|:--------:|
| `url`              | Radarr URL (Including URL Base if set).<br>**Example:** http://192.168.1.12:32788                                                                                                                                                                                                                                  | N/A         | &#9989;  |
| `token`            | Radarr API Token.                                                                                                                                                                                                                                                                                                  | N/A         | &#9989;  |
| `add_missing`      | Adds all missing movies found from all collections to Radarr.<br>Use the `radarr_add_missing` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to add missing per collection.<br>**boolean:** true or false                                                    | false       | &#10060; |
| `add_existing`     | Adds all existing movies in collections to Radarr.<br>Use the `radarr_add_existing` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to add existing per collection.<br>**boolean:** true or false                                                             | false       | &#10060; |
| `upgrade_existing` | Upgrades all existing movies in collections to match the Quality Profile of the collection.<br>Use the `radarr_upgrade_existing` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to upgrade the Quality Profile per collection.<br>**boolean:** true or false | false       | &#10060; |
| `ignore_cache`     | Ignores PMM's cache when adding items to Radarr.<br>Use the `radarr_ignore_cache` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to ignore per collection.<br>**boolean:** true or false                                                                     | false       | &#10060; |
| `root_folder_path` | Default Root Folder Path to use when adding new movies.<br>Use the `radarr_folder` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to set the Root Folder per collection.                                                                                     | N/A         | &#9989;  |
| `monitor`          | Monitor the movie when adding new movies.<br>Use the `radarr_monitor` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to set the Monitor value per collection.<br>**Options:** `movie`, `collection`, `none`                                                  | true        | &#10060; |
| `availability`     | Default Minimum Availability to use when adding new movies.<br>Use the `radarr_availability` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to set the Availability per collection.<br>**Options:** `announced`, `cinemas`, `released`, `db`                 | `announced` | &#9989;  |
| `quality_profile`  | Default Quality Profile to use when adding new movies.<br>Use the `radarr_quality` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to set the Quality Profile per collection.                                                                                 | N/A         | &#9989;  |
| `tag`              | Default list or comma-separated string of tags to use when adding new movies.<br>Use the `radarr_tag` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to set the Tags per collection.                                                                         | ` `         | &#10060; |
| `search`           | Start search for missing movie when adding new movies.<br>Use the `radarr_search` [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition to set the search value per collection.<br>**boolean:** true or false                                                       | false       | &#10060; |
| `plex_path`        | When using `add_existing` or `radarr_add_all` Convert this part of the path to `radarr_path`.                                                                                                                                                                                                                      | ` `         | &#10060; |
| `radarr_path`      | When using `add_existing` or `radarr_add_all` Convert the `plex_path` part of the path to this.                                                                                                                                                                                                                    | ` `         | &#10060; |

* The `token` can be found by going to `Radarr > Settings > General > Security > API Key`

* The `quality_profile` must be the exact name of the desired quality profile, including all spaces and capitalization.

* You can set most attributes per collection by using the [Radarr Details](../metadata/details/arr.md#radarr-definition-settings) in the collection definition.

![Radarr Details](radarr.png)

Based on that UI, the settings would be [settings not based on things in this image are shown as `#`]:

```yaml
radarr:
  url: #
  token: #
  add_missing: #
  add_existing: #
  upgrade_existing: #
  root_folder_path: /movies
  monitor: movie
  availability: announced
  quality_profile: HD-1080p
  tag: 
  search: true
  radarr_path: #
  plex_path: #
```

# Other examples:

Specifying different options for specific libraries:

In this example we have two Radarr instances, standard and 4K, and four libraries showing how one can override individual settings at the library level.  Also, movies are being added to the "Library05" library outside Radarr via a custom script and I want those new movies added to Radarr for tracking.


```
libraries:
  Library01:     # this library uses the default radarr config
    metadata_path:
      - file: config/Movies.yml

  Library02:     # this library overrides radarr root path and profile
    metadata_path:
      - file: config/Movies.yml
    radarr:
      root_folder_path: /data/media/movies/tony
      quality_profile: Better

  Library03:      # this library overrides radarr quality profile
    metadata_path:
      - file: config/Movies.yml
    radarr:
      quality_profile: Best

  Library04:      # this library uses the 4K radarr instance
    metadata_path:
      - file: config/Movies.yml
    radarr:
      url: https://radarr-4k.bing.bang
      token: SOME_OTHER_TOKEN
      root_folder_path: /data/media/movies/geezer
      quality_profile: Bestest

  Library05:      # movies get added by a custom script so they should get added to radarr-4k
    metadata_path:
      - file: config/Movies.yml
    radarr:
      url: https://radarr-4k.bing.bang
      token: SOME_OTHER_TOKEN
      root_folder_path: /data/media/movies/bill
      quality_profile: Bestest
      add_existing: true
      sonarr_path: /data/media/movies/bill
      plex_path: /mnt/unionfs/movies/bill
...
radarr:
  url: https://radarr.bing.bang
  token: SOME_TOKEN
  quality_profile: Good
  add_missing: true
  add_existing: false
  upgrade_existing: false
  root_folder_path: /movies
  monitor: movie
  availability: released
  tag:
  search: false
  radarr_path:
  plex_path:
...
```
