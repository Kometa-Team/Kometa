"""Tests for modules/overlays.py — the Overlays application engine.

Focuses on the simpler public methods: get_overlay_items and remove_overlay.
The compile_overlays and run_overlays methods are deeply coupled to
CollectionBuilder and are tested through integration tests.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed
from tests.conftest import FakeLogger


def make_overlays(**attrs):
    """Create a minimal Overlays instance via __new__."""
    from modules.overlays import Overlays

    o = Overlays.__new__(Overlays)
    defaults = {
        "config": MagicMock(),
        "cache": MagicMock(),
        "library": MagicMock(),
        "overlays": [],
    }
    defaults.update(attrs)
    for k, v in defaults.items():
        setattr(o, k, v)
    return o


class TestInit:
    def test_sets_attributes(self):
        config = MagicMock()
        cache = MagicMock()
        config.Cache = cache
        lib = MagicMock()
        from modules.overlays import Overlays

        o = Overlays(config, lib)
        assert o.config is config
        assert o.cache is cache
        assert o.library is lib
        assert o.overlays == []


class TestGetOverlayItems:
    def test_searches_library_with_label(self):
        o = make_overlays()
        o.library.search.return_value = ["item1", "item2"]
        result = o.get_overlay_items(label="MyLabel")
        o.library.search.assert_called_once_with(label="MyLabel", libtype=None)
        assert result == ["item1", "item2"]

    def test_filters_ignored_items(self):
        o = make_overlays()
        item_a = MagicMock()
        item_a.ratingKey = "101"
        item_b = MagicMock()
        item_b.ratingKey = "102"
        o.library.search.return_value = [item_a, item_b]
        result = o.get_overlay_items(label="Overlay", ignore=["101"])
        assert result == [item_b]

    def test_empty_library_returns_empty(self):
        o = make_overlays()
        o.library.search.return_value = []
        result = o.get_overlay_items()
        assert result == []


class TestRemoveOverlay:
    @pytest.fixture
    def overlay(self):
        o = make_overlays()
        o.library.find_item_assets.return_value = (None, None, None, None, None, None)
        o.library.item_posters.return_value = "/path/to/poster.jpg"
        return o

    def test_removes_label_via_edit_tags(self, overlay, monkeypatch):
        monkeypatch.setattr("modules.overlays.logger", FakeLogger())
        item = MagicMock()
        overlay.remove_overlay(item, "Test Item", "Overlay", ["/tmp/poster.png"])
        overlay.library.edit_tags.assert_called_once_with("label", item, remove_tags=["Overlay"], do_print=False)

    def test_handles_missing_assets_gracefully(self, overlay, monkeypatch):
        monkeypatch.setattr("modules.overlays.logger", FakeLogger())
        overlay.library.find_item_assets.side_effect = Failed("not found")
        overlay.library.item_posters.side_effect = Failed("not found")
        item = MagicMock()
        overlay.remove_overlay(item, "Test", "Overlay", ["/nonexistent"])
        overlay.library.edit_tags.assert_not_called()
