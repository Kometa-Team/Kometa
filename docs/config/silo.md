---
search:
  boost: 3
hide:
  - toc
---
# Silo Attributes

[Silo](https://silo.pzyzbyx.pw/api/v2/docs) is an optional media server. The `plex` connection stays required. A library uses Silo when its [`server`](libraries.md#server) attribute names a `media_servers` entry.

Silo libraries can create and update manual collections and smart collections. A smart collection takes a Silo query document. Plex smart filter addresses are not accepted. Image uploads, labels, deleting an item, and playlists are not available. A collection that needs one of those stops with an error for that collection.

Kometa calls Silo's `/api/v2` API. `token` is a session token or an API key sent on the `Authorization` header. When `profile_id` is set, catalog reads send it on the `X-Profile-Id` header.

```yaml title="config.yml Silo sample"
plex:
  url: http://192.168.1.12:32400
  token: ####################
tmdb:
  apikey: ################################
media_servers:
  Shelf:
    type: silo
    url: http://192.168.1.12:8090
    token: ####################
    profile_id: PROFILE_ID
    timeout: 60
    verify_ssl: true
libraries:
  Movies:
    collection_files:
      - default: basic
  Films:
    server: Shelf
    collection_files:
      - default: basic
```

`Movies` uses the `plex` server. `Films` uses the Silo server named `Shelf`.

<div class="annotate" markdown>

| Attribute    | Description                                                                                          | Allowed Values (default in **bold**)                         |                  Required                  |
|:-------------|:-----------------------------------------------------------------------------------------------------|:-------------------------------------------------------------|:------------------------------------------:|
| `type`       | Media server type.                                                                                   | `silo` or `plex`                                             | :fontawesome-solid-circle-check:{ .green } |
| `url`        | Server URL. Kometa adds `/api/v2` when a Silo URL does not already end with it.                     | Any valid URL<br><strong>Example:</strong> `http://192.168.1.12:8090` | :fontawesome-solid-circle-check:{ .green } |
| `token`      | Session token or API key.                                                                            | Any valid token                                              | :fontawesome-solid-circle-check:{ .green } |
| `profile_id` | Silo profile whose catalog Kometa reads.                                                             | Any profile id                                               |  :fontawesome-solid-circle-xmark:{ .red }  |
| `timeout`    | Timeout for Silo communication, in seconds.                                                          | Integer, e.g. **`60`**                                       |  :fontawesome-solid-circle-xmark:{ .red }  |
| `verify_ssl` | Enable or disable SSL verification for this server.                                                 | `true`, `false`, or leave **blank**                          |  :fontawesome-solid-circle-xmark:{ .red }  |
| `db_cache`   | Plex database cache size in MB. Used when `type` is `plex`.                                          | Integer, e.g. **`40`**                                       |  :fontawesome-solid-circle-xmark:{ .red }  |

</div>

A `type: plex` entry is another Plex server. Its `url`, `token`, `timeout`, `verify_ssl`, and `db_cache` replace that library's `plex` values. Options such as `empty_trash` stay on the `plex` block.

Libraries that omit `server` keep using `plex`.
