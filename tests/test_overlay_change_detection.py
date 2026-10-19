"""Overlay render decisions and saved state use the production implementation."""

import pytest

import modules.builder  # noqa: F401
from modules import cache as cache_module
from modules.cache import Cache
from modules.overlays import overlay_change_reason, write_overlay_state
from tests.conftest import FakeLogger


@pytest.mark.parametrize(
    "cached, current, updated, has_label, expected",
    [
        ({"4K": ("a", None)}, {"4K": "a"}, (), True, ""),
        ({}, {"4K": "a"}, (), True, "New Overlay: 4K"),
        ({"4K": ("a", None)}, {}, (), True, "Overlay Removed: 4K"),
        ({"4K": ("a", None)}, {"4K": "b"}, (), True, "Overlay Changed: 4K"),
        ({"4K": ("a", None)}, {"4K": "a"}, ("4K",), True, "Overlay Image Updated: 4K"),
        ({"4K": ("a", None)}, {"4K": "a"}, (), False, "No Overlay Label"),
        ({"old": ("a", None)}, {"new": "b"}, (), True, "Overlay Removed: old"),
        ({}, {"first": "a", "last": "b"}, (), True, "New Overlay: last"),
    ],
)
def test_overlay_render_reason(cached, current, updated, has_label, expected):
    assert overlay_change_reason(cached, current, updated, has_label) == expected


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_module, "logger", FakeLogger())
    return Cache(str(tmp_path / "test.yml"), 60)


def test_unresolved_overlay_retries_until_resolved(cache):
    table = f"{cache.get_image_table_name('TestLib')}_overlay_state"
    hashes = {"rating": "a", "HDR": "b"}
    # A previously successful overlay must also be removed if it fails this run.
    write_overlay_state(cache, 5173, table, hashes, {"rating": "7.3"}, set())
    write_overlay_state(cache, 5173, table, hashes, {"rating": "7.5"}, {"HDR"})
    saved = cache.query_overlay_state(5173, table)
    assert saved == {"rating": ("a", "7.5")}
    assert overlay_change_reason(saved, hashes) == "New Overlay: HDR"

    write_overlay_state(cache, 5173, table, hashes, {"rating": "7.5"}, set())
    saved = cache.query_overlay_state(5173, table)
    assert saved == {"rating": ("a", "7.5"), "HDR": ("b", None)}
    assert overlay_change_reason(saved, hashes) == ""


def test_overlay_state_replacement_removes_old_entries_and_isolates_items(cache):
    table = f"{cache.get_image_table_name('TestLib')}_overlay_state"
    write_overlay_state(cache, 1, table, {"old": "a"}, {}, set())
    write_overlay_state(cache, 2, table, {"other": "b"}, {}, set())
    write_overlay_state(cache, 1, table, {}, {}, set())
    assert cache.query_overlay_state(1, table) == {}
    assert cache.query_overlay_state(2, table) == {"other": ("b", None)}
