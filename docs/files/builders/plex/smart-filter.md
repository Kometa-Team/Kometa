# Plex Smart Filters

Use `smart_filter` to create a collection whose rules Plex reevaluates as library
data changes. New matching items do not need another Kometa run to join.
Use [Plex Search](search.md) for a manual collection updated on Kometa runs.

!!! important "Music smart playlists"

    Under `music_playlists`, `smart_filter` creates a smart playlist within a
    Music library. It is not supported in regular cross-library Playlist Files.
    Music smart playlists always contain tracks, even when filtering artist-
    or album-level fields.

## Filter structure

Start with exactly one root `all` (AND) or `any` (OR), placing filters beneath it.
Nest these groups for complex rules; use a YAML list if a group name must appear
more than once at the same level. See [query structure](search.md#query-structure)
for the shared syntax and [TMDb people](search.md#tmdb-people) for person-ID resolution.

### Plex builder attributes

Query options sit outside the `all` / `any` group:

{%
    include-markdown "./search.md"
    start="<!--query-options-start-->"
    end="<!--query-options-end-->"
%}

For collections of seasons, episodes, albums, or tracks, set
[builder_level](../../settings.md#builder-level) to the required level.
Smart filters suit membership criteria available entirely within Plex.

## Examples {#example-smart-filter-builders}

=== "AND / OR"

    The first collection requires both Dave Chappelle and Comedy; the second
    accepts either. Plex reevaluates these rules as library metadata changes.

    ```yaml
    collections:
      Dave Chappelle Comedy:
        smart_filter:
          all:
            actor: Dave Chappelle
            genre: Comedy

      Dave Chappelle or Comedy:
        smart_filter:
          any:
            actor: Dave Chappelle
            genre: Comedy
    ```

=== "Date and boolean"

    Includes unplayed movies released after January 1, 2020. The date uses
    `MM/DD/YYYY`; `true` is an unquoted boolean. Changes to play state can change
    membership without a Kometa run.

    ```yaml
    collections:
      Unplayed Recent Movies:
        smart_filter:
          all:
            release.after: 01/01/2020
            unplayed: true
    ```

=== "Rating and limit"

    Shows up to 20 Action movies with an audience rating of at least 7.5, highest
    rating first. The decimal is a minimum rating; the integer limits results.

    ```yaml
    collections:
      Top Action Movies:
        smart_filter:
          all:
            genre: Action
            audience_rating.gte: 7.5
          sort_by: audience_rating.desc
          limit: 20
    ```

=== "Folder exclusion"

    Includes movies outside the configured `/media/movies` library root. `.not`
    excludes that root folder. Plex does not expose nested subfolders as Folder
    Location choices.

    ```yaml
    collections:
      Movies Outside Main Folder:
        smart_filter:
          all:
            folder_location.not: /media/movies
    ```

=== "Decade"

    Includes movies from the 1990s using one numeric value instead of a list of
    ten years. `decade` takes no modifier.

    ```yaml
    collections:
      90s Movies:
        smart_filter:
          any:
            decade: 1990
    ```

## Music filters and smart playlists

In Music, `label` matches the selected item type: `artist_label`, `album_label`,
or `track_label`. The type-specific names can also be used directly.
Artist- or album-level rules, such as `artist_mood`, apply to tracks in music
smart playlists. Kometa's **Items Found** count can report artist or album titles
for those filters, even though the playlist contains tracks.

=== "Exact skip count"

    Creates a Music smart playlist of tracks with exactly one skip. Numeric
    music filters use comparison modifiers: `.is` means equal to the integer,
    rather than a boolean switch.

    ```yaml
    music_playlists:
      Skipped Tracks:
        smart_filter:
          type: track
          all:
            track_skips.is: 1
    ```

=== "Track collection and folder"

    Creates a track collection from the configured music-archive root folder.
    Music `folder_location` filtering requires track level; this example is a
    collection, rather than a Music smart playlist.

    ```yaml
    collections:
      Music From Archive Folder:
        builder_level: track
        smart_filter:
          all:
            folder_location: /media/music-archive
    ```

{%
    include-markdown "./search-options.md"
    start="<!--shared-content-start-->"
%}

{%
    include-markdown "./sort-options.md"
    start="<!--shared-content-start-->"
%}
