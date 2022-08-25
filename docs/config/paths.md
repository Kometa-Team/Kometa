# Path Types

YAML Files are defined by their path type and path location for the [`metadata_path`](libraries.md#metadata-path),  [`overlay_path`](libraries.md#overlay-path), [`playlist_files`](libraries.md#metadata-path), and [`external_templates`](libraries.md#metadata-path) attributes.

They can either be on the local system, online at an url, directly from the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs) repository, or from another [`Custom Repository`](settings.md#custom-repo).

The path types are outlined as follows:

* `- file:` refers to a metadata file which is located within the system that PMM is being run from.
* `- folder:` refers to a directory containing metadata files which is located within the system that PMM is being run from.
* `- url:` refers to a metadata file which is hosted publicly on the internet. 
* `- git:` refers to a metadata file which is hosted on the [Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs).
* `- repo:` refers to a metadata file which is hosted on a custom repository specified aby the user with the [`custom_repo` Setting Attribute](settings.md#custom-repo).

## YAML Controls

You can have some control of yaml files from inside your Configuration file by using YAML Controls.

### Template Variables 

You can define [Template Variables](../metadata/templates.md#template-variables) that will be added to every template in the associated YAML file by adding the `template_variables` attribute to the dictionary defining the file.

#### Example

```yaml
libraries:
  TV Shows:
    metadata_path:
      - git: PMM/genre
        template_variables:
          schedule_separator: never
          collection_mode: hide
      - git: PMM/actor                  # Notice how the `-` starts this "section"
        template_variables:
          schedule_separator: never
          collection_mode: hide
```

In this example there will be two template variables added to every template in the git file PMM/genre.  

`schedule_separator` is set to `never` to not show a separator in this section and `collection_mode` is set to `hide`.

What these variables will do depends on how they're defined in the Metadata File. 

### Schedule

Each [`metadata_path`](libraries.md#metadata-path),  [`overlay_path`](libraries.md#overlay-path), or [`playlist_files`](libraries.md#metadata-path) can be scheduled by adding the `schedule` attribute to the dictionary defining the file.

Below is an example of a scheduled Metadata File, Overlay File, and Playlist File:

```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
        schedule: weekly(friday)
      - git: PMM/actors
        schedule: weekly(saturday)
    overlay_path:
      - git: PMM/overlays/imdb
        schedule: weekly(monday)
playlist_files:
  - file: config/Playlists.yml
    schedule: weekly(sunday)
```

### Asset Directory

You can define custom Asset Directories per file by adding `asset_directory` to the file call.

```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
        asset_directory: assets/Movies
      - git: PMM/actors
        asset_directory: assets/people
    overlay_path:
      - git: PMM/overlays/imdb
playlist_files:
  - file: config/Playlists.yml
    asset_directory:
      - assets/playlists1
      - assets/playlists2
```

## Metadata Path 

The [`metadata_path`](libraries.md#metadata-path) attribute is defined under the [`libraries`](libraries) attribute in your [Configuration File](configuration). 

### Example

<details>
  <summary>Click to Expand</summary>
  <br />

In this example, multiple metadata file path types are defined for the `"TV Shows"` library:

```yaml
libraries:
  TV Shows:
    metadata_path:
      - file: config/TVShows.yml
      - folder: config/TV Shows/
      - git: PMM/chart/tmdb
      - repo: charts
      - url: https://somewhere.com/PopularTV.yml
```

Within the above example, PMM will:

* First, look within the root of the PMM directory (also known as `config/`) for a metadata file named `TVShows.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.
* Then, look within the root of the PMM directory (also known as `config/`) for a directory called `TV Shows`, and then load any metadata files within that directory.
* Then, look at the [meisnate12 folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/meisnate12) within the GitHub Configs Repo for a file called `MovieCharts.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/PMM/chart/imdb.yml).
* Then, look at the within the Custom Defined Repo for a file called `charts.yml`.
* Finally, load the metadata file located at `https://somewhere.com/PopularTV.yml`

</details>

## Overlay Path 

The [`overlay_path`](libraries.md#overlay-path) attribute is defined under the [`libraries`](libraries) attribute in your [Configuration File](configuration). 

### Example

<details>
  <summary>Click to Expand</summary>
  <br />

In this example, multiple overlay file path types are defined for the `"TV Shows"` library:

```yaml
libraries:
  TV Shows:
    overlay_path:
      - file: config/overlays.yml
      - folder: config/overlay configs/
      - git: PMM/overlays/imdb
      - repo: overlays
      - url: https://somewhere.com/Overlays.yml
```

Within the above example, PMM will:

* First, look within the root of the PMM directory (also known as `config/`) for a metadata file named `overlays.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.
* Then, look within the root of the PMM directory (also known as `config/`) for a directory called `overlay configs`, and then load any metadata files within that directory.
* Then, look at the [meisnate12 folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/meisnate12) within the GitHub Configs Repo for a file called `PMM/overlays/imdb.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/PMM/overlays/imdb.yml).
* Then, look at the within the Custom Defined Repo for a file called `overlays.yml`.
* Finally, load the metadata file located at `https://somewhere.com/Overlays.yml`

</details>

## Playlist Files 

The [`playlist_files`](libraries.md#playlist-files-attribute) at the top level in your [Configuration File](configuration). 

### Example

<details>
  <summary>Click to Expand</summary>
  <br />

In this example, multiple `playlist_files` attribute path types are defined:

```yaml
playlist_files:
  - file: config/playlists.yml
  - folder: config/Playlists/
  - git: PMM/playlist
  - repo: playlists
  - url: https://somewhere.com/Playlists.yml
```

Within the above example, PMM will:

* First, look within the root of the PMM directory (also known as `config/`) for a playlist file named `Playlists.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.
* Then, look within the root of the PMM directory (also known as `config/`) for a directory called `Playlists`, and then load any playlist files within that directory.
* Then, look at the [meisnate12 folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/meisnate12) within the GitHub Configs Repo for a file called `MovieCharts.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/meisnate12/Playlists.yml).
* Then, look at the within the Custom Defined Repo for a file called `playlists.yml`.
* Finally, load the playlist file located at `https://somewhere.com/Playlists.yml`

</details>

## External Templates 

The [`external_templates`](../metadata/templates.md#external-templates) attribute is defined at the top level in your [Metadata File](../metadata/metadata). 

### Example

<details>
  <summary>Click to Expand</summary>
  <br />

In this example, multiple external template file path types are defined:

```yaml
external_templates:
  - file: config/templates.yml
  - folder: config/templates/
  - url: https://somewhere.com/templates.yml
  - git: PMM/templates
  - repo: templates
```

Within the above example, PMM will:

* First, look within the root of the PMM directory (also known as `config/`) for a metadata file named `templates.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.
* Then, look within the root of the PMM directory (also known as `config/`) for a directory called `templates`, and then load any metadata files within that directory.
* Then, load the metadata file located at `https://somewhere.com/templates.yml`.
* Then, look at the [PMM folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM) within the GitHub Configs Repo for a file called `templates.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/PMM/templates.yml).
* Finally, look at the within the Custom Defined Repo for a file called `templates.yml`.

</details>
