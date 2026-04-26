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
