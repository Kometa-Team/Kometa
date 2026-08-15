"""Tests for modules/overlays.py — the Overlays application engine.

Focuses on the simpler public methods: get_overlay_items and remove_overlay.
The compile_overlays and run_overlays methods are deeply coupled to
CollectionBuilder and are tested through integration tests.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.mdblist import MDBList
from modules.plex import Plex
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


class TestScanOverlayBackupExtensions:
    """Covers the listdir-snapshot helper that replaced up to 3 os.path.exists() calls per item
    in run_overlays' per-item loop - see the perf-profiling project's steady-state findings."""

    def test_empty_directory_returns_empty_dict(self, tmp_path):
        o = make_overlays()
        o.library.overlay_backup = str(tmp_path)
        assert o._scan_overlay_backup_extensions() == {}

    def test_single_backup_file_found(self, tmp_path):
        o = make_overlays()
        o.library.overlay_backup = str(tmp_path)
        (tmp_path / "12345.png").write_bytes(b"fake")
        result = o._scan_overlay_backup_extensions()
        assert result == {"12345": {".png"}}

    def test_multiple_ratingkeys_each_tracked_separately(self, tmp_path):
        o = make_overlays()
        o.library.overlay_backup = str(tmp_path)
        (tmp_path / "111.png").write_bytes(b"fake")
        (tmp_path / "222.jpg").write_bytes(b"fake")
        (tmp_path / "333.webp").write_bytes(b"fake")
        result = o._scan_overlay_backup_extensions()
        assert result == {"111": {".png"}, "222": {".jpg"}, "333": {".webp"}}

    def test_same_ratingkey_multiple_formats_all_tracked(self, tmp_path):
        # Shouldn't normally happen, but the original per-format exists() code removed all matches, not just the highest-precedence one - the replacement must too.
        o = make_overlays()
        o.library.overlay_backup = str(tmp_path)
        (tmp_path / "999.png").write_bytes(b"fake")
        (tmp_path / "999.jpg").write_bytes(b"fake")
        result = o._scan_overlay_backup_extensions()
        assert result == {"999": {".png", ".jpg"}}

    def test_non_backup_files_ignored(self, tmp_path):
        o = make_overlays()
        o.library.overlay_backup = str(tmp_path)
        (tmp_path / "12345.png").write_bytes(b"fake")
        (tmp_path / "readme.txt").write_bytes(b"fake")
        (tmp_path / "12345.tmp").write_bytes(b"fake")
        result = o._scan_overlay_backup_extensions()
        assert result == {"12345": {".png"}}

    def test_extension_matching_is_exact_case(self, tmp_path):
        # os.path.exists() on a case-sensitive filesystem never matched "12345.PNG" against ".png" - the replacement must not become case-insensitive and start matching it.
        o = make_overlays()
        o.library.overlay_backup = str(tmp_path)
        (tmp_path / "12345.PNG").write_bytes(b"fake")
        result = o._scan_overlay_backup_extensions()
        assert result == {}


class TestMDBListPrefetch:
    def test_prefetches_only_items_with_mdblist_text(self):
        o = make_overlays(cache=None)
        mdb_item = SimpleNamespace(ratingKey=1)
        tmdb_item = SimpleNamespace(ratingKey=2)
        key_to_overlays = {
            1: (mdb_item, ["mdb"]),
            2: (tmdb_item, ["tmdb"]),
        }
        properties = {
            "mdb": SimpleNamespace(name="text(<<mdb_tomatoes_rating>>)"),
            "tmdb": SimpleNamespace(name="text(<<tmdb_rating>>)"),
        }

        o._prefetch_mdblist(key_to_overlays, properties)

        o.library.prefetch_mdblist.assert_called_once_with([mdb_item])

    def test_skips_items_when_all_mdblist_values_are_fresh(self):
        cache = MagicMock()
        cache.query_overlay_value_cache.return_value = ("7.5", False)
        o = make_overlays(cache=cache)
        item = SimpleNamespace(ratingKey=1)

        o._prefetch_mdblist(
            {1: (item, ["mdb"])},
            {"mdb": SimpleNamespace(name="text(<<mdb_imdb_rating>>)")},
        )

        o.library.prefetch_mdblist.assert_not_called()

    def test_prefetches_item_when_any_mdblist_value_is_missing(self):
        cache = MagicMock()
        cache.query_overlay_value_cache.side_effect = [("7.5", False), (None, None)]
        o = make_overlays(cache=cache)
        item = SimpleNamespace(ratingKey=1)

        o._prefetch_mdblist(
            {1: (item, ["mdb"])},
            {"mdb": SimpleNamespace(name="text(<<mdb_imdb_rating>> <<mdb_tmdb_rating>>)")},
        )

        o.library.prefetch_mdblist.assert_called_once_with([item])

    def test_one_thousand_overlay_items_use_ten_requests(self):
        items = [SimpleNamespace(ratingKey=i) for i in range(1000)]
        mdblist = MDBList.__new__(MDBList)
        mdblist.cache = None
        mdblist.expiration = 60
        mdblist.limit = False
        mdblist._run_cache = {}

        def batch_response(url, json_data):
            return (
                [
                    {
                        "id": media_id,
                        "title": f"Movie {media_id}",
                        "released": None,
                        "released_digital": None,
                    }
                    for media_id in json_data["ids"]
                ],
                {},
            )

        mdblist._request = MagicMock(side_effect=batch_response)
        library = Plex.__new__(Plex)
        library.config = SimpleNamespace(MDBList=mdblist)
        library.is_movie = True
        library.is_show = False
        library.get_ids = MagicMock(side_effect=lambda item: (item.ratingKey + 1000, None, None))
        o = make_overlays(cache=None, library=library)

        o._prefetch_mdblist(
            {item.ratingKey: (item, ["rating"]) for item in items},
            {"rating": SimpleNamespace(name="text(<<mdb_tomatoes_rating>>)")},
        )

        assert mdblist._request.call_count == 10
        assert [len(call.kwargs["json_data"]["ids"]) for call in mdblist._request.call_args_list] == [100] * 10


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
