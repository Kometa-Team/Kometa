---
hide:
  - toc
---
# YamTrack Tracked

Finds every tracked item from the configured YamTrack user's movie and TV pages with the selected statuses.

???+ warning "YamTrack Configuration"

    [Configuring YamTrack](../../../config/yamtrack.md) in the config is required for this builder.

### Example YamTrack Tracked Builder

```yaml
collections:
  YamTrack Tracked:
    yamtrack_tracked:
      movies:
        dropped: false
        planning: true
        in_progress: true
        paused: false
        completed: false
      tv_shows:
        dropped: false
        planning: true
        in_progress: true
        paused: false
        completed: false
      anime:
        dropped: false
        planning: true
        in_progress: true
        paused: false
        completed: false
```

In the above example, Kometa adds only items marked `Planning` or `In Progress`.

### Attributes

| Attribute     | Description                            | Values        |
|:--------------|:---------------------------------------|:--------------|
| `movies`      | Movie statuses to include. Optional.   | Status block  |
| `tv_shows`    | TV show statuses to include. Optional. | Status block  |
| `anime`       | Anime statuses to include. Optional.   | Status block  |

Note that `anime` can have both Movies and TV Shows in YamTrack. Kometa will filter only the media type that correlates with the library that is being run.

Status blocks support these boolean attributes. When a status attribute is omitted from a present `movies`, `tv_shows`, or `anime` block, it defaults to `true`.

| Attribute     | YamTrack Status | Accepted Values | Default |
|:--------------|:----------------|:----------------|:--------|
| `dropped`     | Dropped         | `true`/`false`  | `true`  |
| `planning`    | Planning        | `true`/`false`  | `true`  |
| `in_progress` | In Progress     | `true`/`false`  | `true`  |
| `paused`      | Paused          | `true`/`false`  | `true`  |
| `completed`   | Completed       | `true`/`false`  | `true`  |
