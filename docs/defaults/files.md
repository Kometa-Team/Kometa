# List of Defaults Files

The below table outlines the available Defaults files which can be called via `metadata_path` (for Collections), `overlay_path` (for Overlays) and `playlist_files` (for Playlists).

{%
   include-markdown "./collection_list.md"
%}

{%
   include-markdown "./overlay_list.md"
%}

## Playlists

These files apply playlists to the "Playlists" section of Plex and are applied by calling the below paths into the `playlist_files` section of your config.yml

### Playlist Files

| Default              | path       | Example Overlays                                       |
|:---------------------|:-----------|:-------------------------------------------------------|
| [Playlist](playlist.md) | `playlist` | Arrowverse (Timeline Order), Pokémon (Timeline Order)  |
