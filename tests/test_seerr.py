from types import SimpleNamespace

import pytest

import modules.builder as builder_module
import modules.seerr as seerr_module
from modules.builder import CollectionBuilder
from modules.seerr import Seerr
from modules.util import BuilderValidationError
from tests.conftest import FakeLogger


class FakeRequests:
    def __init__(self, status_code=201):
        self.status_code = status_code
        self.calls = []

    def post(self, url, json=None, headers=None):
        self.calls.append((url, json, headers))
        return SimpleNamespace(status_code=self.status_code, json=lambda: {"id": 25}, text="")


def test_movie_request_includes_collection_overrides(monkeypatch):
    monkeypatch.setattr(seerr_module, "logger", FakeLogger())
    requests = FakeRequests()
    seerr = Seerr(requests, {"url": "http://seerr.local/", "apikey": "key"})

    result = seerr.request(
        "movie",
        123,
        is4k=True,
        overrides={"server_id": 2, "quality_profile": 4, "root_folder": "/movies-4k"},
    )

    assert result == {"id": 25}
    assert requests.calls == [
        (
            "http://seerr.local/api/v1/request",
            {"mediaType": "movie", "mediaId": 123, "is4k": True, "serverId": 2, "profileId": 4, "rootFolder": "/movies-4k"},
            {"X-Api-Key": "key"},
        )
    ]


def test_tv_request_maps_profile_name_and_tvdb_id(monkeypatch):
    monkeypatch.setattr(seerr_module, "logger", FakeLogger())
    requests = FakeRequests()
    seerr = Seerr(requests, {"url": "http://seerr.local", "apikey": "key"})

    seerr.request("tv", 456, tvdb_id=789, overrides={"quality_profile": "HD-1080p"})

    assert requests.calls[0][1] == {
        "mediaType": "tv",
        "mediaId": 456,
        "is4k": False,
        "seasons": "all",
        "tvdbId": 789,
        "profileName": "HD-1080p",
    }


def test_collection_seerr_overrides_are_parsed_per_tier(monkeypatch):
    builder = object.__new__(CollectionBuilder)
    builder.library = SimpleNamespace(is_music=False)
    builder.Type = "Movie"
    builder.seerr_details = {}

    builder._seerr(
        "seerr_overrides",
        {
            "standard": {"server_id": 1, "quality_profile": "HD-1080p"},
            "4k": {"server_id": 2, "quality_profile": 4, "root_folder": "/movies-4k"},
        },
    )

    assert builder.seerr_details["overrides"] == {
        "standard": {"server_id": 1, "quality_profile": "HD-1080p"},
        "4k": {"server_id": 2, "quality_profile": 4, "root_folder": "/movies-4k"},
    }
    with pytest.raises(BuilderValidationError, match="keys must be standard or 4k"):
        builder._seerr("seerr_overrides", {"uhd": {"server_id": 2}})


def test_existing_requests_use_each_tier_override(monkeypatch):
    monkeypatch.setattr(builder_module, "logger", FakeLogger())

    class FakeSeerr:
        def __init__(self):
            self.calls = []

        def request(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return {"id": len(self.calls)}

    seerr = FakeSeerr()
    builder = object.__new__(CollectionBuilder)
    builder.library = SimpleNamespace(Seerr=seerr)
    builder.config = SimpleNamespace(Convert=SimpleNamespace())
    builder.Type = "Movie"
    builder.seerr_details = {
        "instance": "both",
        "overrides": {"standard": {"server_id": 1}, "4k": {"server_id": 2}},
    }

    builder._send_seerr_requests([("Existing Movie", 123)], "movie")

    assert seerr.calls == [
        (("movie", 123), {"is4k": False, "tvdb_id": None, "overrides": {"server_id": 1}}),
        (("movie", 123), {"is4k": True, "tvdb_id": None, "overrides": {"server_id": 2}}),
    ]
