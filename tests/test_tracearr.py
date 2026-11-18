import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import modules.tracearr as tracearr_module
from modules.tracearr import Tracearr
from modules.util import Failed
from tests.conftest import FakeLogger, FakeResponse

FIXTURES = Path(__file__).parent / "fixtures" / "tracearr_3_1_2"
SERVER_ID = "550e8400-e29b-41d4-a716-446655440000"
USER_ID = "550e8400-e29b-41d4-a716-446655440001"
BASE = "http://tracearr.test"


def pages(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


@pytest.fixture
def connector(monkeypatch):
    monkeypatch.setattr(tracearr_module, "logger", FakeLogger())
    requests = Mock()
    requests.get.side_effect = [
        FakeResponse({"servers": [{"id": SERVER_ID, "type": "plex", "name": "Plex"}]}),
        FakeResponse({"paths": {"/api/v2/public/watched-media": {"get": {}}}}),
    ]
    library = SimpleNamespace(PlexServer=SimpleNamespace(friendlyName="Plex"), Plex=SimpleNamespace(key="1"), is_movie=True, is_show=False)
    return Tracearr(requests, library, {"url": BASE, "apikey": "trr_pub_test"})


@pytest.mark.parametrize("user", [USER_ID, "alice", " ALICE SMITH ", "1234567", "42", "alice-plex"])
def test_user_identifiers_across_cursor_pages(connector, user):
    connector.requests.get.reset_mock()
    connector.requests.get.side_effect = [FakeResponse(page) for page in pages("users")]
    assert connector._resolve_user(user) == USER_ID
    assert connector._resolve_user(user) == USER_ID  # Reuse the fully paged user list.
    calls = connector.requests.get.call_args_list
    assert len(calls) == 2
    assert calls[1].args[0] == f"{BASE}/api/v2/public/users"
    assert calls[1].kwargs["params"]["cursor"] == "users-page-2"


@pytest.mark.parametrize("display_name", [None, ""])
def test_users_without_display_names_remain_resolvable(connector, display_name):
    users = pages("users")[0]["data"]
    users[0]["identity_name"] = display_name
    connector._users_cache = users
    assert connector._resolve_user("alice") == USER_ID


def test_older_users_without_display_name_field(connector):
    users = pages("users")[0]["data"]
    del users[0]["identity_name"]
    connector._users_cache = users
    assert connector._resolve_user("alice-plex") == USER_ID


@pytest.mark.parametrize("collision", ["display_name", "username"])
def test_ambiguous_names_list_identity_ids(connector, collision):
    first = pages("users")[0]["data"][0]
    second = deepcopy(first)
    second.update(id="550e8400-e29b-41d4-a716-446655440003", username="bob", accounts=[], plex_account_id=None)
    if collision == "username":
        second.update(identity_name=None, username="Alice Smith")
    connector._users_cache = [first, second]
    with pytest.raises(Failed, match="ambiguous") as error:
        connector._resolve_user("Alice Smith")
    assert first["id"] in str(error.value)
    assert second["id"] in str(error.value)
    assert connector._resolve_user(USER_ID) == USER_ID


def test_unknown_user_lists_display_name_and_uuid(connector):
    connector._users_cache = pages("users")[0]["data"]
    with pytest.raises(Failed, match="not found") as error:
        connector._resolve_user("unknown")
    assert f"Alice Smith ({USER_ID})" in str(error.value)


def test_history_builder_uses_v2_identity_and_provider_id(connector):
    connector.requests.get.reset_mock()
    history = pages("history")
    connector.requests.get.side_effect = [FakeResponse(page) for page in pages("users") + history]
    data = {"list_type": "watched", "list_size": 10, "list_days": 30, "list_minimum": 0, "user": "Alice Smith", "watched": True}
    assert connector.get_rating_keys(data, is_playlist=True) == [(27205, "tmdb")]
    calls = connector.requests.get.call_args_list
    assert calls[2].args[0] == f"{BASE}/api/v2/public/history"
    assert calls[3].kwargs["params"]["cursor"] == "history-page-2"
    for call in calls[2:]:
        assert call.kwargs["params"]["user_id"] == USER_ID
        assert call.kwargs["params"]["server_id"] == SERVER_ID
        assert call.kwargs["params"]["watched"] == "true"
        assert call.kwargs["headers"] == {"Authorization": "Bearer trr_pub_test"}
    # v2 counts a resumed play once; segment_count is not a play multiplier.
    aggregate = connector._aggregate_history(history[0]["data"], "watched", 0)[0]
    assert aggregate["completed_sessions"] == 1
    assert aggregate["watch_time_ms"] == 7200000


def test_in_progress_preserves_exact_episode_rating_key(connector):
    connector._users_cache = pages("users")[0]["data"]
    connector.requests.get.side_effect = [FakeResponse(pages("history")[1])]
    show_library = SimpleNamespace(Plex=SimpleNamespace(key="2"), is_movie=False, is_show=True)
    data = {"list_type": "in_progress", "list_size": 10, "list_days": 30, "list_minimum": 0, "user": "Alice Smith"}
    assert connector.get_rating_keys(data, is_playlist=True, libraries=[show_library]) == [("202", "ratingKey")]


def test_watched_media_cursor_pages_and_provider_ids(connector):
    connector.requests.get.reset_mock()
    connector._users_cache = pages("users")[0]["data"]
    movie_page = pages("watched-media")[0]
    # A second movie exercises pagination through the public builder.
    next_page = deepcopy(movie_page)
    next_page["data"][0].update(tmdb_id=None, imdb_id="tt0133093", last_watched_day="2026-10-24")
    next_page["meta"]["nextCursor"] = None
    connector.requests.get.side_effect = [FakeResponse(movie_page), FakeResponse(next_page)]
    data = {"list_type": "watched_media", "list_size": 10, "user": "Alice Smith", "min_state": "watched"}
    assert connector.get_rating_keys(data) == [(27205, "tmdb"), ("tt0133093", "imdb")]
    calls = connector.requests.get.call_args_list
    assert len(calls) == 2
    assert calls[1].kwargs["params"]["cursor"] == "watched-media-page-2"
    for call in calls:
        assert call.args[0] == f"{BASE}/api/v2/public/watched-media"
        assert call.kwargs["params"]["pageSize"] == 1000
        assert call.kwargs["params"]["user_id"] == USER_ID
        assert call.kwargs["params"]["server_id"] == SERVER_ID
    episode = pages("watched-media")[1]["data"][0]
    assert connector._watched_media_item_id(episode, "episode") == ("12345_1_1", "tvdb_episode")


def test_watched_media_requires_advertised_capability(connector):
    connector.v2_paths = set()
    with pytest.raises(Failed, match="requires a Tracearr version"):
        connector.get_rating_keys({"list_type": "watched_media"})


def test_v1_fallback_keeps_legacy_user_resolution(connector):
    connector.requests.get.side_effect = [
        FakeResponse({"servers": [{"id": SERVER_ID, "type": "plex", "name": "Plex"}]}),
        FakeResponse({"message": "Not found"}, status_code=404),
    ]
    legacy = Tracearr(connector.requests, connector.library, {"url": BASE, "apikey": "trr_pub_test"})
    assert legacy.history_version == 1
    assert legacy._resolve_user(" alice ") == "alice"


@pytest.mark.parametrize("endpoint", ["users", "history", "watched-media"])
def test_repeated_cursor_fails_instead_of_looping(connector, endpoint):
    page = pages(endpoint)[0]
    connector.requests.get.side_effect = [FakeResponse(page), FakeResponse(page)]
    with pytest.raises(Failed, match="invalid pagination metadata"):
        if endpoint == "users":
            connector._resolve_user("alice")
        elif endpoint == "history":
            connector._fetch_history({"pageSize": 100})
        else:
            connector.get_rating_keys({"list_type": "watched_media", "list_size": 10, "min_state": "watched"})
