"""Tests for modules/ergast.py — Formula 1 data via the Ergast API."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from tests.conftest import FakeLogger, FakeResponse


class TestRace:
    def test_parses_basic_data(self):
        from modules.ergast import Race

        r = Race(
            {"season": "2025", "round": "1", "raceName": "Bahrain Grand Prix", "date": "2025-03-01"},
            None,
            False,
            False,
        )
        assert r.season == 2025
        assert r.round == 1
        assert r.name == "Bahrain Grand Prix"

    def test_shorten_gp_in_title(self):
        from modules.ergast import Race

        r = Race(
            {"season": "2025", "round": "1", "raceName": "Bahrain Grand Prix", "date": "2025-03-01"},
            None,
            False,
            True,
        )
        assert r.title == "Bahrain GP"


class TestErgast:
    @pytest.fixture
    def adapter(self):
        from modules.ergast import Ergast

        e = Ergast.__new__(Ergast)
        e.requests = MagicMock()
        e.cache = MagicMock()
        e.cache.query_ergast.return_value = (None, None)
        return e

    def test_get_races_returns_list(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.ergast.logger", FakeLogger())
        monkeypatch.setattr("modules.ergast.Race", MagicMock)
        adapter.requests.get.return_value = FakeResponse({"MRData": {"RaceTable": {"Races": [{"season": "2025"}]}}}, 200)
        assert len(adapter.get_races(2025, "en", False, False)) > 0
