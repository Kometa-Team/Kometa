"""Tests for modules/request.py — Version helper and request wrappers."""

from __future__ import annotations

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
