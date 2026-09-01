---
hide:
  - toc
---
# Tracearr Attributes

Configuring [Tracearr](https://docs.tracearr.com/) is optional but can allow you to create Collections based on Tracearr watch history.

A `tracearr` mapping can be either in the root of the config file as a global mapping for all libraries, or you can specify the `tracearr` mapping individually per library.

Below is a `tracearr` mapping example and the full set of attributes:

```yaml title="config.yml Tracearr sample"
tracearr:
  url: http://192.168.1.4:3019
  apikey: trr_pub_################################
  server_id: 550e8400-e29b-41d4-a716-446655440000
```

| Attribute   | Description                                                                                                                                                                                                                           | Allowed Values (default in **bold**)                                  |                  Required                  |
|:------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------|:------------------------------------------:|
| `url`       | Tracearr URL.                                                                                                                                                                                                                         | Any valid URL<br><strong>Example:</strong> `http://192.168.1.4:3019` | :fontawesome-solid-circle-check:{ .green } |
| `apikey`    | Tracearr Public API key.                                                                                                                                                                                                              | A key beginning with `trr_pub_`                                       | :fontawesome-solid-circle-check:{ .green } |
| `server_id` | Tracearr's internal UUID for the Plex server used by this library. Kometa automatically matches the Plex and Tracearr server names when possible; set this when the names differ or more than one Tracearr Plex server has the same name. | A UUID or **blank**                                                    | :fontawesome-solid-circle-xmark:{ .red }   |

???+ tip

    The API key can be found in Tracearr's settings under the Public API section. Tracearr uses Bearer auth and exposes its interactive API reference at `/api-docs`. Kometa probes the v2 Public API when connecting and uses its history identity fields and filters when available. Tracearr versions without v2 automatically fall back to the v1 endpoint and title/year matching:
    `Authorization: Bearer trr_pub_<your_token>`.

???+ tip "Finding the Server ID"

    Leave `server_id` blank initially. Kometa automatically matches the Plex server name reported by Tracearr. If Kometa cannot find a unique match, the error message lists the available Tracearr Plex servers and their UUIDs. Copy the appropriate UUID from the log into `server_id`.

# Other examples

Specifying a second Tracearr instance for a specific library:

```yaml
libraries:
  Movies:
    collection_files:
      - file: config/Movies.yml
  TV Shows:
    collection_files:
      - file: config/TV.yml
    tracearr:
      url: http://192.168.1.14:3019
      apikey: trr_pub_SOME_KEY
      server_id: 550e8400-e29b-41d4-a716-446655440000
...
tracearr:
  url: http://192.168.1.12:3019
  apikey: trr_pub_SOME_OTHER_KEY
...
```
