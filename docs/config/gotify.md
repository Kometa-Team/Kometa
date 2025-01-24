# Gotify Attributes

Configuring [Gotify](https://gotify.net/) is optional but can allow you to send the [webhooks](webhooks.md) 
straight to Gotify.

A `gotify` mapping is in the root of the config file.

Below is a `gotify` mapping example and the full set of attributes:

```yaml
gotify:
  url: ####################################
  token: ####################################
```

| Attribute | Allowed Values           |                  Required                  |
|:----------|:-------------------------|:------------------------------------------:|
| `url`     | Gotify Server Url        | :fontawesome-solid-circle-check:{ .green } |
| `token`   | Gotify Application Token | :fontawesome-solid-circle-check:{ .green } |

Once you have added the configuration data your config.yml you have to add `gotify` to any [webhook](webhooks.md) to send that 
notification to Gotify.

```yaml
webhooks:
  error: gotify
  version: gotify
  run_start: gotify
  run_end: gotify
  changes: gotify
```
