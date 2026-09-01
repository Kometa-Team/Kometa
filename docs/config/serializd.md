---
hide:
  - toc
---
# Serializd Attributes

Configuring [Serializd](https://www.serializd.com/) is optional. It enables Serializd metadata sources, watched synchronization, and [Serializd builders](../files/builders/serializd/overview.md).

A `serializd` mapping can be added to the root of the config file:

```yaml title="config.yml Serializd sample"
serializd:
  email: user@example.com
  password: password
  timeout: 60
```

| Attribute | Description | Allowed Values | Required |
|:----------|:------------|:---------------|:--------:|
| `email` | Serializd account email. | Any valid email | :fontawesome-solid-circle-check:{ .green } |
| `password` | Serializd account password. | Any valid password | :fontawesome-solid-circle-check:{ .green } |
| `timeout` | Number of seconds to wait for each Serializd request. Authentication is retried up to three times after transient connection or timeout failures. | Any integer greater than 0; defaults to `60` | :fontawesome-solid-circle-xmark:{ .red } |

The credentials are used to authenticate with Serializd when Kometa starts. For genre updates, Kometa looks up each show using its TMDb ID. The `serializd` source applies the names in `ShowResponse.genres`, `serializd_nanogenres` applies all returned nanogenres with their leading emoji removed, and `serializd_all` combines both lists.

The `serializd` rating source uses Serializd's community `averageRating` on its native 0–10 scale. It can populate any show or episode audience, critic, or user rating field selected under the mass metadata update operation.

The `serializd_user` rating source uses the authenticated account's episode rating on the same scale. Serializd's API does not expose an authenticated user's show-level rating, so this source is available only for episode rating updates.

The Serializd list, watchlist, and chart builders use Serializd's JSON API. Authentication is required even when requesting public content. Kometa does not fall back to scraping Serializd pages.
