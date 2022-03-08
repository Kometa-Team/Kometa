# Configuration File

Plex Meta Manager uses a YAML configuration file; this file contains swettings that deterimine how Plex Meta Manaegr behaves, and the required connection details needed to connect to Plex Media Server, Radarr, Sonarr, and other third-party services via API.

By default, and unless otherwise stated, Plex Meta Manager looks for the configuration file within `/config/config.yml`

A template Configuration File can be found in the [GitHub Repo](https://github.com/meisnate12/Plex-Meta-Manager/blob/master/config/config.yml.template).

This table outlines the third-party services that Plex Meta Manager can make use of. Each service has specific requirements for setup that can be found by clicking the links within the table.

| Attribute                    |                Required                 |
|:-----------------------------|:---------------------------------------:|
| [`libraries`](libraries)     |                 &#9989;                 |
| [`playlist_files`](playlist) |                &#10060;                 |
| [`settings`](settings)       |                &#10060;                 |
| [`webhooks`](webhooks)       |                &#10060;                 |
| [`plex`](plex)               | &#9989; <br/>Either here or per library |
| [`tmdb`](tmdb)               |                 &#9989;                 |
| [`tautulli`](tautulli)       |                &#10060;                 |
| [`omdb`](omdb)               |                &#10060;                 |
| [`notifiarr`](notifiarr)     |                &#10060;                 |
| [`anidb`](anidb)             |                &#10060;                 |
| [`radarr`](radarr)           |                &#10060;                 |
| [`sonarr`](sonarr)           |                &#10060;                 |
| [`trakt`](trakt)             |                &#10060;                 |
| [`mal`](myanimelist)         |                &#10060;                 |