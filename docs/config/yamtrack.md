# YamTrack

Configuring [YamTrack](https://github.com/FuzzyGrim/YamTrack) is optional but is required for YamTrack list builders to function.

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

YamTrack collection builders read TMDb item links from a YamTrack list page:

```yaml
collections:
  YamTrack List:
    yamtrack_list: https://yamtrack.kometa.team/list/1
```

Use `yamtrack_list_details` to also use the YamTrack list description as the collection summary.

```yaml
collections:
  YamTrack List:
    yamtrack_list_details: https://yamtrack.kometa.team/list/1
```
