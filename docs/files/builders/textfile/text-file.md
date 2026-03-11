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
- an explicit typed value such as `imdb:`, `tmdb:`, `tvdb:`, `plex:`, or `url:`

Numeric lines are interpreted by library type:

- Movie libraries: TMDb IDs
- Show libraries: TVDb IDs
- Playlists or mixed/unknown contexts: generic numeric IDs matched against available movie/show libraries

The `sync_mode: sync` and `collection_order: custom` settings are recommended when you want the collection order to match the file exactly. If a line expands into multiple items from a JSON list URL, those items keep the order returned by that JSON list. If you provide multiple files, they are concatenated in the order listed and treated as a single `text_file` builder.

### JSON List Example

```json
[
  {
    "imdb_id":"tt26443597"
  },
  {
    "tmdb_id":83533
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
tt1234567 # IMDb
12345 # TMDb for movie libraries
plex://movie/5d7768244de0ee001fcc7ff0 # Plex movie GUID
5d7768244de0ee001fcc7ff1
url:https://example.com/list.json
plex:5d7768244de0ee001fcc7ff2 # typed Plex ID

# Show library example
plex://show/63e3eedd166819851638a316 # Plex show GUID
```