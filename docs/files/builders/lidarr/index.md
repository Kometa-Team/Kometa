# Lidarr Builders

Create artist collections from artists already tracked in Lidarr and matched
to your Plex library.

!!! warning "Configure Lidarr first"

    Both builders require a [Lidarr connection](../../../config/lidarr.md)
    and a Plex Music library. These collections contain artists, rather than
    individual albums or tracks.

## Choose a builder

| Builder | Selects | Value |
|:--------|:--------|:------|
| [`lidarr_all`](#lidarr-all) | Every artist tracked in Lidarr | `true` |
| [`lidarr_taglist`](#lidarr-taglist) | Artists with all supplied Lidarr tags | Tag names, or blank for untagged artists |

## All artists {#lidarr-all}

Selects all tracked Lidarr artists that match your Plex library. `true` is an
unquoted boolean. `sync_mode: sync` keeps collection membership synchronized on
Kometa runs.

```yaml
collections:
  All Lidarr Artists:
    lidarr_all: true
    sync_mode: sync
```

## Tags {#lidarr-taglist}

Pass the Lidarr tag names as a comma-separated string. **Every supplied tag must
match (AND)**. Leave the value blank to select artists without tags.

=== "Multiple tags"

    Selects artists carrying both `kometa` and `favorites` in Lidarr. The quoted
    value is one comma-separated string, rather than a boolean or a numeric ID.

    ```yaml
    collections:
      Favorite Kometa Artists:
        lidarr_taglist: "kometa,favorites"
    ```

=== "Blank value"

    Selects Lidarr artists with no tags. The blank value requests untagged
    artists; it does not select every tracked artist.

    ```yaml
    collections:
      Untagged Lidarr Artists:
        lidarr_taglist:
    ```

## Artist matching

Kometa first matches each Lidarr MusicBrainz artist ID to a Plex `mbid://` GUID.
If the ID cannot identify one artist, it accepts an exact, case-insensitive
artist-name match only when unique in Plex. Missing or ambiguous artists are
reported as missing and are not added to the collection.
