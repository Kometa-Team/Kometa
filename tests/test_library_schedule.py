import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft7Validator

import modules.builder  # noqa: F401 - pre-import breaks the plex/meta circular import
from modules import util
from modules.library import Library
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
