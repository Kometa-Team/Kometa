# StevenLu Builders

Follow [StevenLu's Popular Movies list](https://movies.stevenlu.com/) with
`stevenlu_popular`. This builder supports **movies, playlists, and custom sorting**;
it does not support shows.

## Popular movies {#stevenlus-popular-movies-list}

Set `stevenlu_popular` to the unquoted boolean `true` to select every movie on the
list. The builder takes no IDs, URLs, filters, or result limit.

## Example {#example-stevenlus-popular-movies-list-builders}

This collection follows StevenLu's popular movies. `collection_order: custom`
preserves the source list's order; `sync_mode: sync` adds and removes collection
members to match the changing list.

```yaml
collections:
  StevenLu's Popular Movies:
    stevenlu_popular: true
    collection_order: custom
    sync_mode: sync
```
