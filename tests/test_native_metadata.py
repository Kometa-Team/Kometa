"""Native metadata contracts, without using Plex batch edit endpoints."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 -- break circular imports
from modules.mediabrowser import MediaBrowserItem
from modules.native_metadata import apply_edit, backup_metadata, configure_metadata_operations
from modules.silo import SiloItem


def native_item(kind, **data):
    server = SimpleNamespace(type_name=kind, type_label=kind.title(), display_name="Test", url="http://server")
    library = SimpleNamespace(server=server, client=MagicMock(), find_poster_url=lambda item: None, _search_details={})
    library.client.server = server
    if kind == "silo":
        item = SiloItem({"content_id": "movie-1", "type": "movie", "title": "Example", "genres": ["Drama"], "locked_fields": [77], **data}, library)
        library.client.update_metadata.side_effect = lambda key, fields: {**item.data, **fields}
    else:
        item = MediaBrowserItem({"Id": "movie-1", "Type": "Movie", "Name": "Example", "Genres": ["Drama"], "Tags": ["Keep"], "LockedFields": ["SortName"], **data}, library)
        library.client.update_item.side_effect = lambda key, fields: {**item.data, **fields}
        library.client.update_user_data.side_effect = lambda key, fields: {**item.data.get("UserData", {}), **fields}
    return library, item


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_combined_metadata_fields_use_one_native_write(kind):
    library, item = native_item(kind)
    apply_edit(library, item, {"contentRating": "PG", "studio": "Example Studio", "originalTitle": "Original", "originallyAvailableAt": datetime(2020, 1, 2)}, {"genre": (["Comedy"], ["Drama"])})
    if kind == "silo":
        payload = library.client.update_metadata.call_args.args[1]
        assert payload == {"content_rating": "PG", "studios": ["Example Studio"], "original_title": "Original", "release_date": "2020-01-02", "genres": ["Comedy"]}
        assert item.data["locked_fields"] == [77]
        library.client.update_metadata.assert_called_once()
    else:
        payload = library.client.update_item.call_args.args[1]
        assert payload["OfficialRating"] == "PG"
        assert payload["Studios"] == [{"Name": "Example Studio"}]
        assert payload["PremiereDate"] == "2020-01-02T00:00:00Z"
        assert payload["Genres"] == ["Comedy"]
        assert "SortName" in payload["LockedFields"]
        assert "PremiereDate" not in payload["LockedFields"]
        library.client.update_item.assert_called_once()
    assert library._search_details[item.ratingKey] is item


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_native_ratings_scale_critic_and_keep_profile_state(kind):
    library, item = native_item(kind, UserData={"IsFavorite": True, "PlayCount": 3, "Rating": 2})
    apply_edit(library, item, {"rating": "7.5", "audienceRating": "8.2", "userRating": "6.5"})
    payload = library.client.update_item.call_args.args[1]
    assert payload["CriticRating"] == 75
    assert payload["CommunityRating"] == 8.2
    library.client.update_user_data.assert_called_once_with("movie-1", {"Rating": 6.5})
    assert item.data["UserData"] == {"IsFavorite": True, "PlayCount": 3, "Rating": 6.5}


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_clear_and_native_field_locks(kind):
    library, item = native_item(kind)
    apply_edit(library, item, {"contentRating": None}, control="reset")
    if kind == "silo":
        assert library.client.update_metadata.call_args.args[1] == {"content_rating": None}
        assert item.data["locked_fields"] == [77]
    else:
        assert item.data["OfficialRating"] is None
        assert item.data["LockedFields"] == ["SortName"]
        apply_edit(library, item, {"genre": None}, control="lock")
        assert "Genres" in item.data["LockedFields"]
        assert item.genres == ["Drama"]
        apply_edit(library, item, {"genre": None}, control="unlock")
        assert item.data["LockedFields"] == ["SortName"]


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_unsupported_operations_reported_before_item_processing(kind):
    logger = MagicMock()
    params = {
        "mass_collection_mode": "hide",
        "mass_added_at_update": ["tmdb"],
        "mass_imdb_parental_labels": "none",
        "mass_genre_update": ["lock", "tmdb"],
        "mass_poster_update": {"source": "plex", "sources": ["plex", "tmdb"]},
        "mass_square_art_update": {"source": "tmdb"},
    }
    configure_metadata_operations(params, kind, logger)
    assert params["mass_collection_mode"] is None
    assert params["mass_poster_update"]["sources"] == ["tmdb"]
    if kind == "silo":
        assert params["mass_added_at_update"] is None
        assert params["mass_imdb_parental_labels"] is None
        assert params["mass_genre_update"] == ["tmdb"]
        assert params["mass_square_art_update"] is None
    else:
        assert params["mass_added_at_update"] == ["tmdb"]
        assert params["mass_imdb_parental_labels"] == "none"
    assert all("not supported" in args.args[0] for args in logger.error.call_args_list)


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_native_backup_uses_ids_and_excludes_configured_fields(kind):
    library, item = native_item(kind)
    library.name = "Movies"
    library.metadata_backup = {"path": "/tmp/backup.yml", "exclude": ["genre"]}
    library.get_all = lambda: [item]
    library.reload = lambda item: item
    document = SimpleNamespace(data={}, save=MagicMock())
    config = SimpleNamespace(Requests=SimpleNamespace(file_yaml=MagicMock(return_value=document)))
    backup_metadata(config, library, MagicMock())
    record = document.data["native_metadata"]["Test/Movies"]["items"]["movie-1"]
    assert record["title"] == "Example"
    assert "genres" not in record["fields"]
    assert "Genres" not in record["fields"]
    document.save.assert_called_once()


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_native_operations_resolve_sources_and_combine_updates(kind, monkeypatch):
    from modules import operations as operations_module
    from modules.operations import Operations
    from tests.test_operations import make_mass_edit_library

    context, item = native_item(kind, **({"content_rating": "R", "original_title": "Old"} if kind == "silo" else {"OfficialRating": "R", "OriginalTitle": "Old"}))
    library = make_mass_edit_library([item], mass_genre_update=[["Comedy"]], mass_content_rating_update=["PG"], mass_original_title_update=["tmdb"], mass_studio_update=["Example Studio"], mass_originally_available_update=[datetime(2020, 1, 2)])
    library.server = context.server
    library.client = context.client
    config = MagicMock()
    config.TMDb.get_item.return_value = SimpleNamespace(original_title="Original")
    monkeypatch.setattr(operations_module, "logger", MagicMock())
    Operations(config, library).run_operations()
    library.Plex.batchMultiEdits.assert_not_called()
    client = library.client.update_metadata if kind == "silo" else library.client.update_item
    client.assert_called_once()
    payload = client.call_args.args[1]
    if kind == "silo":
        assert payload["original_title"] == "Original"
        assert payload["genres"] == ["Comedy"]
        assert payload["release_date"] == "2020-01-02"
    else:
        assert payload["OriginalTitle"] == "Original"
        assert payload["Genres"] == ["Comedy"]
        assert payload["PremiereDate"] == "2020-01-02T00:00:00Z"


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
@pytest.mark.parametrize("level,filename", [("season", "Season01.jpg"), ("episode", "S01E02.jpg")])
def test_native_child_artwork_uses_season_and_episode_filenames(tmp_path, monkeypatch, kind, level, filename):
    from modules import plex as plex_module
    from modules.plex import Plex

    raw = {"type": level, "season_number": 1, "episode_number": 2} if kind == "silo" else {"Type": level.title(), "IndexNumber": 1 if level == "season" else 2, "ParentIndexNumber": 1}
    library, item = native_item(kind, **raw)
    library.asset_folders = True
    library.dimensional_asset_rename = False
    monkeypatch.setattr(plex_module, "logger", MagicMock())
    (tmp_path / filename).write_bytes(b"image")
    poster, *_ = Plex.find_item_assets(library, item, item_asset_directory=str(tmp_path), asset_directory=[str(tmp_path)], folder_name="Example")
    assert poster.location == str(tmp_path / filename)


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_native_backup_includes_children_without_title_collisions(kind):
    def record(identity, level):
        return native_item(kind, **({"content_id": identity, "type": level} if kind == "silo" else {"Id": identity, "Type": "Series" if level == "show" else level.title()}))[1]

    library, root = native_item(kind, **({"content_id": "show", "type": "series"} if kind == "silo" else {"Id": "show", "Type": "Series"}))
    season = record("season", "season")
    episode = record("episode", "episode")
    root.seasons = lambda: [season]
    season.episodes = lambda: [episode]
    library.name = "TV"
    library.metadata_backup = {"path": "/tmp/backup.yml"}
    library.get_all = lambda: [root]
    library.reload = lambda item: item
    document = SimpleNamespace(data={}, save=MagicMock())
    backup_metadata(SimpleNamespace(Requests=SimpleNamespace(file_yaml=lambda *args, **kwargs: document)), library, MagicMock())
    records = document.data["native_metadata"]["Test/TV"]["items"]
    assert set(records) == {"show", "season", "episode"}


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_episode_rating_operations_use_native_item_writes(kind, monkeypatch):
    from modules import operations as operations_module
    from modules.operations import Operations
    from tests.test_operations import make_mass_edit_library

    context, show = native_item(kind, Id="show", Type="Series")
    _, episode = native_item(kind, Id="episode", Type="Episode", IndexNumber=2, ParentIndexNumber=1)
    items = {"show": show, "episode": episode}
    context.client.update_item.side_effect = lambda identity, fields: {**items[identity].data, **fields}
    library = make_mass_edit_library([show], mass_episode_audience_rating_update=[7.5])
    library.server = context.server
    library.client = context.client
    library.is_movie = False
    library.is_show = True
    library.cached_item_subitems.return_value = [episode]
    monkeypatch.setattr(operations_module, "logger", MagicMock())
    Operations(MagicMock(), library).run_operations()
    assert library.client.update_item.call_args.args[0] == "episode"
    assert library.client.update_item.call_args.args[1]["CommunityRating"] == 7.5
    library.Plex.batchMultiEdits.assert_not_called()


@pytest.mark.parametrize("level,date_field", [("movie", "release_date"), ("series", "first_air_date"), ("season", "air_date"), ("episode", "air_date")])
def test_silo_release_updates_use_native_date_for_item_type(level, date_field):
    library, item = native_item("silo", type=level)
    apply_edit(library, item, {"originallyAvailableAt": datetime(2020, 1, 2)})
    assert library.client.update_metadata.call_args.args[1] == {date_field: "2020-01-02"}
    assert item.originallyAvailableAt == datetime(2020, 1, 2)
