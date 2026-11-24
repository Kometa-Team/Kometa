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

    @pytest.mark.parametrize("identifier, expected", [("tmdb_1049471", ("themoviedb", "1049471")), ("imdb_tt23724682", ("imdb", "tt23724682"))])
    def test_scan_nfo_movie_guid(self, adapter, identifier, expected):
        assert adapter.scan_guid(f"tv.plex.agents.nfo.movie://movie/{identifier}") == expected

    @pytest.mark.parametrize("identifier", ["tmdb_bad", "tmdb_0", "tmdb_-1", "tmdb_123/extra", "imdb_bad", "local_123", ""])
    def test_scan_nfo_movie_does_not_accept_malformed_or_local_ids(self, adapter, identifier):
        assert adapter.scan_guid(f"tv.plex.agents.nfo.movie://movie/{identifier}") == ("movie", "movie")

    def test_nfo_movie_tmdb_guid_maps_and_caches_movie(self, adapter, monkeypatch):
        from types import SimpleNamespace

        import modules.convert as convert_module

        monkeypatch.setattr(convert_module, "logger", MagicMock())
        adapter.cache.query_guid_map.return_value = (None, None, None, None)
        adapter.tmdb_to_imdb = MagicMock(return_value="tt23724682")
        item = SimpleNamespace(guid="tv.plex.agents.nfo.movie://movie/tmdb_1049471", ratingKey=123, title="Outcome")
        library = SimpleNamespace(is_movie=True, is_show=False, is_other=False)

        assert adapter.get_id(item, library) == ("movie", [1049471], ["tt23724682"])
        adapter.cache.update_guid_map.assert_called_once_with(item.guid, "1049471", "tt23724682", None, "movie")

    @pytest.mark.parametrize(
        "identifier, expected",
        [("tvdb_113561", ("thetvdb", "113561")), ("tmdb_1437", ("themoviedb", "1437")), ("imdb_tt0579539", ("imdb", "tt0579539"))],
    )
    def test_scan_nfo_series_guid(self, adapter, identifier, expected):
        assert adapter.scan_guid(f"tv.plex.agents.nfo.series://show/{identifier}") == expected

    @pytest.mark.parametrize("identifier", ["tvdb_0", "tvdb_bad", "tvdb_-1", "tvdb_123/extra", "tmdb_0", "imdb_bad", "local_123", ""])
    def test_scan_nfo_series_does_not_accept_malformed_or_local_ids(self, adapter, identifier):
        assert adapter.scan_guid(f"tv.plex.agents.nfo.series://show/{identifier}") == ("series", "show")

    @pytest.mark.parametrize(
        "guid, expected",
        [
            ("tv.plex.agents.nfo.series://season/tvdb_78874_1", ("series", "season")),
            ("tv.plex.agents.nfo.series://episode/imdb_tt0579539", ("series", "episode")),
        ],
    )
    def test_scan_nfo_series_does_not_treat_seasons_or_episodes_as_shows(self, adapter, guid, expected):
        assert adapter.scan_guid(guid) == expected

    @staticmethod
    def _nfo_show(identifier):
        from types import SimpleNamespace

        item = SimpleNamespace(guid=f"tv.plex.agents.nfo.series://show/{identifier}", ratingKey=123, title="Animaniacs")
        library = SimpleNamespace(is_movie=False, is_show=True, is_other=False)
        return item, library

    def test_nfo_series_tvdb_guid_maps_and_caches_show(self, adapter, monkeypatch):
        import modules.convert as convert_module

        monkeypatch.setattr(convert_module, "logger", MagicMock())
        adapter.cache.query_guid_map.return_value = (None, None, None, None)
        adapter.tvdb_to_imdb = MagicMock(return_value="tt0579539")
        item, library = self._nfo_show("tvdb_113561")

        assert adapter.get_id(item, library) == ("show", [113561], ["tt0579539"])
        adapter.tvdb_to_imdb.assert_called_once_with(113561)
        adapter.cache.update_guid_map.assert_called_once_with(item.guid, "113561", "tt0579539", None, "show")

    def test_nfo_series_tmdb_guid_maps_and_caches_show(self, adapter, monkeypatch):
        import modules.convert as convert_module

        monkeypatch.setattr(convert_module, "logger", MagicMock())
        adapter.cache.query_guid_map.return_value = (None, None, None, None)
        adapter.tmdb_to_tvdb = MagicMock(return_value=113561)
        adapter.tvdb_to_imdb = MagicMock(return_value="tt0579539")
        item, library = self._nfo_show("tmdb_1437")

        assert adapter.get_id(item, library) == ("show", [113561], ["tt0579539"])
        adapter.tmdb_to_tvdb.assert_called_once_with(1437)
        adapter.cache.update_guid_map.assert_called_once_with(item.guid, "113561", "tt0579539", None, "show")

    def test_nfo_series_imdb_guid_without_tvdb_maps_and_caches_imdb_only_show(self, adapter, monkeypatch):
        import modules.convert as convert_module

        monkeypatch.setattr(convert_module, "logger", MagicMock())
        adapter.cache.query_guid_map.return_value = (None, None, None, None)
        adapter.imdb_to_tmdb = MagicMock(return_value=(1437, "show"))
        adapter.tmdb_to_tvdb = MagicMock(return_value=None)
        item, library = self._nfo_show("imdb_tt0579539")

        assert adapter.get_id(item, library) == ("show", [], ["tt0579539"])
        adapter.imdb_to_tmdb.assert_called_once_with("tt0579539")
        adapter.tmdb_to_tvdb.assert_called_once_with(1437)
        adapter.cache.update_guid_map.assert_called_once_with(item.guid, "", "tt0579539", None, "show")

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
