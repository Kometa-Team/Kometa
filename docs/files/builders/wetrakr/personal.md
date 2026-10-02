---
hide:
  - toc
---
# WeTrakr Personal Data

Finds items from the configured WeTrakr account's own tracking list or favorites.

???+ warning "WeTrakr Configuration"

    [Configuring WeTrakr](../../../config/wetrakr.md) in the config is required for these builders. Each of
    these builders reads the personal data of whichever WeTrakr account the configured `authorization` belongs to.

## wetrakr_tracking

WeTrakr's tracking list carries one of six statuses per item: `planning`, `watching`, `waiting`, `watched`,
`paused`, `dropped`. A blank value or `true` includes every status valid for the library type; `false` disables
the builder entirely; an object lets you pick specific statuses.

```yaml
collections:
  WeTrakr Tracking:
    wetrakr_tracking:
    collection_order: custom
    sync_mode: sync

  WeTrakr Currently Watching:
    wetrakr_tracking:
      watching: true
    collection_order: custom
    sync_mode: sync
```

Movie libraries only ever request the `planning`, `watched`, and `dropped` statuses — `watching`, `waiting`, and
`paused` are show-only concepts and are skipped automatically for movie libraries.

## wetrakr_favorites

Accepts a blank value or `true`:

```yaml
collections:
  WeTrakr Favorites:
    wetrakr_favorites:
    collection_order: custom
    sync_mode: sync
```

| Builder             | Blank/`true` means                              | Also accepts             | Library restriction |
|:---------------------|:-------------------------------------------------|:--------------------------|:---------------------|
| `wetrakr_tracking`   | Every status valid for the library type          | Object of specific statuses, or `false` | Movies and Shows    |
| `wetrakr_favorites`  | Entire favorites list                            | —                          | Movies and Shows    |
