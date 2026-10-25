---
hide:
  - toc
---
# Radarr Taglist

Gets Movies from Radarr based on their tags. 

Set the attribute to the tag you want to search for. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string. 

???+ warning "Radarr Configuration"

    [Configuring Radarr](../../../config/radarr.md) in the config is required for any of these builders.

### Example Radarr Taglist Builder(s)

```yaml
collections:
  Radarr Tag1 and Tag2 Movies:
    radarr_taglist: tag1, tag2
```

If no tag is specified then it gets every Movie without a tag.

```yaml
collections:
  Radarr Movies Without Tags:
    radarr_taglist: 
```

### Export to MDBList

When used with [`list_export`](../../settings.md#list-export), `radarr_taglist`
exports matching movies that Kometa can resolve in Plex. With `mode: sync`,
movies absent from those results are removed from the MDBList list. Use a
separate destination list for [`sonarr_taglist`](../../sonarr/taglist.md),
because sync treats the builder's results as the complete list.

```yaml
collections:
  Radarr Test:
    radarr_taglist: kometa_test
    list_export:
      source: mdblist
      name: My Kometa Test Tags
      mode: sync
    build_collection: false
```
