"""Tests for modules/convert.py — ID lookups across sources."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401


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

    def test_tmdb_to_tvdb_normalizes_numeric_string(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (None, None)
        adapter.tmdb.convert_from.return_value = "368207"

        assert adapter.tmdb_to_tvdb(550, fail=False) == 368207
        adapter.cache.update_tmdb_to_tvdb_map.assert_called_once_with(None, 550, 368207)

    def test_tmdb_to_tvdb_rejects_malformed_tmdb_external_id(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (None, None)
        adapter.tmdb.convert_from.return_value = "tt3348258"

        assert adapter.tmdb_to_tvdb(12345, fail=False) is None
        adapter.cache.update_tmdb_to_tvdb_map.assert_not_called()

    def test_tmdb_to_tvdb_rejects_non_decimal_unicode_digit(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (None, None)
        adapter.tmdb.convert_from.return_value = "²"

        assert adapter.tmdb_to_tvdb(12345, fail=False) is None
        adapter.cache.update_tmdb_to_tvdb_map.assert_not_called()

    def test_tmdb_to_tvdb_rechecks_malformed_cached_id(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = ("tt3348258", False)
        adapter.tmdb.convert_from.return_value = 368207

        assert adapter.tmdb_to_tvdb(12345, fail=False) == 368207
        adapter.tmdb.convert_from.assert_called_once_with(12345, "tvdb_id", False)
        adapter.cache.update_tmdb_to_tvdb_map.assert_called_once_with(False, 12345, 368207)

    def test_tmdb_to_tvdb_malformed_id_uses_existing_conversion_warning(self, adapter):
        from modules.util import MappingConvertError

        adapter.cache.query_tmdb_to_tvdb_map.return_value = (None, None)
        adapter.tmdb.convert_from.return_value = "tt3348258"

        with pytest.raises(MappingConvertError, match="No TVDb ID found for TMDb ID '12345'"):
            adapter.tmdb_to_tvdb(12345, fail=True)

    def test_tvdb_to_tmdb_cache_hit(self, adapter):
        adapter.cache.query_tmdb_to_tvdb_map.return_value = (550, False)
        assert adapter.tvdb_to_tmdb(368207, fail=False) == 550

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
