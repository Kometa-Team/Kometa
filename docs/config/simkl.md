---
hide:
  - toc
---
# Simkl Attributes

Configuring [Simkl](https://simkl.com/) is optional. The `simkl_trending` and `simkl_dvd` builders
work without any configuration — data is fetched via the
[Kometa Simkl Service](https://utilities.kometa.wiki/simkl-service) and no Simkl account is required.

A `simkl` mapping can be added to the root of the config file when using authenticated Simkl features.
Kometa renews the short-lived access token automatically using the refresh token and saves the token
lifetime information to `config.yml`.

```yaml title="config.yml Simkl sample"
simkl:
  refresh_token: simkl_rt_##########
  force_refresh: false
```

| Attribute       | Description                                      | Allowed Values              | Required |
|:----------------|:-------------------------------------------------|:----------------------------|:--------:|
| `refresh_token` | Simkl OAuth V2 refresh token. Kometa manages the access token and expiration. | Any valid OAuth V2 refresh token | :fontawesome-solid-circle-xmark:{ .red } |
| `force_refresh` | Always refresh before authenticating instead of trying the saved access token first. | `true` or `false` (default: `false`) | :fontawesome-solid-circle-xmark:{ .red } |

Normally Kometa first authenticates with the saved access token and only refreshes if authentication fails.
Set `force_refresh: true` to skip that check and refresh immediately before authenticating. This can
help avoid a stale access token when another Kometa process shares the same SIMKL grant. Note that
SIMKL invalidates the previous access token on refresh, so simultaneous runs can still invalidate
each other's token.

???+ tip

    Generate a refresh token using the [Kometa Utilities](./authentication.md). Existing OAuth V1
    `user_token` entries are not supported; create a new OAuth V2 token and replace the old `simkl` block.
