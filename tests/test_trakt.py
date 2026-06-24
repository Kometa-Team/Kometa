"""Tests for modules/trakt.py — Trakt.tv list/genre fetcher."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401


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
