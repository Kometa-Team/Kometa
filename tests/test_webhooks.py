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
