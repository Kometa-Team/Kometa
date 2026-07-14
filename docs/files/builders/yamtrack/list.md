---
hide:
  - toc
---
# YamTrack List

Finds every item in the YamTrack List.

The expected input is a YamTrack List URL from the configured YamTrack instance. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists can be updated in YamTrack and are returned in list order.

???+ warning "YamTrack Configuration"

    [Configuring YamTrack](../../../config/yamtrack.md) in the config is required for any of these builders.

???+ tip "Details Builder"

    You can replace `yamtrack_list` with `yamtrack_list_details` if you would like to fetch and use the YamTrack list description as the collection summary.

### Example YamTrack List Builder(s)

```yaml
collections:
  YamTrack List:
    yamtrack_list: https://yamtrack.domain.com/list/1
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  YamTrack List:
    yamtrack_list_details:
      - https://yamtrack.domain.com/list/1
    collection_order: custom
    sync_mode: sync
```

* You can update the collection summary with the YamTrack list description by using `yamtrack_list_details`.
* You can specify multiple lists in `yamtrack_list_details`, but only the first one is used to update the collection summary.
