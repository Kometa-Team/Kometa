"""Tests for modules/webhooks.py."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 — pre-import to break circular deps
from tests.conftest import FakeLogger


class TestWebhooks:
    @pytest.fixture
    def wh(self, monkeypatch):
        monkeypatch.setattr("modules.webhooks.logger", FakeLogger())
        from modules.webhooks import Webhooks

        w = Webhooks.__new__(Webhooks)
        w.config = MagicMock()
        w.config.libraries = []
        w.error_webhooks = []
        w.version_webhooks = []
        w.start_time_webhooks = []
        w.end_time_webhooks = []
        w.changes_webhooks = []
        w.delete_webhooks = []
        w.notifiarr = None
        w.gotify = None
        w.ntfy = None
        w.apprise = None
        return w

    def test_error_hooks_no_webhooks_does_not_raise(self, wh):
        wh.error_hooks("test error", critical=False)

    def test_delete_hooks_no_webhooks_does_not_raise(self, wh):
        wh.delete_hooks("test delete")

    @pytest.mark.parametrize("url", ["<<https://discord.com/api/webhooks/example/secret", "https://example.com/<token>", "example.com/hook", "ftp://example.com/hook", "https://example.com:bad/hook"])
    def test_invalid_url_is_reported_without_sending(self, wh, monkeypatch, url):
        logger = MagicMock()
        monkeypatch.setattr("modules.webhooks.logger", logger)
        wh.library = None
        wh.requests = MagicMock()

        wh._request([url], {"event": "delete"})

        wh.requests.post.assert_not_called()
        logger.error.assert_called_once()
        assert "Cannot send delete notification: invalid webhook URL" in logger.error.call_args.args[0]
        assert url not in logger.error.call_args.args[0]
        logger.stacktrace.assert_not_called()

    @pytest.mark.parametrize("wrapped", [False, True])
    def test_delivery_timeout_continues_to_next_webhook(self, wh, monkeypatch, wrapped):
        from concurrent.futures import Future

        from requests.exceptions import ReadTimeout
        from tenacity import RetryError

        logger = MagicMock()
        monkeypatch.setattr("modules.webhooks.logger", logger)
        wh.library = None
        wh.requests = MagicMock()
        error = ReadTimeout("private webhook token")
        if wrapped:
            future = Future()
            future.set_exception(error)
            error = RetryError(future)
        response = MagicMock(status_code=204)
        response.json.return_value = {}
        wh.requests.post.side_effect = [error, response]

        wh._request(["https://example.com/one", "https://example.com/two"], {"event": "delete"})

        assert wh.requests.post.call_count == 2
        logger.error.assert_called_once()
        assert "webhook server timed out" in logger.error.call_args.args[0]
        assert "private" not in logger.error.call_args.args[0]
        logger.stacktrace.assert_not_called()
