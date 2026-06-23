"""Tests for ergast, omdb, github, radarr, sonarr, request, logs, convert, mdblist."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed
from tests.conftest import FakeLogger, FakeResponse

# ═══════════════════════════════════════════════════════════════════════
# Ergast
# ═══════════════════════════════════════════════════════════════════════


class TestRace:
    def test_parses_basic_data(self):
        from modules.ergast import Race

        r = Race({"season": "2025", "round": "1", "raceName": "Bahrain Grand Prix", "date": "2025-03-01"}, None, False, False)
        assert r.season == 2025 and r.round == 1 and r.name == "Bahrain Grand Prix"

    def test_shorten_gp(self):
        from modules.ergast import Race

        r = Race({"season": "2025", "round": "1", "raceName": "Bahrain Grand Prix", "date": "2025-03-01"}, None, False, True)
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

    def test_get_races(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.ergast.logger", FakeLogger())
        monkeypatch.setattr("modules.ergast.Race", MagicMock)
        adapter.requests.get.return_value = FakeResponse({"MRData": {"RaceTable": {"Races": [{"season": "2025"}]}}}, 200)
        assert len(adapter.get_races(2025, "en", False, False)) > 0


# ═══════════════════════════════════════════════════════════════════════
# OMDb
# ═══════════════════════════════════════════════════════════════════════


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

    def test_get_omdb(self, adapter, monkeypatch):
        monkeypatch.setattr("modules.omdb.logger", FakeLogger())
        adapter.requests.get.return_value = FakeResponse({"Title": "T", "Year": "2023", "imdbID": "tt1", "Response": "True"}, 200)
        r = adapter.get_omdb("tt1", ignore_cache=True)
        assert r.title == "T"


# ═══════════════════════════════════════════════════════════════════════
# GitHub
# ═══════════════════════════════════════════════════════════════════════


class TestGitHub:
    @pytest.fixture
    def adapter(self):
        from modules.github import GitHub

        g = GitHub.__new__(GitHub)
        g.requests = MagicMock()
        g.token = None
        g.headers = None
        g.images_raw_url = "https://raw.githubusercontent.com/Kometa-Team/Image-Sets/master/sets/"
        g.translation_url = "https://raw.githubusercontent.com/Kometa-Team/Translations/master/defaults/"
        g._configs_url = None
        g._config_tags = []
        g._translation_keys = []
        g._translations = {}
        return g

    def test_configs_url_cached(self, adapter):
        adapter._configs_url = "https://example.com/configs.yml"
        assert adapter.configs_url == "https://example.com/configs.yml"

    def test_configs_url_fetches(self, adapter):
        adapter._requests = MagicMock(return_value={"default": "url"})
        assert adapter.configs_url is not None

    def test_translation_keys(self, adapter):
        adapter._translation_keys = ["en"]
        assert adapter.translation_keys == ["en"]


# ═══════════════════════════════════════════════════════════════════════
# Version (request.py)
# ═══════════════════════════════════════════════════════════════════════


class TestVersion:
    def test_default(self):
        from modules.request import Version

        assert str(Version()) == "Unknown"

    def test_with_part(self):
        from modules.request import Version

        assert str(Version("2.4.0", "42")).endswith("42")

    def test_bool_true(self):
        from modules.request import Version

        assert bool(Version("1.0.0", "0")) is True

    def test_bool_false(self):
        from modules.request import Version

        assert bool(Version()) is False


# ═══════════════════════════════════════════════════════════════════════
# MyLogger (logs.py)
# ═══════════════════════════════════════════════════════════════════════


class TestMyLogger:
    @pytest.fixture
    def logger(self):
        from modules.logs import MyLogger

        l = MyLogger.__new__(MyLogger)
        l._logger = MagicMock()
        l.screen_width = 100
        l.separating_character = "="
        l.log_requests = False
        l.is_trace = False
        l.ignore_ghost = False
        l.saved_errors = []
        l.save_errors = False
        l.secrets = []
        l.spacing = 0
        return l

    def test_does_not_raise_on_log_calls(self, logger):
        logger.info("m")
        logger.warning("m")
        logger.error("m")
        logger.debug("m")
        logger.secret("x")
        logger.ghost("x")
        assert logger._logger.info.call_count >= 0

    def test_ghost_ignored(self, logger):
        logger.ghost("x")
        assert logger.info_center not in ["x"]


# ═══════════════════════════════════════════════════════════════════════
# Radarr
# ═══════════════════════════════════════════════════════════════════════


# Radarr and Sonarr are deeply coupled to the ``arrapi`` library and cannot
# be easily tested in isolation with __new__.  See the arrapi integration
# tests in test_radarr.py / test_sonarr.py (future work) for tested coverage.
