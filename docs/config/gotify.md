# Gotify Attributes

Configuring [Gotify](https://gotify.net/) is optional but can allow you to send the [webhooks](webhooks.md) straight to Gotify.

A `gotify` mapping is in the root of the config file, sampled below.

```yaml title="config.yml Goify sample"
gotify:
  url: https://mywebsite.com
  token: thisismytoken
```

| Attribute | Allowed Values            |                  Required                  |
|:----------|:--------------------------|:------------------------------------------:|
| `url`     | Gotify Server URL.        | :fontawesome-solid-circle-check:{ .green } |
| `token`   | Gotify Application Token. | :fontawesome-solid-circle-check:{ .green } |

Once you have added the configuration data your config.yml you have to add `gotify` to any [webhook](webhooks.md) to send that notification to Gotify.

```yaml title="config.yml Gotify webhooks sample"
webhooks:
  error: gotify
  version: gotify
  run_start: gotify
  run_end: gotify
  changes: gotify
```
