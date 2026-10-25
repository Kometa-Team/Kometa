"""Capability matrix and Plex media server object."""

from types import SimpleNamespace

import modules.builder  # noqa: F401 — pre-import to break circular deps
from modules.library import Library
from modules.media_server import CAPABILITY_INFO, PLEX_CAPABILITIES, Capability, CapabilityMatrix, CapabilityStatus, MediaServer, PlexMediaServer, Support, media_server_class
from modules.util import Failed
from tests.factories import make_plex, make_plex_item


def test_capability_catalog_matches_the_feature_matrix():
    assert set(CAPABILITY_INFO) == set(Capability)
    assert len(Capability) == 71
    assert Capability.CREATE_COLLECTION.label == "Create basic collection"
    assert Capability.CREATE_COLLECTION.section == "A1. Create Collection"
    assert Capability.GET_PROVIDER_IDS.label == "Get provider IDs (TMDb, IMDb, etc)"
    assert Capability.GET_PROVIDER_IDS.section == "H3. ID Resolution"
    labels = [capability.label for capability in Capability]
    assert labels.count("Remove items from collection") == 2
    assert {capability.section.split(".", 1)[0] for capability in Capability} == {f"{letter}{number}" for letter, count in [("A", 4), ("B", 3), ("C", 3), ("D", 3), ("E", 3), ("F", 2), ("G", 1), ("H", 3)] for number in range(1, count + 1)}


def test_plex_matrix_is_full_except_the_smart_collection_workaround():
    for capability in Capability:
        status = PLEX_CAPABILITIES.get(capability)
        if capability is Capability.SMART_COLLECTION_WORKAROUND:
            assert status.support is Support.NONE
            assert status.supported is False
            assert "native smart collections" in status.detail
        else:
            assert status.support is Support.FULL
            assert status.supported is True
    assert PLEX_CAPABILITIES.get(Capability.TEST_FILTER).detail == "preview"
    assert PLEX_CAPABILITIES.supports(Capability.CREATE_COLLECTION)
    assert not PLEX_CAPABILITIES.supports(Capability.SMART_COLLECTION_WORKAROUND)


def test_matrix_must_declare_every_capability():
    try:
        CapabilityMatrix({Capability.CREATE_COLLECTION: CapabilityStatus(Support.FULL)})
    except ValueError as error:
        assert "missing" in str(error)
        assert "create_collection" not in str(error)
    else:
        raise AssertionError("incomplete matrix was accepted")

    declared = {capability: CapabilityStatus(Support.FULL) for capability in Capability}
    declared["upload_poster"] = CapabilityStatus(Support.FULL)
    try:
        CapabilityMatrix(declared)
    except ValueError as error:
        assert "unknown" in str(error)
    else:
        raise AssertionError("unknown capability was accepted")


def test_plex_server_reads_the_resolved_plex_block_without_connecting():
    server = PlexMediaServer.from_config(
        {
            "url": "http://192.168.1.12:32400",
            "token": "secret",
            "timeout": 30,
            "verify_ssl": False,
            "db_cache": 40,
        },
        name="Home",
    )

    assert server.type_name == "plex"
    assert server.display_name == "Home"
    assert server.url == "http://192.168.1.12:32400"
    assert server.token == "secret"
    assert server.timeout == 30
    assert server.verify_ssl is False
    assert server.db_cache == 40
    assert server.capabilities is PLEX_CAPABILITIES
    assert media_server_class("plex") is PlexMediaServer
    assert media_server_class("Plex") is PlexMediaServer

    minimal = PlexMediaServer.from_config({"url": "http://plex", "token": "token"})
    assert minimal.display_name == "Plex"
    assert minimal.timeout == 60
    assert minimal.verify_ssl is None
    assert minimal.db_cache is None


def test_require_rejects_unsupported_capabilities_and_returns_partial_limits():
    class Shelf(MediaServer):
        type_name = "silo"
        type_label = "Silo"

        def __init__(self):
            super().__init__(url="http://silo", token="token", name="Shelf")

        @property
        def capabilities(self):
            declared = {capability: CapabilityStatus(Support.NONE) for capability in Capability}
            declared[Capability.CREATE_COLLECTION] = CapabilityStatus(Support.FULL)
            declared[Capability.UPLOAD_POSTER] = CapabilityStatus(Support.PARTIAL, "Sidecar file")
            return CapabilityMatrix(declared)

    server = Shelf()
    assert server.supports(Capability.CREATE_COLLECTION)
    assert server.require(Capability.CREATE_COLLECTION).support is Support.FULL
    assert server.supports(Capability.UPLOAD_POSTER)
    assert server.require(Capability.UPLOAD_POSTER).detail == "Sidecar file"
    assert not server.supports(Capability.DELETE_ITEM)
    try:
        server.require(Capability.DELETE_ITEM)
    except Failed as error:
        assert str(error) == "Shelf does not support Delete item from library"
    else:
        raise AssertionError("unsupported capability was allowed")

    plex = PlexMediaServer.from_config({"url": "http://plex", "token": "token"})
    try:
        plex.require(Capability.SMART_COLLECTION_WORKAROUND)
    except Failed as error:
        assert str(error) == "Plex does not support Smart collection workaround (Not applicable. Plex creates native smart collections.)"
    else:
        raise AssertionError("Plex smart-collection workaround was allowed")

    try:
        media_server_class("emby")
    except Failed as error:
        assert "not supported" in str(error)
        assert "plex" in str(error)
    else:
        raise AssertionError("unregistered server type was accepted")


def test_library_queries_its_server():
    library = SimpleNamespace(server=None)
    assert Library.supports(library, Capability.CREATE_COLLECTION) is False
    try:
        Library.require(library, Capability.CREATE_COLLECTION)
    except Failed as error:
        assert str(error) == "Media server is not configured for this library"
    else:
        raise AssertionError("missing server was allowed")

    library.server = PlexMediaServer.from_config({"url": "http://plex", "token": "token"})
    assert Library.supports(library, Capability.DELETE_COLLECTION)
    Library.require(library, Capability.DELETE_COLLECTION)


def test_plex_operation_stops_before_the_backend_call_when_unsupported():
    class NoCollections(PlexMediaServer):
        @property
        def capabilities(self):
            declared = {capability: CapabilityStatus(Support.FULL) for capability in Capability}
            declared[Capability.DELETE_COLLECTION] = CapabilityStatus(Support.NONE)
            return CapabilityMatrix(declared)

    plex = make_plex(server=NoCollections(url="http://plex", token="token", name="Home"))
    item = make_plex_item()
    try:
        plex.delete_collection(item)
    except Failed as error:
        assert str(error) == "Home does not support Delete collection"
    else:
        raise AssertionError("delete continued without collection support")
    item.delete.assert_not_called()
