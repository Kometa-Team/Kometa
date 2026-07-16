"""Tests for modules/convert.py — ID lookups across sources."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed


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
        tmdb_id, _ = adapter.imdb_to_tmdb("tt123", fail=False)
        assert tmdb_id == 550

    def test_tmdb_to_tvdb_cache_hit(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (368207, False)
        assert adapter.tmdb_to_tvdb(550, fail=False) == 368207

    def test_tvdb_to_tmdb_cache_hit(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (550, False)
        assert adapter.tvdb_to_tmdb(368207, fail=False) == 550

    def test_tmdb_to_tvdb_negative_cache_hit(self, adapter):
        # A cached "confirmed no mapping" row (None value, not expired) must short-circuit without hitting the API.
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (None, False)
        assert adapter.tmdb_to_tvdb(550, fail=False) is None
        adapter.tmdb.convert_from.assert_not_called()

    def test_tmdb_to_tvdb_writes_negative_cache_on_confirmed_miss(self, adapter):
        # No cached row yet (expired=None); the API call succeeds but returns nothing, so the miss gets cached.
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (None, None)
        adapter.tmdb.convert_from.return_value = None
        assert adapter.tmdb_to_tvdb(550, fail=False) is None
        adapter.cache.update_tmdb_to_tvdb_map.assert_called_once_with(None, 550, None, is_negative=True)

    def test_tmdb_to_tvdb_does_not_cache_negative_on_api_error(self, adapter):
        # A network/API error must not be mistaken for a confirmed "no mapping" result.
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (None, None)
        adapter.tmdb.convert_from.side_effect = Failed("boom")
        assert adapter.tmdb_to_tvdb(550, fail=False) is None
        adapter.cache.update_tmdb_to_tvdb_map.assert_not_called()

    def test_tmdb_to_tvdb_positive_result_not_cached_as_negative(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (None, None)
        adapter.tmdb.convert_from.return_value = 368207
        assert adapter.tmdb_to_tvdb(550, fail=False) == 368207
        adapter.cache.update_tmdb_to_tvdb_map.assert_called_once_with(None, 550, 368207)

    def test_hama_suffix_extracts_trailing_id(self):
        from modules.convert import Convert

        assert Convert._hama_suffix("anidb-12345") == "12345"
        assert Convert._hama_suffix("tvdb-67890") == "67890"
        # Hama also has an 'aNNN' anidb format the call sites peel a prefix off later;
        # _hama_suffix just returns everything after the first dash unchanged.
        assert Convert._hama_suffix("anidb-a987") == "a987"

    def test_hama_suffix_raises_on_malformed_id(self):
        from modules.convert import Convert
        from modules.util import MappingConvertError

        with pytest.raises(MappingConvertError, match="Malformed Hama ID 'anidb'"):
            Convert._hama_suffix("anidb")
