import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft7Validator

import modules.builder  # noqa: F401 - pre-import breaks the plex/meta circular import
from modules import util
from modules.library import Library
from modules.schedule_mode import parse_added_duration
from modules.util import Failed, NotScheduled


@pytest.mark.parametrize(
    "mode, valid", [("items(tmdb:550|tmdb:603)", True), ("items(tvdb:1399|imdb:tt0944947|plex:42)", True), ("items(tmdb:00550)", True), ("items()", False), ("items(tmdb:0)", False), ("items(imdb:123)", False), ("items(tmdb:550|)", False)]
)
def test_items_schedule_schema(mode, valid):
    schema = json.loads((Path(__file__).resolve().parents[1] / "json-schema" / "config-schema.json").read_text(encoding="utf-8"))
    validator = Draft7Validator({"$ref": "#/definitions/library-section", "definitions": schema["definitions"]})
    config = {"Movies": {"schedule": [{"schedule": "weekly(monday)", "mode": mode}]}}
    assert validator.is_valid(config) is valid


def test_items_schedule_matches_mixed_ids_without_persistent_cache():
    items = [SimpleNamespace(ratingKey=key) for key in range(1, 6)]
    ids = {
        1: ("movie", [550], ["tt0137523"]),
        2: ("movie", [603], ["tt0133093"]),
        3: ("movie", [604], ["tt0234215"]),
        5: (None, None, None),
    }
    library = SimpleNamespace(
        schedule_mode="items(tmdb:00550|imdb:tt0133093|plex:4|tmdb:550|tvdb:604)",
        is_show=False,
        config=SimpleNamespace(Cache=None, Convert=SimpleNamespace(get_id=lambda item, _: ids[item.ratingKey])),
    )
    assert Library._schedule_item_keys(library, items) == {1, 2, 4}


def test_items_schedule_converts_show_tmdb_ids_and_matches_tvdb():
    calls = []
    library = SimpleNamespace(
        schedule_mode="items(tmdb:1396|tvdb:80379)",
        is_show=True,
        config=SimpleNamespace(
            Convert=SimpleNamespace(
                tmdb_to_tvdb=lambda item_id: calls.append(item_id) or 1399,
                get_id=lambda item, _: ("show", [item.tvdb_id], None),
            )
        ),
    )
    items = [SimpleNamespace(ratingKey=1, tvdb_id=1399), SimpleNamespace(ratingKey=2, tvdb_id=80379), SimpleNamespace(ratingKey=3, tvdb_id=999)]
    assert Library._schedule_item_keys(library, items) == {1, 2}
    assert calls == [1396]


def test_items_schedule_missing_plex_id_keeps_scope_empty_without_conversion():
    library = SimpleNamespace(schedule_mode="items(plex:42)", is_show=False)
    assert Library._schedule_item_keys(library, [SimpleNamespace(ratingKey=1)]) == set()
    assert Library.has_schedule_scope.fget(library)


def test_items_schedule_unresolved_show_id_keeps_scope_empty():
    library = SimpleNamespace(
        schedule_mode="items(tmdb:1396)",
        is_show=True,
        config=SimpleNamespace(Convert=SimpleNamespace(tmdb_to_tvdb=lambda _: None, get_id=lambda *_: (None, None, None))),
    )
    assert Library._schedule_item_keys(library, [SimpleNamespace(ratingKey=1)]) == set()


def test_items_schedule_music_matches_only_plex_keys():
    library = SimpleNamespace(schedule_mode="items(tmdb:550|plex:2)", is_show=False, is_music=True)
    assert Library._schedule_item_keys(library, [SimpleNamespace(ratingKey=1), SimpleNamespace(ratingKey=2)]) == {2}


@pytest.mark.parametrize("mode", ["items()", "items(550)", "items(tmdb:)", "items(tmdb:0)", "items(tvdb:-1)", "items(imdb:123)", "items(plex:abc)", "items(foo:1)", "items(tmdb:550|)", "items(tmdb:550)"])
def test_items_schedule_validates_even_for_empty_library(mode):
    library = SimpleNamespace(schedule_mode=mode, is_show=False)
    if mode == "items(tmdb:550)":
        assert Library._schedule_item_keys(library, []) == set()
    else:
        with pytest.raises(Failed, match="Config Error"):
            Library._schedule_item_keys(library, [])


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


@pytest.mark.parametrize("mode,duration", [("added(30m)", timedelta(minutes=30)), ("added(1h)", timedelta(hours=1)), ("added(12d)", timedelta(days=12)), ("added(7)", timedelta(days=7)), ("added(01)", timedelta(days=1)), ("Added(1H)", timedelta(hours=1))])
def test_added_duration_units(mode, duration):
    assert parse_added_duration(mode) == duration


@pytest.mark.parametrize("mode", ["added(0)", "added(-1h)", "added(1.5h)", "added(2w)", "added(1hm)", "added()"])
def test_added_duration_rejects_invalid_values(mode):
    with pytest.raises(ValueError):
        parse_added_duration(mode)


@pytest.mark.parametrize("mode,duration", [("added(30m)", timedelta(minutes=30)), ("added(1h)", timedelta(hours=1)), ("added(12d)", timedelta(days=12)), ("added(7)", timedelta(days=7))])
def test_added_mode_includes_cutoff_boundary(mode, duration, monkeypatch):
    now = datetime(2026, 10, 14, 15, 0, tzinfo=timezone.utc)

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now if tz else now.replace(tzinfo=None)

    monkeypatch.setattr("modules.library.datetime", FrozenDateTime)
    library = SimpleNamespace(schedule_mode=mode, is_show=False)
    items = [
        SimpleNamespace(ratingKey=1, addedAt=now - duration),
        SimpleNamespace(ratingKey=2, addedAt=now - duration - timedelta(microseconds=1)),
        SimpleNamespace(ratingKey=3, addedAt=now - timedelta(seconds=1)),
    ]
    assert Library._schedule_item_keys(library, items) == {1, 3}


def test_added_mode_includes_recent_show_episode(monkeypatch):
    now = datetime(2026, 10, 14, 15, 0, tzinfo=timezone.utc)

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now if tz else now.replace(tzinfo=None)

    monkeypatch.setattr("modules.library.datetime", FrozenDateTime)
    seen = []
    library = SimpleNamespace(schedule_mode="added(1h)", is_show=True, get_items_added_since=lambda kind, cutoff: seen.append((kind, cutoff)) or [SimpleNamespace(grandparentRatingKey=42)])
    shows = [SimpleNamespace(ratingKey=42, addedAt=now - timedelta(days=30))]
    assert Library._schedule_item_keys(library, shows) == {42}
    assert seen == [("episode", now - timedelta(hours=1))]


@pytest.mark.parametrize("mode,valid", [("added(30m)", True), ("added(1h)", True), ("added(12d)", True), ("added(7)", True), ("added(01)", True), ("Added(1H)", True), ("added(0m)", False), ("added(1w)", False), ("added(1.5h)", False)])
def test_added_mode_schema(mode, valid):
    schema = json.loads((Path(__file__).resolve().parents[1] / "json-schema" / "config-schema.json").read_text(encoding="utf-8"))
    validator = Draft7Validator({"$ref": "#/definitions/library-section", "definitions": schema["definitions"]})
    config = {"Movies": {"schedule": [{"schedule": "weekly(monday)", "mode": mode}]}}
    assert validator.is_valid(config) is valid


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
