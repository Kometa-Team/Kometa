# Floppy

Configuring [Floppy](https://github.com/dannyvfilms/Floppy) is required for the `floppy_list` builder.

Add a `floppy` mapping at the root of the config file:

```yaml
floppy:
  url: https://floppy.example.com
  token: API_TOKEN
```

| Attribute | Description | Required |
|:----------|:------------|:--------:|
| `url` | Floppy server URL | :fontawesome-solid-circle-check:{ .green } |
| `token` | API token from **Settings → Advanced**. Required for private lists; optional for public lists. | :fontawesome-solid-circle-xmark:{ .red } |

When no token is configured, Kometa reads Floppy's anonymous public-list JSON exports. With a token, Kometa uses the `/api/v1` list endpoint and can read lists available to that account.

## Rating Updates

Floppy can be used as a source for movie, show, and episode mass-rating updates. Rating updates require an API token because Floppy ratings belong to the authenticated user.

Floppy's 0–10 decimal ratings are rounded to Plex's half-star increments. Plex stores ratings on a 0–10 API scale and displays each whole point as half a star; for example, `9.9` becomes `10.0` (5 stars) and `9.4` becomes `9.0` (4.5 stars).

```yaml
libraries:
  TV Shows:
    operations:
      mass_user_rating_update: floppy
      mass_episode_user_rating_update: floppy
```

Use the same `floppy` source under any of the audience, critic, or user slots:

```yaml
operations:
  mass_critic_rating_update: floppy
  mass_episode_user_rating_update: floppy
```
