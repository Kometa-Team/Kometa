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