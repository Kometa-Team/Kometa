---
hide:
  - toc
---
# Floppy List

Finds every supported movie, show, or episode in a Floppy list. The expected input is a list URL from the configured Floppy instance. Multiple URLs are supported. Episode entries require `builder_level: episode` and are added as the exact listed episodes.

Public lists work without a token. Episode collections read exact episode entries from the list RSS feed. Private lists require an API token in the [Floppy connector](../../../config/floppy.md). Use `floppy_list_details` to copy the Floppy list description to the Plex collection summary.

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
