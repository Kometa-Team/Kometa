import importlib
import sys
import types
from types import SimpleNamespace


class FakeLogger:
    def __init__(self):
        self.warning_messages = []

    def warning(self, message):
        self.warning_messages.append(str(message))

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def _load_plex(monkeypatch):
    monkeypatch.delitem(sys.modules, "modules.plex", raising=False)
    monkeypatch.delitem(sys.modules, "modules.builder", raising=False)
    monkeypatch.delitem(sys.modules, "modules.util", raising=False)
    monkeypatch.delitem(sys.modules, "modules.library", raising=False)
    monkeypatch.delitem(sys.modules, "modules.poster", raising=False)
    monkeypatch.delitem(sys.modules, "modules.request", raising=False)

    fake_builder = types.ModuleType("modules.builder")
    fake_builder.date_attributes = set()
    fake_builder.date_filters = set()
    fake_builder.string_filters = set()
    fake_builder.boolean_filters = set()
    fake_builder.number_filters = set()
    monkeypatch.setitem(sys.modules, "modules.builder", fake_builder)

    fake_util = types.ModuleType("modules.util")
    fake_util.logger = FakeLogger()
    fake_util.Failed = Exception
    monkeypatch.setitem(sys.modules, "modules.util", fake_util)

    fake_library = types.ModuleType("modules.library")
    fake_library.Library = type("Library", (), {})
    monkeypatch.setitem(sys.modules, "modules.library", fake_library)

    fake_poster = types.ModuleType("modules.poster")
    fake_poster.ImageData = object
    monkeypatch.setitem(sys.modules, "modules.poster", fake_poster)

    fake_request = types.ModuleType("modules.request")
    from urllib.parse import parse_qs, quote_plus, urlparse

    fake_request.parse_qs = parse_qs
    fake_request.quote_plus = quote_plus
    fake_request.urlparse = urlparse
    monkeypatch.setitem(sys.modules, "modules.request", fake_request)

    fake_tenacity = types.ModuleType("tenacity")

    def _identity(value=None, **_kwargs):
        return value

    def retry(*_args, **_kwargs):
        def decorator(func):
            return func

        return decorator

    fake_tenacity.retry = retry
    fake_tenacity.retry_if_not_exception_type = _identity
    fake_tenacity.stop_after_attempt = _identity
    fake_tenacity.wait_fixed = _identity
    monkeypatch.setitem(sys.modules, "tenacity", fake_tenacity)

    plex_module = importlib.import_module("modules.plex")
    return plex_module


def test_get_collection_falls_back_to_full_collection_inventory_when_search_misses(monkeypatch):
    plex_module = _load_plex(monkeypatch)
    logger = FakeLogger()
    monkeypatch.setattr(plex_module, "logger", logger)
    plex = plex_module.Plex.__new__(plex_module.Plex)
    hidden_collection = SimpleNamespace(title="Hidden Collection")
    search_calls = []
    inventory_calls = []

    def search(*args, **kwargs):
        search_calls.append((args, kwargs))
        return []

    def get_all_collections(label=None):
        inventory_calls.append(label)
        return [hidden_collection, SimpleNamespace(title="Other Collection")]

    plex.search = search
    plex.get_all_collections = get_all_collections

    assert plex.get_collection("Hidden Collection", force_search=True) is hidden_collection
    assert len(search_calls) == 1
    assert inventory_calls == [None]


def test_get_collection_warns_when_inventory_has_duplicate_exact_matches(monkeypatch):
    plex_module = _load_plex(monkeypatch)
    logger = FakeLogger()
    monkeypatch.setattr(plex_module, "logger", logger)
    plex = plex_module.Plex.__new__(plex_module.Plex)
    first = SimpleNamespace(title="Duplicate Collection")
    second = SimpleNamespace(title="Duplicate Collection")

    plex.search = lambda *args, **kwargs: []
    plex.get_all_collections = lambda label=None: [first, second]

    assert plex.get_collection("Duplicate Collection", force_search=True) is first
    assert any("Multiple collections found with title 'Duplicate Collection'" in msg for msg in logger.warning_messages)


def test_create_blank_collection_skips_create_when_collection_already_exists(monkeypatch):
    plex_module = _load_plex(monkeypatch)
    logger = FakeLogger()
    monkeypatch.setattr(plex_module, "logger", logger)
    plex = plex_module.Plex.__new__(plex_module.Plex)
    existing_collection = SimpleNamespace(title="Existing Collection")
    query_calls = []

    plex.get_collection = lambda *args, **kwargs: existing_collection
    plex._query = lambda *args, **kwargs: query_calls.append((args, kwargs))
    plex.is_movie = True
    plex.is_show = False
    plex.Plex = SimpleNamespace(key=1)
    plex.PlexServer = SimpleNamespace(_uriRoot=lambda: "http://plex")

    assert plex.create_blank_collection("Existing Collection") is existing_collection
    assert query_calls == []
    assert any("already exists; skipping creation" in msg for msg in logger.warning_messages)


def test_create_smart_collection_skips_create_when_collection_already_exists(monkeypatch):
    plex_module = _load_plex(monkeypatch)
    logger = FakeLogger()
    monkeypatch.setattr(plex_module, "logger", logger)
    plex = plex_module.Plex.__new__(plex_module.Plex)
    existing_collection = SimpleNamespace(title="Existing Collection")
    query_calls = []
    test_calls = []

    plex.get_collection = lambda *args, **kwargs: existing_collection
    plex._query = lambda *args, **kwargs: query_calls.append((args, kwargs))
    plex.test_smart_filter = lambda uri_args: test_calls.append(uri_args)
    plex.build_smart_filter = lambda uri_args: f"smart://{uri_args}"
    plex.Plex = SimpleNamespace(key=1)

    assert plex.create_smart_collection("Existing Collection", 1, "key=value", ignore_blank_results=False) is existing_collection
    assert query_calls == []
    assert test_calls == []
    assert any("already exists; skipping creation" in msg for msg in logger.warning_messages)
