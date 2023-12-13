---
search:
  boost: 5 
---

# Library Attributes

## Library Attributes

Within the [Configuration File](configuration.md), the `libraries` attribute specifies the Plex libraries that the user wants Plex Meta Manager to act on.

Attributes are used to instruct Plex Meta Manager what actions to take, such as "load the following libraries" or "execute the following Collection Definition files". These attributes can be specified individually per library, or can be inherited from the global value if it has been set. If an attribute is specified at both the library and global level, then the library level attribute will take priority.

### Example

This example is an advanced version of the library mappings which highlights some attributes being set at the global level, and some being set at the library level:

???+ example "Example Library Mappings"

    In this example, the `"TV Shows On Second Plex"` library has a library-level `plex` configuration, which takes priority over the `plex` configuration set at the global level.
    
    The `"Anime"` library also has a library-level `radarr` configuration, which takes priority over the `radarr` configuration set at the global level.

    ```yaml
    libraries:
      Movies:
        collection_files:
          - file: config/Movies.yml
          - pmm: imdb
          - pmm: studio
          - pmm: genre
          - pmm: actor
        operations:
          mass_critic_rating_update: tmdb
          split_duplicates: true
      TV Shows:
        collection_files:
          - file: config/TV Shows.yml
          - pmm: tmdb
          - pmm: network
        overlay_files:
          - remove_overlays: false
          - file: config/Overlays.yml
      TV Shows On Second Plex:
        library_name: TV Shows
        plex:
          url: http://192.168.1.98:32400
          token: ####################
        collection_files:
          - file: config/TV Shows.yml
          - pmm: tmdb
          - pmm: network
      Anime:
        collection_files:
          - file: config/Anime.yml
          - pmm: myanimelist
        radarr:
          url: http://192.168.1.45:7878
          token: ################################
          root_folder_path: S:/Anime
        settings:
          asset_directory: config/assets/anime
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

### Attributes

The available attributes for each library are as follows:

| Attribute                                           | Description                                                                                                                                                                                                           |
|:----------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`library_name`](#library-name)                     | Used to specify the Library's name.<br>*required only when trying to use multiple libraries with the same name.*<br>**Values:** Library Name<br>**Default:** Base Attribute Name                                      |
| [`collection_files`](#collection-file)              | Used to define [Collection Files](data/collections.md).<br>**Values:** Location of Collection YAML files.<br>**Default:** `/config/<<MAPPING_NAME>>.yml`                                                              |
| [`metadata_files`](#metadata-file)                  | Used to define [Metadata Files](data/collections.md).<br>**Values:** Location of Metadata YAML files.                                                                                                                 |
| [`overlay_files`](#overlay-file)                    | Used to define [Overlay Files](data/overlays.md) .<br>**Values:** Location of Overlay YAML files.                                                                                                                     |
| [`report_path`](#report-path)                       | Location to create the YAML file listing added, removed, filtered, and missing items for this library.<br>**Values:** Location of the report file.<br>**Default:** `/config/<<MAPPING_NAME>>_report.yml`              |
| [`template_variables`](#library-template-variables) | Library template variables to be applied to every Collection, Metadata, and Overlay file run.<br>**Values:** Values are specified by each particular file.                                                            |
| [`schedule`](../builders/details/schedule.md)       | Used to schedule when this library is run.<br>**Values:** Any [schedule option](../builders/details/schedule.md)<br>**Default:** `daily`                                                                              |
| [`operations`](operations.md)                       | Used to specify Library Operations to run.<br>**Values:** Any [Library Operation](operations.md)                                                                                                                      |
| [`settings`](settings.md)                           | Used to override global `setting` values for this library only.<br>**Values:** Any `setting` attribute that overrides a global value.<br>**Default:** global value                                                    |
| [`plex`](plex.md)                                   | Used to override global `plex` values for this library only. **`plex` Attribute is required either here or globally**<br>**Values:** Any `plex` attribute that overrides a global value.<br>**Default:** global value |
| [`radarr`](radarr.md)                               | Used to override global `radarr` values for this library only.<br>**Values:** Any `radarr` attribute that overrides a global value.<br>**Default:** global value                                                      |
| [`sonarr`](sonarr.md)                               | Used to override global `sonarr` values for this library only.<br>**Values:** Any `sonarr` attribute that overrides a global value.<br>**Default:** global value                                                      |
| [`tautulli`](tautulli.md)                           | Used to override global `tautulli` values for this library only.<br>**Values:** Any `tautulli` attribute that overrides a global value.<br>**Default:** global value                                                  |

### Library Name

Each library that the user wants Plex Meta Manager to interact with must be documented with a library attribute. A library attribute is represented by the mapping name (i.e. `Movies` or `TV Shows`), this must have a unique name that correlates with a library of the same name within the Plex Media Server. In the situation that two servers are being connected to which both have libraries of the same name, the `library_name` attribute can be utilized to specify the real Library Name, whilst the library attribute's mapping name can be made into a placeholder. This is showcased below:

???+ Library Name Example
    
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
    
    * In this example, `"Movies01"`, `"TV Shows"`, and `"Anime"` will all use the global plex server (**http://192.168.1.12:32400**) which is defined using the global `plex` mapping. `"Movies02"` will use the plex server **http://192.168.1.35:32400** which is defined under its `plex` mapping over the global mapping.

### Collection File

The `collection_files` attribute is used to define [Collection Files](data/collections.md) by specifying the path type and path of the files that will be executed against the parent library. See [Path Types](../builders/files.md#paths) for how to define them.

```yaml
libraries:
  TV Shows:
    collection_files:
      - file: config/TV Shows.yml
      - pmm: tmdb
      - pmm: network
```

By default, when `collection_files` is missing Plex Meta Manager will look within the root PMM directory for a collection file called `<MAPPING_NAME>.yml`. In this example, Plex Meta Manager will look for a file named `TV Shows.yml`.

```yaml
libraries:
  TV Shows:
```

### Metadata File

The `metadata_files` attribute is used to define Metadata Files by specifying the path of the files that will be executed against the parent library. See [Path Types](../builders/files.md#paths) for how to define them.

???+ tip

    As of Plex Meta Manager 1.20.0 "Metadata Files" refers to YAML files which refers to managing the metadata of items [movies, shows, music] within your library, and "Collection Files" refers to YAML files which define Collections.

    In previous version of Plex Meta Manager, "Metadata Files" could mean either of the above.


```yaml
libraries:
  TV Shows:
    metadata_files:
      - file: config/metadata.yml
```

### Overlay File

The `overlay_files` attribute is used to define [Overlay Files](data/overlays.md) by specifying the path type and path of the files that will be executed against the parent library. See [Path Types](../builders/files.md#paths) for how to define them.

```yaml
libraries:
  TV Shows:
    collection_files:
      - file: config/TV Shows.yml
    overlay_files:
      - file: config/Overlays.yml
```

### Special Overlay File Calls

#### Remove Overlays

    
You can remove overlays from a library by adding `remove_overlays: true` to `overlay_files`.

???+ warning "Proceed with Caution"

    This will remove all overlays from your library, but will not delete the overlaid images from your system, resulting in [image bloat](../pmm/essentials/scripts/image-cleanup.md).

    ```yaml
    libraries:
      TV Shows:
        collection_files:
          - file: config/TV Shows.yml
        overlay_files:
          - remove_overlays: true
          - file: config/Overlays.yml
    ```

#### Reapply Overlays

You can reapply overlays from a library by adding `reapply_overlays: true` to `overlay_files`. This will reapply overlays to every item in your library.

???+ danger "Important Notice"

    This will reapply all overlays on each run until this attribute is set to `false`, which will result in [image bloat](../pmm/essentials/scripts/image-cleanup.md).

    ```yaml
    libraries:
      TV Shows:
        collection_files:
          - file: config/TV Shows.yml
        overlay_files:
          - reapply_overlays: true
          - file: config/Overlays.yml
    ```

#### Reset Overlays

You can reset overlays from a library by adding `reset_overlays` to `overlay_files` and setting it to either `tmdb` or `plex` depending on where you want to source the images from. This will use the reset image when overlaying items in your library.

???+ danger "Important Notice"

    This will reset all posters to the desired source on each run until this attribute is set to `false`, and will reapply all overlays on each run, which will result in [image bloat](../pmm/essentials/scripts/image-cleanup.md).


    ```yaml
    libraries:
      TV Shows:
        collection_files:
          - file: config/TV Shows.yml
        overlay_files:
          - reset_overlays: plex
          - file: config/Overlays.yml
    ```

### Schedule Overlays

You can schedule all overlays from a library by adding `schedule` to `overlay_files` and setting it to [Any Schedule Option](../builders/details/schedule.md).
    
You cannot schedule individual Overlay Files, as any unscheduled overlay file will be removed each time PMM is run.

???+ tip "Example"

    ```yaml
    libraries:
      TV Shows:
        collection_files:
          - file: config/TV Shows.yml
        overlay_files:
          - schedule: weekly(sunday)
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

### Library Template Variables

Library template variables to be applied to every Metadata and Overlay file run.

```yaml
libraries:
  Movies:
    template_variables:
      collection_mode: hide_items
```
