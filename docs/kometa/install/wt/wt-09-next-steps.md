### What comes next:

If you want to remove those overlays, open the config file, change the value of `remove_overlays` to `true`, and rerun Kometa.

```
    remove_overlays: true
    overlay_files:
      - default: resolution
```

If you want to remove those collections, open the config file, remove or comment out [add `#` to the beginning] any or all of those lines under `collection_files`, and delete the collections manually from Plex.

```yaml
libraries:
  All The Movies:
    collection_files:
      # - default: basic               # This is a file within the defaults folder in the Repository
      # - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
      # - file: config/Movies.yml
    remove_overlays: false
    overlay_files:
      - default: resolution
```

Edit `Movies.yml` to reflect the actions you want Kometa to perform on *your* libraries.

TV Shows and other libraries work the same way as you've seen above.  Create a section under `libraries:` in the config.yml, refer to default files or create a collection file, define collections, run the script.

Investigate the rest of the wiki to learn about everything Kometa can do for you.

### Runtime and Environment Flags

The command in this walkthrough will run all collections and libraries immediately.  If you want to modify that behavior to run just one or some collections, or just one library, or just overlays or the like, review the [Run Commands & Environment Variables](../../environmental.md).

### Creating Collections, Overlays, Playlists, etc.

These things are all generally defined in collection files that are referred to in the config file.  The starting point for creating these files is [here](../../../files/collections.md).
