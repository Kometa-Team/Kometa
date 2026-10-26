# Sonarr Builders

Select existing Plex series from [Sonarr](https://sonarr.tv/) records.
These builders do not support playlists or custom sorting.

!!! warning "Configure Sonarr first"

    Both builders require [Sonarr configuration](../../../config/sonarr.md)
    and a show library for Plex collections. MDBList-only syncing is described below.

## Choose a builder

| Builder | Selects | Value |
|:--------|:--------|:------|
| [`sonarr_all`](#sonarr-all) | All series in Sonarr | `true` |
| [`sonarr_taglist`](#sonarr-taglist) | series selected by Sonarr tags | Tag string, YAML list, or blank |

## All series {#sonarr-all}

<span id="example-sonarr-all-builders"></span>

Selects all series tracked in Sonarr that can be included from your Plex library.
`true` is an unquoted boolean, rather than a string or a result limit.

```yaml
collections:
  All Sonarr Series:
    sonarr_all: true
```

## Tags {#sonarr-taglist}

Use a tag string or supply multiple tags as a YAML list or comma-separated
string, such as `"tag1,tag2"`. A blank builder value selects untagged series.
These are Sonarr tags, rather than Plex labels.

<span id="example-sonarr-taglist-builders"></span>

=== "Tag names"

    Selects series using the supplied `tag1` and `tag2` tags. Replace those names
    with your Sonarr tags. The YAML list supplies strings; the equivalent
    comma-separated form is `sonarr_taglist: "tag1,tag2"`.

    ```yaml
    collections:
      Tagged Sonarr Series:
        sonarr_taglist:
          - tag1
          - tag2
    ```

=== "Blank value"

    Selects series with no Sonarr tags. Leaving the value blank has a different
    meaning from passing a tag name or enabling the all-items builder.

    ```yaml
    collections:
      Untagged Sonarr Series:
        sonarr_taglist:
    ```

### Sync to MDBList {#sync-to-mdblist}

With [`sync_to_mdb_list`](../../settings.md#mdblist-sync-example), `sonarr_taglist`
uses matching Sonarr records as the source of truth, even when those items are
not in Plex or no Plex collection is built. Removing a tag in Sonarr also removes
the corresponding series from the MDBList static list.

Only series are removed by this sync. It can share a list with
[`radarr_taglist`](../radarr/index.md#radarr-taglist) syncing from Radarr.

This example syncs series tagged `kometa_test` to the named MDBList static list.
`build_collection: false` disables the Plex collection; it does not disable the
MDBList sync. The tag and destination name are strings; `false` is a boolean.

```yaml
collections:
  Sonarr Tag Sync:
    sonarr_taglist: kometa_test
    sync_to_mdb_list: My Kometa Test Tags
    build_collection: false
```
