---
search:
  boost: 3
hide:
  - toc
---
# Jellyfin and Emby Attributes

[Jellyfin](https://jellyfin.org/) and [Emby](https://emby.media/) are media servers. A library uses one when its [`server`](libraries.md#server) attribute names a `media_servers` entry with `type: jellyfin` or `type: emby`. That library does not need a `plex` block. [`tmdb`](tmdb.md) stays required.

Both servers use the MediaBrowser API. Kometa sends `token` on the `X-Emby-Token` header. `user` selects the user for catalog and playlist calls. When `user` is omitted, Kometa uses the first administrator from `/Users`.

Movie and TV libraries can build boxset collections and playlists. Kometa can edit titles, summaries, tags, genres, and studios, and it can upload poster, backdrop, logo, banner, and overlay images. A local file is uploaded as bytes. A URL is sent to the server, which downloads it. Plex smart-filter addresses are not accepted. A collection that needs a dynamic Plex filter stops with an error for that collection.

```yaml title="config.yml Jellyfin sample"
tmdb:
  apikey: ################################
media_servers:
  Cinema:
    type: jellyfin
    url: http://192.168.1.12:8096
    token: ####################
    user: USER_ID
    timeout: 60
    verify_ssl: true
libraries:
  Films:
    server: Cinema
    collection_files:
      - default: basic
```

```yaml title="config.yml Emby sample"
tmdb:
  apikey: ################################
media_servers:
  Theater:
    type: emby
    url: http://192.168.1.12:8096
    token: ####################
libraries:
  Films:
    server: Theater
    collection_files:
      - default: basic
```

`Films` uses the named server. Add a `plex` block when another library in the same file uses Plex.

<div class="annotate" markdown>

| Attribute    | Description                                                                                          | Allowed Values (default in **bold**)                         |                  Required                  |
|:-------------|:-----------------------------------------------------------------------------------------------------|:-------------------------------------------------------------|:------------------------------------------:|
| `type`       | Media server type.                                                                                   | `jellyfin` or `emby`                                         | :fontawesome-solid-circle-check:{ .green } |
| `url`        | Server URL.                                                                                          | Any valid URL<br><strong>Example:</strong> `http://192.168.1.12:8096` | :fontawesome-solid-circle-check:{ .green } |
| `token`      | API key.                                                                                             | Any valid API key                                            | :fontawesome-solid-circle-check:{ .green } |
| `user`       | User id for catalog and playlist calls. Omit to use the first administrator.                        | Any user id                                                  |  :fontawesome-solid-circle-xmark:{ .red }  |
| `timeout`    | Timeout for server communication, in seconds.                                                        | Integer, e.g. **`60`**                                       |  :fontawesome-solid-circle-xmark:{ .red }  |
| `verify_ssl` | Enable or disable SSL verification for this server.                                                 | `true`, `false`, or leave **blank**                          |  :fontawesome-solid-circle-xmark:{ .red }  |

</div>

Libraries that omit `server` keep using `plex`.
