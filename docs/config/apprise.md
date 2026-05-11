---
hide:
  - toc
---
# Apprise Attributes

Configuring [Apprise](https://github.com/caronc/apprise) is optional but can allow you to send [webhooks](webhooks.md) to any notification services defined in an Apprise configuration file.

Apprise supports many notification services, including Discord, Matrix, Pushover, Signal, Telegram, and email. Kometa does not configure those services directly; it loads the Apprise configuration file and lets Apprise route each notification.

An `apprise` mapping is in the root of the config file, sampled below.

```yaml title="config.yml Apprise sample"
apprise:
  config: /config/apprise.yml
```

| Attribute | Description                              | Allowed Values (default in **bold**) |                  Required                  |
|:----------|:-----------------------------------------|:-------------------------------------|:------------------------------------------:|
| `config`  | Path or URL to an Apprise configuration. | Any valid path or URL                | :fontawesome-solid-circle-check:{ .green } |

## Apprise Configuration File

The Apprise configuration file contains the service URLs that should receive notifications.

```yaml title="apprise.yml sample"
urls:
  - tgram://bottoken/ChatID
  - pover://user@token
```

The configuration can be a local file or a remote URL.

```yaml title="config.yml local Apprise config"
apprise:
  config: /config/apprise.yml
```

```yaml title="config.yml remote Apprise config"
apprise:
  config: https://example.com/apprise.yml
```

Once you have added the configuration data to your `config.yml`, add `apprise` to any [webhook](webhooks.md) to send that notification through Apprise.

```yaml title="config.yml Apprise webhooks sample"
webhooks:
  error: apprise
  version: apprise
  run_start: apprise
  run_end: apprise
  delete: apprise
  changes: apprise
```

Apprise validates that at least one notification service is loaded from the configured file when Kometa starts. Delivery failures from individual Apprise services are logged as warnings.
