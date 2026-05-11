# Apprise Notification Provider — Design Spec

**Date:** 2026-04-26
**Status:** Approved

## Summary

Add Apprise (Python library) as a notification provider in Kometa, using an Apprise config file (local path or remote URL) to define which services receive notifications. Follows the existing provider pattern established by Gotify and ntfy.

## Approach

Use the `apprise` Python library directly (no separate API server required). The user points Kometa at an Apprise config file; Apprise handles routing to all configured services (Telegram, Pushover, Matrix, etc.).

## New File: `modules/apprise_notify.py`

```python
import apprise as apprise_lib
from modules import util, webhooks
from modules.util import Failed

logger = util.logger

_PRIORITY_MAP = {
    1: apprise_lib.NotifyType.INFO,
    2: apprise_lib.NotifyType.INFO,
    3: apprise_lib.NotifyType.INFO,
    4: apprise_lib.NotifyType.SUCCESS,
    5: apprise_lib.NotifyType.FAILURE,
}

class AppriseNotify:
    def __init__(self, requests, params):
        config_path = params["config"]
        logger.secret(config_path)
        self._apobj = apprise_lib.Apprise()
        ac = apprise_lib.AppriseConfig()
        ac.add(config_path)
        self._apobj.add(ac)
        if not len(self._apobj):
            raise Failed("Apprise Error: No valid notification services loaded from config")

    def notification(self, json):
        message, title, priority = webhooks.get_message(json)
        self._apobj.notify(
            title=title,
            body=message,
            notify_type=_PRIORITY_MAP.get(priority, apprise_lib.NotifyType.INFO),
        )
```

**Design notes:**
- Named `apprise_notify.py` (not `apprise.py`) to avoid shadowing the `apprise` package.
- `requests` parameter accepted but unused — present for consistency with all other providers.
- No test notification sent on init; instead validates that at least one service loaded from config. This avoids spamming potentially many services on every Kometa startup.
- Priority mapping: 1–3 → `INFO`, 4 (run start/end) → `SUCCESS`, 5 (errors) → `FAILURE`.

## `config.py` Changes

1. **Import** alongside other providers:
   ```python
   from modules.apprise_notify import AppriseNotify
   ```

2. **Config key normalization** (alongside other `pop` calls, ~line 437):
   ```python
   if "apprise" in self.data:
       self.data["apprise"] = self.data.pop("apprise")
   ```

3. **Factory initialization** (after ntfy block, ~line 797):
   ```python
   self.AppriseFactory = None
   if "apprise" in self.data:
       logger.info("Connecting to Apprise...")
       try:
           self.AppriseFactory = AppriseNotify(
               self.Requests,
               {"config": check_for_attribute(self.data, "config", parent="apprise", throw=True)},
           )
       except Failed as e:
           if str(e).endswith("is blank"):
               logger.warning(e)
           else:
               logger.stacktrace()
               logger.error(e)
       logger.info(f"Apprise Connection {'Failed' if self.AppriseFactory is None else 'Successful'}")
   else:
       logger.info("apprise attribute not found")
   ```

4. **Pass into both `Webhooks` instantiations:**
   ```python
   # system-level (~line 807)
   self.Webhooks = Webhooks(self, self.webhooks, notifiarr=self.NotifiarrFactory,
                            gotify=self.GotifyFactory, ntfy=self.NtfyFactory,
                            apprise=self.AppriseFactory)

   # library-level (~line 2175)
   library.Webhooks = Webhooks(self, {}, library=library, notifiarr=self.NotifiarrFactory,
                               gotify=self.GotifyFactory, apprise=self.AppriseFactory)
   ```

## `webhooks.py` Changes

1. **`Webhooks.__init__` signature:**
   ```python
   def __init__(self, config, system_webhooks, library=None, notifiarr=None, gotify=None, ntfy=None, apprise=None):
       ...
       self.apprise = apprise
   ```

2. **Dispatch in `_request`** (after ntfy block, ~line 113):
   ```python
   elif webhook == "apprise":
       if self.apprise:
           self.apprise.notification(json)
   ```

## Config Template (`config/config.yml.template`)

After the ntfy block:
```yaml
apprise:
  config:                          # Enter path or URL to Apprise config file (Optional)
```

## Dependency (`pyproject.toml`)

```toml
apprise>=1.9.0
```

## User Config Example

```yaml
apprise:
  config: /config/apprise.yml   # local path

webhooks:
  error: apprise
  run_start: apprise
  run_end: apprise
  version: apprise
  delete: apprise
  changes: apprise
```

Or with a remote URL:
```yaml
apprise:
  config: http://apprise-server/notify/apprise.yml
```

## Files Changed

| File | Change |
|------|--------|
| `modules/apprise_notify.py` | New file |
| `modules/config.py` | Import, factory init, pass to Webhooks |
| `modules/webhooks.py` | `__init__` param + dispatch branch |
| `config/config.yml.template` | Add `apprise` block |
| `pyproject.toml` | Add `apprise>=1.9.0` dependency |
