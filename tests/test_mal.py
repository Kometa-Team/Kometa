"""Tests for modules/mal.py — MyAnimeList client."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed
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
        m._delay = None
        return m

    def test_genres_populates_on_first_access(self, adapter):
        adapter._jikan_request = MagicMock(return_value={"data": [{"mal_id": 1, "name": "Action"}]})
        genres = adapter.genres
        assert "Action" in genres
        assert genres["Action"] == 1

    @pytest.mark.parametrize("method,args", [("_request", ("https://api.myanimelist.net/v2/anime",)), ("_jikan_request", ("anime/1",))])
    def test_rate_limit_failure_propagates_from_json_request(self, adapter, method, args):
        adapter.authorization = {"access_token": "fake"}
        adapter.requests.get_json.side_effect = Failed("URL Error: Too many requests - https://example.com")

        with pytest.raises(Failed, match="Too many requests"):
            getattr(adapter, method)(*args)
