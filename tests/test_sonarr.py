"""Tests for Sonarr using __new__ + mock api attribute."""

from unittest.mock import MagicMock


class TestSonarrGetTvdbIds:
    def _make(self):
        import modules.sonarr

        modules.sonarr.logger = MagicMock()
        s = modules.sonarr.Sonarr.__new__(modules.sonarr.Sonarr)
        mock_api = MagicMock()
        mock_api.quality_profile.return_value = []
        mock_api.all_tags.return_value = []
        s.api = mock_api
        s.url = "http://sonarr:8989"
        s.token = "fake"
        s.requests = MagicMock()
        s.cache = MagicMock()
        s.root_folder_path = "/tv"
        s.quality_profile = 1
        s.monitor = "all"
        s.search = False
        s.cutoff_search = False
        s.series_type = "standard"
        s.season_folder = True
        return s, mock_api

    def test_empty_when_no_series(self):
        s, api = self._make()
        api.all_series = MagicMock(return_value=[])
        assert s.get_tvdb_ids("sonarr_add_all", None) == []
