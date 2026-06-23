"""Tests for Trakt, AniDB, AniList, MAL — API integration modules."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed
from tests.conftest import FakeLogger

# ═══════════════════════════════════════════════════════════════════════
# Trakt
# ═══════════════════════════════════════════════════════════════════════


class TestTrakt:
    @pytest.fixture
    def adapter(self):
        from modules.trakt import Trakt

        t = Trakt.__new__(Trakt)
        t._request = MagicMock()
        t._slugs = None
        t._movie_genres = None
        t._show_genres = None
        t._movie_languages = None
        t._show_languages = None
        t._movie_countries = None
        t._show_countries = None
        t._movie_certifications = None
        t._show_certifications = None
        return t

    def test_movie_genres(self, adapter):
        adapter._request.return_value = [{"slug": "action"}, {"slug": "comedy"}]
        assert adapter.movie_genres == ["action", "comedy"]

    def test_movie_genres_caches(self, adapter):
        adapter._request.return_value = [{"slug": "action"}]
        _ = adapter.movie_genres
        adapter._request.reset_mock()
        assert adapter.movie_genres == ["action"]
        adapter._request.assert_not_called()

    def test_show_genres(self, adapter):
        adapter._request.return_value = [{"slug": "drama"}]
        assert adapter.show_genres == ["drama"]

    def test_slugs_is_property(self, adapter):
        """slugs is a @property — accessed without ()."""
        adapter._request.return_value = [{"ids": {"slug": "my-list"}}]
        assert adapter.slugs == ["my-list"]


# ═══════════════════════════════════════════════════════════════════════
# AniDB
# ═══════════════════════════════════════════════════════════════════════


class TestAniDB:
    @pytest.fixture
    def adapter(self):
        from modules.anidb import AniDB

        a = AniDB.__new__(AniDB)
        a._is_authorized = False
        return a

    def test_is_authorized_false_initially(self, adapter):
        assert adapter.is_authorized is False


# ═══════════════════════════════════════════════════════════════════════
# AniList
# ═══════════════════════════════════════════════════════════════════════


class TestAniList:
    @pytest.fixture
    def adapter(self, monkeypatch):
        monkeypatch.setattr("modules.anilist.logger", FakeLogger())
        from modules.anilist import AniList

        a = AniList.__new__(AniList)
        a.requests = MagicMock()
        a._request = MagicMock()
        return a

    def test_validate_id(self, adapter):
        adapter._request.return_value = {"data": {"Media": {"id": 1, "title": {"romaji": "Naruto", "english": None}}}}
        result = adapter._validate_id(1)
        assert result == (1, "Naruto")

    def test_validate_id_uses_english(self, adapter):
        adapter._request.return_value = {"data": {"Media": {"id": 2, "title": {"romaji": "Naru", "english": "Naruto EN"}}}}
        result = adapter._validate_id(2)
        assert result == (2, "Naruto EN")


class TestAniListValidate:
    def test_validate_anilist_ids_all_missing(self, monkeypatch):
        monkeypatch.setattr("modules.anilist.logger", FakeLogger())
        from modules.anilist import AniList

        a = AniList.__new__(AniList)
        a.requests = MagicMock()
        a._request = MagicMock(side_effect=Failed("not found"))
        with pytest.raises(Failed, match="No valid"):
            a.validate_anilist_ids("1, 2", studio=False)


# ═══════════════════════════════════════════════════════════════════════
# MyAnimeList
# ═══════════════════════════════════════════════════════════════════════


class TestMyAnimeList:
    @pytest.fixture
    def adapter(self, monkeypatch):
        monkeypatch.setattr("modules.mal.logger", FakeLogger())
        from modules.mal import MyAnimeList

        m = MyAnimeList.__new__(MyAnimeList)
        m.requests = MagicMock()
        m.cache = MagicMock()
        m.client_id = "fake"
        m.client_secret = "fake"
        m._genres = {}
        m._studios = {}
        return m

    def test_genres_populates(self, adapter):
        adapter._jikan_request = MagicMock(return_value={"data": [{"mal_id": 1, "name": "Action"}]})
        genres = adapter.genres
        assert "Action" in genres
        assert genres["Action"] == 1
