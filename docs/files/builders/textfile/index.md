# Text and File Lists

Select movies, shows, seasons, or episodes using IDs written directly in YAML or
stored in a local or remote file. Both builders support playlists and custom
sorting. No external service configuration is required.

## Choose a builder

| Builder | Input | Best for |
|:--------|:------|:---------|
| [`text`](#text) | Scalar, literal multiline string, or YAML list | IDs maintained with the collection definition |
| [`text_file`](#text-file) | File path, URL, or YAML list of paths and URLs | Lists maintained separately or fetched remotely |

Use `collection_order: custom` to preserve source order and `sync_mode: sync` to
keep membership synchronized. Entries expanding into JSON items retain their
returned order. Multiple files are concatenated in the listed order and treated
as one builder input, rather than separate builder groups.

## Identifier reference {#supported-values}

Both builders use the same entry syntax:

| Value | Selects |
|:------|:--------|
| `tt0079945` or an IMDb title URL | IMDb title |
| Numeric ID, such as `174` | TMDb movie in movie libraries; TVDb show in show libraries |
| `imdb:tt0079945`, `tmdb:154`, `tvdb:361702` | Explicit identifier type |
| `plex://movie/<24-char-id>`, `plex://show/<24-char-id>`, `plex://episode/<24-char-id>` | Plex metadata GUID |
| Bare 24-character Plex metadata ID or `plex:<id>` | Plex metadata item |
| `tvdb_season:<parts>`, `tvdb_episode:<parts>` | Season or episode; see syntax below |
| `url:https://example.com/list.json` or a JSON-list URL | Expanded items from a JSON list |

In playlists and mixed/unknown contexts, bare numeric IDs are matched against
available movie/show libraries. Prefer typed values for clarity. In mixed contexts,
`tmdb:` considers both movie and show IDs; only the type resolving in the configured
libraries is added, preserving line order even when types are interleaved.

Blank lines and lines beginning with `#` are ignored. A trailing comment starts
with whitespace followed by `#`. YAML removes comments from scalar and list values
before Kometa receives them; comments inside literal multiline strings are handled
as part of the text input. Quote metadata IDs if YAML could treat them as numbers
or remove leading zeroes.

## Inline text {#text}

`text` accepts a single string or integer, a literal multiline string, or a YAML
list of strings and integers. Entries are processed in their declared order.

<span id="single-value"></span>
<span id="multiline-string"></span>
<span id="yaml-list"></span>

=== "Single value"

    Selects Star Trek: The Motion Picture by IMDb ID. For a movie library,
    `text: 174` would instead select Star Trek VI using a numeric TMDb ID.

    ```yaml
    collections:
      Star Trek:
        text: tt0079945
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiline string"

    Selects the three movies in the declared order. `|-` keeps one ID per line,
    and the inline comments explain each entry without becoming part of the ID.

    ```yaml
    collections:
      Star Trek Movies:
        text: |-
          tt0079945 # Star Trek: The Motion Picture
          174       # Star Trek VI, assumed TMDb in a movie library
          tmdb:154  # Star Trek II, explicit TMDb
        collection_order: custom
        sync_mode: sync
    ```

=== "YAML list"

    Selects the same three movies using a list of string and integer values.
    This is an ordered source list, rather than an AND/OR search expression.

    ```yaml
    collections:
      Star Trek Movies:
        text:
          - tt0079945
          - 174
          - tmdb:154
        collection_order: custom
        sync_mode: sync
    ```

!!! important "Keep multiline entries on separate lines"

    Use literal `|` or `|-` blocks. Folded `>` blocks replace line breaks with
    spaces and destroy the entry structure. `>|` is not valid YAML syntax.

### Mixed playlist {#playlist-example}

Selects movies and shows in the declared order. Replace the library names with
your configured libraries. Typed IDs clarify each source across mixed libraries.

```yaml
playlists:
  Mixed Watchlist:
    libraries: Movies, TV Shows
    text: |-
      tt0079945
      tmdb:154
      tvdb:361702
      plex://show/63e3eedd166819851638a316
    sync_mode: sync
```

### JSON URL entries {#url-entries}

An embedded URL must return a [JSON list](#json-list-example), not plain-text
lines. This example selects one movie, followed by items expanded from the remote
JSON response. Replace the example URL with your own source.

```yaml
collections:
  Combined Picks:
    text: |-
      tt0079945
      url:https://example.com/additional-items.json
    collection_order: custom
    sync_mode: sync
```

## Files and remote sources {#text-file}

`text_file` accepts a local file path or remote URL, or a YAML list of either.
Each non-empty, non-comment line uses the shared identifier syntax. A remote
source can return plain text or a JSON list, including gzip-compressed JSON.
Use `text_file` rather than `text` when a remote URL returns plain text.

<span id="example-text-file-builders"></span>

=== "Local file"

    Reads IDs from a file maintained separately from this collection definition.
    The value is a path string; file contents determine the selected items.

    ```yaml
    collections:
      Hand-Curated Picks:
        text_file: config/lists/hand-curated.txt
        collection_order: custom
        sync_mode: sync
    ```

=== "Combined local and remote"

    Reads the priority file first, then appends the remote source in its returned
    order. Replace the paths and URL. Source boundaries do not create separate
    builder groups; only the combined item order is retained.

    ```yaml
    collections:
      Combined Text Files:
        text_file:
          - config/lists/priority.txt
          - https://example.com/overflow.txt
        collection_order: custom
        sync_mode: sync
    ```

### File contents {#example-text-file-contents}

This movie-library file mixes IDs, Plex identifiers, a comment, and a JSON source.

```text
# Movie library example
tt0079945 # Star Trek: The Motion Picture
174       # Star Trek VI, assumed TMDb
tmdb:154  # Star Trek II, explicit TMDb
plex://movie/5d7768243c3c2a001fbca85b
5d776824880197001ec901ab
plex:5d7768244de0ee001fcc7ff2
url:https://example.com/list.json
```

## Seasons and episodes {#episode-and-season-part-syntax}

Both builders support show-part collections when `builder_level` is set to
`season` or `episode`.

| Entry | At season level | At episode level |
|:------|:----------------|:-----------------|
| `tvdb_season:12345_1` or `tvdb_season:12345/1` | Selects season 1 | Expands season 1 to every episode |
| `tvdb_episode:12345_1_2`, `tvdb_episode:12345-1-2`, or `tvdb_episode:12345/1/2` | Use episode level | Selects season 1, episode 2 |

`12345` is a show TVDb ID. Repeated references to the same episode are deduplicated.

This episode collection reads exact episodes from a file. For example,
`tvdb_season:383275/1` expands Tracker season 1; `tvdb_episode:383275_1_2` targets
its second episode. IMDb episode IDs, such as `tt22408116`, are also supported.

```yaml
collections:
  Tracker Episodes:
    builder_level: episode
    text_file: config/lists/tracker-episodes.txt
    collection_order: custom
    sync_mode: sync
```

## JSON list format {#json-list-example}

A remote JSON list can mix supported identifiers and show parts. This valid JSON
example demonstrates direct ID fields, a dictionary for an episode, and a typed
ID array. Replace the IDs with your own items.

```json
[
  {"imdb_id": "tt26443597"},
  {"tmdb_id": 83533},
  {"tvdb_season": "12345_1"},
  {"tvdb_episode": {"tvdb_id": 12345, "season": 1, "episode": 2}},
  {"type": "tvdb_episode", "id": [12345, 1, 3]}
]
```
