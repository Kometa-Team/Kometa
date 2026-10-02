---
hide:
  - toc
---
# WeTrakr

Configuring [WeTrakr](https://wetrakr.com/) is optional but is required for `wetrakr_*` builders to function.

The `wetrakr` attribute is found at the root of the config file. Unlike FlickList's single non-expiring API key,
WeTrakr uses OAuth2 with token rotation: a 7-day access token backed by a 180-day sliding refresh token that
rotates on every use. Kometa refreshes the access token automatically before it expires and rewrites the
`authorization` block back into your config file each time, so Kometa needs write access to the config file.

```yaml
wetrakr:
  authorization:
    access_token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    refresh_token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    expires_at: 2026-10-05T00:00:00Z
```

| Attribute       | Description                                                       | Required                                   |
|:----------------|:--------------------------------------------------------------------|:------------------------------------------:|
| `client_id`     | WeTrakr app client id. Optional — a shared public client id is used if omitted. | :fontawesome-solid-circle-xmark:{ .red }   |
| `authorization` | The access/refresh token block described below                   | :fontawesome-solid-circle-check:{ .green } |

## Getting authorization

Run the WeTrakr page on the [Kometa Utilities website](https://utilities.kometa.wiki) and follow its device-code
flow. It hands you a paste-ready `wetrakr:` block, the same pattern used for Plex, MyAnimeList, and SIMKL. The
client secret behind that flow is never sent to Kometa or exposed in your config — only the resulting
`access_token`/`refresh_token`/`expires_at` values are.

## Token lifecycle and `read_only`

Kometa checks the access token's expiry before every run and refreshes it automatically when it's due to expire
soon. If your config has `read_only: true` set, Kometa cannot write the refreshed token back to disk, so it will
not attempt a refresh — if the token has already expired in that case, the run fails with an error asking you to
either re-authenticate via the Kometa Utilities WeTrakr page or turn off `read_only`.

## Rate limits

WeTrakr enforces both a per-minute rate limit and a daily quota. Kometa backs off and retries automatically on a
per-minute `429`, honoring the `RateLimit-Reset` header. A daily quota hit is different: it will not clear until
midnight UTC, so Kometa fails that run immediately rather than sleeping through the rest of the day. If you're
running large `wetrakr_user_lists` or multi-status `wetrakr_tracking` builds regularly, keep an eye on how close
to the daily quota a full run gets you.

