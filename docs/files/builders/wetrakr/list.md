---
hide:
  - toc
---
# WeTrakr List

Finds every item in a WeTrakr list, or across a WeTrakr user's public lists.

???+ warning "WeTrakr Configuration"

    [Configuring WeTrakr](../../../config/wetrakr.md) in the config is required for these builders.

## wetrakr_list

The expected input is a WeTrakr list URL (`https://wetrakr.com/lists/13255`) or its bare numeric id (`13255`).
Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

The `sync_mode: sync` and `collection_order: custom` settings are recommended since WeTrakr lists can be
updated externally and are returned in list order.

Private and friends-only lists are only readable when they belong to the authenticated WeTrakr account; a
private list belonging to someone else returns an error naming the list.

???+ tip "Details Builder"

    You can replace `wetrakr_list` with `wetrakr_list_details` if you would like to fetch and use the
    WeTrakr list description as the collection summary. Only the first list's description is used when
    multiple lists are given.

### Example WeTrakr List Builder(s)

```yaml
collections:
  WeTrakr List:
    wetrakr_list: https://wetrakr.com/lists/13255
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  WeTrakr List:
    wetrakr_list_details:
      - 13255
      - 1033032976
    collection_order: custom
    sync_mode: sync
```

## wetrakr_user_lists

Finds the union of every item across a WeTrakr user's public lists.

The expected input is the user's **numeric WeTrakr user id**, not a username or profile URL — WeTrakr profile
URLs (`wetrakr.com/user/<username>`) are username-based and cannot currently be resolved to a numeric id. See
the [known limitation](../../../config/wetrakr.md#known-limitation) on the config page.

A user with many public lists means more requests; Kometa logs how many lists it found for that user before
processing them. Locked or non-public lists in that user's list collection are skipped automatically.

### Example WeTrakr User Lists Builder

```yaml
collections:
  WeTrakr Community Picks:
    wetrakr_user_lists: 275
    collection_order: custom
    sync_mode: sync
```
