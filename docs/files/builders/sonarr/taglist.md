---
hide:
  - toc
---
# Sonarr Taglist

Gets Series from Sonarr based on their tags. 

Set the attribute to the tag you want to search for. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated 
string. 

???+ warning "Sonarr Configuration"

    [Configuring Sonarr](../../../config/sonarr.md) in the config is required for any of these builders.

### Example Sonarr Taglist Builder(s)

```yaml
collections:
  Sonarr Tag1 and Tag2 Series:
    sonarr_taglist: tag1, tag2
```

If no tag is specified then it gets every Movie without a tag.

```yaml
collections:
  Sonarr Series Without Tags:
    sonarr_taglist: 
```