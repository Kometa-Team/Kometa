# Config File

Plex Meta Manager uses a YAML configuration file; this file contains settings that determine how Plex Meta Manager 
behaves, and the required connection details needed to connect to Plex Media Server, Radarr, Sonarr, and other 
third-party services via API.

By default, and unless otherwise stated, Plex Meta Manager looks for the configuration file at `/config/config.yml`.

A template Configuration File can be found in the 
[GitHub Repo](https://github.com/meisnate12/Plex-Meta-Manager/blob/master/config/config.yml.template).

This table outlines the third-party services that Plex Meta Manager can make use of. Each service has specific 
requirements for setup that can be found by clicking the links within the table.

| Attribute                                   | Required                                                              |
|:--------------------------------------------|:----------------------------------------------------------------------|
| [`libraries`](libraries.md)                 | :fontawesome-solid-circle-check:{ .green }                            |
| [`playlist_files`](../notused/playlists.md) | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`settings`](settings.md)                   | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`webhooks`](webhooks.md)                   | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`plex`](plex.md)                           | :fontawesome-solid-circle-check:{ .green } Either here or per library |
| [`tmdb`](tmdb.md)                           | :fontawesome-solid-circle-check:{ .green }                            |
| [`github`](github.md)                       | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`tautulli`](tautulli.md)                   | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`omdb`](omdb.md)                           | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`notifiarr`](notifiarr.md)                 | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`gotify`](gotify.md)                       | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`anidb`](anidb.md)                         | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`radarr`](radarr.md)                       | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`sonarr`](sonarr.md)                       | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`trakt`](trakt.md)                         | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`mal`](myanimelist.md)                     | :fontawesome-solid-circle-xmark:{ .red }                              |

## Configuration File Example

This example outlines what a "standard" config.yml file might look like when in use.

~~~yaml
{%    
  include-markdown "../../config/config.yml.template" 
  comments=false
%}
~~~