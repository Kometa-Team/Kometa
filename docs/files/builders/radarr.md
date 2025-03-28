---
hide:
  - toc
---
# Radarr Builders

You can find items in your Plex using the features of [Radarr](https://radarr.video/).

???+ warning "Radarr Configuration"

    [Configuring Radarr](../../config/radarr.md) in the config is required for any of these builders.

| Builder                             | Description                                  |             Works with Movies              |             Works with Shows             |   Works with Playlists and Custom Sort   |
|:------------------------------------|:---------------------------------------------|:------------------------------------------:|:----------------------------------------:|:----------------------------------------:|
| [`radarr_all`](#radarr-all)         | Gets all Movies in Radarr.                   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |
| [`radarr_taglist`](#radarr-taglist) | Gets Movies from Radarr based on their tags. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |

=== "Radarr All"

    Gets all Movies in Radarr.

    ### Example Radarr All Builder(s)

    ```yaml
    collections:
      ALL Radarr Movies:
        radarr_all: true
    ```

=== "Radarr Taglist"
    
    Gets Movies from Radarr based on their tags. 
    
    Set the attribute to the tag you want to search for. Multiple values are supported as either a list or a comma-separated string. 

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