"""Tests for modules/request.py — Version helper and request wrappers."""

from __future__ import annotations

import pytest

import modules.builder  # noqa: F401


class TestVersion:
    def test_default_str_is_unknown(self):
        from modules.request import Version

        assert str(Version()) == "Unknown"

    def test_str_includes_part(self):
        from modules.request import Version

        assert str(Version("2.4.0", "42")).endswith("42")

    def test_truthy_when_versioned(self):
        from modules.request import Version

        assert bool(Version("1.0.0", "0")) is True

    def test_falsy_when_unknown(self):
        from modules.request import Version

        assert bool(Version()) is False


class TestGetHeader:
    """Regression: get_header used to return None when called with all-None args."""

    def test_passthrough_when_headers_provided(self):
        from modules.request import get_header

        assert get_header({"X-Custom": "1"}, False, None) == {"X-Custom": "1"}

    def test_returns_dict_with_user_agent_when_header_true(self):
        from modules.request import get_header

        result = get_header(None, True, None)
        assert "User-Agent" in result
        assert "Accept-Language" in result

    def test_returns_empty_dict_when_everything_falsy(self):
        """Used to return None (implicit) — now returns {} so callers can safely .pop()."""
        from modules.request import get_header

        assert get_header(None, False, None) == {}


class TestYAML:
    """Regression: YAML used to crash with TypeError when neither path nor input_data set."""

    def test_missing_both_path_and_input_data_raises_failed(self):
        from modules.request import YAML
        from modules.util import Failed

        with pytest.raises(Failed, match="Either path or input_data must be provided"):
            YAML()


def make_requests():
    """Bare Requests instance without hitting the network or cloudscraper."""
    from modules.request import Requests

    return Requests.__new__(Requests)


class RecordingSession:
    """Stand-in for requests.Session that records call kwargs."""

    def __init__(self, response=None):
        from types import SimpleNamespace

        self.calls = []
        self._response = response if response is not None else SimpleNamespace(status_code=200)

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return self._response

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return self._response


class FakeStreamResponse:
    def __init__(self, chunks):
        self._chunks = chunks
        self.headers = {"content-length": str(sum(len(c) for c in chunks))}

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size=8192):
        yield from self._chunks

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class CountingLogger:
    def __init__(self):
        self.ghost_messages = []

    def ghost(self, message):
        self.ghost_messages.append(str(message))

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class TestTimeouts:
    """A stalled external server must not hang a run forever."""

    def test_get_sends_default_timeout(self):
        import modules.request as request_module

        req = make_requests()
        req.session = RecordingSession()
        req.get("http://example.com")
        assert req.session.calls[0][2].get("timeout") == request_module.DEFAULT_TIMEOUT

    def test_post_sends_default_timeout(self):
        import modules.request as request_module

        req = make_requests()
        req.session = RecordingSession()
        req.post("http://example.com")
        assert req.session.calls[0][2].get("timeout") == request_module.DEFAULT_TIMEOUT


class TestRetryPolicy:
    """Retries back off exponentially instead of sleeping a fixed 10s each attempt."""

    def test_get_uses_exponential_backoff(self):
        from tenacity import wait_exponential

        from modules.request import Requests

        assert isinstance(Requests.get.retry.wait, wait_exponential)

    def test_post_uses_exponential_backoff(self):
        from tenacity import wait_exponential

        from modules.request import Requests

        assert isinstance(Requests.post.retry.wait, wait_exponential)


class TestGetStream:
    def test_progress_logging_is_throttled(self, monkeypatch, tmp_path):
        import modules.request as request_module

        fake_logger = CountingLogger()
        monkeypatch.setattr(request_module, "logger", fake_logger)
        chunks = [b"x" * 100] * 200
        req = make_requests()
        req.session = RecordingSession(response=FakeStreamResponse(chunks))
        location = tmp_path / "out.bin"

        req.get_stream("http://example.com/file", str(location))

        assert location.read_bytes() == b"x" * 20000
        # Chunks arrive instantly here, so a throttled loop logs far fewer
        # than one ghost per 8KB chunk (previously 200 messages).
        assert len(fake_logger.ghost_messages) < 10
        assert "100.00" in fake_logger.ghost_messages[-1]

    def test_stream_sends_timeout(self, monkeypatch, tmp_path):
        import modules.request as request_module

        monkeypatch.setattr(request_module, "logger", CountingLogger())
        req = make_requests()
        req.session = RecordingSession(response=FakeStreamResponse([b"data"]))
        req.get_stream("http://example.com/file", str(tmp_path / "out.bin"))
        assert req.session.calls[0][2].get("timeout") == request_module.DEFAULT_TIMEOUT


class TestNoVerifySSL:
    """Per-session SSL opt-outs must not silence InsecureRequestWarning process-wide."""

    def test_scoped_session_keeps_warnings_enabled(self, monkeypatch):
        import urllib3

        calls = []
        monkeypatch.setattr(urllib3, "disable_warnings", lambda *args, **kwargs: calls.append(args))
        import requests as requests_lib

        req = make_requests()
        req.session = requests_lib.Session()
        scoped = req.create_session(verify_ssl=False)
        assert scoped.verify is False
        assert calls == []

    def test_global_opt_out_disables_warnings(self, monkeypatch):
        import urllib3

        calls = []
        monkeypatch.setattr(urllib3, "disable_warnings", lambda *args, **kwargs: calls.append(args))
        import requests as requests_lib

        req = make_requests()
        req.session = requests_lib.Session()
        req.no_verify_ssl()
        assert req.session.verify is False
        assert len(calls) == 1
