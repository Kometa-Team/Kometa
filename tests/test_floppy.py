from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.floppy as floppy_module
from modules.builder import CollectionBuilder
from modules.floppy import Floppy
from modules.util import Failed
from tests.conftest import FakeLogger, FakeResponse


class Requests:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []

    def get(self, url, headers=None, params=None):
        self.calls.append((url, headers))
        if params:
            url += "?" + "&".join(f"{key}={value}" for key, value in params.items())
        response = self.payloads[url]
        return response if isinstance(response, FakeResponse) else FakeResponse(response)


@pytest.fixture(autouse=True)
def patch_logger(monkeypatch):
    monkeypatch.setattr(floppy_module, "logger", FakeLogger())


def test_public_movie_list_uses_radarr_json_feed():
    url = "https://floppy.kometa.team/list/1/json?arr=radarr"
    floppy = Floppy(Requests({url: [{"id": 550}, {"id": 13}]}), {"url": "https://floppy.kometa.team", "token": None})
    assert floppy.get_ids("https://floppy.kometa.team/list/1", is_movie=True) == [(550, "tmdb"), (13, "tmdb")]


@pytest.mark.parametrize("level", [None, "season", "episode"])
@pytest.mark.parametrize("authenticated", [False, True])
def test_season_episode_lists_preserve_order_and_parent_identity(level, authenticated):
    root = "https://floppy.kometa.team"
    rows = [
        {"media_type": "season", "source": "tmdb", "media_id": "1396", "season_number": 1},
        {"media_type": "movie", "source": "tmdb", "media_id": "550"},
        {"media_type": "episode", "source": "tvdb", "media_id": "81189", "season_number": 2, "episode_number": 3},
        {"media_type": "season", "source": "tmdb", "media_id": "1396", "season_number": 3},
    ]
    if authenticated:
        payloads = {f"{root}/api/v1/lists/1/items?limit=1000": {"results": [{"item": row} for row in rows + rows[:1]], "pagination": {"next": None}}}
    else:
        rss = "<rss><channel>" + "".join(f"<item><guid>{guid}</guid></item>" for guid in ["tmdb:season:1396:s1", "tmdb:movie:550", "tvdb:episode:81189:s2:e3", "tmdb:season:1396:s3", "tmdb:season:1396:s1"]) + "</channel></rss>"
        payloads = {f"{root}/list/1/rss": FakeResponse(content=rss.encode())}
    floppy = Floppy(Requests(payloads), {"url": root, "token": "test" if authenticated else None})
    expected = [("1396_1", "tmdb_season")]
    if level is None:
        expected.append((550, "tmdb"))
    expected.extend([("81189_2", "tvdb_season") if level == "season" else ("81189_2_3", "tvdb_episode"), ("1396_3", "tmdb_season")])
    assert floppy.get_ids(f"{root}/list/1", is_movie=None if level is None else False, builder_level=level) == expected


@pytest.mark.parametrize("level, expected", [("show", [(1396, "tmdb_show")]), ("season", [("1396_1", "tmdb_season")]), ("episode", [("1396_1", "tmdb_season")]), (None, [("1396_1", "tmdb_season")])])
def test_tracked_season_uses_documented_type_endpoint(level, expected):
    root = "https://floppy.kometa.team"
    row = {"item": {"media_type": "season", "source": "tmdb", "media_id": "1396", "season_number": 1}, "status": 3}
    requests = Requests({f"{root}/api/v1/media/season?limit=100&offset=0": {"results": [row]}})
    floppy = Floppy(requests, {"url": root, "token": "test"})
    assert floppy.get_tracked_ids({"type": ["season"], "status": ["all"]}, is_movie=None if level is None else False, builder_level=level) == (expected, [])


@pytest.mark.parametrize(
    "row",
    [
        {"media_type": "season", "source": "tmdb", "media_id": "1396"},
        {"media_type": "season", "source": "tmdb", "media_id": "1396", "season_number": -1},
        {"media_type": "episode", "source": "tmdb", "media_id": "1396", "season_number": 1, "episode_number": "bad"},
        {"media_type": "season", "source": "imdb", "media_id": "tt0903747", "season_number": 1},
    ],
)
def test_unmatchable_parts_do_not_become_whole_shows(row):
    assert Floppy._api_id(row, None) is None


def test_api_part_lists_follow_pagination_without_collapsing_seasons():
    root = "https://floppy.kometa.team"
    first = f"{root}/api/v1/lists/1/items?limit=1000"
    second = f"{root}/api/v1/lists/1/items?offset=1000"
    row = {"media_type": "season", "source": "tmdb", "media_id": "1396", "season_number": 0}
    requests = Requests({first: {"results": [row], "pagination": {"next": second}}, second: {"results": [dict(row, season_number=2)], "pagination": {"next": None}}})
    floppy = Floppy(requests, {"url": root, "token": "test"})
    assert floppy.get_ids(f"{root}/list/1", None) == [("1396_0", "tmdb_season"), ("1396_2", "tmdb_season")]
    assert len(requests.calls) == 2


def test_list_export_uses_media_list_route_without_tracking():
    root = "https://floppy.kometa.team"
    requests = Requests(
        {
            f"{root}/api/v1/lists?limit=100": {"results": [{"id": 7, "name": "Test"}], "pagination": {"next": None}},
            f"{root}/api/v1/lists/7/items?limit=100": {"results": [{"id": 21, "media_type": "movie", "source": "tmdb", "media_id": "550"}], "pagination": {"next": None}},
        }
    )
    requests.session = MagicMock()
    requests.session.put.return_value = FakeResponse({"results": []})
    requests.session.delete.return_value = FakeResponse(None, status_code=204)
    floppy = Floppy(requests, {"url": root, "token": "secret"})

    floppy.sync_list("Test", [(550, "tmdb"), (1399, "tmdb_show")], "sync")

    requests.session.put.assert_called_once()
    assert requests.session.put.call_args.args[0] == f"{root}/api/v1/media/tv/tmdb/1399/lists/7"
    requests.session.delete.assert_not_called()


def test_list_export_syncs_empty_without_media_tracking():
    root = "https://floppy.kometa.team"
    requests = Requests(
        {
            f"{root}/api/v1/lists?limit=100": {"results": [{"id": 7, "name": "Test"}], "pagination": {"next": None}},
            f"{root}/api/v1/lists/7/items?limit=100": {"results": [{"id": 1, "media_type": "tv", "source": "tmdb", "media_id": "97546"}], "pagination": {"next": None}},
        }
    )
    requests.session = MagicMock()
    requests.session.delete.return_value = FakeResponse(None, status_code=204)
    floppy = Floppy(requests, {"url": root, "token": "secret"})

    floppy.sync_list(7, [], "sync")

    requests.session.delete.assert_called_once()
    assert requests.session.delete.call_args.args[0] == f"{root}/api/v1/media/tv/tmdb/97546/lists/7"
    requests.session.put.assert_not_called()


def test_list_export_creates_missing_named_list():
    root = "https://floppy.kometa.team"
    requests = Requests(
        {
            f"{root}/api/v1/lists?limit=100": {"results": [], "pagination": {"next": None}},
            f"{root}/api/v1/lists/8/items?limit=100": {"results": [], "pagination": {"next": None}},
        }
    )
    requests.post = MagicMock(return_value=FakeResponse({"id": 8, "name": "New"}, status_code=201))
    requests.session = MagicMock()
    floppy = Floppy(requests, {"url": root, "token": "secret"})

    floppy.sync_list("New", [], "sync")

    requests.post.assert_called_once_with(f"{root}/api/v1/lists", json={"name": "New"}, headers={"X-API-Key": "secret"})


def test_list_export_does_not_remove_items_after_failed_add():
    root = "https://floppy.kometa.team"
    requests = Requests(
        {
            f"{root}/api/v1/lists?limit=100": {"results": [{"id": 7, "name": "Test"}], "pagination": {"next": None}},
            f"{root}/api/v1/lists/7/items?limit=100": {"results": [{"id": 21, "media_type": "movie", "source": "tmdb", "media_id": "550"}], "pagination": {"next": None}},
        }
    )
    requests.session = MagicMock()
    requests.session.put.return_value = FakeResponse({"detail": "Media not found"}, status_code=404)
    floppy = Floppy(requests, {"url": root, "token": "secret"})

    with pytest.raises(Failed, match="Media not found"):
        floppy.sync_list("Test", [(1399, "tmdb_show")], "sync")

    requests.session.delete.assert_not_called()


def test_public_show_list_uses_sonarr_json_feed():
    url = "https://floppy.kometa.team/list/1/json?arr=sonarr"
    floppy = Floppy(Requests({url: [{"id": 1399}]}), {"url": "https://floppy.kometa.team", "token": None})
    assert floppy.get_ids("https://floppy.kometa.team/list/1", is_movie=False) == [(1399, "tmdb_show")]


def test_public_episode_list_uses_rss_feed():
    json_url = "https://floppy.kometa.team/list/1/json?arr=sonarr"
    rss_url = "https://floppy.kometa.team/list/1/rss"
    rss_data = "<rss><channel><item><guid>tmdb:episode:97546:s1:e1</guid></item><item><guid>tmdb:episode:97546:s1:e2</guid></item></channel></rss>"
    floppy = Floppy(
        Requests({json_url: [], rss_url: FakeResponse(content=rss_data.encode("utf-8"))}),
        {"url": "https://floppy.kometa.team", "token": None},
    )
    assert floppy.get_ids("https://floppy.kometa.team/list/1", is_movie=False, is_episode=True) == [
        ("97546_1_1", "tmdb_episode"),
        ("97546_1_2", "tmdb_episode"),
    ]


def test_rejects_list_from_another_host():
    floppy = Floppy(Requests({}), {"url": "https://floppy.kometa.team", "token": None})
    with pytest.raises(Failed, match="must be a list URL"):
        floppy.validate_lists("Collection", "https://other.example/list/1")


def test_dictionary_builder_parses_sync_tags():
    floppy = Floppy(Requests({}), {"url": "https://floppy.kometa.team", "token": None})
    assert floppy.validate_lists("Collection", {"url": "https://floppy.kometa.team/list/1", "sync_tags": True}) == [{"url": "https://floppy.kometa.team/list/1", "sync_tags": True}]


def test_tracked_validation_defaults_types_to_library():
    floppy = Floppy(Requests({}), {"url": "https://floppy.kometa.team", "token": None})
    assert floppy.validate_tracked("Collection", {"status": ["completed", "in progress"]}, is_movie=False) == {
        "status": ["completed", "in_progress"],
        "type": ["show", "season"],
    }


def test_public_csv_returns_description_and_tags():
    url = "https://floppy.kometa.team/list/1/export"
    csv_data = 'row_type,list_uid,list_description,list_tags\nlist,1,"A useful list","[""One"", ""Two""]"\n'
    floppy = Floppy(
        Requests({url: FakeResponse(content=csv_data.encode("utf-8"))}),
        {"url": "https://floppy.kometa.team", "token": None},
    )
    assert floppy.get_list_details({"url": "https://floppy.kometa.team/list/1"}) == (
        "A useful list",
        ["One", "Two"],
    )


def test_details_builder_sets_summary_and_item_labels():
    list_data = {"url": "https://floppy.kometa.team/list/2", "sync_tags": True}
    service = SimpleNamespace(
        validate_lists=lambda *_: [list_data],
        get_list_details=lambda *_: ("Public description", ["Crime", "Favorite"]),
    )
    builder = SimpleNamespace(
        Type="Collection",
        config=SimpleNamespace(Floppy=service),
        builders=[],
        summaries={},
        item_details={"item_label": ["Existing"]},
    )
    CollectionBuilder._floppy(builder, "floppy_list_details", list_data)
    assert builder.builders == [("floppy_list", list_data)]
    assert builder.summaries == {"floppy_list_details": "Public description"}
    assert builder.item_details["item_label"] == ["Existing", "Crime", "Favorite"]
