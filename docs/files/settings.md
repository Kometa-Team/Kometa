---
search:
  boost: 3
hide:
  - tags
tags:
  - addons
  - name
  - limit
  - template
  - schedule
  - run_again
  - sync_mode
  - builder_level
  - minimum_items
  - delete_below_minimum
  - delete_not_scheduled
  - tmdb_region
  - validate_builders
  - cache_builders
  - blank_collection
  - build_collection
  - server_preroll
  - missing_only_released
  - only_filter_missing
  - show_filtered
  - show_unfiltered
  - show_missing
  - save_report
  - ignore_ids
  - ignore_imdb_ids
  - name_mapping
  - test
  - tmdb_birthday
  - changes_webhooks
  - sync_to_mdb_list
  - sync_to_flicklist_list
  - sync_missing_to_flicklist_list
  - sync_to_wetrakr_list
  - sync_missing_to_wetrakr_list
  - run_definition
  - default_percent
  - ignore_blank_results
  - only_run_on_create
  - delete_collections_named
---

# Definition Options

Control how an individual collection, playlist, or overlay definition runs and
handles its results. Place options beside the builder, not inside its dictionary.
Availability varies by option; collection-only restrictions are noted below.

## Quick start

Selects Action movies, caps the definition at 50 items, and synchronizes membership
on each run. `50` is an integer; `sync` is a mode string. The name shown in Plex
is different from the YAML mapping key.

```yaml
collections:
  Weekly Action:
    name: Action Picks
    plex_search:
      all:
        genre: Action
    limit: 50
    sync_mode: sync
```

## Option reference

**Inherited** means the same-named setting from the
[configuration settings](../config/settings.md) is used unless overridden here.
A dash means this page does not specify a default. Booleans use unquoted `true`
or `false`; names, IDs, and paths use the value forms indicated.

### Names and templates

| Attribute | Value | Default | Purpose |
|:----------|:------|:--------|:--------|
| `name` | String | - | Name displayed in Plex instead of the YAML mapping key. |
| `name_mapping` | String | - | Filesystem asset name when the definition name contains invalid path characters. See [image assets](../kometa/guides/assets.md). |
| `template` | Dictionary | - | Template and variables for this definition; see [templates](templates.md). |

### Collection creation and membership

| Attribute | Value | Default | Purpose |
|:----------|:------|:--------|:--------|
| `blank_collection` | Boolean | `false` | Create an empty collection without builders or added items. |
| `build_collection` | Boolean | `true` | If false, do not create the collection; Radarr/Sonarr additions can still run. Not supported for playlists. |
| <span id="builder-level"></span>`builder_level` | `season`, `episode`, `album`, `track` | - | Select the item level for compatible collections/overlays, builders, and filters; originally supported by `plex_all`, `plex_search`, and `imdb_list`. Check individual builders for other supported levels. |
| `limit` | Positive number | - | Maximum items in the definition. |
| `minimum_items` | Positive number | Inherited | Minimum items required before adding to the definition. |
| `sync_mode` | `sync`, `append` | Inherited | Control builder membership syncing; see [sync mode](../config/settings.md#sync-mode). |
| `default_percent` | Integer, 1-100 | `50` | Default threshold for child-item special filters; see [example](#default-percent-example). |
| `smart_label` | Sort string or dictionary | - | Label builder results to create a [smart collection](#smart-label-definitions). |

### Scheduling and execution

| Attribute | Value | Default | Purpose |
|:----------|:------|:--------|:--------|
| `schedule` | [Schedule option](../config/schedule.md) | `daily` | When to run; defaults to daily. |
| `run_definition` | Boolean, library type, or list | - | Run conditions; one false or mismatched type prevents a run. See [run conditions](#scheduling-and-run-conditions). |
| `only_run_on_create` | Boolean | `false` | Run only if the collection does not already exist. |
| `run_again` | Boolean | `false` | Try adding missing items again after the daily run. |
| `cache_builders` | Number, 0 or greater | `0` | Cache builder results for this many days. `1` is useful across libraries/servers in the same run. |
| `test` | Boolean | `false` | Select this definition for `--run-tests` test mode. |
| `tmdb_birthday` | Date-condition dictionary | - | Run relative to the TMDb person birthday. |
| `tmdb_deathday` | Date-condition dictionary | - | Run relative to the TMDb person deathday. |

### Errors, exclusions, and missing items

| Attribute | Value | Default | Purpose |
|:----------|:------|:--------|:--------|
| `ignore_blank_results` | Boolean | `false` | Suppress errors caused by blank builder results. |
| `validate_builders` | Boolean | `true` | If false, a failed builder does not fail the definition. |
| `ignore_ids` | YAML list or comma-separated TMDb/TVDb IDs | Inherited | Combine with library and global ignore IDs. |
| `ignore_imdb_ids` | YAML list or comma-separated IMDb IDs | Inherited | Combine with library and global ignored IMDb IDs. |
| `missing_only_released` | Boolean | Inherited | Exclude unreleased items from missing-item lists. |
| `only_filter_missing` | Boolean | Inherited | Apply filters only to missing items. |
| `delete_below_minimum` | Boolean | Inherited | Delete when results fall below the minimum. |
| `delete_not_scheduled` | Boolean | Inherited | Delete when skipped because the definition is not scheduled. |
| `delete_collections_named` | YAML list of names | - | Delete Plex collections with the given names. |

### Reports, artwork, and server actions

| Attribute | Value | Default | Purpose |
|:----------|:------|:--------|:--------|
| `show_filtered` | Boolean | Inherited | Display items rejected by filters. |
| `show_unfiltered` | Boolean | Inherited | Display items that pass filters. |
| `show_missing` | Boolean | Inherited | Display missing items. |
| `save_report` | Boolean | Inherited | Save a report for this definition. |
| `changes_webhooks` | YAML list of webhooks | - | Override definition-change webhooks for this definition. |
| `hub_priority` | Positive integer | None | Order a promoted collection hub; see [requirements](#hub-priority). |
| `tmdb_region` | Region value | - | Set the region for `tmdb_popular`, `tmdb_now_playing`, `tmdb_top_rated`, and `tmdb_upcoming`. |
| `server_preroll` | String, list, or nested list | - | Set Plex Movie pre-roll video; see [examples](#server-preroll-example). |

### External list destinations

| Attribute | Value | Default | Purpose |
|:----------|:------|:--------|:--------|
| `sync_to_mdb_list` | Name or dictionary | - | Sync movie/show results to an MDBList static list; [example](#mdblist-sync-example). |
| `sync_to_flicklist_list` | Numeric ID or exact name | - | Sync to one of your FlickList lists; [example](#flicklist-sync-example). |
| `sync_missing_to_flicklist_list` | Boolean | `false` | Also sync missing items to the selected FlickList destination. |
| `sync_to_wetrakr_list` | Numeric ID or exact name | - | Sync to one of your WeTrakr lists; [example](#wetrakr-sync-example). |
| `sync_missing_to_wetrakr_list` | Boolean | `false` | Also sync missing items to the selected WeTrakr destination. |

For asset filenames, `name_mapping` can replace characters that are invalid in a
path while `name` keeps the desired Plex display title. Windows filenames cannot
contain `<`, `>`, `:`, `"`, `/`, `\`, `?`, or `*`.

## Artwork overrides {#asset-directory}

`asset_directory` overrides artwork directories for one collection. It accepts
an existing directory, a list of directories, or a mapping with `movies`, `shows`,
`music`, and `collections` keys. All accepted forms affect **only the collection's
own artwork**, not `item_assets` directories. Media-type keys choose artwork
according to the library type.

Explicit overrides use the collection name or `name_mapping` for asset names.
Empty values inherit the collection-file, library, or global setting; when none
is configured, the existing `asset_directory` applies. See
[collection asset settings](../config/settings.md#asset-directory) for layout and
download behaviour.

This collection uses the specified directory for its own artwork. Replace it
with an existing directory; the dictionary does not relocate artwork for the
movies selected by `plex_all`.

```yaml
collections:
  My Collection:
    asset_directory:
      collections: config/assets/my_collection_artwork
    plex_all: true
```

## Scheduling and run conditions

`run_definition` accepts `movie`, `show`, `artist`, `true`, or `false`, as a single
value, YAML list, or comma-separated string. **One `false` or unmatched library
type prevents the definition from running.**

`tmdb_birthday` and `tmdb_deathday` use the dates for `tmdb_person`. Each accepts
`this_month` as a boolean and `before` / `after` as numbers of days, zero or greater.

This example runs an actor collection during their birthday month. `this_month`
is a nested boolean; `2157` identifies Robin Williams on TMDb. The definition
also includes its builder, rather than relying on the date option to select items.

```yaml
collections:
  Robin Williams Birthday Month:
    tmdb_person: 2157
    tmdb_birthday:
      this_month: true
    tmdb_actor: 2157
```

`test: true` selects a definition when running in
[test mode](../kometa/environmental.md) (`--run-tests`); definitions without that
flag are skipped in test mode.

## Hub priority

`hub_priority` requires the collection to be promoted through `visible_library`,
`visible_home`, or `visible_shared`, and requires Plex Pass. Lower positive
numbers appear first, before any `auto_sort_hubs` ordering.

Hub sorting, including priority, is skipped for targeted `--run-collections` or
`--run-files` runs because those runs do not know every collection's priority.

## External list syncing

These options sync movie/show results to external lists. They are separate from
`sync_mode`, which controls membership in the Kometa definition.

### MDBList sync example

`sync_to_mdb_list` finds a static list by **exact name**, creating it if absent.
Use a name string or a dictionary containing `name` and optional `mode`.
`mode: sync` is the default: it adds missing items and removes entries no longer
present. `append` adds without removing existing entries.

=== "Synchronize by name"

    Syncs movies added in the last 30 days to the named MDBList static list.
    The name is a string; list membership is updated, rather than merely appended.

    ```yaml
    collections:
      Recently Added:
        plex_search:
          all:
            added: 30
        sync_to_mdb_list: "Recently Added"
    ```

=== "Append dictionary"

    Adds movies with a user rating of at least 8 to the Favourites list without
    removing older entries. `mode: append` applies to MDBList, not the Plex collection.

    ```yaml
    collections:
      Favourites:
        plex_search:
          all:
            user_rating.gte: 8.0
        sync_to_mdb_list:
          name: "Favourites"
          mode: append
    ```

### FlickList sync example

`sync_to_flicklist_list` accepts a numeric list ID or exact name among your own
FlickList lists. A matching list is reused; a list is created if no match exists.

Selects recently added items and syncs them to the named list. The boolean
`sync_missing_to_flicklist_list` also enables syncing missing items.

```yaml
collections:
  Recent FlickList Picks:
    plex_search:
      all:
        added: 30
    sync_to_flicklist_list: "Recently Added"
    sync_missing_to_flicklist_list: true
```

### WeTrakr sync example

`sync_to_wetrakr_list` also accepts a numeric list ID or exact name among your own
lists, reusing a match or creating a list when no match exists. Free accounts are
limited to **5 lists of 250 items each**. Exceeding either limit produces the
account's upgrade message.

This example uses a numeric ID instead of a list-name string. Replace `13255`
with one of your own list IDs. Missing items are included when the boolean is enabled.

```yaml
collections:
  Recent WeTrakr Picks:
    plex_search:
      all:
        added: 30
    sync_to_wetrakr_list: 13255
    sync_missing_to_wetrakr_list: true
```

!!! note "FlickList and WeTrakr sync limits"

    Both support movies and shows; season/episode collections are skipped with
    one warning. Neither preserves the collection's custom order on the remote
    side. Existing remote items that cannot be confidently matched are left
    in place, rather than removed. Missing-item syncing defaults to `false`.

## Smart label definitions

Smart labels use non-Plex builder results to create a Plex smart collection.
Kometa labels each selected item, then creates a smart filter for that label.
Plex reevaluates the filter as labels change; **the external source is not fetched
again until Kometa runs**. Users can also add or remove the label themselves.

=== "Sort string"

    Fetches the MCU list, applies a label matching the collection name to its
    items, and creates a smart collection ordered by release date, newest first.

    ```yaml
    collections:
      Marvel Cinematic Universe:
        mdblist_list: https://mdblist.com/lists/stealthgyro/marvel-cinematic-universe-mcu
        smart_label: release.desc
    ```

=== "Expanded dictionary"

    Has the same effect as the short form. `<<smart_label>>` resolves to the
    collection's label, here Marvel Cinematic Universe.

    ```yaml
    collections:
      Marvel Cinematic Universe:
        mdblist_list: https://mdblist.com/lists/stealthgyro/marvel-cinematic-universe-mcu
        smart_label:
          sort_by: release.desc
          all:
            label: <<smart_label>>
    ```

=== "Additional rules"

    Labels items from the same source, then shows only unplayed items featuring
    Robert Downey Jr. The label follows this collection's longer name. `true`
    is a boolean; the actor name is a string filter.

    ```yaml
    collections:
      Unplayed MCU With Robert Downey Jr:
        mdblist_list: https://mdblist.com/lists/stealthgyro/marvel-cinematic-universe-mcu
        smart_label:
          sort_by: release.desc
          all:
            label: <<smart_label>>
            unplayed: true
            actor: "Robert Downey Jr."
    ```

### Smart labels & Plex collectionless

Smart collections avoid the usual manual-collection show/hide rules and can
resolve [collectionless display issues](builders/plex/builders.md#plex-collectionless).
Use the method consistently: a useful rule is no more than one manual collection
per library item, with broader groups implemented as smart labels.

Smart collections cannot use `custom` sorting to preserve the external builder's
order. If you need that order together with collection visibility handling, use
[Plex Collectionless](builders/plex/builders.md#plex-collectionless) instead.

## Default percent example

`default_percent` sets the threshold for `episodes`, `seasons`, `tracks`, and
`albums` [special filters](filters.md#special-filters) when they do not specify a
threshold. It defaults to 50 and accepts integers from 1 through 100.

This collection requires at least 35% of a show's episodes to have a user rating
of 7 or higher. `35` is a percentage, while `7` is the nested rating threshold.
The option belongs in the definition file, not `config.yml`.

```yaml
collections:
  Shows With Rated Episodes:
    plex_all: true
    default_percent: 35
    filters:
      episodes:
        user_rating.gte: 7
```

## Server preroll example

`server_preroll` sets Plex's **Movie pre-roll video** field under Settings > Extras.
Use it with a schedule to change prerolls over the year. Place this in a definition
file, not `config.yml`; `build_collection: false` avoids creating a Plex collection.
Use file paths appropriate to your Plex server. See [Plex Extras](https://support.plex.tv/articles/202920803-extras/).

=== "Scheduled strings"

    Uses one January preroll, a different base selection from February through
    November, and another for December. The schedules are strings; `false`
    disables collection creation while leaving the preroll action available.

    ```yaml
    collections:
      January Preroll:
        build_collection: false
        server_preroll: /media/prerolls/january.mp4
        schedule: range(01/01-01/31)
      Base Preroll:
        build_collection: false
        server_preroll: /media/prerolls/base1.mp4;/media/prerolls/base2.mp4
        schedule: range(02/01-11/30)
      December Preroll:
        build_collection: false
        server_preroll: /media/prerolls/december.mp4
        schedule: range(12/01-12/31)
    ```

=== "Choose one"

    A flat YAML list becomes semicolon-separated choices. Plex plays one of
    these files before the movie, rather than playing all of them.

    ```yaml
    collections:
      Random Preroll:
        build_collection: false
        server_preroll:
          - /media/prerolls/file1.mp4
          - /media/prerolls/file2.mp4
          - /media/prerolls/file3.mp4
    ```

=== "Play all"

    One nested list becomes a comma-separated sequence. Plex plays all three
    files in order. The double dash starts a list inside the outer list.

    ```yaml
    collections:
      Preroll Sequence:
        build_collection: false
        server_preroll:
          - - /media/prerolls/file1.mp4
            - /media/prerolls/file2.mp4
            - /media/prerolls/file3.mp4
    ```

=== "Mixed choices"

    Plex chooses file1, both file2 and file3, or file4. Top-level entries become
    semicolon-separated choices; the nested list becomes a comma-separated sequence.

    ```yaml
    collections:
      Mixed Prerolls:
        build_collection: false
        server_preroll:
          - /media/prerolls/file1.mp4
          - - /media/prerolls/file2.mp4
            - /media/prerolls/file3.mp4
          - /media/prerolls/file4.mp4
    ```

The mixed form produces
`/media/prerolls/file1.mp4;/media/prerolls/file2.mp4,/media/prerolls/file3.mp4;/media/prerolls/file4.mp4`.
