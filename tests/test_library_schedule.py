from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import modules.builder  # noqa: F401 - pre-import breaks the plex/meta circular import
from modules import util
from modules.library import Library
from modules.util import NotScheduled


def test_schedule_not_inverts_each_rule_independently():
    monday = datetime(2026, 6, 15, 12, 0)
    with pytest.raises(NotScheduled):
        util.schedule_check("test", "weekly.not(monday)", monday, 12)

    assert util.schedule_check("test", "weekly.not(monday)", datetime(2026, 6, 16, 12, 0), 12) == ""

    # Rules remain ORed after an individual modifier is evaluated.
    assert util.schedule_check("test", ["weekly.not(monday)", "weekly(monday)"], monday, 12)


def test_schedule_unknown_modifier_is_not_treated_as_a_normal_schedule():
    with pytest.raises(NotScheduled):
        util.schedule_check("test", "weekly.future(monday)", datetime(2026, 6, 15, 12, 0), 12)


def test_library_schedule_modes_select_the_expected_items(monkeypatch):
    now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
    library = SimpleNamespace(config=SimpleNamespace(run_hour=12), scheduled_cached_keys={2})
    items = [
        SimpleNamespace(ratingKey=1, addedAt=now - timedelta(days=2)),
        SimpleNamespace(ratingKey=2, addedAt=now - timedelta(days=10)),
        SimpleNamespace(ratingKey=3, addedAt=now - timedelta(days=1)),
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

    library.schedule_mode = "full"
    assert Library._schedule_item_keys(library, items) == {1, 2, 3}
