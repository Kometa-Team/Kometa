# Floppy

Configuring [Floppy](https://github.com/dannyvfilms/Floppy) is required for the `floppy_list` and `floppy_tracked` builders and to use `floppy` as a ratings update source.

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

When no token is configured, Kometa can only read public lists. With a token, Kometa can read all lists available to the account.
