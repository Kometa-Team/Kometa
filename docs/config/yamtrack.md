# YamTrack

Configuring [YamTrack](https://github.com/FuzzyGrim/YamTrack) is optional but is required for YamTrack builders to function.

A `yamtrack` mapping is in the root of the config file, sampled below.

```yaml
yamtrack:
  url: https://yamtrack.domain.com
  username: USERNAME
  password: PASSWORD
```

| Attribute  | Description              | Required |
|:-----------|:-------------------------|:--------:|
| `url`      | YamTrack server URL      | :fontawesome-solid-circle-check:{ .green } |
| `username` | YamTrack username        | :fontawesome-solid-circle-check:{ .green } |
| `password` | YamTrack password        | :fontawesome-solid-circle-check:{ .green } |

YamTrack lists and tracked pages now extract TVDB show IDs from `/details/tvdb/tv/{id}` links alongside existing TMDb IDs. TVDB-tracked shows match via Plex's native TVDB show mapping — no configuration changes are needed.
