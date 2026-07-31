---
search:
  boost: 2
---

# Serializd List

The `serializd_list` builder finds every show in a public Serializd list.

```yaml
collections:
  Live Action Ranked:
    serializd_list: https://www.serializd.com/list/live-action-ranked-662885
    collection_order: custom
    sync_mode: sync
```

Multiple list URLs can be supplied as a YAML list. Items retain the order returned by Serializd.
