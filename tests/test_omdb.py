"""Tests for modules/omdb.py — OMDb API integration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from tests.conftest import FakeLogger, FakeResponse


class TestOMDb:
    @pytest.fixture
    def adapter(self):
        from modules.omdb import OMDb

        o = OMDb.__new__(OMDb)
        o.requests = MagicMock()
        o.cache = MagicMock()
        o.cache.query_omdb.return_value = ({}, None)
        o.apikey = "k"
        o.expiration = 30
        o.limit = False
        return o

    def test_get_omdb_parses_response(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.omdb.logger", FakeLogger())
        adapter.requests.get.return_value = FakeResponse({"Title": "T", "Year": "2023", "imdbID": "tt1", "Response": "True"}, 200)
        r = adapter.get_omdb("tt1", ignore_cache=True)
        assert r.title == "T"
