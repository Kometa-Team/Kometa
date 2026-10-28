from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401
from modules.builder import CollectionBuilder
from modules.media_server import PlexMediaServer
from modules.mediabrowser import EmbyMediaServer, JellyfinMediaServer
from modules.silo import SiloMediaServer
from modules.tautulli import Tautulli, require_plex, supports_library
from modules.util import Failed


@pytest.mark.parametrize("server_class", [SiloMediaServer, JellyfinMediaServer, EmbyMediaServer])
def test_non_plex_tautulli_rejected_before_requests(server_class):
    library = SimpleNamespace(server=server_class(url="http://server", token="token", name="Target"))
    requests = MagicMock()
    assert not supports_library(library)
    with pytest.raises(Failed, match="only supports Plex libraries"):
        Tautulli(requests, library, {})
    requests.assert_not_called()
    assert requests.mock_calls == []
    tautulli = Tautulli.__new__(Tautulli)
    tautulli.library = library
    with pytest.raises(Failed, match="only supports Plex libraries"):
        tautulli.get_rating_keys({}, False)


@pytest.mark.parametrize("method", ["tautulli_popular", "tautulli_top", "tautulli_watched"])
def test_non_plex_builder_guard_precedes_parameter_parsing(method):
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.library = SimpleNamespace(server=SiloMediaServer(url="http://server", token="token"))
    with pytest.raises(Failed, match="only supports Plex libraries"):
        builder._tautulli(method, None)


def test_plex_and_legacy_libraries_remain_supported():
    for library in [SimpleNamespace(), SimpleNamespace(server=PlexMediaServer(url="http://plex", token="token"))]:
        assert supports_library(library)
        require_plex(library)
