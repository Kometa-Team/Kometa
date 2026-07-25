"""Shared test fixtures, fakes, and utilities for all Kometa test modules.

Use these instead of redefining FakeLogger / FakeResponse / FakeRequests
in every test file.  Import the classes directly; use the autouse fixtures
for logger patching.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from lxml import html as lxml_html

# ═══════════════════════════════════════════════════════════════════════
# Shared Fake Classes
# ═══════════════════════════════════════════════════════════════════════


class FakeLogger:
    """Captures log output for assertions.

    Supports all methods that the real MyLogger exposes: info, warning,
    error, debug, separator, secret, and clear_errors.  Unknown methods
    return a no-op lambda so this can be monkeypatched onto any module
    without AttributeError.
    """

    def __init__(self):
        self.info_messages: list[str] = []
        self.warning_messages: list[str] = []
        self.error_messages: list[str] = []
        self.debug_messages: list[str] = []
        self.secrets: list[str] = []
        self.saved_errors: list[str] = []
        self.save_errors = False

    # ── Standard log methods ────────────────────────────────────────

    def info(self, message: str = "") -> None:
        self.info_messages.append(str(message))

    def warning(self, message: str) -> None:
        self.warning_messages.append(str(message))

    def error(self, message: str) -> None:
        self.error_messages.append(str(message))

    def debug(self, message: str = "") -> None:
        self.debug_messages.append(str(message))

    def separator(self, *args: Any, **kwargs: Any) -> None:
        pass  # separator is cosmetic; never assert on it

    # ── Secret redaction helpers (used by test_config) ───────────────

    def secret(self, text: str) -> None:
        if text and str(text) not in self.secrets:
            self.secrets.append(str(text))

    def clear_errors(self) -> None:
        self.saved_errors = []

    # ── Catch-all for any other logger calls ─────────────────────────

    def __getattr__(self, name: str) -> Any:
        return lambda *args, **kwargs: None


class FakeResponse:
    """Mimics a ``requests.Response`` for test use.

    Parameters
    ----------
    payload : optional
        Data returned by ``.json()`` (and serialised into ``.content``
        if ``content`` is not provided explicitly).
    status_code : int
        HTTP status (default 200).
    content : optional bytes
        Raw body.  If omitted, ``json.dumps(payload).encode("utf-8")``
        is used.
    headers : dict
        Response headers (default empty).
    json_error : optional Exception
        If set, ``.json()`` will raise this exception instead of
        returning the payload.
    """

    def __init__(
        self,
        payload: Any = None,
        status_code: int = 200,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
        json_error: Exception | None = None,
    ):
        self.payload = payload
        self.status_code = status_code
        self.content = json.dumps(payload).encode("utf-8") if content is None and payload is not None else content
        self.headers = headers or {}
        self.json_error = json_error
        self.text = str(payload) if payload is not None else self.content

    def json(self) -> Any:
        if self.json_error:
            raise self.json_error
        return self.payload


class FakeRequests:
    """Mimics the ``modules.request.Requests`` API for test use.

    Supports the two call patterns used across the codebase:

    * ``.get(url)`` → returns a ``FakeResponse``
    * ``.get_cloudscrape_html(url, language=None)`` → returns an lxml
      HTML element tree
    * ``.file_yaml(path, **kwargs)`` → returns a ``YAML`` object
    * ``.has_new_version()`` → returns ``False``

    Parameters
    ----------
    get_payloads : dict[str, Any]
        Mapping of URL → payload (or FakeResponse).  Used by ``.get()``.
    html_pages : dict[str, str]
        Mapping of URL → raw HTML string.  Used by
        ``.get_cloudscrape_html()``.
    """

    def __init__(
        self,
        get_payloads: dict[str, Any] | None = None,
        html_pages: dict[str, str] | None = None,
    ):
        self.get_payloads = get_payloads or {}
        self.html_pages = html_pages or {}

    def get(self, url: str) -> FakeResponse:
        payload = self.get_payloads[url]
        return payload if isinstance(payload, FakeResponse) else FakeResponse(payload)

    def get_cloudscrape_html(self, url: str, language: str | None = None) -> Any:
        return lxml_html.fromstring(self.html_pages.get(url, "<html><body></body></html>"))

    def file_yaml(self, path: str, **kwargs: Any) -> Any:
        from modules.request import YAML

        return YAML(path=path, **kwargs)

    @staticmethod
    def has_new_version() -> bool:
        return False


class FakeCache:
    """Mimics ``modules.cache.Cache`` for ID-map lookups.

    Starts with an optional initial mapping of ID → value.
    Tracks all updates so tests can verify write-behaviour.

    Parameters
    ----------
    initial : dict[str, Any] | None
        Pre-populated cache entries (letterboxd_id → tmdb_id, etc.).
    """

    def __init__(self, initial: dict[str, Any] | None = None):
        self.map: dict[str, Any] = initial or {}
        self.updates: list[tuple[str, Any]] = []

    def query_letterboxd_map(self, letterboxd_id: str) -> tuple[Any, bool] | tuple[None, None]:
        if letterboxd_id in self.map:
            return self.map[letterboxd_id], False
        return None, None

    def update_letterboxd_map(self, expired: bool, letterboxd_id: str, tmdb_id: int) -> None:
        self.map[letterboxd_id] = tmdb_id
        self.updates.append((letterboxd_id, tmdb_id))

    def __getattr__(self, name: str) -> Any:
        return lambda *args, **kwargs: None


# ═══════════════════════════════════════════════════════════════════════
# Autouse Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def patch_util_logger(monkeypatch: pytest.MonkeyPatch) -> FakeLogger:
    """Patch ``modules.util.logger`` with a ``FakeLogger``.

    This runs automatically before every test.  Individual test files
    that need to patch their own module-level logger can do so
    explicitly — this fixture only touches ``util.logger`` to prevent
    ``AttributeError: 'NoneType' object has no attribute 'info'`` during
    import.
    """
    logger = FakeLogger()
    monkeypatch.setattr("modules.util.logger", logger)
    return logger


# ═══════════════════════════════════════════════════════════════════════
# Shared Factory Functions
# ═══════════════════════════════════════════════════════════════════════


def make_simple_namespace(**kwargs: Any) -> SimpleNamespace:
    """Quick helper to build a ``SimpleNamespace`` from kwargs."""
    return SimpleNamespace(**kwargs)


def make_mock_response(payload: Any = None, status_code: int = 200) -> MagicMock:
    """Return a ``unittest.mock.MagicMock`` that looks like a response.

    Use this for modules that expect a ``requests.Response``-like object
    rather than the thin ``FakeResponse`` wrapper.
    """
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = json.dumps(payload).encode("utf-8") if payload is not None else b""
    resp.text = str(payload) if payload is not None else ""
    resp.json.return_value = payload
    return resp
