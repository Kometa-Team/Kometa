from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 - pre-import breaks circular imports
from modules import cache as cache_module
from modules import convert, library, meta
from tests.conftest import FakeLogger


@pytest.fixture
def adapter(monkeypatch, tmp_path):
    logger = FakeLogger()
    for module in [cache_module, convert, library, meta]:
        monkeypatch.setattr(module, "logger", logger)
    adapter = convert.Convert.__new__(convert.Convert)
    adapter.cache = cache_module.Cache(str(tmp_path / "config.yml"), 30)
    adapter.tmdb_to_tvdb = MagicMock(return_value=None)
    adapter.imdb_to_tmdb = MagicMock(return_value=(107124, "show"))
    return adapter


def show_item(*guids):
    return SimpleNamespace(guid="plex://show/5f2e583cb434b2004044d348", ratingKey=123, title="Animaniacs", guids=[SimpleNamespace(id=guid) for guid in guids])


def show_library(adapter):
    return SimpleNamespace(
        config=SimpleNamespace(Convert=adapter),
        is_movie=False,
        is_show=True,
        is_music=False,
        is_other=False,
        type="Show",
        movie_map={},
        movie_rating_key_map={},
        show_map={},
        show_rating_key_map={},
        imdb_map={},
        imdb_rating_key_map={},
        anidb_map={},
        mal_map={},
        plex_map_levels=set(),
        map_plex_ids=MagicMock(),
        cache_imdb_ratings=MagicMock(),
        cache_imdb_genres=MagicMock(),
    )


@pytest.mark.parametrize("use_cache", [True, False])
@pytest.mark.parametrize("tvdb_id", [None, 72879])
def test_show_mapping_preserves_imdb_when_tvdb_conversion_has_no_result(adapter, use_cache, tvdb_id):
    if not use_cache:
        adapter.cache = None
    adapter.tmdb_to_tvdb.return_value = tvdb_id
    item = show_item("imdb://tt6951546", "tmdb://107124")

    assert adapter.get_id(item, show_library(adapter)) == ("show", [tvdb_id] if tvdb_id else [], ["tt6951546"])
    adapter.tmdb_to_tvdb.assert_called_once_with(107124)


@pytest.mark.parametrize("cached", [False, True])
def test_metadata_matches_imdb_only_show_with_fresh_or_cached_mapping(adapter, cached):
    item = show_item("imdb://tt6951546", "tmdb://107124")
    plex_library = show_library(adapter)
    library.Library.map_guids(plex_library, [item])
    if cached:
        plex_library = show_library(adapter)
        library.Library.map_guids(plex_library, [(item.ratingKey, item.guid)])
    assert plex_library.imdb_map == {"tt6951546": [item.ratingKey]}
    assert plex_library.imdb_rating_key_map == {item.ratingKey: "tt6951546"}
    assert plex_library.show_map == {}
    assert plex_library.show_rating_key_map == {}
    adapter.tmdb_to_tvdb.assert_called_once_with(107124)

    plex_library.fetch_item = MagicMock(return_value=item)
    metadata_file = meta.MetadataFile.__new__(meta.MetadataFile)
    metadata_file.library = plex_library
    metadata_file.type_str = "Metadata File"
    definition = {"match": {"mapping_id": "tt6951546"}}
    metadata_file.metadata = {"animaniacs_2020": definition}
    metadata_file.update_metadata_item = MagicMock()

    metadata_file.update_metadata()

    plex_library.fetch_item.assert_called_once_with(item.ratingKey)
    metadata_file.update_metadata_item.assert_called_once_with(item, "animaniacs_2020", definition, {"match": "match"})


def test_imdb_only_mapping_is_reused_from_guid_cache(adapter):
    item = show_item("imdb://tt6951546", "tmdb://107124")
    plex_library = show_library(adapter)
    assert adapter.get_id(item, plex_library) == ("show", [], ["tt6951546"])
    item.guids = []
    adapter.tmdb_to_tvdb.reset_mock()

    media_type, tvdb_ids, imdb_ids = adapter.get_id(item, plex_library)

    assert media_type == "show"
    assert not tvdb_ids
    assert imdb_ids == ["tt6951546"]
    adapter.tmdb_to_tvdb.assert_not_called()


def test_show_without_imdb_or_tvdb_still_fails_mapping(adapter):
    item = show_item("tmdb://107124")

    assert adapter.get_id(item, show_library(adapter)) == (None, None, None)


def test_legacy_imdb_show_guid_preserves_id_when_tvdb_conversion_fails(adapter):
    item = show_item()
    item.guid = "com.plexapp.agents.imdb://tt6951546?lang=en"

    assert adapter.get_id(item, show_library(adapter)) == ("show", [], ["tt6951546"])
