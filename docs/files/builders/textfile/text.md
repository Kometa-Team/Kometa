---
hide:
  - toc
---
# Text

Finds items using IDs written directly in the collection or playlist YAML. It supports the same identifier syntax as the [`text_file`](text-file.md) builder without requiring a separate file.

The builder accepts a scalar string or integer, a literal multiline string, or a list of strings and integers. Entries are processed in their declared order.

The `sync_mode: sync` and `collection_order: custom` settings are recommended when you want the collection and its order to exactly match the inline source.

## Supported Values

Each entry can contain one of the following:

- a TMDb ID
- a TVDb ID
- an IMDb ID or IMDb title URL
- a URL returning a JSON list of supported items
- `plex://movie/<24-char-id>`
- `plex://show/<24-char-id>`
- `plex://episode/<24-char-id>`
- a bare 24-character Plex metadata ID
- an explicit typed value such as `imdb:`, `tmdb:`, `tvdb:`, `tvdb_season:`, `tvdb_episode:`, `plex:`, or `url:`

Blank lines and lines beginning with `#` are ignored. Literal multiline strings can also contain trailing inline comments introduced by whitespace followed by `#`.

Numeric entries are interpreted by library type:

- Movie libraries: TMDb IDs
- Show libraries: TVDb IDs
- Playlists or mixed/unknown contexts: generic numeric IDs matched against the available movie/show libraries

On show libraries, `text` can be used with `builder_level: season` or `builder_level: episode`. The `tvdb_season` and `tvdb_episode` forms described in the [`text_file` documentation](text-file.md#episode-and-season-part-syntax) target the corresponding show parts.

## Single Value

```yaml
collections:
  Star Trek:
    text: tt0079945 # Star Trek: The Motion Picture
    collection_order: custom
    sync_mode: sync
```

YAML removes the trailing comment from a scalar or list value before Kometa receives it.

An unquoted numeric ID is also accepted:

```yaml
collections:
  Star Trek VI:
    text: 174
```

## Multiline String

Use YAML's literal `|` or `|-` block style so each identifier remains on its own line:

```yaml
collections:
  Star Trek Movies:
    text: |-
      tt0079945   # Star Trek: The Motion Picture IMDb
      174         # Star Trek VI: The Undiscovered Country assumed TMDb
      tmdb:154    # Star Trek II: The Wrath of Khan unambiguous TMDb
      plex://movie/5d7768243c3c2a001fbca85b # Plex movie GUID
      5d776824880197001ec901ab              # Plex movie GUID
    collection_order: custom
    sync_mode: sync
```

Do not use YAML's folded `>` block style. Folded blocks replace line breaks with spaces, which destroys the one-entry-per-line structure. `>|` is not valid YAML syntax.

## YAML List

```yaml
collections:
  Star Trek Movies:
    text:
      - tt0079945
      - 174
      - tmdb:154
      - plex://movie/5d7768243c3c2a001fbca85b
      - 5d776824880197001ec901ab
    collection_order: custom
    sync_mode: sync
```

List entries may be strings or integers. Quote Plex metadata IDs if YAML could interpret the value as a number or discard leading zeroes.

## Playlist Example

```yaml
playlists:
  Mixed Watchlist:
    text: |-
      tt0079945
      tmdb:154
      tvdb:361702
      plex://show/63e3eedd166819851638a316
    sync_mode: sync
```

In a playlist, `tmdb:` entries are considered as both movie and show IDs so mixed item types retain their declared order. Only the type that resolves on the configured Plex libraries is added.

## URL Entries

A URL within `text` must return a JSON list in the format supported by [`text_file`](text-file.md#json-list-example):

```yaml
collections:
  Combined List:
    text: |-
      tt0079945
      url:https://example.com/additional-items.json
```

Use `text_file` when the remote URL returns plain-text lines rather than a JSON list.
