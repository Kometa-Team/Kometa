from types import SimpleNamespace

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
    url = "https://floppy.example/list/1/json?arr=radarr"
    floppy = Floppy(Requests({url: [{"id": 550}, {"id": 13}]}), {"url": "https://floppy.example", "token": None})
    assert floppy.get_ids("https://floppy.example/list/1", is_movie=True) == [(550, "tmdb"), (13, "tmdb")]


def test_public_show_list_uses_sonarr_json_feed():
    url = "https://floppy.example/list/1/json?arr=sonarr"
    floppy = Floppy(Requests({url: [{"id": 1399}]}), {"url": "https://floppy.example", "token": None})
    assert floppy.get_ids("https://floppy.example/list/1", is_movie=False) == [(1399, "tmdb_show")]


def test_private_list_uses_api_key_and_maps_movie_and_show_ids():
    connection_url = "https://floppy.example/api/v1/lists?limit=1"
    list_url = "https://floppy.example/api/v1/lists/2/items?limit=1000"
    requests = Requests(
        {
            connection_url: {"results": []},
            list_url: {
                "pagination": {"next": None},
                "results": [
                    {"item": {"media_type": "movie", "source": "tmdb", "media_id": "550"}},
                    {"item": {"media_type": "tv", "source": "tmdb", "media_id": "1399"}},
                ],
            },
        }
    )
    floppy = Floppy(requests, {"url": "https://floppy.example", "token": "secret"})
    floppy.test_connection()
    assert floppy.get_ids("https://floppy.example/list/2", is_movie=None) == [(550, "tmdb"), (1399, "tmdb_show")]
    assert all(headers == {"X-API-Key": "secret"} for _, headers in requests.calls)


def test_rejects_list_from_another_host():
    floppy = Floppy(Requests({}), {"url": "https://floppy.example", "token": None})
    with pytest.raises(Failed, match="must be a list URL"):
        floppy.validate_lists("Collection", "https://other.example/list/1")


def test_private_list_reports_forbidden():
    url = "https://floppy.example/api/v1/lists/2/items?limit=1000"
    floppy = Floppy(Requests({url: FakeResponse({}, status_code=403)}), {"url": "https://floppy.example", "token": "wrong"})
    with pytest.raises(Failed, match="private"):
        floppy.get_ids("https://floppy.example/list/2", is_movie=True)


def test_dictionary_builder_parses_sync_tags():
    floppy = Floppy(Requests({}), {"url": "https://floppy.example", "token": None})
    assert floppy.validate_lists("Collection", {"url": "https://floppy.example/list/1", "sync_tags": True}) == [{"url": "https://floppy.example/list/1", "sync_tags": True}]


def test_tracked_validation_defaults_types_to_library():
    floppy = Floppy(Requests({}), {"url": "https://floppy.example", "token": "secret"})
    assert floppy.validate_tracked("Collection", {"status": ["completed", "in progress"]}, is_movie=False) == {
        "status": ["completed", "in_progress"],
        "type": ["show", "season"],
    }


def test_tracked_api_filters_status_types_and_maps_ids():
    base = "https://floppy.example/api/v1/media/"
    payloads = {
        f"{base}?media_type=movie&limit=100&offset=0&status=3": [{"tracked": True, "status": 3, "item": {"media_type": "movie", "source": "tmdb", "media_id": "550"}}],
        f"{base}?media_type=anime&limit=100&offset=0&status=3": [{"tracked": True, "status": 3, "item": {"media_type": "anime", "source": "mal", "media_id": "123"}}],
    }
    floppy = Floppy(Requests(payloads), {"url": "https://floppy.example", "token": "secret"})
    tracked = {"status": ["completed"], "type": ["movie", "anime"]}
    assert floppy.get_tracked_ids(tracked, is_movie=True) == ([(550, "tmdb")], [123])


def test_tracked_api_maps_floppy_media_response_envelope():
    url = "https://floppy.example/api/v1/media/?media_type=movie&limit=100&offset=0&status=1"
    response = {"results": [{"tracked": True, "status": 1, "item": {"media_type": "movie", "source": "tmdb", "media_id": "123"}}]}
    floppy = Floppy(Requests({url: response}), {"url": "https://floppy.example", "token": "secret"})
    assert floppy.get_tracked_ids({"status": ["in_progress"], "type": ["movie"]}, is_movie=True) == ([(123, "tmdb")], [])


def test_tracked_api_all_uses_unfiltered_request():
    url = "https://floppy.example/api/v1/media/?media_type=movie&limit=100&offset=0"
    floppy = Floppy(Requests({url: [{"tracked": True, "status": 3, "item": {"media_type": "movie", "source": "tmdb", "media_id": "550"}}]}), {"url": "https://floppy.example", "token": "secret"})
    assert floppy.get_tracked_ids({"status": ["all"], "type": ["movie"]}, is_movie=True) == ([(550, "tmdb")], [])


def test_public_csv_returns_description_and_tags():
    url = "https://floppy.example/list/1/export"
    csv_data = 'row_type,list_uid,list_description,list_tags\nlist,1,"A useful list","[""One"", ""Two""]"\n'
    floppy = Floppy(
        Requests({url: FakeResponse(content=csv_data.encode("utf-8"))}),
        {"url": "https://floppy.example", "token": None},
    )
    assert floppy.get_list_details({"url": "https://floppy.example/list/1"}) == (
        "A useful list",
        ["One", "Two"],
    )


def test_details_builder_sets_summary_and_item_labels():
    list_data = {"url": "https://floppy.example/list/2", "sync_tags": True}
    service = SimpleNamespace(
        validate_lists=lambda *_: [list_data],
        get_list_details=lambda *_: ("Private description", ["Crime", "Favorite"]),
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
    assert builder.summaries == {"floppy_list_details": "Private description"}
    assert builder.item_details["item_label"] == ["Existing", "Crime", "Favorite"]


def test_user_ratings_are_cached_mapped_and_rounded_to_half_stars():
    url = "https://floppy.example/api/v1/export/csv?include_lists=0&include_collection=0"
    csv_data = "row_type,media_id,source,media_type,season_number,episode_number,score\n" "media,1399,tmdb,tv,,,9.9\n" "media,1399,tmdb,episode,2,3,8.0\n" "media,1399,tmdb,episode,2,4,8.5\n"
    requests = Requests({url: FakeResponse(content=csv_data.encode("utf-8"))})
    floppy = Floppy(requests, {"url": "https://floppy.example", "token": "secret"})
    assert floppy.get_rating("tv", tmdb_id=1399) == 10.0
    assert floppy.get_rating("episode", tmdb_id=1399, season=2, episode=3) == 8.0
    assert floppy.get_rating("episode", tmdb_id=1399, season=2, episode=4) == 9.0
    assert len(requests.calls) == 1


def test_overlay_rating_preserves_floppy_decimal_precision():
    url = "https://floppy.example/api/v1/export/csv?include_lists=0&include_collection=0"
    csv_data = "row_type,media_id,source,media_type,season_number,episode_number,score\nmedia,550,tmdb,movie,,,9.9\n"
    service = Floppy(Requests({url: FakeResponse(content=csv_data.encode("utf-8"))}), {"url": "https://floppy.example", "token": "secret"})
    assert service.get_overlay_rating("movie", tmdb_id=550) == 9.9
    assert service.get_rating("movie", tmdb_id=550) == 10.0


def test_rating_updates_require_token():
    floppy = Floppy(Requests({}), {"url": "https://floppy.example", "token": None})
    with pytest.raises(Failed, match="API token"):
        floppy.get_rating("movie", tmdb_id=550)
