### What comes next:

If you want to remove those overlays, open the config file, change the value of `remove_overlays` to `true`, and rerun PMM.

```
    overlay_path:
      - remove_overlays: true
      - pmm: resolution
```

If you want to remove those collections, open the config file, remove or comment out [add `#` to the beginning] any or all of those lines under `metadata_path`, and delete the collections manually from Plex.

```yaml
libraries:
  Main Movies:
    metadata_path:
      # - pmm: basic               # This is a file within the defaults folder in the Repository
      # - pmm: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
      # - file: config/Movies.yml
    overlay_path:
      - remove_overlays: false
      - pmm: resolution
```

Edit `Movies.yml` to reflect the actions you want PMM to perform on *your* libraries.

TV Shows and other libraries work the same way as you've seen above.  Create a section under `Libraries:` in the config.yml, refer to default files or create a metadata file, define collections, run the script.

Investigate the rest of the wiki to learn about everything Plex-Meta-Manager can do for you.

### Runtime and Environment Flags

The command in this walkthrough will run all collections and libraries immediately.  If you want to modify that behavior to run just one or some collections, or just one library, or just overlays or the like, review the [Run Commands & Environment Variables](../../environmental.md).

### Creating Collections, Overlays, Playlists, etc.

These things are all generally defined in metadata files that are referred to in the config file.  The starting point for creating these files is [here](../../../metadata/metadata.md).

