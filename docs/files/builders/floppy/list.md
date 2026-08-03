---
hide:
  - toc
---
# Floppy List

Finds every supported movie or show in a Floppy list. The expected input is a list URL from the configured Floppy instance. Multiple URLs are supported.

Public lists work without a token. Private lists require an API token in the [Floppy connector](../../../config/floppy.md). Use `floppy_list_details` to copy the Floppy list description to the Plex collection summary.

Each list also accepts an optional `sync_tags` attribute. When enabled, the Floppy list tags are added as Plex labels to the items in the resulting collection.

The `sync_mode: sync` and `collection_order: custom` settings are recommended because Floppy lists can change and their list order is preserved.

```yaml
collections:
  Floppy List:
    floppy_list_details:
      url: https://floppy.example.com/list/1
      sync_tags: true
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  Floppy Lists:
    floppy_list:
      - url: https://floppy.example.com/list/1
        sync_tags: false
      - url: https://floppy.example.com/list/2
        sync_tags: true
    collection_order: custom
    sync_mode: sync
```
