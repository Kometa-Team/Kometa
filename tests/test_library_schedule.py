from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import modules.builder  # noqa: F401 - pre-import breaks the plex/meta circular import
from modules import util
from modules.library import Library
from modules.util import NotScheduled


def test_schedule_not_inverts_one_rule():
    monday = datetime(2026, 6, 15, 12, 0)
    with pytest.raises(NotScheduled):
        util.schedule_check("test", "weekly.not(monday)", monday, 12)

    assert util.schedule_check("test", "weekly.not(monday)", datetime(2026, 6, 16, 12, 0), 12) == ""


def test_schedule_modes_select_expected_items(monkeypatch):
    now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
    library = SimpleNamespace(scheduled_cached_keys={2}, is_show=False)
    items = [
        SimpleNamespace(ratingKey=1, title="Alpha", addedAt=now - timedelta(days=2)),
        SimpleNamespace(ratingKey=2, title="Beta", addedAt=now - timedelta(days=10)),
        SimpleNamespace(ratingKey=3, title="#Number", addedAt=now - timedelta(days=1)),
    ]

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now if tz else now.replace(tzinfo=None)

    monkeypatch.setattr("modules.library.datetime", FrozenDateTime)

    library.schedule_mode = "added(7)"
    assert Library._schedule_item_keys(library, items) == {1, 3}
    library.schedule_mode = "diff"
    assert Library._schedule_item_keys(library, items) == {1, 3}
    library.schedule_mode = "index(a-b#)"
    assert Library._schedule_item_keys(library, items) == {1, 2, 3}


def test_tv_diff_selects_shows_with_changed_seasons(monkeypatch):
    monkeypatch.setattr("modules.library.logger", SimpleNamespace(ghost=lambda *_: None))
    seasons = {
        1: [SimpleNamespace(ratingKey=11, updatedAt=100), SimpleNamespace(ratingKey=12, updatedAt=200)],
        2: [SimpleNamespace(ratingKey=21, updatedAt=300)],
    }
    library = SimpleNamespace(
        schedule_mode="diff",
        is_show=True,
        config=SimpleNamespace(Cache=SimpleNamespace(query_xml_updated_at=lambda _: {("1", "11"): "100", ("1", "12"): "150", ("2", "21"): "300"})),
        xml_library_id=7,
        xml_updates=[],
        cached_item_subitems=lambda show, _: seasons[show.ratingKey],
    )

    assert Library._schedule_item_keys(library, [SimpleNamespace(ratingKey=1, title="Changed"), SimpleNamespace(ratingKey=2, title="Unchanged")]) == {1}
    assert library.xml_updates == [("1", "11", "100"), ("1", "12", "200"), ("2", "21", "300")]
