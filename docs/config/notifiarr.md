# Notifiarr Attributes

Configuring [Notifiarr](https://notifiarr.com) is optional but can allow you to send the [webhooks](webhooks) straight to notifiarr.

A `notifiarr` mapping is in the root of the config file.

Below is a `notifiarr` mapping example and the full set of attributes:

```yaml
notifiarr:
  apikey: ####################################
```

| Attribute | Allowed Values                           | Required |
|:----------|:-----------------------------------------|:--------:|
| `apikey`  | Notifiarr API Key                        | &#9989;  |

Once you have added the apikey your config.yml you have to add `notifiarr` to any [webhook](webhooks) to send that notification to Notifiarr.

```yaml
webhooks:
  error: notifiarr
  version: notifiarr
  run_start: notifiarr
  run_end: notifiarr
  changes: notifiarr
```
