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
