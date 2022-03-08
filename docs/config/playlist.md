# Playlist Files

## Overview

As playlists are not tied to one specific library and can combine media from multiple libraries, they require their own special [Playlist File](../metadata/metadata) to work.

You can define Playlist Files by using `playlist_files` mapper. They can either be on the local system, online at an url, or directly from the [Plex Meta Manager Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs) repository.

## Path Types

In this example, four `playlist_files`attribute path types are defined:

```yaml
playlist_files:
  - file: config/playlists.yml
  - folder: config/Playlists/
  - git: meisnate12/Playlists
  - url: https://somewhere.com/Playlists.yml
```
The four path types are outlined as follows:

* `- file:` refers to a playlist file which is located within the system that PMM is being run from.
* `- folder:` refers to a directory containing playlist files which is located within the system that PMM is being run from.
* `- git:` refers to a playlist file which is hosted on GitHub.  This file is assumed to be in the [Configs Repo](https://github.com/meisnate12/Plex-Meta-Manager-Configs) unless the user has specified a custom repository with the 
* `- url:` refers to a playlist file which is hosted publicly on the internet.

Within the above example, PMM will:

* First, look within the root of the PMM directory (also known as `config/`) for a playlist file named `Playlists.yml`. If this file does not exist, PMM will skip the entry and move to the next one in the list.
* Then, look within the root of the PMM directory (also known as `config/`) for a directory called `Playlists`, and then load any playlist files within that directory.
* Then, look at the [meisnate12 folder](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/meisnate12) within the GitHub Configs Repo for a file called `MovieCharts.yml` which it finds [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs/blob/master/meisnate12/Playlists.yml).
* Finally, load the playlist file located at `https://somewhere.com/Playlists.yml`