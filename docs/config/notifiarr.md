---
hide:
  - toc
---
# Notifiarr Attributes

Configuring [Notifiarr](https://notifiarr.com) is optional but can allow you to send the [webhooks](webhooks.md) straight to notifiarr.

A `notifiarr` mapping is in the root of the config file, sampled below.

```yaml title="config.yml Notifiarr sample"
notifiarr:
  apikey: apikeygoeshere
```

| Attribute  | Description             | Allowed Values (default in **bold**)        |                   Required                   |
|:-----------|:------------------------|:--------------------------------------------|:--------------------------------------------:|
| `apikey`   | Notifiarr API key.      | Any valid key or leave **blank**            | :fontawesome-solid-circle-check:{ .green }   |

Once you have added the apikey your config.yml you have to add `notifiarr` to any [webhook](webhooks.md) to send that notification to Notifiarr.

```yaml title="config.yml Notifiarr webhooks sample"
webhooks:
  error: notifiarr
  version: notifiarr
  run_start: notifiarr
  run_end: notifiarr
  changes: notifiarr
```
