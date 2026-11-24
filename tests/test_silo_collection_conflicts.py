"""Recover from collection revision churn without overwriting concurrent edits."""

import pytest

import modules.builder  # noqa: F401 - break circular imports
from modules.silo import SiloClient, SiloHTTPError
from modules.util import Failed
from tests.conftest import FakeLogger, FakeResponse
from tests.test_silo import FakeSession, _server


@pytest.fixture(autouse=True)
def no_network_or_delays(monkeypatch):
    monkeypatch.setattr("modules.silo.logger", FakeLogger())
    monkeypatch.setattr("modules.silo.time.sleep", lambda _: None)


def client(responses):
    return SiloClient(_server(pace_requests=False), session=FakeSession(responses))


def record(data, revision):
    return FakeResponse(data, headers={"ETag": revision})


def test_collection_read_retries_conflict_and_keeps_fresh_etag():
    api = client([FakeResponse({}, status_code=409), record({"id": "one"}, '"v2"')])
    assert api.get_collection("one") == ({"id": "one"}, '"v2"')
    assert len(api.session.calls) == 2
    assert all(call["method"] == "GET" for call in api.session.calls)


@pytest.mark.parametrize("status,count", [(409, 3), (403, 1), (500, 1)])
def test_collection_read_retries_are_bounded_and_specific(status, count):
    api = client([FakeResponse({}, status_code=status) for _ in range(count)])
    with pytest.raises(Failed, match=f"returned {status}"):
        api.get_collection("one")
    assert len(api.session.calls) == count


def test_patch_recovers_after_unrelated_revision_change():
    before = {"id": "one", "description": "Before", "title": "Old Title"}
    current = {**before, "title": "Someone else's title"}
    api = client([record(before, '"v1"'), FakeResponse({}, status_code=412), record(current, '"v2"'), record({**current, "description": "After"}, '"v3"')])
    api.get_collection("one")
    result, etag = api.update_collection("one", {"description": "After"}, '"v1"')
    assert result["title"] == "Someone else's title"
    assert etag == '"v3"'
    assert api.session.calls[-1]["headers"] == {"If-Match": '"v2"'}
    assert api.session.calls[-1]["json"] == {"description": "After"}


def test_patch_preserves_conflicting_edit_to_same_field():
    api = client([record({"description": "Before"}, '"v1"'), FakeResponse({}, status_code=412), record({"description": "Someone else's summary"}, '"v2"')])
    api.get_collection("one")
    with pytest.raises(SiloHTTPError, match="412"):
        api.update_collection("one", {"description": "After"}, '"v1"')
    assert [call["method"] for call in api.session.calls] == ["GET", "PATCH", "GET"]


def test_patch_skips_fields_already_at_desired_values():
    api = client([record({"description": "Before", "sort_config": {}}, '"v1"'), FakeResponse({}, status_code=412), record({"description": "After", "sort_config": {}}, '"v2"'), record({"description": "After", "sort_config": {"field": "title"}}, '"v3"')])
    api.get_collection("one")
    api.update_collection("one", {"description": "After", "sort_config": {"field": "title"}}, '"v1"')
    assert api.session.calls[-1]["json"] == {"sort_config": {"field": "title"}}


def test_patch_does_not_write_when_all_values_already_match():
    api = client([record({"description": "Before"}, '"v1"'), FakeResponse({}, status_code=412), record({"description": "After"}, '"v2"')])
    api.get_collection("one")
    assert api.update_collection("one", {"description": "After"}, '"v1"') == ({"description": "After"}, '"v2"')
    assert len(api.session.calls) == 3


@pytest.mark.parametrize("etag", ['"unknown"', "*", None])
def test_patch_without_matching_snapshot_does_not_retry(etag):
    api = client([FakeResponse({}, status_code=412)])
    with pytest.raises(SiloHTTPError, match="412"):
        api.update_collection("one", {"description": "After"}, etag)
    assert len(api.session.calls) == 1


def test_patch_retry_is_bounded():
    api = client([record({"description": "Before"}, '"v1"'), FakeResponse({}, status_code=412), record({"description": "Before"}, '"v2"'), FakeResponse({}, status_code=412)])
    api.get_collection("one")
    with pytest.raises(SiloHTTPError, match="412"):
        api.update_collection("one", {"description": "After"}, '"v1"')
    assert len(api.session.calls) == 4


def test_patch_refresh_requires_observed_etag():
    api = client([record({"description": "Before"}, '"v1"'), FakeResponse({}, status_code=412), FakeResponse({"description": "Before"})])
    api.get_collection("one")
    with pytest.raises(SiloHTTPError, match="412"):
        api.update_collection("one", {"description": "After"}, '"v1"')
    assert len(api.session.calls) == 3
