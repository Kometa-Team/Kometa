"""Silo promotion rows keep acting-profile Home and shared defaults independent."""

from copy import deepcopy
from itertools import product
from types import SimpleNamespace

import pytest

import modules.builder  # noqa: F401 -- break circular imports
from modules.silo import SiloClient, SiloCollection, SiloHTTPError
from modules.silo_sections import CollectionVisibility
from modules.util import Failed
from tests.conftest import FakeLogger, FakeResponse
from tests.test_silo import FakeSession, _library, _server


class SectionClient:
    def __init__(self):
        self.server = SimpleNamespace(profile_id="acting")
        self.rows = []
        self.overrides = []
        self.calls = []
        self.etag = '"current"'
        self.error = None
        self.profile_reads = 0
        self.change_on_recheck = False

    def _items(self, method, path, params=None):
        self.calls.append((method, path, deepcopy(params), None, None))
        if path == "/admin/sections":
            return deepcopy([row for row in self.rows if row["scope"] == params["scope"] and row.get("library_id") == params.get("library_id")])
        assert path == "/profile/sections" and params == {"scope": "home"}
        self.profile_reads += 1
        if self.change_on_recheck and self.profile_reads == 2:
            self.overrides.append({"id": "concurrent", "hidden": True})
        return deepcopy(self.overrides)

    def request(self, method, path, params=None, json_body=None, headers=None):
        self.calls.append((method, path, deepcopy(params), deepcopy(json_body), headers))
        if method == "GET" and path in ("/admin/sections", "/profile/sections"):
            return {"items": self._items(method, path, params)}, {}
        if method == "POST":
            row = {"id": str(len(self.rows) + 1), **deepcopy(json_body)}
            self.rows.append(row)
            return deepcopy(row), {}
        if method == "PUT":
            assert path == "/profile/sections" and params == {"scope": "home"}
            self.overrides = deepcopy(json_body["overrides"])
            return None, {}
        row = next(row for row in self.rows if path == f"/admin/sections/{row['id']}")
        if method == "GET":
            return deepcopy(row), {"ETag": self.etag} if self.etag else {}
        assert method == "PATCH" and headers == {"If-Match": self.etag}
        if self.error:
            raise self.error
        row.update(json_body)
        return deepcopy(row), {}

    @property
    def writes(self):
        return [call for call in self.calls if call[0] != "GET"]


@pytest.fixture
def visibility():
    client = SectionClient()
    return CollectionVisibility(client, "library-1"), client, SimpleNamespace(id="collection-1", title="Example")


def effective(client):
    library = any(row["scope"] == "library" and row["enabled"] for row in client.rows)
    shared = any(row["scope"] == "home" and row["enabled"] for row in client.rows)
    personal = any(row.get("is_user_added") and not row.get("hidden") and not row.get("removed") for row in client.overrides)
    home = personal or any(row["scope"] == "home" and row["enabled"] and not any(value.get("section_id") == row["id"] and (value.get("hidden") or value.get("removed")) for value in client.overrides) for row in client.rows)
    return library, home, shared


@pytest.mark.parametrize("flags", list(product((False, True), repeat=3)))
def test_flags_are_independent_and_repeated_runs_do_not_write(visibility, flags):
    service, client, collection = visibility
    details = dict(zip(("visible_library", "visible_home", "visible_shared"), flags))
    assert service.update(collection, details) is any(flags)
    assert effective(client) == flags
    assert all(row["config"] == {"library_collection_id": collection.id} for row in client.rows)
    assert all(row.get("library_id") == "library-1" for row in client.rows if row["scope"] == "library")
    client.calls.clear()
    assert service.update(collection, details) is False
    assert not client.writes
    assert not any(call[1].startswith("/users") or call[1].startswith("/profiles") for call in client.calls)


@pytest.mark.parametrize("initial", list(product((False, True), repeat=2)))
@pytest.mark.parametrize("key,value", list(product(("visible_home", "visible_shared"), (False, True))))
def test_changing_one_home_flag_preserves_the_other(visibility, initial, key, value):
    service, client, collection = visibility
    service.update(collection, dict(zip(("visible_home", "visible_shared"), initial)))
    service.update(collection, {key: value})
    expected = dict(zip(("visible_home", "visible_shared"), initial))
    expected[key] = value
    assert effective(client)[1:] == (expected["visible_home"], expected["visible_shared"])
    client.calls.clear()
    assert service.update(collection, {key: value}) is False
    assert not client.writes


def test_existing_rows_reuse_ids_and_preserve_profile_customizations(visibility):
    service, client, collection = visibility
    service.update(collection, {"visible_home": True, "visible_shared": True})
    row = client.rows[0]
    row.update({"position": 8, "item_limit": 42, "featured": True})
    unrelated = {"id": "other", "section_id": "resume", "hidden": True, "position": 0, "config": {}, "created_at": "read-only"}
    custom = {"id": "ours", "section_id": row["id"], "position": 3, "title": "My heading", "config": {}, "hidden": False}
    client.overrides = [unrelated, custom]
    service.update(collection, {"visible_home": False})
    assert client.overrides[0] == {key: value for key, value in unrelated.items() if key != "created_at"}
    assert client.overrides[1] == {**custom, "hidden": True}
    assert row["position"] == 8 and row["item_limit"] == 42 and row["featured"] is True
    assert row["enabled"] is True  # Other profiles still inherit the shared row.
    assert len(client.rows) == 1


@pytest.mark.parametrize("scope", ["home", "library"])
def test_duplicate_collection_rows_fail_without_writes(visibility, scope):
    service, client, collection = visibility
    row = {"id": "1", "scope": scope, "section_type": "collection", "config": {"library_collection_id": collection.id}, "enabled": True}
    if scope == "library":
        row["library_id"] = "library-1"
    client.rows = [row, {**row, "id": "2"}]
    with pytest.raises(Failed, match="multiple"):
        service.update(collection, {"visible_shared" if scope == "home" else "visible_library": False})
    assert not client.writes


def test_missing_validator_never_overwrites_admin_section(visibility):
    service, client, collection = visibility
    service.update(collection, {"visible_library": True})
    client.calls.clear()
    client.etag = None
    with pytest.raises(Failed, match="no ETag"):
        service.update(collection, {"visible_library": False})
    assert not client.writes


@pytest.mark.parametrize("status", [409, 412])
def test_concurrent_admin_change_propagates_without_stale_retry(visibility, status):
    service, client, collection = visibility
    service.update(collection, {"visible_library": True})
    client.calls.clear()
    client.error = SiloHTTPError("changed", status)
    with pytest.raises(SiloHTTPError, match="changed"):
        service.update(collection, {"visible_library": False})
    assert len(client.writes) == 1


def test_profile_change_during_read_is_not_overwritten(visibility):
    service, client, collection = visibility
    client.change_on_recheck = True
    with pytest.raises(Failed, match="Profile Home sections changed"):
        service.update(collection, {"visible_home": True})
    assert not client.writes
    assert client.overrides == [{"id": "concurrent", "hidden": True}]


def test_omitted_flags_do_not_read_or_write_sections(visibility):
    service, client, collection = visibility
    assert service.update(collection, {}) is False
    assert not client.calls


def test_collection_metadata_routes_promotion_through_native_api(monkeypatch):
    from modules import silo

    logger = FakeLogger()
    monkeypatch.setattr(silo, "logger", logger)
    record = {"id": "col-1", "title": "Example"}
    section = {"id": "row-1", "scope": "library", "section_type": "collection", "enabled": True, "title": "Example", "config": {"library_collection_id": "col-1"}}
    session = FakeSession([FakeResponse(record), FakeResponse({"items": []}), FakeResponse(section)])
    library = _library(SiloClient(_server(pace_requests=False), session=session))
    assert library.update_collection_details(SiloCollection(record), None, {"visible_library": True}) == ["Visibility"]
    assert session.calls[-1]["method"] == "POST"
    assert session.calls[-1]["url"].endswith("/admin/sections")
    assert session.calls[-1]["json"]["library_id"] == str(library.library_id)
    assert session.calls[-1]["profile"] == "profile"
    assert not logger.warning_messages and not logger.error_messages


@pytest.mark.parametrize("payload", [None, {}, {"items": None}, {"items": ["invalid"]}, {"items": [], "page": {"has_more": True}}])
@pytest.mark.parametrize("profile", [False, True])
def test_incomplete_layouts_are_not_replaced(payload, profile):
    responses = [FakeResponse({"items": []})] if profile else []
    session = FakeSession([*responses, FakeResponse(payload)])
    client = SiloClient(_server(pace_requests=False), session=session)
    with pytest.raises(Failed, match="Incomplete section list"):
        CollectionVisibility(client, "library-1").update(SimpleNamespace(id="col-1", title="Example"), {"visible_home": True})
    assert all(call["method"] == "GET" for call in session.calls)


def test_unknown_profile_fields_are_not_silently_dropped(visibility):
    service, client, collection = visibility
    client.overrides = [{"id": "future", "new_server_option": True}]
    with pytest.raises(Failed, match="Unrecognized profile section fields"):
        service.update(collection, {"visible_home": True})
    assert not client.writes


def test_profile_override_limit_is_checked_before_replacement(visibility):
    service, client, collection = visibility
    client.overrides = [{"id": str(index), "hidden": True} for index in range(500)]
    with pytest.raises(Failed, match="too many section overrides"):
        service.update(collection, {"visible_home": True})
    assert not client.writes


def test_renamed_collection_updates_its_existing_row(visibility):
    service, client, collection = visibility
    service.update(collection, {"visible_library": True})
    collection.title = "New title"
    service.update(collection, {"visible_library": True})
    assert len(client.rows) == 1 and client.rows[0]["title"] == "New title"


@pytest.mark.parametrize("active", [False, True])
@pytest.mark.parametrize("flag", ["visible_library", "visible_home", "visible_shared"])
def test_scheduled_visibility_reaches_silo_as_a_boolean(monkeypatch, visibility, flag, active):
    from datetime import datetime

    from modules import builder as builder_module
    from modules.util import NotScheduled
    from tests.factories import make_builder

    def schedule_check(*args, **kwargs):
        if not active:
            raise NotScheduled("Outside schedule")

    monkeypatch.setattr(builder_module.util, "schedule_check", schedule_check)
    builder = make_builder(details={}, current_time=datetime(2026, 1, 1), config=SimpleNamespace(run_hour=0))
    builder._details(flag, "range(12/01-12/31)", flag, {flag: flag})
    assert builder.details[flag] is active
    service, client, collection = visibility
    service.update(collection, builder.details)
    assert effective(client)[("visible_library", "visible_home", "visible_shared").index(flag)] is active


def test_personal_row_identifiers_are_distinct_between_profiles(visibility):
    service, client, collection = visibility
    first = service._personal_id(collection)
    client.server.profile_id = "another-profile"
    assert service._personal_id(collection) != first


def test_implicit_primary_profile_uses_the_same_identifier_as_explicit_selection():
    session = FakeSession([FakeResponse({"items": [{"id": "parent", "is_primary": True}]})])
    client = SiloClient(_server(profile_id=None, pace_requests=False), session=session)
    service = CollectionVisibility(client, "library-1")
    collection = SimpleNamespace(id="col-1")
    implicit = service._personal_id(collection)
    assert service._personal_id(collection) == implicit
    assert len(session.calls) == 1
    client.server.profile_id = "parent"
    assert service._personal_id(collection) == implicit
