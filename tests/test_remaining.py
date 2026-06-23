"""Tests for library.py, webhooks.py, poster.py, convert.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed
from tests.conftest import FakeLogger

# ═══════════════════════════════════════════════════════════════════════
# Library (abstract base — tested through Plex)
# ═══════════════════════════════════════════════════════════════════════

# Library is an ABC with abstract methods. Tested via test_plex.py.


# ═══════════════════════════════════════════════════════════════════════
# Webhooks
# ═══════════════════════════════════════════════════════════════════════


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

    def test_error_hooks_no_webhooks(self, wh):
        wh.error_hooks("test error", critical=False)
        # Should not raise

    def test_delete_hooks_no_webhooks(self, wh):
        wh.delete_hooks("test delete")
        # Should not raise


# ═══════════════════════════════════════════════════════════════════════
# ImageData (poster.py)
# ═══════════════════════════════════════════════════════════════════════


class TestImageData:
    def test_stores_attributes(self, tmp_path):
        from modules.poster import ImageData

        path = tmp_path / "test.jpg"
        path.write_bytes(b"data")
        d = ImageData("poster", str(path), prefix="test", image_type="poster", is_url=False, compare="abc")
        assert d.attribute == "poster"
        assert d.compare == "abc"

    def test_url_mode_skips_file_check(self):
        from modules.poster import ImageData

        d = ImageData("poster", "http://example.com/poster.jpg", is_url=True)
        assert d.location == "http://example.com/poster.jpg"

    def test_str(self, tmp_path):
        from modules.poster import ImageData

        path = tmp_path / "test.jpg"
        path.write_bytes(b"data")
        d = ImageData("poster", str(path))
        assert str(d) is not None


# ═══════════════════════════════════════════════════════════════════════
# Convert
# ═══════════════════════════════════════════════════════════════════════


class TestConvert:
    @pytest.fixture
    def adapter(self):
        from modules.convert import Convert

        c = Convert.__new__(Convert)
        c.requests = MagicMock()
        c.cache = MagicMock()
        c.tmdb = MagicMock()
        return c

    def test_tmdb_to_imdb_cache_hit(self, adapter):
        adapter.cache.query_imdb_to_tmdb_map.return_value = ("tt999", False)
        assert adapter.tmdb_to_imdb(550, is_movie=True, fail=False) == "tt999"

    def test_imdb_to_tmdb_cache_hit(self, adapter):
        adapter.cache.query_imdb_to_tmdb_map.return_value = (550, False, None)
        tmdb_id, tmdb_type = adapter.imdb_to_tmdb("tt123", fail=False)
        assert tmdb_id == 550

    def test_tmdb_to_tvdb_cache_hit(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (368207, False)
        assert adapter.tmdb_to_tvdb(550, fail=False) == 368207

    def test_tvdb_to_tmdb_cache_hit(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (550, False)
        assert adapter.tvdb_to_tmdb(368207, fail=False) == 550
