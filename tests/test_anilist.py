"""Tests for modules/anilist.py — AniList GraphQL client."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed
from tests.conftest import FakeLogger


class TestAniList:
    @pytest.fixture
    def adapter(self, monkeypatch):
        monkeypatch.setattr("modules.anilist.logger", FakeLogger())
        from modules.anilist import AniList

        a = AniList.__new__(AniList)
        a.requests = MagicMock()
        a._request = MagicMock()
        return a

    def test_validate_id_uses_romaji_when_no_english(self, adapter):
        adapter._request.return_value = {"data": {"Media": {"id": 1, "title": {"romaji": "Naruto", "english": None}}}}
        result = adapter._validate_id(1)
        assert result == (1, "Naruto")

    def test_validate_id_prefers_english_title(self, adapter):
        adapter._request.return_value = {"data": {"Media": {"id": 2, "title": {"romaji": "Naru", "english": "Naruto EN"}}}}
        result = adapter._validate_id(2)
        assert result == (2, "Naruto EN")


class TestAniListValidate:
    def test_validate_anilist_ids_all_missing_raises(self, monkeypatch):
        monkeypatch.setattr("modules.anilist.logger", FakeLogger())
        from modules.anilist import AniList

        a = AniList.__new__(AniList)
        a.requests = MagicMock()
        a._request = MagicMock(side_effect=Failed("not found"))
        with pytest.raises(Failed, match="No valid"):
            a.validate_anilist_ids("1, 2", studio=False)
