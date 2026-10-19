"""Behaviour shared by every tracker connector built on modules.tracker, run against each one.

A new connector joins by adding one Harness subclass and listing it in HARNESSES.
"""

from datetime import UTC, datetime, timedelta

import pytest

import modules.flicklist as flicklist_module
import modules.tracker as tracker_module
import modules.wetrakr as wetrakr_module
from modules.flicklist import FlickList
from modules.util import Failed
from modules.wetrakr import WeTrakr
from tests.conftest import FakeLogger
from tests.tracker_fakes import FakeConvert, FakeRequests, FakeResponse


def _bucket(media_type):
    return "movies" if media_type == "movie" else "shows"


class Harness:
    """Hides how one connector shapes its requests and responses so the shared tests state each behaviour once."""

    name = ""
    cls = None
    module = None
    list_ids = (0, 0)
    list_url = ""

    def make(self, responses):
        raise NotImplementedError

    def item_row(self, ids, media_type):
        raise NotImplementedError

    def add_result(self, not_found=(), already=()):
        raise NotImplementedError

    def sent_adds(self, connector):
        raise NotImplementedError

    def sent_removes(self, connector):
        raise NotImplementedError

    def rating_row(self, ids, media_type, rating):
        return {**self.item_row(ids, media_type), "rating": rating}

    @staticmethod
    def lists_response(list_id, name):
        return FakeResponse(json_data=[{"id": list_id, "name": name}], headers={})


class WeTrakrHarness(Harness):
    name = "wetrakr"
    cls = WeTrakr
    module = wetrakr_module
    list_ids = (13255, 1033032976)
    list_url = "https://wetrakr.com/lists/{id}"

    def make(self, responses):
        expires_at = (datetime.now(UTC) + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        authorization = {"access_token": "tok1", "refresh_token": "ref1", "expires_at": expires_at}
        return WeTrakr(FakeRequests(responses), False, {"client_id": "cid", "config_path": "/cfg.yml", "authorization": authorization})

    def item_row(self, ids, media_type):
        return {"type": media_type, "ids": ids}

    @staticmethod
    def _grouped(items, build):
        grouped = {}
        for ids, media_type in items:
            grouped.setdefault(_bucket(media_type), []).append(build(ids))
        return grouped

    def add_result(self, not_found=(), already=()):
        result = {"added": {"total": 0}}
        if not_found:
            result["notFound"] = self._grouped(not_found, lambda ids: {"ids": ids})
        if already:
            # WeTrakr reports a duplicate as an errored entry, not as a separate list like FlickList.
            result["errored"] = self._grouped(already, lambda ids: {"ids": ids, "error": "Already added!"})
        return FakeResponse(json_data=result)

    @staticmethod
    def _sent(connector, suffix):
        sent = []
        for url, payload, _headers in connector.requests.posts:
            if url.endswith(suffix):
                for key, media_type in (("movies", "movie"), ("shows", "show")):
                    sent.extend((entry["ids"], media_type) for entry in payload[key])
        return sent

    def sent_adds(self, connector):
        return self._sent(connector, "/items")

    def sent_removes(self, connector):
        return self._sent(connector, "/items/remove")


class FlickListHarness(Harness):
    name = "flicklist"
    cls = FlickList
    module = flicklist_module
    list_ids = (4821, 9310)
    list_url = "https://flicklist.tv/list/{id}"

    def make(self, responses):
        return FlickList(FakeRequests(responses), False, {"api_key": "fs_live_test"})

    def item_row(self, ids, media_type):
        return {"ids": ids, "media_type": media_type}

    def add_result(self, not_found=(), already=()):
        return FakeResponse(json_data={"existing": [self.item_row(*item) for item in already], "not_found": [self.item_row(*item) for item in not_found]})

    @staticmethod
    def _sent(calls):
        return [(item["ids"], item["media_type"]) for _url, payload, _headers in calls for item in payload["items"]]

    def sent_adds(self, connector):
        return self._sent(connector.requests.posts)

    def sent_removes(self, connector):
        return self._sent(connector.requests.deletes)


HARNESSES = [WeTrakrHarness(), FlickListHarness()]


@pytest.fixture(params=HARNESSES, ids=[h.name for h in HARNESSES])
def harness(request):
    return request.param


@pytest.fixture
def logs(harness, monkeypatch):
    """Each module keeps its own ``logger = util.logger``, which is None under test, so patch the ones sync_list logs through."""
    fake = FakeLogger()
    monkeypatch.setattr(harness.module, "logger", fake)
    monkeypatch.setattr(tracker_module, "logger", fake)
    return fake


def _ok():
    return FakeResponse(json_data={})


def _sync_connector(harness, current=(), *batches):
    """A connector whose next responses are: the list lookup, the current items, then one per batch call."""
    return harness.make([harness.lists_response(harness.list_ids[0], "My List"), FakeResponse(json_data=list(current), headers={}), *batches])


# --- list ids and validation ---


@pytest.mark.parametrize("form", ["int", "digits", "url", "url_with_trailing_slash"])
def test_parse_list_id_accepts_bare_id_and_url(harness, form):
    list_id = harness.list_ids[0]
    url = harness.list_url.format(id=list_id)
    value = {"int": list_id, "digits": str(list_id), "url": url, "url_with_trailing_slash": url + "/"}[form]
    assert harness.cls._parse_list_id(value) == list_id


def test_parse_list_id_rejects_garbage(harness):
    with pytest.raises(Failed, match="Could not parse a list id"):
        harness.cls._parse_list_id("not-a-list")


def test_validate_lists_returns_ids_for_multiple_values(harness):
    first, second = harness.list_ids
    connector = harness.make([])
    assert connector.validate_lists("Collection", [str(first), harness.list_url.format(id=second)]) == [first, second]


def test_validate_lists_rejects_dict_entries(harness):
    connector = harness.make([])
    with pytest.raises(Failed, match="cannot be a dictionary"):
        connector.validate_lists("Collection", [{"bad": True}])


def test_user_agent_includes_local_version(harness):
    assert harness.make([]).user_agent == "Kometa/2.4.8-build5 (+https://kometa.wiki)"


# --- list resolution ---


def test_resolve_list_matches_by_exact_name(harness):
    list_id = harness.list_ids[0]
    connector = harness.make([harness.lists_response(list_id, "Recently Added")])
    assert connector._resolve_list("Recently Added") == (list_id, False)


def test_resolve_list_matches_by_numeric_id(harness):
    list_id = harness.list_ids[0]
    connector = harness.make([harness.lists_response(list_id, "Watchlist")])
    assert connector._resolve_list(list_id) == (list_id, False)


def test_resolve_list_unknown_id_raises_failed(harness):
    connector = harness.make([harness.lists_response(1, "Other")])
    with pytest.raises(Failed, match="not found among your own lists"):
        connector._resolve_list(harness.list_ids[0])


# --- user ratings ---


def test_user_ratings_key_movies_by_tmdb_and_shows_by_tvdb(harness):
    movies = harness.make([FakeResponse(json_data=[harness.rating_row({"tmdb": 550}, "movie", 8.0)], headers={})])
    shows = harness.make([FakeResponse(json_data=[harness.rating_row({"tvdb": 81189}, "show", 7.5)], headers={})])
    assert movies.user_ratings(True) == {550: 8.0}
    assert shows.user_ratings(False) == {81189: 7.5}


def test_user_ratings_skips_items_with_no_rating(harness):
    connector = harness.make([FakeResponse(json_data=[harness.rating_row({"tmdb": 550}, "movie", None)], headers={})])
    assert connector.user_ratings(True) == {}


def test_user_ratings_skips_items_missing_the_relevant_id(harness):
    # A show that only carries a tmdb id has no tvdb key to be rated under.
    connector = harness.make([FakeResponse(json_data=[harness.rating_row({"tmdb": 1396}, "show", 8.0)], headers={})])
    assert connector.user_ratings(False) == {}


# --- sync_list ---


def test_sync_list_adds_new_items_and_removes_stale_ones(harness):
    connector = _sync_connector(harness, [harness.item_row({"tmdb": 999}, "movie")], _ok(), _ok())
    connector.sync_list(FakeConvert(), harness.list_ids[0], [({"tmdb": 550}, "movie")])
    assert harness.sent_adds(connector) == [({"tmdb": 550}, "movie")]
    assert harness.sent_removes(connector) == [({"tmdb": 999}, "movie")]


def test_sync_list_leaves_unmatched_current_items_alone_and_warns(harness, logs):
    connector = _sync_connector(harness, [harness.item_row({}, "movie")], _ok())
    connector.sync_list(FakeConvert(), harness.list_ids[0], [({"tmdb": 550}, "movie")])
    assert harness.sent_adds(connector) == [({"tmdb": 550}, "movie")]
    assert harness.sent_removes(connector) == []
    assert any("had no usable id at all; leaving them in place" in message for message in logs.warning_messages)


def test_sync_list_unresolved_tvdb_conversion_does_not_delete_the_matching_tmdb_item(harness):
    # The desired show only carries tvdb (Convert missed this run) and the current item carries tmdb and that same tvdb: they must still match.
    connector = _sync_connector(harness, [harness.item_row({"tmdb": 1396, "tvdb": 81189}, "show")], _ok(), _ok())
    connector.sync_list(FakeConvert(), harness.list_ids[0], [({"tvdb": 81189}, "show")])
    assert harness.sent_adds(connector) == []
    assert harness.sent_removes(connector) == []


def test_sync_list_logs_items_the_service_could_not_find_as_errors_and_does_not_raise(harness, logs):
    connector = _sync_connector(harness, [], harness.add_result(not_found=[({"tmdb": 550}, "movie")]))
    connector.sync_list(FakeConvert(), harness.list_ids[0], [({"tmdb": 550}, "movie")])
    assert any("1 item(s) not found while syncing" in message for message in logs.error_messages)
    assert any("(1 not found" in message for message in logs.info_messages)


def test_sync_list_logs_items_already_on_the_list_at_debug_and_not_as_a_failure(harness, logs):
    connector = _sync_connector(harness, [], harness.add_result(already=[({"tmdb": 603}, "movie")]))
    connector.sync_list(FakeConvert(), harness.list_ids[0], [({"tmdb": 603}, "movie")])
    assert any("already" in message for message in logs.debug_messages)
    assert logs.error_messages == []
    assert logs.warning_messages == []
