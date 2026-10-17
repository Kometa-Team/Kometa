---
search:
  boost: 3
hide:
  - toc
---
# Seerr

Seerr can receive movie and show requests from Kometa collection builders and route them to its configured Radarr and Sonarr instances. Configure Seerr's regular and 4K servers in Seerr; Kometa selects the tier for each request.

```yaml
seerr:
  url: http://192.168.1.12:5055
  apikey: your_seerr_api_key
```

Enable requests for media missing from the Plex library with `seerr_add_missing`. Use `seerr_add_existing` to also request media already in that library, such as requesting a 4K version of an existing movie. Set `seerr_instance` to `standard`, `4k`, or `both`; the default is `standard`. `both` submits a separate request for each tier.

```yaml
collections:
  Popular Movies:
    imdb_list: https://www.imdb.com/list/ls000000000/
    seerr_add_missing: true
    seerr_instance: both

  Popular Shows:
    tmdb_popular: 20
    seerr_add_missing: true
    seerr_instance: 4k

  Upgrade Existing Movies:
    tmdb_list: 12345
    seerr_add_existing: true
    seerr_instance: 4k
    seerr_overrides:
      4k:
        server_id: 2
        quality_profile: 4
        root_folder: /media/movies-4k
```

`seerr_overrides` can specify `server_id`, `quality_profile`, and `root_folder` separately for `standard` and `4k`. A quality profile may be an ID or name. Unset values use Seerr's defaults for that tier. Requests are made separately, so a failure or duplicate in one tier does not prevent the other tier from being attempted. Kometa requests all seasons for shows.

Seerr can be configured globally and overridden per library. Library-level values inherit any global value not specified:

```yaml
libraries:
  Movies:
    seerr:
      url: http://seerr-movies:5055
      apikey: your_library_seerr_api_key
```

Existing Radarr and Sonarr settings remain independent; enabling their `add_missing` options sends requests directly as well.
