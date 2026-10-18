"""Regression tests for scoped SSL warning suppression."""

import warnings
from types import SimpleNamespace

import urllib3


def test_scoped_unverified_session_suppresses_insecure_request_warning(monkeypatch):
    import requests

    from modules.request import Requests

    def warning_request(self, method, url, **kwargs):
        warnings.warn("unverified request", urllib3.exceptions.InsecureRequestWarning)
        return SimpleNamespace(status_code=200)

    monkeypatch.setattr(requests.Session, "request", warning_request)
    req = Requests.__new__(Requests)

    session = req.create_session(verify_ssl=False)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        response = session.get("https://example.com")

    assert response.status_code == 200
    assert not any(isinstance(item.message, urllib3.exceptions.InsecureRequestWarning) for item in caught)


def test_scoped_unverified_session_does_not_disable_warnings_globally(monkeypatch):
    import urllib3

    from modules.request import Requests

    calls = []
    monkeypatch.setattr(urllib3, "disable_warnings", lambda *args, **kwargs: calls.append(args))
    req = Requests.__new__(Requests)

    session = req.create_session(verify_ssl=False)

    assert session.verify is False
    assert calls == []
