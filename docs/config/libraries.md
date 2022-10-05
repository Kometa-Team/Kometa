# Library & Playlist Files Attributes

## Library Attributes

Within the [Configuration File](configuration), the `libraries:` attribute specifies the Plex libraries that the user wants Plex Meta Manager to act on.

Attributes are used to instruct Plex Meta Manager what actions to take, such as "load the following libraries" or "execute the following Collection Definition files". These attributes can be specified individually per library, or can be inherited from the global value if it has been set. If an attribute is specified at both the library and global level, then the library level attribute will take priority.

### Example

This example is an advanced version of the library mappings which highlights some attributes being set at the global level, and some being set at the library level:

<details>
  <summary>Click to Expand</summary>
  <br />

In this example, the `"TV Shows On Second Plex"` library has a library-level `plex` configuration, which takes priority over the `plex` configuration set at the global level. <br>

The `"Anime"` library also has a library-level `radarr` configuration, which takes priority over the `radarr` configuration set at the global level.

```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
      - pmm: imdb
      - pmm: studio
      - pmm: genre
      - pmm: actor
    operations:
      mass_critic_rating_update: tmdb
      split_duplicates: true
  TV Shows:
    metadata_path:
      - file: config/TV Shows.yml
      - pmm: tmdb
      - pmm: network
    overlay_path:
      - remove_overlays: false
      - file: config/Overlays.yml
  TV Shows On Second Plex:
    library_name: TV Shows
    plex:
      url: http://192.168.1.98:32400
      token: ####################
    metadata_path:
      - file: config/TV Shows.yml
      - pmm: tmdb
      - pmm: network
  Anime:
    metadata_path:
      - file: config/Anime.yml
      - pmm: myanimelist
    radarr:
      url: http://192.168.1.45:7878
      token: ################################
      root_folder_path: S:/Anime
    settings:
      asset_directory:
        config/assets/anime
plex:
  url: http://192.168.1.12:32400
  token: ####################
radarr:
  url: http://192.168.1.12:7878
  token: ################################
  add: true
  root_folder_path: S:/Movies
  monitor: true
  availability: announced
  quality_profile: HD-1080p
  tag: pmm
  search: false
```
</details>

### Attributes

The available attributes for each library are as follows:

| Attribute                                   | Values                                                                                                |                Default                |            Required             |
|:--------------------------------------------|:------------------------------------------------------------------------------------------------------|:-------------------------------------:|:-------------------------------:|
| [`library_name`](#library-name)             | Library name (required only when trying to use multiple libraries with the same name)                 |          Base Attribute Name          |            &#10060;             |
| [`metadata_path`](#metadata-path)           | Location of Metadata YAML files                                                                       |    `/config/<<MAPPING_NAME>>.yml`     |            &#10060;             |
| [`overlay_path`](#overlay-path)             | Location of Overlay YAML files                                                                        |                 None                  |            &#10060;             |
| [`report_path`](#report-path)               | Location to create the YAML file listing added, removed, filtered, and missing items for this library | `/config/<<MAPPING_NAME>>_report.yml` |            &#10060;             |
| [`template_variables`](#template-variables) | Library template variables to be applied to every Metadata and Overlay file run.                      |                  N/A                  |            &#10060;             |
| [`schedule`](../metadata/details/schedule)  | Use any [schedule option](../metadata/details/schedule) to control when this library is run.          |                 daily                 |            &#10060;             |
| [`operations`](operations)                  | Library Operations to run                                                                             |                  N/A                  |            &#10060;             |
| [`settings`](settings)                      | Any `setting` attribute that overrides a global value                                                 |                global                 |            &#10060;             |
| [`plex`](plex)                              | Any `plex` attribute that overrides a global value                                                    |                global                 | &#9989; Either here or globally |
| [`radarr`](radarr)                          | Any `radarr` attribute that overrides a global value                                                  |                global                 |            &#10060;             |
| [`sonarr`](sonarr)                          | Any `sonarr` attribute that overrides a global value                                                  |                global                 |            &#10060;             |
| [`tautulli`](tautulli)                      | Any `tautulli` attribute that overrides a global value                                                |                global                 |            &#10060;             |

### Library Name

Each library that the user wants Plex Meta Manager to interact with must be documented with a library attribute. A library attribute is represented by the mapping name (i.e. `Movies` or `TV Shows`), this must have a unique name that correlates with a library of the same name within the Plex Media Server. In the situation that two servers are being connected to which both have libraries of the same name, the `library_name` attribute can be utilized to specify the real Library Name, whilst the library attribute's mapping name can be made into a placeholder. This is showcased below:
<details>
  <summary>Click to Expand</summary>
  <br />

```yaml
libraries:
  Movies01:
    library_name: Movies
  Movies02:
    library_name: Movies
    plex:
      url: http://192.168.1.35:32400
      token: ####################
  TV Shows:
  Anime:
plex:
  url: http://192.168.1.12:32400
  token: ####################
```

* In this example, `"Movies01"`, `"TV Shows"`, and `"Anime"` will all use the global plex server (http://192.168.1.12:32400) which is defined using the global `plex` mapping. `"Movies02"` will use the plex server http://192.168.1.35:32400 which is defined under its `plex` mapping over the global mapping.
</details>

### Metadata Path

The `metadata_path` attribute is used to define [Metadata Files](../metadata/metadata) by specifying the path type and path of the files that will be executed against the parent library. See [Path Types](paths) for how to define them.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - file: config/TV Shows.yml
      - pmm: tmdb
      - pmm: network
```

By default, when `metadata_path` is missing the script will look within the root PMM directory for a metadata file called `<MAPPING_NAME>.yml`. In this example, Plex Meta Manager will look for a file named `TV Shows.yml`.

```yaml
libraries:
  TV Shows:
```

### Overlay Path

The `overlay_path` attribute is used to define [Overlay Files](../metadata/overlay) by specifying the path type and path of the files that will be executed against the parent library. See [Path Types](paths) for how to define them.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - file: config/TV Shows.yml
    overlay_path:
      - file: config/Overlays.yml
```

#### Remove Overlays

You can remove overlays from a library by adding `remove_overlays: true` to `overlay_path`. This will remove all overlays when run and not generate new ones.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - file: config/TV Shows.yml
    overlay_path:
      - remove_overlays: true
      - file: config/Overlays.yml
```

#### Reapply Overlays

You can reapply overlays from a library by adding `reapply_overlays: true` to `overlay_path`. This will reapply overlays to every item in your library.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - file: config/TV Shows.yml
    overlay_path:
      - reapply_overlays: true
      - file: config/Overlays.yml
```

#### Reset Overlays

You can reset overlays from a library by adding `reset_overlays` to `overlay_path` and setting it to either `tmdb` or `plex` depending on where you want to source the images from. This will use the reset image when overlaying items in your library.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - file: config/TV Shows.yml
    overlay_path:
      - reset_overlays: plex
      - file: config/Overlays.yml
```

### Report Path

The `report_path` attribute is used to define where to save the YAML Report file. This file is used to store information about what media is added, removed, filtered, and missing from the Plex library compared to what is expected from the Metadata file.

If your Metadata file creates a collection with `Movie 1`, `Movie 2` and `Movie 3` but your Plex library only has `Movie 1` and `Movie 3`, then the missing YAML file will be updated to inform the user that `Movie 2` was missing from the library.

The default and recommended path is `/config/<<MAPPING_NAME>>report.yml` where `<<MAPPING_NAME>>` is the name of the library attribute, as showcased below:

```yaml
libraries:
  Movies:
    report_path: /config/Movies_report.yml
```

Alternatively, Report YAML files can be placed in their own directory, as below:

```yaml
libraries:
  Movies:
    report_path: /config/reports/Movies.yml
```

### Template Variables

Library template variables to be applied to every Metadata and Overlay file run.

```yaml
libraries:
  Movies:
    template_variables:
      collection_mode: true
```

## Playlist Files Attribute

As playlists are not tied to one specific library and can combine media from multiple libraries, they require their own special [Playlist Files](../metadata/metadata) to work.

You can define Playlist Files by using `playlist_files` mapper by specifying the path type and path of the files that will be executed. See [Path Types](paths) for how to define them.

```yaml
playlist_files:
  - file: config/playlists.yml
  - pmm: playlist
```
