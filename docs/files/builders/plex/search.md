# Plex Search

Use `plex_search` to select existing library items when Kometa runs. For
Plex-maintained membership that updates as library data changes, use
[Smart Filters](smart-filter.md).

## Query structure

Start with exactly one root `all` (AND) or `any` (OR). Place filters beneath it;
`sort_by`, `limit`, `validate`, and `type` are query options outside that root.
Nest `all` and `any` for complex rules. For repeated group names at the same
level, use a YAML list of groups rather than duplicate dictionary keys.

| Value type | Example | Meaning |
|:-----------|:--------|:--------|
| String | `genre: Action` | Match a genre |
| Boolean | `hdr: true` | Require HDR |
| Number | `audience_rating.gte: 7.5` | Inclusive minimum rating |
| Date | `release.after: 01/01/2020` | Released after the date |
| Relative interval | `added.last: 30` | Added in the last 30 days |

!!! important "Select the item level"

    Use [builder_level](../../settings.md#builder-level) for collections of
    seasons, episodes, albums, or tracks. Filter and sort availability depends
    on the library and selected level; see the references below.

## Plex builder attributes

These options also apply to `smart_filter`:

<!--query-options-start-->
| Attribute | Value | Default |
|:----------|:------|:--------|
| `limit` | `all` or a positive integer | `all` |
| `sort_by` | Supported sort string or YAML list | `random` |
| `validate` | Boolean; whether validation errors fail the collection | `true` |
<!--query-options-end-->

Use `collection_order: custom` to preserve search order in a manual collection,
and `sync_mode: sync` to synchronize membership on Kometa runs.

## Examples {#example-plex-search-builders}

=== "AND / OR"

    The first collection requires both Dave Chappelle and Comedy; the second
    accepts either. Names are strings; `all` and `any` control the logic.

    ```yaml
    collections:
      Dave Chappelle Comedy:
        plex_search:
          all:
            actor: Dave Chappelle
            genre: Comedy

      Dave Chappelle or Comedy:
        plex_search:
          any:
            actor: Dave Chappelle
            genre: Comedy
    ```

=== "Nested logic"

    Requires a year of 2020 or later and either Action or Comedy. The outer
    `all` combines the year rule with the inner `any` group.

    ```yaml
    collections:
      Recent Action or Comedy:
        plex_search:
          all:
            year.gte: 2020
            any:
              genre:
                - Action
                - Comedy
    ```

=== "Boolean, decimal, and limit"

    Selects up to 20 HDR movies rated at least 7.5 by the audience, highest rated
    first. `true` is a boolean, `7.5` is a decimal, and `20` is an integer.

    ```yaml
    collections:
      Highly Rated HDR Movies:
        collection_order: custom
        sync_mode: sync
        plex_search:
          all:
            hdr: true
            audience_rating.gte: 7.5
          sort_by: audience_rating.desc
          limit: 20
    ```

=== "Multiple sort fields"

    Selects up to 20 movies from 2010 onward, sorting by year newest first and
    audience rating within each year. Earlier sort entries take priority.

    ```yaml
    collections:
      Best Recent Movies by Year:
        collection_order: custom
        plex_search:
          all:
            year.gte: 2010
          sort_by:
            - year.desc
            - audience_rating.desc
          limit: 20
    ```

=== "Episode level"

    Selects up to 100 episodes from shows whose title ends in Simpsons, highest
    audience rating first. `builder_level` makes the collection contain episodes;
    `type: episode` selects that search level.

    ```yaml
    collections:
      Top 100 Simpsons Episodes:
        collection_order: custom
        builder_level: episode
        plex_search:
          type: episode
          sort_by: audience_rating.desc
          limit: 100
          all:
            title.ends: "Simpsons"
    ```

### TMDb people

Set `tmdb_person` to TMDb person IDs or URLs, then use `tmdb` as the value for
`actor`, `director`, `producer`, or `writer`. Kometa resolves IDs to names before
searching. The same approach works with `smart_filter`.

Selects movies with Quentin Tarantino in any of the four roles. `138` is a TMDb
person ID; `tmdb` requests name resolution.

```yaml
collections:
  Quentin Tarantino:
    tmdb_person: 138
    plex_search:
      any:
        actor: tmdb
        director: tmdb
        producer: tmdb
        writer: tmdb
```

## Building and checking a query

Use Plex's Advanced Filters UI to check the rules you want to reproduce. For
help, share filter settings in [Discussions](https://github.com/Kometa-Team/Kometa/discussions)
or [Discord](https://kometa.wiki/en/latest/discord/).

{%
    include-markdown "./search-options.md"
  start="<!--shared-content-start-->"
%}

{%
    include-markdown "./sort-options.md"
  start="<!--shared-content-start-->"
%}
