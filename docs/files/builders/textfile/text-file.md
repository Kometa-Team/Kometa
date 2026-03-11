---
hide:
  - toc
---
# Text File

Finds items using a manually created local text file.

The expected input is a path to a text file or a list of text file paths.

Each non-empty line can contain one of the following. Lines beginning with `#` are ignored, and you can also add trailing inline comments using ` # comment` after a value:

- a TMDb ID
- a TVDb ID
- an IMDb ID or IMDb title URL
- a URL returning a JSON list of supported items, including gzip-compressed JSON responses
- `plex://movie/<24-char-id>`
- `plex://show/<24-char-id>`
- `plex://episode/<24-char-id>`
- a bare 24-character Plex metadata ID
- an explicit typed value such as `imdb:`, `tmdb:`, `tvdb:`, `tvdb_season:`, `tvdb_episode:`, `plex:`, or `url:`

Numeric lines are interpreted by library type:

- Movie libraries: TMDb IDs
- Show libraries: TVDb IDs
- Playlists or mixed/unknown contexts: generic numeric IDs matched against available movie/show libraries

The `sync_mode: sync` and `collection_order: custom` settings are recommended when you want the collection order to match the file exactly. If a line expands into multiple items from a JSON list URL, those items keep the order returned by that JSON list. If you provide multiple files, they are concatenated in the order listed and treated as a single `text_file` builder.

On show libraries, `text_file` can also be used with `builder_level: season` or `builder_level: episode` collections. In those cases, `tvdb_season` and `tvdb_episode` entries can target specific show parts directly.

### Episode and Season Part Syntax

For show-part collections, the following explicit values are supported:

- `tvdb_season:12345_1`
- `tvdb_season:12345/1`
- `tvdb_episode:12345_1_2`
- `tvdb_episode:12345-1-2`
- `tvdb_episode:12345/1/2`

Behavior depends on the collection level:

- `builder_level: season` + `tvdb_season` finds the matching season.
- `builder_level: episode` + `tvdb_season` expands to every episode in that season.
- `builder_level: episode` + `tvdb_episode` finds one specific episode.

If multiple lines point at the same episode, Kometa will only keep the episode once in the final collection.

### JSON List Example

```json
[
  {
    "imdb_id":"tt26443597"
  },
  {
    "tmdb_id":83533
  },
  {
    "tvdb_season":"12345_1"
  },
  {
    "tvdb_episode":{
      "tvdb_id":12345,
      "season":1,
      "episode":2
    }
  },
  {
    "type":"tvdb_episode",
    "id":[12345, 1, 3]
  },
  ...
]
```

### Example Text File Builder(s)

```yaml
collections:
  My Hand Curated List:
    text_file: config/lists/hand-curated.txt
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  Tracker Episodes:
    builder_level: episode
    text_file: config/lists/tracker-episodes.txt
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  My Combined Text Files:
    text_file:
      - config/lists/priority.txt
      - config/lists/overflow.txt
    collection_order: custom
    sync_mode: sync
```

When multiple files are listed, Kometa reads them as one `text_file` builder input in the order shown above. The file boundaries are not kept as separate builder groups; only the combined item order is preserved.

### Example Text File Contents

```text
# Movie library example
tt0079945   # Star Trek: The Motion Picture IMDb
174         # Star Trek VI: The Undiscovered Country assumed TMDb
tmdb:154    # Star Trek II: The Wrath of Khan unambiguous TMDb
plex://movie/5d7768243c3c2a001fbca85b # Plex movie GUID
5d776824880197001ec901ab              # Plex movie GUID
plex:5d7768244de0ee001fcc7ff2         # typed Plex GUID
url:https://example.com/list.json     # URL returning a JSON list
    # [see example JSON list above]

# Show library example
tt8466564    # Obi-Wan Kenobi IMDB
tmdb:83867   # Andor unambiguous TMDB
361702       # The Mandalorian assumed TVDb
tvdb:393117  # Ahsoka unambiguous TVDb
plex://show/63e3eedd166819851638a316 # Plex show GUID

# Episode example
tt22408116  # Tracker S1.E1 Klamath Falls
tt30221360  # Tracker S1.E3 Springland
tt31092062  # Tracker S1.E5 St. Louis
tt31092069  # Tracker S1.E7 Chicago
tvdb_season:383275/1 # Tracker Season 1 expanded to episodes in episode-level collections
tvdb_episode:383275_1_2 # Tracker S1.E2 Missoula


# Playlist or mixed library example
tt0079945    # Star Trek: The Motion Picture IMDb
tmdb:154     # Star Trek II: The Wrath of Khan unambiguous TMDB
tvdb:361702  # The Mandalorian unambiguous TVDb
plex://show/63e3eedd166819851638a316 # Plex show GUID
```