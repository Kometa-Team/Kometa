# ntfy Attributes

Configuring [ntfy](https://ntfy.sh/) is optional but can allow you to send the [webhooks](webhooks.md) straight to ntfy.

A `ntfy` mapping is in the root of the config file.

Below is a `ntfy` mapping example and the full set of attributes:

```yaml
ntfy:
  url: ####################################
  token: ####################################
  topic: kometa
```

| Attribute | Allowed Values         |                  Required                  |
|:----------|:-----------------------|:------------------------------------------:|
| `url`     | ntfy Server Url        | :fontawesome-solid-circle-check:{ .green } |
| `token`   | ntfy User Access Token | :fontawesome-solid-circle-check:{ .green } |
| `topic`   | ntfy Topic             | :fontawesome-solid-circle-check:{ .green } |

Once you have added the configuration data your config.yml you have to add `ntfy` to any [webhook](webhooks.md) to send that notification to ntfy.

```yaml
webhooks:
  error: ntfy
  version: ntfy
  run_start: ntfy
  run_end: ntfy
  changes: ntfy
```
