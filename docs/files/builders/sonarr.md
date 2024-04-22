# Sonarr Builders

You can find items in your Plex using the features of [Sonarr](https://sonarr.tv/).

[Configuring Sonarr](../../config/sonarr.md) in the config is required for any of these builders.

| Attribute                           | Description                                  |            Works with Movies             |              Works with Shows              |   Works with Playlists and Custom Sort   |
|:------------------------------------|:---------------------------------------------|:----------------------------------------:|:------------------------------------------:|:----------------------------------------:|
| [`sonarr_all`](#sonarr-all)         | Gets all Series in Sonarr.                   | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| [`sonarr_taglist`](#sonarr-taglist) | Gets Series from Sonarr based on their tags. | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |

## Sonarr All

Gets all Series in Sonarr.

```yaml
collections:
  ALL Sonarr Series:
    sonarr_all: true
```

## Sonarr Taglist

Gets Series from Sonarr based on their tags. 

Set the attribute to the tag you want to search for. Multiple values are supported as either a list or a comma-separated 
string. 

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