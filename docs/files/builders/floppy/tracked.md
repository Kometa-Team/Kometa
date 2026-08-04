# Floppy Tracked

Finds items in the configured Floppy instance by tracking status. A private Floppy API token is required.

`status` accepts `no_status`, `completed`, `in_progress`, `planning`, `paused`, `dropped`, or `all`. The `all` value includes every tracked item regardless of status. `type` accepts `movie`, `show`, `season`, and `anime`; it defaults to `movie` for movie libraries and `show,season` for show libraries.

```yaml
collections:
  Tracked In Progress:
    floppy_tracked:
      status: in_progress

  Tracked Anime:
    floppy_tracked:
      status: [completed, in_progress]
      type: anime
```

Anime entries are read by MyAnimeList ID and converted through Kometa's existing anime mappings. Only anime that resolves to an item in the current library is included.
