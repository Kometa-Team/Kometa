"""Capability matrix, Plex media server object, and the credential scope of a server session."""

import base64
from types import SimpleNamespace

import pytest
import requests

import modules.builder  # noqa: F401 — pre-import to break circular deps
from modules.library import Library
from modules.media_server import CAPABILITY_INFO, PLEX_CAPABILITIES, Capability, CapabilityMatrix, CapabilityStatus, MediaServer, PlexMediaServer, ServerSession, Support, media_server_class
from modules.util import Failed
from tests.conftest import FakeLogger, recording_session
from tests.factories import make_plex, make_plex_item


def test_connection_logging_reports_remote_metadata_and_missing_values():
    from modules.media_server import log_server_connection
    from tests.conftest import FakeLogger

    server = PlexMediaServer("http://remote", "secret", name="Configured")
    logger = FakeLogger()
    log_server_connection(logger, server, lambda: {"name": "Remote", "version": "1.2", "os": "Linux", "os_version": "6.1"})
    assert logger.info_messages == ["Connected to server Remote version 1.2", "Running on Linux version 6.1"]
    logger = FakeLogger()
    log_server_connection(logger, server, lambda: {})
    assert logger.info_messages == ["Connected to server Configured version not reported", "Operating system: not reported"]


def test_connection_info_failure_does_not_prevent_connection():
    from modules.media_server import log_server_connection
    from tests.conftest import FakeLogger

    def load():
        raise Failed("Access denied")

    logger = FakeLogger()
    log_server_connection(logger, PlexMediaServer("http://remote", "secret", name="Configured"), load)
    assert logger.warning_messages
    assert "Connected to server Configured version not reported" in logger.info_messages


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
        media_server_class("kodi")
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


def test_server_session_sends_the_credential_only_to_the_server() -> None:
    session = ServerSession("HTTP://Media:8096/", "Jellyfin")
    session.headers["X-Emby-Token"] = "token"
    adapter = recording_session(session)
    for url in ("http://media:8096/System/Info", "https://images.example.invalid/poster.png", "http://media:8097/System/Info", "https://media:8096/System/Info", "http://media.evil.invalid/System/Info"):
        session.get(url)
    assert [request.headers.get("X-Emby-Token") for request in adapter.requests] == ["token", None, None, None, None]


def test_server_session_scopes_a_bearer_credential_to_the_server_origin() -> None:
    # A Silo poster sits outside the /api/v2 base path, so the rule is the origin and not the path.
    session = ServerSession("http://silo:8090/api/v2", "Silo")
    session.headers["Authorization"] = "Bearer token"
    adapter = recording_session(session)
    session.get("http://silo:8090/posters/movie-1.png")
    session.get("https://cdn.example.invalid/poster.png")
    assert [request.headers.get("Authorization") for request in adapter.requests] == ["Bearer token", None]


@pytest.mark.parametrize(
    "base,target,kept",
    [
        ("http://media:8096", "https://other.example.invalid/System/Info", False),
        ("http://media:8096", "https://media:8920/System/Info", False),
        ("http://media:8096", "http://media:8096/System/Info/", True),
        ("http://media", "https://media/System/Info", True),
    ],
)
def test_server_session_applies_the_redirect_rule_of_requests_to_each_credential_header(base: str, target: str, kept: bool) -> None:
    # requests drops Authorization on a redirect by itself. X-Emby-Token needs the same rule.
    session = ServerSession(base, "Emby")
    session.headers["X-Emby-Token"] = "token"
    adapter = recording_session(session, redirect=target)
    session.get(f"{base}/System/Info")
    assert [request.headers.get("X-Emby-Token") for request in adapter.requests] == ["token", "token" if kept else None]


def test_server_session_warns_once_when_the_server_redirects_off_its_origin(patch_util_logger: FakeLogger) -> None:
    session = ServerSession("http://media:8096", "Emby")
    session.headers["X-Emby-Token"] = "token"
    for _attempt in (1, 2):
        recording_session(session, redirect="https://media:8920/System/Info")
        session.get("http://media:8096/System/Info")
    assert len(patch_util_logger.warning_messages) == 1
    assert "https://media:8920" in patch_util_logger.warning_messages[0]


def test_server_session_does_not_warn_for_an_external_download_redirect(patch_util_logger: FakeLogger) -> None:
    session = ServerSession("http://media:8096", "Emby")
    session.headers["X-Emby-Token"] = "token"
    recording_session(session, redirect="https://cdn.example.invalid/poster.png")
    session.get("https://images.example.invalid/poster.png")
    assert patch_util_logger.warning_messages == []


def test_server_session_keeps_a_credential_that_the_caller_supplies() -> None:
    session = ServerSession("http://media:8096", "Jellyfin")
    session.headers["X-Emby-Token"] = "token"
    adapter = recording_session(session)
    session.get("https://images.example.invalid/poster.png", headers={"X-Emby-Token": "image host key"})
    assert adapter.requests[0].headers["X-Emby-Token"] == "image host key"


def test_server_session_keeps_the_credentials_of_the_server_url() -> None:
    # A reverse proxy can ask for HTTP basic authentication with user:password@ in the URL. requests turns that into Authorization.
    session = ServerSession("http://silo:8090/api/v2", "Silo")
    session.headers["Authorization"] = "Bearer token"
    adapter = recording_session(session)
    session.get("http://user:pass@silo:8090/api/v2/system/info")
    assert adapter.requests[0].headers["Authorization"] == "Basic " + base64.b64encode(b"user:pass").decode()


def test_server_session_normalizes_the_server_address() -> None:
    # The server address in the configuration can spell the host in Unicode or in punycode. Both compare equal.
    punycode = "média.test".encode("idna").decode()
    session = ServerSession(f"http://{punycode}:8096", "Jellyfin")
    session.headers["X-Emby-Token"] = "token"
    adapter = recording_session(session)
    session.get("http://média.test:8096/System/Info")
    session.get(f"http://{punycode}:8096/System/Info")
    session.get("http://other.test:8096/System/Info")
    assert [request.headers.get("X-Emby-Token") for request in adapter.requests] == ["token", "token", None]


def test_server_session_refuses_a_redirect_to_a_malformed_address() -> None:
    # A bad port in the redirect must fail like a bad URL, not with a ValueError that the clients do not catch.
    session = ServerSession("http://media:8096", "Emby")
    session.headers["X-Emby-Token"] = "token"
    adapter = recording_session(session, redirect="https://media:abc/System/Info")
    with pytest.raises(requests.exceptions.InvalidURL):
        session.get("http://media:8096/System/Info")
    assert len(adapter.requests) == 1


def test_server_session_warning_names_the_final_address(patch_util_logger: FakeLogger) -> None:
    # The user copies that address into url, so it keeps the path and brackets an IPv6 host.
    session = ServerSession("http://media:8080/jellyfin", "Jellyfin")
    session.headers["X-Emby-Token"] = "token"
    recording_session(session, redirect="https://media/jellyfin/System/Info")
    session.get("http://media:8080/jellyfin/System/Info")
    session = ServerSession("http://[::1]:8096", "Emby")
    session.headers["X-Emby-Token"] = "token"
    recording_session(session, redirect="https://[::1]:8920/System/Info")
    session.get("http://[::1]:8096/System/Info")
    assert "redirected a request to https://media/jellyfin/System/Info." in patch_util_logger.warning_messages[0]
    assert "redirected a request to https://[::1]:8920/System/Info." in patch_util_logger.warning_messages[1]


def test_server_session_does_not_warn_when_the_request_held_no_token(patch_util_logger: FakeLogger) -> None:
    # An external image can redirect to the server and away again. That chain never held the token.
    session = ServerSession("http://media:8096", "Emby")
    session.headers["X-Emby-Token"] = "token"
    adapter = recording_session(session, redirect=["http://media:8096/System/Info", "https://other.example.invalid/System/Info"])
    session.get("https://images.example.invalid/poster.png")
    assert patch_util_logger.warning_messages == []
    assert [request.headers.get("X-Emby-Token") for request in adapter.requests] == [None, None, None]


def test_server_session_scopes_a_header_added_after_construction() -> None:
    # No header names are listed, so a credential that a later change adds is scoped from its first commit.
    session = ServerSession("http://media:8096", "Jellyfin")
    session.headers["Accept"] = "application/json"
    session.headers["Authorization"] = 'MediaBrowser Token="token"'
    adapter = recording_session(session)
    session.get("http://media:8096/System/Info")
    session.get("https://images.example.invalid/poster.png")
    server, external = adapter.requests
    assert (server.headers["Authorization"], server.headers["Accept"]) == ('MediaBrowser Token="token"', "application/json")
    assert ("Authorization" not in external.headers, external.headers["Accept"]) == (True, "*/*")
