---
hide:
  - toc
---
# Spotify Attributes

Spotify configuration is optional. It prepares Kometa to read playlists owned by the authorized Spotify account or playlists where that account is a collaborator, along with supported personal-library data for music collection builders.

Create an application in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard), add the same redirect URI there and in Kometa's configuration, then add its Client ID and Client Secret:

```yaml title="config.yml Spotify sample"
spotify:
  client_id: YOUR_CLIENT_ID
  client_secret: YOUR_CLIENT_SECRET
  redirect_uri: http://127.0.0.1:8888/callback
  authorization: {}
```

| Attribute | Description | Required |
|:----------|:------------|:--------:|
| `client_id` | Spotify application Client ID. | :fontawesome-solid-circle-check:{ .green } |
| `client_secret` | Spotify application Client Secret. | :fontawesome-solid-circle-check:{ .green } |
| `redirect_uri` | Redirect URI registered for the Spotify application. | :fontawesome-solid-circle-check:{ .green } |
| `authorization` | Managed by Kometa. Leave it as `{}` before the first authorization. | :fontawesome-solid-circle-xmark:{ .red } |

Register the exact `redirect_uri` in the Spotify Developer Dashboard. Spotify permits an HTTP redirect only for an explicit loopback IP address such as `127.0.0.1`; it does not permit `localhost`.

On the first run, Kometa opens the Spotify authorization page and asks for the full redirect URL after approval. It writes the access token, refresh token, and expiry to `authorization`. Future runs refresh the access token automatically; an expired refresh token starts authorization again.

Use an HTTPS `redirect_uri`, except for a local `http://127.0.0.1` loopback address. Spotify does not permit `http://localhost` or wildcard redirect URIs.