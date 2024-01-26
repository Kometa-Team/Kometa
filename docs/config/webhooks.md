# Webhooks Attributes

Configuring Webhooks is optional but can allow you to receive notifications when certain events happen.

Discord and Slack Direct webhooks are supported just use the correct urls. 

A `webhooks` mapping is in the root of the config file.

Below is a `webhooks` mapping example and the full set of attributes:

```yaml
webhooks:
  error: https://www.myspecialdomain.com/pmm
  version:
  run_start:
  run_end:
  changes:
```

| Attribute                               |                   Global                   |                  Library                   |                  Collection                  |
|:----------------------------------------|:------------------------------------------:|:------------------------------------------:|:--------------------------------------------:|
| [`error`](#error-notifications)         | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |   :fontawesome-solid-circle-xmark:{ .red }   |
| [`version`](#version-notifications)     | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |   :fontawesome-solid-circle-xmark:{ .red }   |
| [`run_start`](#run-start-notifications) | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |   :fontawesome-solid-circle-xmark:{ .red }   |
| [`run_end`](#run-end-notifications)     | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |   :fontawesome-solid-circle-xmark:{ .red }   |
| [`delete`](#delete-notifications)       | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |   :fontawesome-solid-circle-xmark:{ .red }   |
| [`changes`](#changes-notifications)     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-check:{ .green }  |

* Each Attribute can be either a webhook url as a string or a comma-separated list of webhooks urls.
* To send notifications to [Notifiarr](notifiarr.md) just add `notifiarr` to a webhook instead of the webhook url.
* To send notifications to [Gotify](gotify.md) just add `gotify` to a webhook instead of the webhook url.

## Error Notifications

The Error notification will be sent whenever an error occurs. The payload that is sent is different Depending on which 
level the error occurs.

### Global JSON Payload

```yaml
{
  "event": "error",             // Event
  "error": str,                 // Error Message
  "critical": bool              // Critical Error
}
```

### Library JSON Payload

```yaml
{
  "event": "error",             // Event
  "error": str,                 // Error Message
  "critical": bool,             // Critical Error
  "server_name": str,           // Server Name
  "library_name": str           // Library Name
}
```

### Collection JSON Payload

```yaml
{
  "event": "error",             // Event
  "error": str,                 // Error Message
  "critical": bool,             // Critical Error
  "server_name": str,           // Server Name
  "library_name": str,          // Library Name
  "collection": str             // Collection Name
}
```

### Playlist JSON Payload

```yaml
{
  "event": "error",             // Event
  "error": str,                 // Error Message
  "critical": bool,             // Critical Error
  "server_name": str,           // Server Name
  "playlist": str               // Playlist Name
}
```

## Version Notifications

The Version notification will be sent at the beginning of a run if there is a newer version available.

### JSON Payload

```yaml
{
  "event": "version",           // Event
  "current": str,               // Current Version
  "latest": str,                // Latest Version 
  "notes": str                  // Sends the latest release notes or new commits to develop since your version
}
```

## Run Start Notifications

The Run Start notification will be sent at the beginning of every run.

### JSON Payload

```yaml
{
  "event": "run_start",         // Event
  "start_time": str,            // Time Run is started Format "YY-mm-dd HH:MM:SS"
}
```

## Run End Notifications

The Run End notification will be sent at the end of every run with statistics.

### JSON Payload

```yaml
{
  "event": "run_end",           // Event
  "start_time": str,            // Time Run started Format "YY-mm-dd HH:MM:SS"
  "end_time": str,              // Time Run ended Format "YY-mm-dd HH:MM:SS"
  "run_time": str,              // Time Run took to complete Format "HH:MM"
  "collections_created": int,   // Number of Collections/Playlists Created
  "collections_modified": int,  // Number of Collections/Playlists Modified
  "collections_deleted": int,   // Number of Collections/Playlists Removed
  "items_added": int,           // Number of Items added across all Collections/Playlists
  "items_removed": int,         // Number of Items removed across all Collections/Playlists
  "added_to_radarr": int,       // Number of Items added to Radarr
  "added_to_sonarr": int,       // Number of Items added to Sonarr
  "names": [                    // List of Dictionaries
    "name": str,                // Name of collection or playlist in the run 
    "library": str              // Library the collection is in or PLAYLIST
  ]
}
```

## Delete Notifications

The Delete Notification will be sent whenever a collection/playlist is deleted containing the following payload.

### JSON Payload

```yaml
{
  "event": "delete",            // Event
  "message": str,               // Status Message
  "server_name": str,           // Server Name
  "library_name": str,          // Library Name (Only if a Collection is deleted)
}
```

## Changes Notifications

The Changes Notification will be sent after each collection/playlist containing the following payload if the 
collection/playlist has been created, has new items, or has had items removed.

### JSON Payload

```yaml
{
  "event": "changes",           // Event
  "server_name": str,           // Server Name
  "library_name": str,          // Library Name
  "collection": str,            // Collection Name only in payload for a collection
  "playlist": str,              // Playlist Name only in payload for a playlist
  "created": bool,              // Was the Collection/Playlist Created on this run
  "poster": str,                // Base64 Encoded Collection/Playlist Poster if no poster_url is found
  "poster_url": str,            // Collection/Playlist Poster URL if available
  "background": str,            // Base64 Encoded Collection/Playlist Background if no poster_url is found
  "background_url": str,        // Collection/Playlist Background URL if available
  "additions": [                // List of Dictionaries
    "title": str,               // Title of addition
    "tmdb_id": int,             // TMDb ID of addition only appears if it's a Movie
    "tvdb_id": int              // TVDb ID of addition only appears if it's a Show
  ],
  "removals": [                 // List of Dictionaries
    "title": str,               // Title of removal
    "tmdb_id": int,             // TMDb ID of removal only appears if it's a Movie
    "tvdb_id": int              // TVDb ID of removal only appears if it's a Show
  ],
  "radarr_adds": [              // List of Dictionaries
    "title": str,               // Title of the Radarr Add
    "id":  int                  // TMDb ID of the Radarr Add
  ],
  "sonarr_adds": [              // List of Dictionaries
    "title": str,               // Title of the Sonarr Add
    "id":  int                  // TVDb ID of the Sonarr Add
  ]
}
```
