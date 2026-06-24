"""Tests for Radarr using __new__ + mock api attribute."""

from __future__ import annotations

from unittest.mock import MagicMock

import modules.builder  # noqa: F401
from tests.conftest import FakeLogger


def _make_adapter(monkeypatch) -> tuple:
    """Return (Radarr_instance, mock_api) with all constructor attributes set."""
    monkeypatch.setattr("modules.radarr.logger", FakeLogger())
    from modules.radarr import Radarr

    r = Radarr.__new__(Radarr)
    mock_api = MagicMock()
    mock_api.quality_profile.return_value = []
    mock_api.respect_list_exclusions_when_adding = MagicMock()
    mock_api._validate_add_options = MagicMock()
    mock_api.all_movies.return_value = []
    mock_api.all_tags.return_value = []
    r.api = mock_api
    r.requests = MagicMock()
    r.cache = MagicMock()
    r.url = "http://radarr:7878"
    r.token = "fake"
    r.profiles = []
    r.add_missing = False
    r.add_existing = False
    r.upgrade_existing = False
    r.monitor_existing = False
    r.root_folder_path = "/movies"
    r.monitor = "movieOnly"
    r.availability = "announced"
    r.quality_profile = 1
    r.tag = []
    r.search = False
    r.radarr_path = ""
    r.plex_path = ""
    r.ignore_cache = False
    return r, mock_api


class TestRadarrGetTmdbIds:
    def test_all_returns_all_movies(self, monkeypatch):
        r, api = _make_adapter(monkeypatch)
        m = MagicMock()
        m.tmdbId = 550
        api.all_movies.return_value = [m]
        assert r.get_tmdb_ids("radarr_all", None) == [(550, "tmdb")]

    def test_taglist_filters_by_tag(self, monkeypatch):
        r, api = _make_adapter(monkeypatch)
        tag = MagicMock()
        tag.id = 1
        tag.label = "action"
        api.all_tags.return_value = [tag]
        movie = MagicMock()
        movie.tmdbId = 550
        movie_tag = MagicMock()
        movie_tag.id = 1
        movie.tags = [movie_tag]
        api.all_movies.return_value = [movie]
        assert r.get_tmdb_ids("radarr_taglist", ["action"]) == [(550, "tmdb")]

    def test_empty_when_no_movies(self, monkeypatch):
        r, api = _make_adapter(monkeypatch)
        api.all_movies.return_value = []
        assert r.get_tmdb_ids("radarr_all", None) == []


class TestRadarrEditTags:
    def test_add_tags_does_not_raise(self, monkeypatch):
        r, api = _make_adapter(monkeypatch)
        api.edit_multiple_movies.return_value = ([], [])
        r.edit_tags([550], ["action"], "")
