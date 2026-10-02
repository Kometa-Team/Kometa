"""Tests for modules/request.py — Version helper and request wrappers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError
from tenacity import wait_none

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


class TestYAMLReadOnly:
    """read_only=True swaps in ruamel's safe loader for files Kometa never save()s back out."""

    def test_read_only_still_parses_content_correctly(self, tmp_path):
        from modules.request import YAML

        path = tmp_path / "data.yml"
        path.write_text("collections:\n  Test:\n    key: value\n")
        yaml = YAML(path=str(path), read_only=True)
        assert yaml.data == {"collections": {"Test": {"key": "value"}}}

    def test_read_only_save_raises_failed(self, tmp_path):
        from modules.request import YAML
        from modules.util import Failed

        path = tmp_path / "data.yml"
        path.write_text("a: 1\n")
        yaml = YAML(path=str(path), read_only=True)
        with pytest.raises(Failed, match="read_only"):
            yaml.save()

    def test_read_only_input_data_save_raises_failed(self):
        """input_data (no path) already can't write anywhere - read_only=True still guards it explicitly."""
        from modules.request import YAML
        from modules.util import Failed

        yaml = YAML(input_data=b"a: 1\n", read_only=True)
        with pytest.raises(Failed, match="read_only"):
            yaml.save()

    def test_default_not_read_only_can_still_save(self, tmp_path):
        """Regression: the read_only change must not affect any existing read-write caller."""
        from modules.request import YAML

        path = tmp_path / "data.yml"
        path.write_text("a: 1\n")
        yaml = YAML(path=str(path))
        assert yaml.read_only is False
        yaml.data["a"] = 2
        yaml.save()
        assert path.read_text() == "a: 2\n"


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

    def head(self, url, **kwargs):
        self.calls.append(("head", url, kwargs))
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

        from modules import util
        from modules.request import Requests

        assert isinstance(Requests.get.retry.wait, util.wait_for_retry_after_header)
        assert isinstance(Requests.get.retry.wait.fallback, wait_exponential)

    def test_post_uses_exponential_backoff(self):
        from tenacity import wait_exponential

        from modules import util
        from modules.request import Requests

        assert isinstance(Requests.post.retry.wait, util.wait_for_retry_after_header)
        assert isinstance(Requests.post.retry.wait.fallback, wait_exponential)

    def test_head_uses_exponential_backoff(self):
        from tenacity import wait_exponential

        from modules import util
        from modules.request import Requests

        assert isinstance(Requests.head.retry.wait, util.wait_for_retry_after_header)
        assert isinstance(Requests.head.retry.wait.fallback, wait_exponential)

    @staticmethod
    def rate_limited_response(retry_after="30"):
        response = MagicMock(status_code=429, reason="Too Many Requests", headers={"Retry-After": retry_after}, content=b"")
        response.raise_for_status.side_effect = HTTPError(response=response)
        return response

    @pytest.mark.parametrize("method", ["get", "head", "post"])
    def test_retries_rate_limits_for_shared_methods(self, monkeypatch, method):
        from modules.request import Requests

        limited = self.rate_limited_response()
        success = SimpleNamespace(status_code=200)
        req = make_requests()
        req.session = MagicMock()
        getattr(req.session, method).side_effect = [limited, success]
        monkeypatch.setattr(getattr(Requests, method).retry, "wait", wait_none())

        assert getattr(req, method)("https://example.com/rate-limited") is success
        assert getattr(req.session, method).call_count == 2

    def test_rate_limit_exhaustion_becomes_failed(self, monkeypatch):
        from modules.request import Requests
        from modules.util import Failed

        limited = self.rate_limited_response()
        req = make_requests()
        req.session = MagicMock()
        req.session.get.return_value = limited
        monkeypatch.setattr(Requests.get.retry, "wait", wait_none())

        with pytest.raises(Failed, match="Too many requests.*rate-limited"):
            req.get("https://example.com/rate-limited")
        assert req.session.get.call_count == 6

    def test_non_rate_limit_response_is_not_retried(self):
        unavailable = SimpleNamespace(status_code=503)
        req = make_requests()
        req.session = MagicMock()
        req.session.get.return_value = unavailable

        assert req.get("https://example.com/unavailable") is unavailable
        req.session.get.assert_called_once()

    @pytest.mark.parametrize(
        ("retry_after", "expected"),
        [
            ("30", 30),
            ("-10", 0),
            ("invalid", None),
            (None, None),
        ],
    )
    def test_retry_after_seconds(self, retry_after, expected):
        from modules.util import wait_for_retry_after_header

        assert wait_for_retry_after_header.parse(retry_after) == expected

    def test_retry_after_http_date(self):
        from modules.util import wait_for_retry_after_header

        now = datetime(2026, 8, 24, 22, 0, tzinfo=timezone.utc)
        retry_after = format_datetime(now + timedelta(seconds=45), usegmt=True)

        assert wait_for_retry_after_header.parse(retry_after, now=now) == 45


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


class _FakeImageResponse:
    def __init__(self, status_code=200, content_type="image/png", content=b"fake-png-bytes"):
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}
        self.content = content


def make_image_requests():
    """Bare Requests instance with just the attributes get_image() touches, plus its get()/head() cast to MagicMock for mock-attribute access (same cast pattern test_plex.py uses for this pyright gotcha)."""
    req = make_requests()
    req._image_url_cache = {}
    req.image_content_types = ["image/png", "image/jpeg", "image/webp"]
    req.get = MagicMock()
    req.head = MagicMock()
    return req, cast(MagicMock, req.get), cast(MagicMock, req.head)


class TestGetImageMemoization:
    """get_image() used to hit the network on every call, even for a URL already fetched this run."""

    def test_repeat_url_does_not_refetch(self):
        req, mock_get, _ = make_image_requests()
        mock_get.return_value = _FakeImageResponse()
        first = req.get_image("https://example.com/badge.png")
        second = req.get_image("https://example.com/badge.png")
        assert first is second
        assert mock_get.call_count == 1  # second call must be served from the memo, not a second fetch

    def test_different_urls_both_fetch(self):
        req, mock_get, _ = make_image_requests()
        mock_get.return_value = _FakeImageResponse()
        req.get_image("https://example.com/a.png")
        req.get_image("https://example.com/b.png")
        assert mock_get.call_count == 2

    def test_failure_is_not_cached_and_retries_next_call(self):
        from modules.util import Failed

        req, mock_get, _ = make_image_requests()
        mock_get.side_effect = [_FakeImageResponse(status_code=404), _FakeImageResponse(status_code=200)]
        with pytest.raises(Failed):
            req.get_image("https://example.com/missing.png")
        second = req.get_image("https://example.com/missing.png")
        assert second.status_code == 200
        assert mock_get.call_count == 2  # a failed lookup must not poison the cache - retried fresh next call

    def test_non_image_content_type_not_cached(self):
        from modules.util import Failed

        req, mock_get, _ = make_image_requests()
        mock_get.return_value = _FakeImageResponse(content_type="text/html")
        with pytest.raises(Failed):
            req.get_image("https://example.com/not-an-image")
        with pytest.raises(Failed):
            req.get_image("https://example.com/not-an-image")
        assert mock_get.call_count == 2

    def test_cached_response_content_unchanged(self):
        req, mock_get, _ = make_image_requests()
        mock_get.return_value = _FakeImageResponse(content=b"real-bytes")
        first = req.get_image("https://example.com/badge.png")
        second = req.get_image("https://example.com/badge.png")
        assert first.content == b"real-bytes"
        assert second.content == b"real-bytes"

    def test_session_argument_path_also_memoizes(self):
        req, _, _unused_head = make_image_requests()
        session = MagicMock()
        session.get.return_value = _FakeImageResponse()
        req.get_image("https://example.com/badge.png", session=session)
        req.get_image("https://example.com/badge.png", session=session)
        assert session.get.call_count == 1


class TestGetImageValidateOnly:
    """validate_only=True (builder.py's url_poster/url_background/url_logo/url_square_art checks) uses HEAD instead of GET - same status/Content-Type validation, without downloading the body."""

    def test_validate_only_uses_head_not_get(self):
        req, mock_get, mock_head = make_image_requests()
        mock_head.return_value = _FakeImageResponse()
        req.get_image("https://example.com/badge.png", validate_only=True)
        assert mock_head.call_count == 1
        assert mock_get.call_count == 0

    def test_default_still_uses_get(self):
        req, mock_get, mock_head = make_image_requests()
        mock_get.return_value = _FakeImageResponse()
        req.get_image("https://example.com/badge.png")
        assert mock_get.call_count == 1
        assert mock_head.call_count == 0

    def test_validate_only_repeat_url_does_not_refetch(self):
        req, _, mock_head = make_image_requests()
        mock_head.return_value = _FakeImageResponse()
        first = req.get_image("https://example.com/badge.png", validate_only=True)
        second = req.get_image("https://example.com/badge.png", validate_only=True)
        assert first is second
        assert mock_head.call_count == 1

    def test_validate_only_raises_failed_on_404(self):
        from modules.util import Failed

        req, _, mock_head = make_image_requests()
        mock_head.return_value = _FakeImageResponse(status_code=404)
        with pytest.raises(Failed):
            req.get_image("https://example.com/missing.png", validate_only=True)

    def test_validate_only_raises_failed_on_non_image_content_type(self):
        from modules.util import Failed

        req, _, mock_head = make_image_requests()
        mock_head.return_value = _FakeImageResponse(content_type="text/html")
        with pytest.raises(Failed):
            req.get_image("https://example.com/not-an-image", validate_only=True)

    def test_head_and_get_cache_entries_are_independent(self):
        """A validate_only HEAD response (no body) must never be served back to a caller that needs real content, or vice versa."""
        req, mock_get, mock_head = make_image_requests()
        mock_head.return_value = _FakeImageResponse()
        mock_get.return_value = _FakeImageResponse(content=b"real-bytes")
        head_result = req.get_image("https://example.com/badge.png", validate_only=True)
        get_result = req.get_image("https://example.com/badge.png")
        assert head_result is not get_result
        assert mock_head.call_count == 1
        assert mock_get.call_count == 1

    def test_session_argument_path_uses_head_when_validate_only(self):
        req, _, _unused_head = make_image_requests()
        session = MagicMock()
        session.head.return_value = _FakeImageResponse()
        req.get_image("https://example.com/badge.png", session=session, validate_only=True)
        assert session.head.call_count == 1
        assert session.head.call_args.kwargs.get("allow_redirects") is True
        assert session.get.call_count == 0


class TestGetImageStableAssetSkip:
    """validate_only checks against Kometa's own shipped assets (Default-Images, People-Images-*) skip the network round-trip entirely - only arbitrary user url_poster/url_background/url_logo/url_square_art values need live validation."""

    def test_kometa_team_url_skips_network_when_validate_only(self):
        req, mock_get, mock_head = make_image_requests()
        result = req.get_image("https://raw.githubusercontent.com/Kometa-Team/Default-Images/master/award/logos/BAFTA.png", validate_only=True)
        assert result is None
        assert mock_head.call_count == 0
        assert mock_get.call_count == 0

    def test_kometa_team_people_images_url_skips_network_when_validate_only(self):
        req, mock_get, mock_head = make_image_requests()
        result = req.get_image("https://raw.githubusercontent.com/Kometa-Team/People-Images-Portrait/master/A/Images/Actor.jpg", validate_only=True)
        assert result is None
        assert mock_head.call_count == 0
        assert mock_get.call_count == 0

    def test_kometa_team_url_still_fetches_when_not_validate_only(self):
        """The skip is scoped to validate_only - a real poster/background/logo download must still hit the network."""
        req, mock_get, mock_head = make_image_requests()
        mock_get.return_value = _FakeImageResponse()
        result = req.get_image("https://raw.githubusercontent.com/Kometa-Team/Default-Images/master/award/logos/BAFTA.png")
        assert result is not None
        assert mock_get.call_count == 1
        assert mock_head.call_count == 0

    def test_arbitrary_user_url_still_validated(self):
        """The staleness risk this validation exists to catch is arbitrary/user-supplied URLs - those must never be skipped."""
        req, mock_get, mock_head = make_image_requests()
        mock_head.return_value = _FakeImageResponse()
        req.get_image("https://example.com/my-custom-poster.jpg", validate_only=True)
        assert mock_head.call_count == 1

    def test_other_github_org_url_still_validated(self):
        """Only the Kometa-Team org prefix is trusted - a different GitHub org/user is not Kometa's own maintained content."""
        req, mock_get, mock_head = make_image_requests()
        mock_head.return_value = _FakeImageResponse()
        req.get_image("https://raw.githubusercontent.com/some-other-user/posters/master/poster.jpg", validate_only=True)
        assert mock_head.call_count == 1

    def test_kometa_team_url_skip_not_cached(self):
        """Skipped calls return None without touching _image_url_cache - nothing to memoize since no network call was made."""
        req, mock_get, mock_head = make_image_requests()
        req.get_image("https://raw.githubusercontent.com/Kometa-Team/Default-Images/master/award/logos/BAFTA.png", validate_only=True)
        assert req._image_url_cache == {}


class TestHeadFollowsRedirects:
    """requests defaults HEAD to not following redirects (unlike GET) - Requests.head() must override that so validate_only behaves the same as GET for a redirected URL."""

    def test_head_passes_allow_redirects_true(self):
        req = make_requests()
        req.session = RecordingSession()  # pyright: ignore[reportAttributeAccessIssue]
        req.head("http://example.com")
        assert req.session.calls[0][2].get("allow_redirects") is True  # pyright: ignore[reportAttributeAccessIssue]


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


class _FakeYamlResponse:
    def __init__(self, status_code=200, content=b"a: 1\n"):
        self.status_code = status_code
        self.content = content


class TestGetYamlReadOnly:
    """Requests.get_yaml() never sets a path (save() was already a no-op), so it always requests the fast read_only loader."""

    def test_result_is_read_only(self):
        req = make_requests()
        req.get = MagicMock(return_value=_FakeYamlResponse())
        result = req.get_yaml("https://example.com/data.yml")
        assert result.read_only is True
        assert result.data == {"a": 1}

    def test_result_save_raises_failed(self):
        from modules.util import Failed

        req = make_requests()
        req.get = MagicMock(return_value=_FakeYamlResponse())
        result = req.get_yaml("https://example.com/data.yml")
        with pytest.raises(Failed, match="read_only"):
            result.save()


class TestFileYamlReadOnlyPassthrough:
    """Requests.file_yaml()'s read_only kwarg must reach the underlying YAML object unchanged in both directions."""

    def test_read_only_true_passes_through(self, tmp_path):
        req = make_requests()
        path = tmp_path / "data.yml"
        path.write_text("a: 1\n")
        result = req.file_yaml(str(path), read_only=True)
        assert result.read_only is True

    def test_default_is_not_read_only(self, tmp_path):
        req = make_requests()
        path = tmp_path / "data.yml"
        path.write_text("a: 1\n")
        result = req.file_yaml(str(path))
        assert result.read_only is False

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
