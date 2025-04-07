---
hide:
  - toc
---
# Config File

Kometa uses a YAML configuration file; this file contains settings that determine how Kometa behaves, and the required 
connection details needed to connect to Plex Media Server, Radarr, Sonarr, and other third-party services via API.

By default, and unless otherwise stated, Kometa looks for the configuration file at `/config/config.yml`.

A template Configuration Template File can be found in the  [GitHub Repo](https://github.com/Kometa-Team/Kometa/blob/master/config/config.yml.template).

If Kometa cannot find the `config.yml` at the default location, it will attempt to rename `config.yml.template` for the user. If the template file cannot be found, 
Kometa will attempt to download a copy from the GitHub repository in line with the user's current branch. 
If this also fails, the user will have to download the Configuration Template File from  the above link and manually rename it to `config.yml`.

This table outlines the third-party services (also known as **Connectors**) that Kometa can make use of. Each service has specific 
requirements for setup that can be found by clicking the links within the table or in the sidebar.

???+ tip "Connectors"

     Although most connectors are not required for core Kometa functionality, some (such as Trakt and MDBList) are commonly used for third-party lists, so we would recommend configuring This connector.
    
    <div class="annotate" markdown>
    
    | Attribute                          | Required                                                                 |
    |:-----------------------------------|:------------------------------------------------------------------------|
    | [`plex`](plex.md)(1)               | :fontawesome-solid-circle-check:{ .green }                              |
    | [`tmdb`](tmdb.md)                  | :fontawesome-solid-circle-check:{ .green }                              |
    | [`libraries`](libraries.md)        | :fontawesome-solid-circle-check:{ .green }                              |
    | [`playlist_files`](playlists.md)   | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`settings`](settings.md)          | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`webhooks`](webhooks.md)(2)       | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`tautulli`](tautulli.md)(3)       | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`github`](github.md)              | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`omdb`](omdb.md)                  | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`mdblist`](mdblist.md)            | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`notifiarr`](notifiarr.md)        | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`gotify`](gotify.md)              | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`ntfy`](ntfy.md)                  | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`anidb`](anidb.md)                | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`radarr`](radarr.md)(4)           | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`sonarr`](sonarr.md)(5)           | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`trakt`](trakt.md)                | :fontawesome-solid-circle-xmark:{ .red }                                |
    | [`mal`](myanimelist.md)            | :fontawesome-solid-circle-xmark:{ .red }                                |

    </div>

    1. This connector can be configured either at the root level of the Config File, or per-library – examples are available on the connector's page.  
    2. This connector can be configured either at the root level of the Config File, or per-library – examples are available on the connector's page.  
    3. This connector can be configured either at the root level of the Config File, or per-library – examples are available on the connector's page.  
    4. This connector can be configured either at the root level of the Config File, or per-library – examples are available on the connector's page.  
    5. This connector can be configured either at the root level of the Config File, or per-library – examples are available on the connector's page.  

## Configuration Template File Example

The below in an extract of the `config.yml.template` and is the initial values that are set if you follow any of the installation guides.

```yaml title="config.yml.template"
{%    
  include-markdown "../../config/config.yml.template" 
  comments=false
%}
```
