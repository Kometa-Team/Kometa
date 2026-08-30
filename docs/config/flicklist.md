---
hide:
  - toc
---
# FlickList

Configuring [FlickList](https://flicklist.tv/) is optional but is required for `flicklist_*` builders to function.

The `flicklist` attribute is found at the root of the config file. FlickList authentication is a single, non-expiring
API key; there is no OAuth flow, no refresh token, and no expiry to maintain. The only lifecycle event is the key
being revoked, which returns a `401` and requires minting a new key.

```yaml
flicklist:
  api_key: fs_live_xxxxxxxxxxxxxxxx
```

| Attribute | Description       | Required                                   |
|:----------|:------------------|:------------------------------------------:|
| `api_key` | FlickList API key | :fontawesome-solid-circle-check:{ .green } |

## Getting an API key

* **FlickList's own dashboard.** Any FlickList account can mint a key from Developer → Your Apps, no waiting or
  approval required. Read and write scopes are both selectable, and page size is configurable there (up to 500).
* **Kometa Utilities.** A future addition to the [Kometa Utilities website](https://utilities.kometa.wiki), the
  same site used to authenticate Plex, MyAnimeList, SIMKL, and Trakt, will offer a guided device-code flow that
  mints a key and hands you a paste-ready `flicklist:` block. Not yet available; this page will be updated once
  it ships.

## Scopes

`flicklist_list`, `flicklist_list_details`, and `flicklist_user_lists` work with a `read` scope key (or, for public
lists, no key at all). Every other `flicklist_*` builder reads the authenticated user's own data and requires
`read` scope. A key missing the required scope returns a clear error naming which scope is missing.

## Rate limits

FlickList allows 1,000 requests/hour per API key. Builds that page through list contents or a user's public lists
consume more requests the larger those lists are; a user with dozens of public lists will see a correspondingly
longer run and a log line naming how many lists are being processed. Kometa backs off automatically on a `429`
and honors the `Retry-After` header when present.

## What FlickList doesn't have

Rotten Tomatoes and Metacritic scores, and structured awards data, are not available from FlickList's API and
there are no plans to add them. Kometa's existing MDBList/OMDb bridge remains the source for that data regardless
of whether FlickList is configured.

## Known limitation

Public FlickList lists can be read without any credential at all, but Kometa currently requires the `flicklist`
config block to be present before any `flicklist_*` builder is accepted — consistent with how every other Kometa
connector works. If you only ever consume public lists and would rather skip configuring an API key, this is a
known limitation, not a bug.
