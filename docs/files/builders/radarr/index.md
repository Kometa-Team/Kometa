# Radarr Builders

Select existing Plex movies from [Radarr](https://radarr.video/) records.
These builders do not support playlists or custom sorting.

!!! warning "Configure Radarr first"

    Both builders require [Radarr configuration](../../../config/radarr.md)
    and a movie library for Plex collections. MDBList-only syncing is described below.

## Choose a builder

| Builder | Selects | Value |
|:--------|:--------|:------|
| [`radarr_all`](#radarr-all) | All movies in Radarr | `true` |
| [`radarr_taglist`](#radarr-taglist) | movies selected by Radarr tags | Tag string, YAML list, or blank |

## All movies {#radarr-all}

<span id="example-radarr-all-builders"></span>

Selects all movies tracked in Radarr that can be included from your Plex library.
`true` is an unquoted boolean, rather than a string or a result limit.

```yaml
collections:
  All Radarr Movies:
    radarr_all: true
```

## Tags {#radarr-taglist}

Use a tag string or supply multiple tags as a YAML list or comma-separated
string, such as `"tag1,tag2"`. A blank builder value selects untagged movies.
These are Radarr tags, rather than Plex labels.

<span id="example-radarr-taglist-builders"></span>

=== "Tag names"

    Selects movies using the supplied `tag1` and `tag2` tags. Replace those names
    with your Radarr tags. The YAML list supplies strings; the equivalent
    comma-separated form is `radarr_taglist: "tag1,tag2"`.

    ```yaml
    collections:
      Tagged Radarr Movies:
        radarr_taglist:
          - tag1
          - tag2
    ```

=== "Blank value"

    Selects movies with no Radarr tags. Leaving the value blank has a different
    meaning from passing a tag name or enabling the all-items builder.

    ```yaml
    collections:
      Untagged Radarr Movies:
        radarr_taglist:
    ```

### Sync to MDBList {#sync-to-mdblist}

With [`sync_to_mdb_list`](../../settings.md#mdblist-sync-example), `radarr_taglist`
uses matching Radarr records as the source of truth, even when those items are
not in Plex or no Plex collection is built. Removing a tag in Radarr also removes
the corresponding movie from the MDBList static list.

Only movies are removed by this sync. It can share a list with
[`sonarr_taglist`](../sonarr/index.md#sonarr-taglist) syncing from Sonarr.

This example syncs movies tagged `kometa_test` to the named MDBList static list.
`build_collection: false` disables the Plex collection; it does not disable the
MDBList sync. The tag and destination name are strings; `false` is a boolean.

```yaml
collections:
  Radarr Tag Sync:
    radarr_taglist: kometa_test
    sync_to_mdb_list: My Kometa Test Tags
    build_collection: false
```
