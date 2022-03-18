# Radarr Attributes

Configuring [Radarr](https://radarr.video/) is optional but will allow you to send movies to a Radarr instance when they're found missing while updating a library's collections. 

Radarr V2 may work, but it is not supported please upgrade to V3 if you can.

A `radarr` mapping can be either in the root of the config file as global mapping for all libraries, or you can specify the `radarr` mapping individually per library.

Below is a `radarr` mapping example and the full set of attributes:
```yaml
radarr:
  url: http://192.168.1.12:32788
  token: ################################
  add_missing: false
  add_existing: false
  root_folder_path: S:/Movies
  monitor: true
  availability: announced
  quality_profile: HD-1080p
  tag: pmm
  search: false
  radarr_path: /media
  plex_path: /share/CACHEDEV1_DATA/Multimedia
```

| Attribute          | Allowed Values                                                                                                                                                                                                                                                                      |   Default   | Required |
|:-------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------:|:--------:|
| `url`              | Radarr URL (Including URL Base if set).<br>**Example:** http://192.168.1.12:32788                                                                                                                                                                                                   |     N/A     | &#9989;  |
| `token`            | Radarr API Token.                                                                                                                                                                                                                                                                   |     N/A     | &#9989;  |
| `add_missing`      | Adds all missing movies found from all collections to Radarr.<br>Use the `radarr_add_missing` [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition to add missing per collection.<br>**boolean:** true or false                                    |    false    | &#10060; |
| `add_existing`     | Adds all existing movies in collections to Radarr.<br>Use the `radarr_add_existing` [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition to add existing per collection.<br>**boolean:** true or false                                             |    false    | &#10060; |
| `root_folder_path` | Default Root Folder Path to use when adding new movies.<br>Use the `radarr_folder` [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition to set the Root Folder per collection.                                                                     |     N/A     | &#9989;  |
| `monitor`          | Monitor the movie when adding new movies.<br>Use the `radarr_monitor` [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition to set the Monitor value per collection.                                                                                |    true     | &#10060; |
| `availability`     | Default Minimum Availability to use when adding new movies.<br>Use the `radarr_availability` [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition to set the Availability per collection.<br>**Options:** `announced`, `cinemas`, `released`, `db` | `announced` | &#9989;  |
| `quality_profile`  | Default Quality Profile to use when adding new movies.<br>Use the `radarr_quality` [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition to set the Quality Profile per collection.                                                                 |     N/A     | &#10060; |
| `tag`              | Default this list or comma-separated string of tags to use when adding new movies.<br>Use the `radarr_tag` [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition to set the Tags per collection.                                                    |     ` `     | &#10060; |
| `search`           | Start search for missing movie when adding new movies.<br>Use the `radarr_search` [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition to set the search value per collection.<br>**boolean:** true or false                                       |    false    | &#10060; |
| `plex_path`        | When using `add_existing` or `radarr_add_all` Convert this part of the path to `radarr_path`.                                                                                                                                                                                       |     ` `     | &#10060; |
| `radarr_path`      | When using `add_existing` or `radarr_add_all` Convert the `plex_path` part of the path to this.                                                                                                                                                                                     |     ` `     | &#10060; |

* The `token` can be found by going to `Radarr > Settings > General > Security > API Key`

* The `quality_profile` must be the exact name of the desired quality profile, including all spaces and capitalization.

* You can set most attributes per collection by using the [Radarr Details](../metadata/details/arr.md#radarr-details) in the collection definition.

![Radarr Details](radarr.png)
