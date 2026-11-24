"""Silo shelves preserve existing collections and guard every membership write."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from ruamel.yaml import YAML

import modules.builder  # noqa: F401 - break circular imports
from modules.meta import DataFile, MetadataFile
from modules.silo import SiloClient, SiloCollection
from modules.util import BuilderValidationError, Failed
from tests.conftest import FakeLogger, FakeRequests, FakeResponse
from tests.factories import make_builder
from tests.test_meta import make_datafile
from tests.test_silo import FakeSession, _library, _server


@pytest.fixture(autouse=True)
def loggers(monkeypatch):
    monkeypatch.setattr("modules.builder.logger", FakeLogger())
    monkeypatch.setattr("modules.silo.logger", FakeLogger())


def client(responses):
    return SiloClient(_server(pace_requests=False), session=FakeSession(responses))


@pytest.mark.parametrize("existing", [False, True])
def test_shelf_assignment_creates_or_reuses_regular_shelf(existing):
    record = {"id": "ours", "title": "Family Favorites"}
    shelf = {"id": "family", "name": "Family Movie Night", "kind": "regular"}
    responses = [FakeResponse(record), FakeResponse({"items": [shelf] if existing else []})]
    if not existing:
        responses.append(FakeResponse(shelf, status_code=201))
    responses += [FakeResponse({"ordered_ids": ["manual-collection"]}, headers={"ETag": '"shelf-v1"'}), FakeResponse({}, status_code=200)]
    responses += [FakeResponse({"ordered_ids": ["family", "ungrouped"]}), FakeResponse({"items": [shelf]})]
    api = client(responses)
    library = _library(api)
    library.original_mapping_name = "Movies@my-silo"
    assert library.update_collection_details(SiloCollection(record), None, {"silo_shelf": "Family Movie Night"}) == ["Shelf"]
    call = next(call for call in api.session.calls if call["method"] == "PUT")
    assert call["json"] == {"ordered_ids": ["manual-collection", "ours"]}
    assert call["headers"] == {"If-Match": '"shelf-v1"'}
    assert call["params"] == {"library_id": "lib-1", "move_omitted": "reject"}
    if not existing:
        assert api.session.calls[2]["json"] == {"name": "Family Movie Night", "default_sort_mode": "name_asc"}


def test_shelf_repeat_is_read_only():
    api = client([FakeResponse({"ordered_ids": ["ours", "manual-collection"]})])
    assert api.place_on_shelf("lib-1", "family", "ours") is False
    assert len(api.session.calls) == 1


@pytest.mark.parametrize("order,headers", [({"ordered_ids": []}, {}), ({"ordered_ids": [], "has_more": True}, {"ETag": '"v1"'}), ({}, {"ETag": '"v1"'})])
def test_incomplete_or_unguarded_shelf_order_refuses_write(order, headers):
    api = client([FakeResponse(order, headers=headers)])
    with pytest.raises(Failed):
        api.place_on_shelf("lib-1", "family", "ours")
    assert len(api.session.calls) == 1


def test_stale_shelf_revision_is_not_replayed():
    api = client([FakeResponse({"ordered_ids": []}, headers={"ETag": '"v1"'}), FakeResponse({}, status_code=412)])
    with pytest.raises(Failed, match="412"):
        api.place_on_shelf("lib-1", "family", "ours")
    assert len(api.session.calls) == 2


@pytest.mark.parametrize("shelves", [[{"id": "reserved", "name": "Family", "kind": "user_collections"}], [{"id": "one", "name": "Family", "kind": "regular"}, {"id": "two", "name": "family", "kind": "regular"}]])
def test_reserved_or_ambiguous_shelf_does_not_move_collections(shelves):
    api = client([FakeResponse({"id": "ours"}), FakeResponse({"items": shelves})])
    library = _library(api)
    with pytest.raises(Failed, match="ambiguous or reserved"):
        library.update_collection_details(SiloCollection({"id": "ours"}), None, {"silo_shelf": "Family"})
    assert len(api.session.calls) == 2


@pytest.mark.parametrize("value", [None, "", "  ", False, [], {}])
def test_shelf_requires_nonempty_string(value):
    builder = make_builder(library=SimpleNamespace(server=_server()), overlay=None)
    with pytest.raises(BuilderValidationError, match="nonempty string"):
        builder._details("silo_shelf", value, "silo_shelf", {})


@pytest.mark.parametrize("kind", ["plex", "silo", "jellyfin", "emby"])
def test_explicit_shelf_is_only_applied_to_silo(kind):
    builder = make_builder(library=SimpleNamespace(server=SimpleNamespace(type_name=kind)), overlay=None)
    builder._details("silo_shelf", " Family ", "silo_shelf", {})
    assert builder.details.get("silo_shelf") == ("Family" if kind == "silo" else None)


@pytest.mark.parametrize("enabled,kind", [(True, "silo"), (False, "silo"), (True, "plex")])
def test_default_shelf_uses_resolved_separator_name_even_when_separator_disabled(enabled, kind):
    root = Path(__file__).resolve().parents[1]
    templates = YAML(typ="safe").load((root / "defaults/templates.yml").read_text())["templates"]
    metadata = make_datafile(library=SimpleNamespace(silo_shelves=enabled, server=SimpleNamespace(type_name=kind), type="Movie", name="Movies"), templates={"separator": (templates["separator"], {})}, temp_vars={"use_separator": False})
    data = {"collections": {"Genre Collections": {"template": {"name": "separator", "separator": "genre"}, "name": "Genres"}}}
    assert MetadataFile._silo_default_shelf(metadata, data) == ("Genres" if enabled and kind == "silo" else None)


@pytest.mark.parametrize("explicit", [True, False])
def test_collection_template_overrides_automatic_shelf(explicit):
    metadata = make_datafile(templates={"custom": ({"silo_shelf": "Custom"} if explicit else {}, {})})
    data = metadata.apply_template(None, "Test", {}, {"name": "custom"}, {})
    builder = make_builder(metadata=SimpleNamespace(silo_default_shelf="Automatic"), data=data, overlay=None)
    methods = {key: key for key in data}
    builder._inherit_silo_shelf(methods)
    assert data["silo_shelf"] == ("Custom" if explicit else "Automatic")


def test_automatic_shelf_survives_disabled_heading_in_real_metadata_file(monkeypatch):
    root = Path(__file__).parent / "fixtures/multi_server"
    data = YAML(typ="safe").load((root / "shelves-default.yml").read_text())
    monkeypatch.setattr(DataFile, "load_file", lambda *args, **kwargs: data)
    library = SimpleNamespace(server=_server(), silo_shelves=True, name="Movies", type="Movie", is_music=False, collections=[], metadatas=[])
    config = SimpleNamespace(GitHub=SimpleNamespace(configs_url="", translation_keys=["en"]), requested_files=[], playlist_names=[])
    metadata = MetadataFile(config, library, "File", "shelves.yml", {}, None, "collection")
    assert metadata.silo_default_shelf == "Kometa Multi-Server Validation Shelf"
    assert list(metadata.collections) == ["Kometa Multi-Server Shelf Automatic"]


def test_multiple_automatic_headings_require_explicit_assignment():
    metadata = make_datafile(library=SimpleNamespace(silo_shelves=True, server=_server(), name="Movies", type="Movie"), templates={"separator": ({"run_definition": False}, {})})
    data = {"collections": {name: {"template": {"name": "separator"}} for name in ("Genres", "Studios")}}
    with pytest.raises(Failed, match="one separator"):
        MetadataFile._silo_default_shelf(metadata, data)


@pytest.mark.parametrize("override,expected", [(None, 60), ("020", 20), (100, 100)])
def test_shelf_section_resolves_defaults_and_config_overrides(override, expected):
    root = Path(__file__).resolve().parents[1]
    templates = YAML(typ="safe").load((root / "defaults/templates.yml").read_text())["templates"]
    metadata = make_datafile(
        library=SimpleNamespace(silo_shelves=True, server=_server(), type="Movie", name="Movies"),
        templates={"separator": (templates["separator"], {"collection_section": "060"})},
        temp_vars={"use_separator": False, **({"collection_section": override} if override is not None else {})},
    )
    data = {"collections": {"Genres": {"template": {"name": "separator", "separator": "genre"}}}}
    assert MetadataFile._silo_default_shelf(metadata, data) == "Genres"
    assert metadata.silo_default_shelf_section == expected
    builder = make_builder(library=SimpleNamespace(server=_server()), metadata=metadata, overlay=None)
    builder._details("silo_shelf", "Genres", "silo_shelf", {})
    assert builder.details["_silo_shelf_section"] == expected


@pytest.mark.parametrize("section", [True, -1, "alphabetical", 1.5])
def test_invalid_shelf_section_is_rejected(section):
    metadata = make_datafile(library=SimpleNamespace(silo_shelves=True, server=_server(), name="Movies", type="Movie"), templates={"separator": ({"default": {"collection_section": section}}, {})})
    with pytest.raises(Failed, match="nonnegative integer"):
        MetadataFile._silo_default_shelf(metadata, {"collections": {"Genres": {"template": {"name": "separator"}}}})


def test_shelf_sections_move_to_top_followed_by_alphabetical_shelves():
    ids = ["later", "manual", "ungrouped", "earlier", "tied"]
    api = client([FakeResponse({"ordered_ids": ids}, headers={"ETag": '"groups-v1"'}), FakeResponse({"items": [{"id": "manual", "name": "Zebra"}]}), FakeResponse({})])
    assert api.order_shelves("lib-1", {"later": 100, "earlier": 20, "tied": 20}) is True
    call = api.session.calls[-1]
    assert call["json"] == {"ordered_ids": ["earlier", "tied", "later", "ungrouped", "manual"]}
    assert call["headers"] == {"If-Match": '"groups-v1"'}
    assert call["url"].endswith("/admin/libraries/lib-1/collection-groups/order")


def test_shelf_section_order_is_idempotent():
    api = client([FakeResponse({"ordered_ids": ["earlier", "later", "ungrouped"]})])
    assert api.order_shelves("lib-1", {"later": 100, "earlier": 20}) is False
    assert len(api.session.calls) == 1


@pytest.mark.parametrize("order,headers", [({"ordered_ids": ["later", "earlier"]}, {}), ({"ordered_ids": [], "has_more": True}, {"ETag": '"v1"'}), ({}, {"ETag": '"v1"'}), ({"ordered_ids": ["ungrouped", "earlier"]}, {"ETag": '"v1"'})])
def test_missing_or_incomplete_shelf_order_refuses_reordering(order, headers):
    api = client([FakeResponse(order, headers=headers)])
    with pytest.raises(Failed):
        api.order_shelves("lib-1", {"later": 100, "earlier": 20})
    assert len(api.session.calls) == 1


def test_shelf_reorder_revision_conflict_is_not_retried():
    api = client([FakeResponse({"ordered_ids": ["later", "earlier", "ungrouped"]}, headers={"ETag": '"v1"'}), FakeResponse({}, status_code=412)])
    with pytest.raises(Failed, match="412"):
        api.order_shelves("lib-1", {"later": 100, "earlier": 20})
    assert len(api.session.calls) == 2


def test_library_orders_multiple_categories_even_when_membership_is_unchanged():
    shelves = [{"id": "late", "name": "Genres", "kind": "regular"}, {"id": "early", "name": "Charts", "kind": "regular"}, {"id": "manual", "name": "Manual", "kind": "regular"}]
    order = {"ordered_ids": ["late", "early", "manual", "ungrouped"]}
    responses = []
    for collection_id in ("one", "two"):
        responses.extend([FakeResponse({"id": collection_id}), FakeResponse({"items": shelves}), FakeResponse({"ordered_ids": [collection_id]}), FakeResponse(order, headers={"ETag": '"groups-v1"'}), FakeResponse({"items": shelves})])
    responses.append(FakeResponse({}))
    api = client(responses)
    library = _library(api)
    library.original_mapping_name = "Movies@my-silo"
    assert library.update_collection_details(SiloCollection({"id": "one"}), None, {"silo_shelf": "Genres", "_silo_shelf_section": 60}) == []
    assert library.update_collection_details(SiloCollection({"id": "two"}), None, {"silo_shelf": "Charts", "_silo_shelf_section": 20}) == ["Shelf"]
    assert api.session.calls[-1]["json"] == {"ordered_ids": ["early", "late", "manual", "ungrouped"]}


def test_one_category_moves_above_no_heading_and_manual_shelves():
    api = client([FakeResponse({"ordered_ids": ["ungrouped", "manual", "genres"]}, headers={"ETag": '"v1"'}), FakeResponse({"items": [{"id": "manual", "name": "Manual"}]}), FakeResponse({})])
    assert api.order_shelves("lib-1", {"genres": 60}) is True
    assert api.session.calls[-1]["json"] == {"ordered_ids": ["genres", "manual", "ungrouped"]}


def test_shelves_without_sections_sort_by_case_insensitive_display_name():
    shelves = [{"id": "z", "name": "Zebra"}, {"id": "a", "name": "alpha"}, {"id": "b", "name": "Beta"}]
    api = client([FakeResponse({"ordered_ids": ["z", "ungrouped", "b", "a"]}, headers={"ETag": '"v1"'}), FakeResponse({"items": shelves}), FakeResponse({})])
    assert api.order_shelves("lib-1", {}) is True
    assert api.session.calls[-1]["json"] == {"ordered_ids": ["a", "b", "ungrouped", "z"]}


def test_missing_shelf_name_refuses_order_write():
    api = client([FakeResponse({"ordered_ids": ["missing", "ungrouped"]}, headers={"ETag": '"v1"'}), FakeResponse({"items": []})])
    with pytest.raises(Failed, match="Shelf name missing"):
        api.order_shelves("lib-1", {})
    assert all(call["method"] == "GET" for call in api.session.calls)


AWARD_DEFAULTS = sorted(path.stem for path in (Path(__file__).resolve().parents[1] / "defaults/award").glob("*.yml") if path.stem != "separator_award")
CHART_DEFAULTS = sorted(path.stem for path in (Path(__file__).resolve().parents[1] / "defaults/chart").glob("*.yml") if path.stem != "separator_chart")


def default_metadata(default_name, *, enabled=True, kind="silo", temp_vars=None, library_type="Movie"):
    library = SimpleNamespace(silo_shelves=enabled, server=SimpleNamespace(type_name=kind), type=library_type, name="Movies")
    config = SimpleNamespace(Requests=FakeRequests())
    base = make_datafile(config=config, type="Default", path=default_name, library=library, temp_vars=temp_vars or {})
    metadata = MetadataFile.__new__(MetadataFile)
    vars(metadata).update(vars(base))
    data = metadata.load_file("Default", default_name)
    metadata.external_templates(data)
    return metadata, data


@pytest.mark.parametrize("name", AWARD_DEFAULTS)
def test_all_packaged_award_defaults_use_shared_award_shelf(name):
    metadata, data = default_metadata(name)
    metadata.silo_default_shelf = metadata._silo_default_shelf(data)
    assert metadata.silo_default_shelf == "Award Collections"
    assert metadata.silo_default_shelf_section == 130
    assert "Award Collections" not in (data.get("collections") or {})
    builder = make_builder(metadata=metadata, data={}, overlay=None)
    builder._inherit_silo_shelf({})
    assert builder.data["silo_shelf"] == "Award Collections"


@pytest.mark.parametrize("name", ["oscars", "award/oscars", "award/oscars.yml"])
def test_award_shelf_honors_name_and_section_overrides_without_separator_in_config(name):
    metadata, data = default_metadata(name, temp_vars={"use_separator": False, "collection_section": "090", "name_separator": "My Awards"})
    assert metadata._silo_default_shelf(data) == "My Awards"
    assert metadata.silo_default_shelf_section == 90


@pytest.mark.parametrize("enabled,kind", [(False, "silo"), (True, "plex"), (True, "emby"), (True, "jellyfin")])
def test_award_shelf_fallback_is_opt_in_and_silo_only(enabled, kind):
    metadata, data = default_metadata("oscars", enabled=enabled, kind=kind)
    assert metadata._silo_default_shelf(data) is None
    assert metadata.silo_default_shelf_section is None


def test_custom_file_with_award_name_is_not_automatically_grouped():
    metadata, data = default_metadata("oscars")
    metadata._default_collection_path = "/config/award/oscars.yml"
    assert metadata._silo_default_shelf(data) is None


def test_emmy_show_library_uses_same_award_shelf():
    metadata, data = default_metadata("emmy", library_type="Show")
    assert metadata._silo_default_shelf(data) == "Award Collections"
    assert metadata.silo_default_shelf_section == 130


@pytest.mark.parametrize("sections", [(140, 160), (160, 140)])
def test_matching_shelf_names_merge_different_sections_using_lowest_value(sections):
    api = MagicMock()
    api.get_collection.side_effect = [({"id": name, "title": name}, '"v1"') for name in ("one", "two", "three")]
    api.list_shelves.return_value = [{"id": "actors", "name": "Actors Collections", "kind": "regular"}]
    api.place_on_shelf.return_value = True
    observed = []
    api.order_shelves.side_effect = lambda library_id, values: observed.append(dict(values)) or False
    library = _library(api)
    library.original_mapping_name = "Movies@my-silo"
    for name, section in zip(("one", "two", "three"), (*sections, None)):
        details = {"silo_shelf": "actors collections"}
        if section is not None:
            details["_silo_shelf_section"] = section
        assert library.update_collection_details(SiloCollection({"id": name}), None, details) == ["Shelf"]
    assert observed == [{"actors": sections[0]}, {"actors": 140}, {"actors": 140}]
    assert [call.args for call in api.place_on_shelf.call_args_list] == [("lib-1", "actors", name) for name in ("one", "two", "three")]
    api.create_shelf.assert_not_called()


@pytest.mark.parametrize("name", CHART_DEFAULTS)
def test_all_packaged_chart_defaults_use_shared_chart_shelf(name):
    metadata, data = default_metadata(f"chart/{name}")
    metadata.silo_default_shelf = metadata._silo_default_shelf(data)
    assert metadata.silo_default_shelf == "Chart Collections"
    assert metadata.silo_default_shelf_section == (10 if name == "basic" else 20)
    builder = make_builder(metadata=metadata, data={}, overlay=None)
    builder._inherit_silo_shelf({})
    assert builder.data["silo_shelf"] == "Chart Collections"


@pytest.mark.parametrize("name", ["tmdb", "chart/tmdb", "chart/tmdb.yml"])
def test_chart_shelf_honors_name_and_section_overrides(name):
    metadata, data = default_metadata(name, temp_vars={"use_separator": False, "collection_section": "025", "name_separator": "My Charts"})
    assert metadata._silo_default_shelf(data) == "My Charts"
    assert metadata.silo_default_shelf_section == 25


@pytest.mark.parametrize("enabled,kind", [(False, "silo"), (True, "plex"), (True, "emby"), (True, "jellyfin")])
def test_chart_shelf_fallback_is_opt_in_and_silo_only(enabled, kind):
    metadata, data = default_metadata("chart/tmdb", enabled=enabled, kind=kind)
    assert metadata._silo_default_shelf(data) is None


def test_custom_file_with_chart_name_is_not_automatically_grouped():
    metadata, data = default_metadata("chart/tmdb")
    metadata._default_collection_path = "/config/chart/tmdb.yml"
    assert metadata._silo_default_shelf(data) is None
