"""Tests for modules/github.py — GitHub raw-file fetcher and configs index."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401


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

    def test_configs_url_returns_cached_value(self, adapter):
        adapter._configs_url = "https://example.com/configs.yml"
        assert adapter.configs_url == "https://example.com/configs.yml"

    def test_configs_url_fetches_when_unset(self, adapter):
        adapter._requests = MagicMock(return_value={"default": "url"})
        assert adapter.configs_url is not None

    def test_translation_keys_returns_cached_list(self, adapter):
        adapter._translation_keys = ["en"]
        assert adapter.translation_keys == ["en"]
