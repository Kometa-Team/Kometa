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

    @pytest.mark.parametrize(
        ("local", "latest", "branch", "tags", "expected"),
        [
            ("2.4.8", "2.5.0", "nightly", ["2.4.8"], "v2.4.8/"),
            ("2.5.0", "2.5.0", "nightly", ["2.5.0"], "master/"),
            ("2.5.0", "2.5.0", "master", ["2.5.0"], "v2.5.0/"),
            ("2.4.8", "2.5.0", "nightly", ["2.0.0"], "master/"),
        ],
        ids=["tagged_release_behind_latest", "current_on_a_non_master_branch", "current_on_master", "no_tag_for_the_local_version"],
    )
    def test_configs_url_uses_the_versioned_configs_only_when_a_release_tag_exists(self, adapter, local, latest, branch, tags, expected):
        from modules.github import configs_raw_url

        adapter.requests.local.main = local
        adapter.requests.latest.main = latest
        adapter.requests.branch = branch
        adapter._config_tags = tags
        assert adapter.configs_url == f"{configs_raw_url}/{expected}"

    def test_translation_keys_returns_cached_list(self, adapter):
        adapter._translation_keys = ["en"]
        assert adapter.translation_keys == ["en"]
