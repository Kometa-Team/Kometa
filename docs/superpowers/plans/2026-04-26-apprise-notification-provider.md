# Apprise Notification Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Apprise (Python library) as a notification provider so Kometa can route notifications to any service supported by an Apprise config file (local path or remote URL).

**Architecture:** A new `AppriseNotify` class in `modules/apprise_notify.py` follows the identical shape of `Gotify`/`Ntfy`. `config.py` loads it from config YAML and passes it into `Webhooks`. `webhooks.py` dispatches to it when the webhook value is `"apprise"`.

**Tech Stack:** Python 3.12+, `apprise>=1.9.0`, pytest, existing `modules/util.py` / `modules/webhooks.py` patterns.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `modules/apprise_notify.py` | `AppriseNotify` class — load config, send notifications |
| Create | `tests/test_apprise_notify.py` | Unit tests for `AppriseNotify` |
| Modify | `pyproject.toml` | Add `apprise>=1.9.0` dependency |
| Modify | `modules/webhooks.py` | Add `apprise` param + dispatch branch |
| Modify | `modules/config.py` | Import, factory init, pass to `Webhooks` |
| Modify | `config/config.yml.template` | Document `apprise:` config block |

---

### Task 1: Add `apprise` dependency

**Files:**
- Modify: `pyproject.toml:7-44`

- [ ] **Step 1: Add the dependency**

In `pyproject.toml`, insert `"apprise>=1.9.0",` into the `dependencies` list in alphabetical order (between `"arrapi==1.4.14",` and `"babel>=2.18.0",`):

```toml
dependencies = [
    "apprise>=1.9.0",
    "arrapi==1.4.14",
    ...
]
```

- [ ] **Step 2: Install it**

```bash
uv sync
```

Expected: resolves and installs `apprise` with no errors.

- [ ] **Step 3: Verify import works**

```bash
python -c "import apprise; print(apprise.__version__)"
```

Expected: prints a version string like `1.9.x`.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat: add apprise dependency"
```

---

### Task 2: Create `modules/apprise_notify.py` (TDD)

**Files:**
- Create: `tests/test_apprise_notify.py`
- Create: `modules/apprise_notify.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_apprise_notify.py`:

```python
from unittest.mock import MagicMock, patch
import pytest

from modules.util import Failed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_params(config_path="/config/apprise.yml"):
    return {"config": config_path}


def _make_apobj(num_services=1):
    """Return a mock Apprise instance whose len() returns num_services."""
    apobj = MagicMock()
    apobj.__len__ = MagicMock(return_value=num_services)
    return apobj


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------

class TestAppriseNotifyInit:
    @patch("modules.apprise_notify.apprise_lib")
    def test_loads_config_path(self, mock_lib):
        """AppriseConfig.add is called with the configured path."""
        from modules.apprise_notify import AppriseNotify
        ac = MagicMock()
        apobj = _make_apobj(1)
        mock_lib.AppriseConfig.return_value = ac
        mock_lib.Apprise.return_value = apobj

        AppriseNotify(requests=None, params=_make_params("/my/apprise.yml"))
        ac.add.assert_called_once_with("/my/apprise.yml")

    @patch("modules.apprise_notify.apprise_lib")
    def test_raises_failed_when_no_services_loaded(self, mock_lib):
        """Raises Failed when the Apprise object has zero loaded services."""
        from modules.apprise_notify import AppriseNotify
        ac = MagicMock()
        apobj = _make_apobj(0)
        mock_lib.AppriseConfig.return_value = ac
        mock_lib.Apprise.return_value = apobj

        with pytest.raises(Failed, match="No valid notification services"):
            AppriseNotify(requests=None, params=_make_params())

    @patch("modules.apprise_notify.apprise_lib")
    def test_succeeds_when_services_loaded(self, mock_lib):
        """No exception raised when at least one service loads successfully."""
        from modules.apprise_notify import AppriseNotify
        ac = MagicMock()
        apobj = _make_apobj(2)
        mock_lib.AppriseConfig.return_value = ac
        mock_lib.Apprise.return_value = apobj

        instance = AppriseNotify(requests=None, params=_make_params())
        assert instance is not None


# ---------------------------------------------------------------------------
# notification() tests
#
# _PRIORITY_MAP is built at import time from real apprise_lib.NotifyType
# string constants: INFO="info", SUCCESS="success", FAILURE="failure".
# We inject a mock _apobj after construction and assert against those strings.
# ---------------------------------------------------------------------------

class TestAppriseNotifyNotification:
    def _make_instance(self):
        """Build an AppriseNotify and swap _apobj for a fresh mock."""
        from modules.apprise_notify import AppriseNotify
        with patch("modules.apprise_notify.apprise_lib") as mock_lib:
            mock_lib.AppriseConfig.return_value = MagicMock()
            mock_lib.Apprise.return_value = _make_apobj(1)
            instance = AppriseNotify(requests=None, params=_make_params())
        mock_apobj = MagicMock()
        instance._apobj = mock_apobj
        return instance, mock_apobj

    def test_run_end_sends_success(self):
        """run_end event (priority 4) maps to NotifyType.SUCCESS = 'success'."""
        instance, mock_apobj = self._make_instance()
        instance.notification({
            "event": "run_end",
            "start_time": "2026-01-01 05:00:00",
            "end_time": "2026-01-01 05:30:00",
            "run_time": "30 minutes",
            "collections_created": 1,
            "collections_modified": 2,
            "collections_deleted": 0,
            "items_added": 10,
            "items_removed": 0,
            "added_to_radarr": 0,
            "added_to_sonarr": 0,
        })
        mock_apobj.notify.assert_called_once()
        _, kwargs = mock_apobj.notify.call_args
        assert kwargs["notify_type"] == "success"
        assert kwargs["title"] == "Run Completed"

    def test_error_sends_failure(self):
        """error event (priority 5) maps to NotifyType.FAILURE = 'failure'."""
        instance, mock_apobj = self._make_instance()
        instance.notification({
            "event": "error",
            "error": "Something went wrong",
            "critical": True,
        })
        mock_apobj.notify.assert_called_once()
        _, kwargs = mock_apobj.notify.call_args
        assert kwargs["notify_type"] == "failure"
        assert "Error" in kwargs["title"]

    def test_version_sends_info(self):
        """version event (priority 2) maps to NotifyType.INFO = 'info'."""
        instance, mock_apobj = self._make_instance()
        instance.notification({
            "event": "version",
            "current": "2.3.1",
            "latest": "2.4.0",
            "notes": "Bug fixes",
        })
        mock_apobj.notify.assert_called_once()
        _, kwargs = mock_apobj.notify.call_args
        assert kwargs["notify_type"] == "info"
        assert kwargs["title"] == "New Version Available"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_apprise_notify.py -v
```

Expected: all tests fail with `ModuleNotFoundError: No module named 'modules.apprise_notify'`.

- [ ] **Step 3: Create `modules/apprise_notify.py`**

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

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_apprise_notify.py -v
```

Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/apprise_notify.py tests/test_apprise_notify.py
git commit -m "feat: add AppriseNotify provider module"
```

---

### Task 3: Update `modules/webhooks.py`

**Files:**
- Modify: `modules/webhooks.py:80-91` (class `__init__`)
- Modify: `modules/webhooks.py:108-113` (`_request` dispatch block)

- [ ] **Step 1: Add `apprise` param to `Webhooks.__init__`**

In `modules/webhooks.py`, change the `__init__` signature at line 80 from:

```python
def __init__(self, config, system_webhooks, library=None, notifiarr=None, gotify=None, ntfy=None):
```

to:

```python
def __init__(self, config, system_webhooks, library=None, notifiarr=None, gotify=None, ntfy=None, apprise=None):
```

Then add `self.apprise = apprise` in the body alongside the other assignments (after `self.ntfy = ntfy`):

```python
        self.ntfy = ntfy
        self.apprise = apprise
```

- [ ] **Step 2: Add dispatch branch in `_request`**

In `_request`, after the `elif webhook == "ntfy":` block (~line 113), add:

```python
            elif webhook == "apprise":
                if self.apprise:
                    self.apprise.notification(json)
```

The full dispatch section should then read:

```python
            if webhook == "notifiarr":
                if self.notifiarr:
                    for x in range(6):
                        response = self.notifiarr.notification(json)
                        if response.status_code < 500:
                            break
            elif webhook == "gotify":
                if self.gotify:
                    self.gotify.notification(json)
            elif webhook == "ntfy":
                if self.ntfy:
                    self.ntfy.notification(json)
            elif webhook == "apprise":
                if self.apprise:
                    self.apprise.notification(json)
            else:
```

- [ ] **Step 3: Run existing tests to confirm nothing broke**

```bash
pytest tests/ -v
```

Expected: all previously passing tests still pass.

- [ ] **Step 4: Commit**

```bash
git add modules/webhooks.py
git commit -m "feat: add apprise dispatch to Webhooks"
```

---

### Task 4: Update `modules/config.py`

**Files:**
- Modify: `modules/config.py` (import, key normalization, factory init, Webhooks calls)

- [ ] **Step 1: Add import**

At the top of `modules/config.py`, add alongside the other provider imports (~line 12):

```python
from modules.apprise_notify import AppriseNotify
```

The imports block should look like:

```python
from modules.apprise_notify import AppriseNotify
from modules.convert import Convert
from modules.ergast import Ergast
from modules.github import GitHub
from modules.gotify import Gotify
```

- [ ] **Step 2: Add config key normalization**

Find the block around line 433 that contains:

```python
        if "ntfy" in self.data:
            self.data["ntfy"] = self.data.pop("ntfy")
```

Add immediately after it:

```python
        if "apprise" in self.data:
            self.data["apprise"] = self.data.pop("apprise")
```

- [ ] **Step 3: Add factory initialization**

Find the ntfy factory block that ends with (~line 797):

```python
        else:
            logger.info("ntfy attribute not found")
```

Add this block immediately after:

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

- [ ] **Step 4: Pass `AppriseFactory` into system-level `Webhooks`**

Find (~line 807):

```python
        self.Webhooks = Webhooks(self, self.webhooks, notifiarr=self.NotifiarrFactory, gotify=self.GotifyFactory, ntfy=self.NtfyFactory)
```

Replace with:

```python
        self.Webhooks = Webhooks(self, self.webhooks, notifiarr=self.NotifiarrFactory, gotify=self.GotifyFactory, ntfy=self.NtfyFactory, apprise=self.AppriseFactory)
```

- [ ] **Step 5: Pass `AppriseFactory` into library-level `Webhooks`**

Find (~line 2175):

```python
                library.Webhooks = Webhooks(self, {}, library=library, notifiarr=self.NotifiarrFactory, gotify=self.GotifyFactory)
```

Replace with:

```python
                library.Webhooks = Webhooks(self, {}, library=library, notifiarr=self.NotifiarrFactory, gotify=self.GotifyFactory, apprise=self.AppriseFactory)
```

- [ ] **Step 6: Run all tests**

```bash
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add modules/config.py
git commit -m "feat: wire AppriseNotify into config and Webhooks"
```

---

### Task 5: Update config template

**Files:**
- Modify: `config/config.yml.template:124-127`

- [ ] **Step 1: Add apprise block**

In `config/config.yml.template`, find the ntfy block:

```yaml
ntfy:
  url: http://192.168.1.12:80      # Enter ntfy server URL (Optional)
  token:                           # Enter ntfy Access Token (Optional)
  topic:                           # Enter ntfy Topic (Optional)
```

Add immediately after:

```yaml
apprise:
  config:                          # Enter path or URL to Apprise config file (Optional)
```

- [ ] **Step 2: Commit**

```bash
git add config/config.yml.template
git commit -m "docs: add apprise config block to template"
```

---

### Task 6: Full test run

- [ ] **Step 1: Run the full test suite**

```bash
pytest tests/ -v
```

Expected: all tests pass, zero failures.

- [ ] **Step 2: Verify import chain**

```bash
python -c "from modules.apprise_notify import AppriseNotify; print('OK')"
```

Expected: prints `OK` with no errors.
