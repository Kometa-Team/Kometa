---
hide:
  - toc
---
# FlickList List

Finds every item in a FlickList list, or across a FlickList user's public lists.

???+ warning "FlickList Configuration"

    [Configuring FlickList](../../../config/flicklist.md) in the config is required for these builders.

## flicklist_list

The expected input is a FlickList list URL (`https://flicklist.tv/list/4821`) or its bare numeric id (`4821`).
Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

The `sync_mode: sync` and `collection_order: custom` settings are recommended since FlickList lists can be
updated externally and are returned in list order.

???+ tip "Details Builder"

    You can replace `flicklist_list` with `flicklist_list_details` if you would like to fetch and use the
    FlickList list description as the collection summary. Only the first list's description is used when
    multiple lists are given.

### Example FlickList List Builder(s)

```yaml
collections:
  FlickList List:
    flicklist_list: https://flicklist.tv/list/4821
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  FlickList List:
    flicklist_list_details:
      - 4821
      - 9310
    collection_order: custom
    sync_mode: sync
```

## flicklist_user_lists

Finds the union of every item across a named FlickList user's public lists.

The expected input is a FlickList username. This does not require an API key with any particular scope — public
lists are readable without authentication — but Kometa still requires the `flicklist` config block to be present.

A user with many public lists means more requests; Kometa logs how many lists it found for that user before
processing them.

### Example FlickList User Lists Builder

```yaml
collections:
  FlickList Community Picks:
    flicklist_user_lists: some_flicklist_username
    collection_order: custom
    sync_mode: sync
```
