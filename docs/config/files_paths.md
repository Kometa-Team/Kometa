# Files & Paths

When using Plex Meta Manager, the structure of each library is made up of Files and Paths

???+ example "Example Library Structure"

    ```yaml
    libraries:
      Movies:
        collection_files:
          - pmm: imdb
    ```

    In the above example, `collection_files` is the type of File, which tells PMM that the entries that follow will create/update collections and `- pmm:` is the type of Path, which PMM that the file it is looking for is a PMM Defaults file.

    These ideas will be further outlined on this page.

## Files

Files define the structure and format for creating Collections, Overlays, Playlists, and Metadata Edits within your libraries.

Files are modular and when properly leveraged, they not only facilitate the management of your library's collections and metadata but also serve as a crucial backup resource in case a restore is necessary.

There are four main File types that can be utilized against Plex servers:

| File Type                                                                                                        | Description                                                                                                                              |
|:-----------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|
| [Collection Files](data/collections.md)                                                                          | Defines the data for building collections, allowing you to group and showcase your library in unique ways                                |
| [Overlay Files](data/overlays.md)                                                                                | Defines the data for building overlays, allowing you to place information such as resolutions and ratings onto your posters.             |
| Metadata Files ([Movies](data/metadata/movie.md)/[Shows](data/metadata/show.md)/[Music](data/metadata/music.md)) | Defines the data for editing metadata, allowing you to find and manipulate the metadata on individual items within your library.         |
| [Playlist Files](data/playlists.md)                                                                              | Defines the data for building playlists, allowing you to combine media from multiple libraries and share them with users on your server  |

Collection, Overlay and Metadata Files can be linked to libraries in the [Libraries Attribute](libraries) within the [Configuration File](../config/configuration.md).

## Example Files

This is a basic Files structure showing the use of all four File types.

???+ example "Example Files"

    Unlike the other three, Playlist Files are not defined per-library.

    Theis examples utilizes the [PMM Defaults](../defaults/files.md)

    ```yaml
    libraries:
      Movies:
        collection_files:
          - pmm: imdb
        overlay_files:
          - pmm: resolution
        metadata_files:
          - file: config/metadata.yml
    playlist_files:
      - pmm: playlists
    ```

# Paths

YAML Files are defined by their path type and path location for the [`collection_files`](libraries.md#collection-file), [`overlay_files`](libraries.md#overlay-file), [`playlist_files`](data/playlists), and [`external_templates`](../builders/templates).

They can either be on the local system, online at an url, directly from the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs) repository, or from another [`Custom Repository`](settings.md#custom-repo).

The path types are outlined as follows:

* `- file:` refers to a collection file which is located within the system that PMM is being run from.

* `- folder:` refers to a directory containing collection files which is located within the system that PMM is being run from.

* `- pmm:` refers to a [PMM Defaults](../defaults/files.md) builders/overlay/playlist file. 

* `- url:` refers to a collection file which is hosted publicly on the internet. 

* `- git:` refers to a collection file which is hosted on the [Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs).

* `- repo:` refers to a collection file which is hosted on a custom repository specified by the user with the [`custom_repo` Setting Attribute](settings.md#custom-repo).

## Example Paths

```yaml
libraries:
  Movies:
    collection_files:
      - file: config/path/to/file.yml
      - folder: config/path/to/folder
```
File and folder paths need to be accessible to PMM at those paths; this is typically only something you need to consider when using Docker.
```
      - url: https://example.com/path/to/file.yml
```
This needs to point directly to the YAML file.  A common error is using a gitHub link that points to the *page displaying the YAML*.  In gitHub, for instance, click on the "Raw" button and use *that* link.
```
      - git: meisnate12/People # this links to https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/meisnate12/People.yml
```
Note that you enter the bits of the items path relative to the top level of the repo [`meisnate12/People`] and you don't need the `.yml` extension.
```
      - repo: People
```
This is assuming the `custom_repo` setting is `https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/meisnate12`
Note that as with `- git:` you enter the bits of the items path relative to repo [`meisnate12/People`] and you don't need the `.yml` extension.
Note that as with `- git:` you enter the bits of the items path relative to repo [`meisnate12/People`] and you don't need the `.yml` extension.
```
      - pmm: oscars
```
The values you'd enter here are listed in the [default metadata guide](../defaults/guide.md).

## YAML Controls

You can have some control of yaml files from inside your Configuration file by using YAML Controls.

### Template Variables 

You can define [Template Variables](../builders/templates.md#template-variables) that will be added to every template in the associated YAML file by adding the `template_variables` attribute to the dictionary defining the file.

#### Example

```yaml
libraries:
  TV Shows:
    collection_files:
      - pmm: genre
        template_variables:
          schedule_separator: never
          collection_mode: hide
      - pmm: actor                  # Notice how the `-` starts this "section"
        template_variables:
          schedule_separator: never
          collection_mode: hide
```

In this example there will be two template variables added to every template in the git file pmm: genre.  

`schedule_separator` is set to `never` to not show a separator in this section and `collection_mode` is set to `hide`.

What these variables will do depends on how they're defined in the Collection File. 

### Schedule

Each [`collection_files`](libraries.md#collection-file),  [`overlay_files`](libraries.md#overlay-file), or [`playlist_files`](data/playlists) can be scheduled by adding the `schedule` attribute to the dictionary defining the file.

Below is an example of a scheduled Collection File and Playlist File:

```yaml
libraries:
  Movies:
    collection_files:
      - file: config/Movies.yml
        schedule: weekly(friday)
      - pmm: actors
        schedule: weekly(saturday)
playlist_files:
  - file: config/Playlists.yml
    schedule: weekly(sunday)
```

### Asset Directory

You can define custom Asset Directories per file by adding `asset_directory` to the file call.

???+ important 

    Assets can be stored anywhere on the host system that PMM has visibility of (i.e. if using docker, the directory must be mounted/visible to the docker container).

```yaml
libraries:
  Movies:
    collection_files:
      - file: config/Movies.yml
        asset_directory: <path_to_assets>/Movies
      - pmm: actors
        asset_directory: <path_to_assets>/people
    overlay_files:
      - pmm: imdb
playlist_files:
  - file: config/Playlists.yml
    asset_directory:
      - <path_to_assets>/playlists1
      - <path_to_assets>/playlists2
```

## Collection File 

The [`collection_files`](libraries.md#collection-file) attribute is defined under the [`libraries`](libraries.md) attribute in your [Configuration File](configuration.md). 

??? example
    
    In this example, multiple collection file path types are defined for the `"TV Shows"` library:
    
    ```yaml
    libraries:
      TV Shows:
        collection_files:
          - file: config/TVShows.yml
          - folder: config/TV Shows/
          - pmm: tmdb
          - repo: charts
          - url: https://somewhere.com/PopularTV.yml
    ```
    
    Within the above example, PMM will:

    * First, look within the root of the PMM directory (also known as `config/`) for a collection file named `TVShows.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.

    * Then, look within the root of the PMM directory (also known as `config/`) for a directory called `TV Shows`, and then load any collection files within that directory.

    * Then, look in the [defaults folder](https://github.com/meisnate12/Plex-Meta-Manager/tree/master/defaults) within the local PMM folder [or docker container] for a file called `tmdb.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/master/defaults/chart/tmdb.yml).

    * Then, look within the Custom Defined Repo for a file called `charts.yml`.

    * Finally, load the collection file located at `https://somewhere.com/PopularTV.yml`

## Overlay File 

The [`overlay_files`](libraries.md#overlay-file) attribute is defined under the [`libraries`](libraries.md) attribute in your [Configuration File](configuration.md). 

??? example

    In this example, multiple overlay file path types are defined for the `"TV Shows"` library:
    
    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - file: config/overlays.yml
          - folder: config/overlay configs/
          - pmm: imdb
          - repo: overlays
          - url: https://somewhere.com/Overlays.yml
    ```

    Within the above example, PMM will:

    * First, look within the root of the PMM directory (also known as `config/`) for a collection file named `overlays.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.

    * Then, look within the root of the PMM directory (also known as `config/`) for a directory called `overlay configs`, and then load any collection files within that directory.

    * Then, look in the [defaults folder](https://github.com/meisnate12/Plex-Meta-Manager/tree/master/defaults) within the local PMM folder [or docker container] for a file called `imdb.yml`.

    * Then, look within the Custom Defined Repo for a file called `overlays.yml`.

    * Finally, load the collection file located at `https://somewhere.com/Overlays.yml`

## Playlist Files 

The [`playlist_files`](data/playlists.md) at the top level in your [Configuration File](configuration.md). 

??? example

    In this example, multiple `playlist_files` attribute path types are defined:
    
    ```yaml
    playlist_files:
      - file: config/playlists.yml
      - folder: config/Playlists/
      - pmm: playlist
      - repo: playlists
      - url: https://somewhere.com/Playlists.yml
    ```
    
    Within the above example, PMM will:

    * First, look within the root of the PMM directory (also known as `config/`) for a playlist file named `Playlists.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.

    * Then, look within the root of the PMM directory (also known as `config/`) for a directory called `Playlists`, and then load any playlist files within that directory.

    * Then, look in the [defaults folder](https://github.com/meisnate12/Plex-Meta-Manager/tree/master/defaults) within the local PMM folder [or docker container] for a file called `playlist.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/master/defaults/playlist.yml).

    * Then, look within the Custom Defined Repo for a file called `playlists.yml`.

    * Finally, load the playlist file located at `https://somewhere.com/Playlists.yml`

## External Templates 

The [`external_templates`](../builders/templates.md#external-templates) attribute is defined at the top level in your [Collection File](data/collections.md). 

??? example
    
    In this example, multiple external template file path types are defined:
    
    ```yaml
    external_templates:
    - file: config/templates.yml
    - folder: config/templates/
    - url: https://somewhere.com/templates.yml
    - pmm: templates
    - repo: templates
    ```
    
    Within the above example, PMM will:

    * First, look within the root of the PMM directory (also known as `config/`) for a collection file named `templates.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.

    * Then, look within the root of the PMM directory (also known as `config/`) for a directory called `templates`, and then load any collection files within that directory.

    * Then, load the collection file located at `https://somewhere.com/templates.yml`.

    * Then, look in the [defaults folder](https://github.com/meisnate12/Plex-Meta-Manager/tree/master/defaults) within the local PMM folder [or docker container] for a file called `templates.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager/blob/master/defaults/templates.yml).

    * Finally, look at the within the Custom Defined Repo for a file called `templates.yml`.