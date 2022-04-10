# Path Types

YAML Files are defined by their path type and path location for the [`metadata_path`](libraries.md#metadata-path), [`playlist_files`](libraries.md#metadata-path), and [`external_templates`](libraries.md#metadata-path) attributes.

They can either be on the local system, online at an url, directly from the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs) repository, or from another [`Custom Repository`](settings.md#custom-repo).

The path types are outlined as follows:

* `- file:` refers to a metadata file which is located within the system that PMM is being run from.
* `- folder:` refers to a directory containing metadata files which is located within the system that PMM is being run from.
* `- url:` refers to a metadata file which is hosted publicly on the internet. 
* `- git:` refers to a metadata file which is hosted on the [Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs).
* `- repo:` refers to a metadata file which is hosted on a custom repository specified aby the user with the [`custom_repo` Setting Attribute](settings.md#custom-repo).

## Template Variables 

[Template Variables](../metadata/templates.md#template-variables) can be added to every template in any defined YAML file by adding the `template_variables` attribute to the dictionary defining the file.

### Example

```yaml
libraries:
  TV Shows:
    metadata_path:
      - git: PMM/genre
        template_variables:
          schedule_separator: never
          collection_mode: hide
```

In this example there will be two template variables added to every template in the git file PMM/genre.  

`schedule_separator` is set to `never` to not show a separator in this section and `collection_mode` is set to `hide`.

What these variables will do depends on how they're defined in the Metadata File. 

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
      - git: meisnate12/ShowCharts
      - repo: charts
      - url: https://somewhere.com/PopularTV.yml
```

Within the above example, PMM will:

* First, look within the root of the PMM directory (also known as `config/`) for a metadata file named `TVShows.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.
* Then, look within the root of the PMM directory (also known as `config/`) for a directory called `TV Shows`, and then load any metadata files within that directory.
* Then, look at the [meisnate12 folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/meisnate12) within the GitHub Configs Repo for a file called `MovieCharts.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/meisnate12/MovieCharts.yml).
* Then, look at the within the Custom Defined Repo for a file called `charts.yml`.
* Finally, load the metadata file located at `https://somewhere.com/PopularTV.yml`

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
  - git: meisnate12/Playlists
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
