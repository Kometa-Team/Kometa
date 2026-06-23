"""Tests for modules/poster.py — ImageData and friends."""

from __future__ import annotations

import pytest

import modules.builder  # noqa: F401


class TestImageData:
    def test_stores_attributes(self, tmp_path):
        from modules.poster import ImageData

        path = tmp_path / "test.jpg"
        path.write_bytes(b"data")
        d = ImageData(
            "poster",
            str(path),
            prefix="test",
            image_type="poster",
            is_url=False,
            compare="abc",
        )
        assert d.attribute == "poster"
        assert d.compare == "abc"

    def test_url_mode_skips_file_check(self):
        from modules.poster import ImageData

        d = ImageData("poster", "http://example.com/poster.jpg", is_url=True)
        assert d.location == "http://example.com/poster.jpg"

    def test_str_returns_something(self, tmp_path):
        from modules.poster import ImageData

        path = tmp_path / "test.jpg"
        path.write_bytes(b"data")
        d = ImageData("poster", str(path))
        assert str(d) is not None
