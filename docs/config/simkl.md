---
hide:
  - toc
---
# Simkl Attributes

Configuring [Simkl](https://simkl.com/) is optional. The `simkl_trending` and `simkl_dvd` builders
work without any configuration — data is fetched via the
[Kometa Simkl Service](https://utilities.kometa.wiki/simkl-service) and no Simkl account is required.

NOTE: This is here for future expansion; there is no builder that currently uses it and there is no need to configure it at this time.

A `simkl` mapping can be added to the root of the config file as shown below.

```yaml title="config.yml Simkl sample"
simkl:
  user_token: ##########
```

| Attribute    | Description            | Allowed Values               |                 Required                  |
|:-------------|:-----------------------|:-----------------------------|:-----------------------------------------:|
| `user_token` | Simkl User API token.  | Any valid token or **blank** | :fontawesome-solid-circle-xmark:{ .red }  |

???+ tip

    A Simkl user token can be obtained from the [Kometa Utilities](./authentication.md).
