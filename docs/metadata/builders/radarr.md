# Radarr Builders

You can find items in your Plex using the features of [Radarr](https://radarr.video/).

[Configuring Radarr](../../config/radarr) in the config is required for any of these builders.

| Attribute                           | Description                                  | Works with Movies | Works with Shows | Works with Playlists and Custom Sort |
|:------------------------------------|:---------------------------------------------|:-----------------:|:----------------:|:------------------------------------:|
| [`radarr_all`](#radarr-all)         | Gets all Movies in Radarr.                   |      &#9989;      |     &#10060;     |               &#10060;               |
| [`radarr_taglist`](#radarr-taglist) | Gets Movies from Radarr based on their tags. |      &#9989;      |     &#10060;     |               &#10060;               |

## Radarr All

Gets all Movies in Radarr.

```yaml
collections:
  ALL Radarr Movies:
    radarr_all: true
```

## Radarr Taglist

Gets Movies from Radarr based on their tags. 

Set the attribute to the tag you want to search for. Multiple values are supported as either a list or a comma-separated string. 

```yaml
collections:
  Radarr Movies Without Tags:
    radarr_taglist: action, drama
```

If no tag is specified then it gets every Movie without a tag.

```yaml
collections:
  Radarr Movies Without Tags:
    radarr_taglist: 
```