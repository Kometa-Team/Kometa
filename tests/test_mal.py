"""Tests for modules/mal.py — MyAnimeList client."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from tests.conftest import FakeLogger


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

    def test_genres_populates_on_first_access(self, adapter):
        adapter._jikan_request = MagicMock(
            return_value={"data": [{"mal_id": 1, "name": "Action"}]}
        )
        genres = adapter.genres
        assert "Action" in genres
        assert genres["Action"] == 1
