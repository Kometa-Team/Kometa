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
    url = "https://floppy.kometa.team/list/1/json?arr=radarr"
    floppy = Floppy(Requests({url: [{"id": 550}, {"id": 13}]}), {"url": "https://floppy.kometa.team", "token": None})
    assert floppy.get_ids("https://floppy.kometa.team/list/1", is_movie=True) == [(550, "tmdb"), (13, "tmdb")]


def test_public_show_list_uses_sonarr_json_feed():
    url = "https://floppy.kometa.team/list/1/json?arr=sonarr"
    floppy = Floppy(Requests({url: [{"id": 1399}]}), {"url": "https://floppy.kometa.team", "token": None})
    assert floppy.get_ids("https://floppy.kometa.team/list/1", is_movie=False) == [(1399, "tmdb_show")]


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
