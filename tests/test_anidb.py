"""Tests for modules/anidb.py — AniDB anime database client."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import modules.builder  # noqa: F401
from tests.conftest import FakeLogger


def make_cached_anidb_data(**overrides):
    data = {
        "main_title": "Test Anime",
        "titles": "{}",
        "studio": None,
        "rating": 8.5,
        "average": 8.0,
        "score": None,
        "released": None,
        "tags": "{}",
        "mal_id": None,
        "imdb_id": None,
        "tmdb_id": None,
        "tmdb_type": None,
    }
    data.update(overrides)
    return data


class TestAniDB:
    @pytest.fixture
    def adapter(self):
        from modules.anidb import AniDB

        a = AniDB.__new__(AniDB)
        a._is_authorized = False
        return a

    def test_is_authorized_false_initially(self, adapter):
        assert adapter.is_authorized is False

    @pytest.mark.parametrize("value", [-0.1, 10.1, "bad", float("nan"), float("inf"), True])
    def test_invalid_rating_is_reported_and_marked_uncacheable(self, value, monkeypatch):
        from modules.anidb import AniDBObj

        logger = FakeLogger()
        monkeypatch.setattr("modules.anidb.logger", logger)

        result = AniDBObj(SimpleNamespace(language="en"), 1, make_cached_anidb_data(rating=value))

        assert not result.ratings_valid
        assert any("response will not be cached" in message for message in logger.warning_messages)

    def test_missing_rating_is_not_invalid(self):
        from modules.anidb import AniDBObj

        result = AniDBObj(SimpleNamespace(language="en"), 1, make_cached_anidb_data(rating=None))

        assert result.ratings_valid
