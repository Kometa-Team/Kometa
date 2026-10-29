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
        "split_duplicates": True,
        "mass_collection_mode": "hide",
        "mass_added_at_update": ["tmdb"],
        "mass_imdb_parental_labels": "none",
        "mass_genre_update": ["lock", "tmdb"],
        "mass_poster_update": {"source": "plex", "sources": ["plex", "tmdb"]},
        "mass_square_art_update": {"source": "tmdb"},
    }
    configure_metadata_operations(params, kind, logger)
    assert params["split_duplicates"] is (kind != "silo")
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
def test_native_backup_uses_regular_metadata_and_excludes_configured_fields(kind):
    library, item = native_item(kind)
    library.name = "Movies"
    library.metadata_backup = {"path": "/tmp/backup.yml", "exclude": ["genre"]}
    library.get_all = lambda: [item]
    library.reload = lambda item: item
    document = SimpleNamespace(data={}, save=MagicMock())
    config = SimpleNamespace(Requests=SimpleNamespace(file_yaml=MagicMock(return_value=document)))
    backup_metadata(config, library, MagicMock())
    record = document.data["metadata"]["Example"]
    assert record["title"] == "Example"
    assert "genre" not in record
    assert "native_metadata" not in document.data
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
    records = document.data["metadata"]
    assert records["Example"]["seasons"][0]["episodes"][0]["title"] == "Example"
    assert "native_metadata" not in document.data
    records["Example"]["seasons"][0]["episodes"][0]["url_poster"] = "https://example.com/episode.jpg"
    backup_metadata(SimpleNamespace(Requests=SimpleNamespace(file_yaml=lambda *args, **kwargs: document)), library, MagicMock())
    assert records["Example"]["seasons"][0]["episodes"][0]["url_poster"] == "https://example.com/episode.jpg"


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


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_added_date_clear_is_reported_before_processing_and_guarded(kind):
    params = {"mass_added_at_update": ["remove", "reset", datetime(2020, 1, 2)]}
    logger = MagicMock()
    configure_metadata_operations(params, kind, logger)
    assert params["mass_added_at_update"] == [datetime(2020, 1, 2)]
    assert logger.error.call_count == 2
    library, item = native_item(kind)
    from modules.util import Failed

    with pytest.raises(Failed, match="Clearing the added date"):
        apply_edit(library, item, {"addedAt": None}, control="reset")
    library.client.update_item.assert_not_called()


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_rating_and_original_title_locks_match_native_server_enum(kind):
    library, item = native_item(kind)
    apply_edit(library, item, {"originalTitle": "Original", "rating": 7.5, "audienceRating": 8.2})
    payload = library.client.update_item.call_args.args[1]
    native_locks = set(payload.get("LockedFields", []))
    assert bool(native_locks & {"OriginalTitle", "CommunityRating", "CriticRating"}) is (kind == "emby")
    assert payload["CriticRating"] == 75
    assert payload["CommunityRating"] == 8.2


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
@pytest.mark.parametrize("episodes", [False, True])
def test_native_stored_rating_sources_run_through_operations_without_provider_requests(kind, episodes, monkeypatch):
    from modules import operations as operations_module
    from modules.operations import Operations
    from tests.test_operations import make_mass_edit_library

    context, item = native_item(kind, CommunityRating=7.2, Type="Episode" if episodes else "Movie")
    root = native_item(kind, Type="Series")[1] if episodes else item
    context.client.update_item.side_effect = lambda key, fields: {**item.data, **fields}
    option = "mass_episode_critic_rating_update" if episodes else "mass_critic_rating_update"
    library = make_mass_edit_library([root], **{option: [f"{kind}_community"]})
    library.server = context.server
    library.client = context.client
    library.is_movie = not episodes
    library.is_show = episodes
    library.cached_item_subitems.return_value = [item]
    config = MagicMock()
    monkeypatch.setattr(operations_module, "logger", MagicMock())
    Operations(config, library).run_operations()
    assert library.client.update_item.call_args.args[1]["CriticRating"] == 72
    config.TMDb.get_item.assert_not_called()
    library.Plex.batchMultiEdits.assert_not_called()


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_movie_tvdb_lookup_uses_native_provider_id_without_plex_guids(kind, monkeypatch):
    from modules import operations as operations_module
    from modules.operations import Operations
    from tests.test_operations import make_mass_edit_library

    context, item = native_item(kind, ProviderIds={"Tvdb": "34"})
    library = make_mass_edit_library([item], mass_genre_update=["tvdb"])
    library.server = context.server
    library.client = context.client
    config = MagicMock()
    config.TVDb.get_tvdb_obj.return_value = SimpleNamespace(genres=["Mystery"])
    monkeypatch.setattr(operations_module, "logger", MagicMock())
    Operations(config, library).run_operations()
    config.TVDb.get_tvdb_obj.assert_called_once_with(34, is_movie=True)
    assert "Mystery" in library.client.update_item.call_args.args[1]["Genres"]


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_missing_provider_ids_are_reported_with_operation_names(kind, monkeypatch):
    from modules import operations as operations_module
    from modules.operations import Operations
    from tests.test_operations import make_mass_edit_library

    context, item = native_item(kind)
    library = make_mass_edit_library(
        [item],
        mass_original_title_update=["anidb_official", "anidb", "Unknown"],
        mass_square_art_update={"source": "tvdb", "ignore_locked": False},
    )
    library.server = context.server
    library.client = context.client
    library.find_item_assets.return_value = (None, None, None, None, None, None)
    config = MagicMock()
    config.Convert.ids_to_anidb.return_value = None
    logger = MagicMock()
    monkeypatch.setattr(operations_module, "logger", logger)

    Operations(config, library).run_operations()

    messages = [str(call.args[0]) for call in logger.info.call_args_list if call.args]
    assert messages.count("Original Title | No AniDB ID found") == 1
    assert messages.count("Square Art | No TVDb ID found") == 1
    assert any("Original Title | Unknown" in message for message in messages)
    config.AniDB.get_anime.assert_not_called()
    config.TVDb.get_tvdb_obj.assert_not_called()
    library.square_art_update.assert_not_called()


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_native_backup_sync_tags_provider_matching_and_schema(kind):
    import json
    from pathlib import Path

    import jsonschema

    data = {"tmdb_id": 123, "genres": [], "user_rating": 0} if kind == "silo" else {"ProviderIds": {"Tmdb": "123"}, "Genres": [], "Tags": ["Keep"], "CriticRating": 85, "UserData": {"Rating": 0}}
    library, item = native_item(kind, **data)
    library.metadata_backup = {"path": "/tmp/backup.yml", "sync_tags": True, "exclude": ["country"]}
    library.get_all = lambda: [item]
    library.reload = lambda item: item
    document = SimpleNamespace(data={"metadata": {123: {"genre": "Stale", "summary": "Saved"}}}, save=MagicMock())
    backup_metadata(SimpleNamespace(Requests=SimpleNamespace(file_yaml=lambda *args, **kwargs: document)), library, MagicMock())
    record = document.data["metadata"][123]
    assert record["genre.sync"] == []
    assert "genre" not in record
    assert "country.sync" not in record
    assert record["user_rating"] == 0
    if kind != "silo":
        assert record["critic_rating"] == 8.5
        assert record["label.sync"] == "Keep"
    schema = json.loads(Path("json-schema/metadata-schema.json").read_text())
    # JSON object keys are strings when validating the YAML document as JSON.
    jsonschema.validate(json.loads(json.dumps(document.data)), schema)
    logger = MagicMock()
    params = {"metadata_backup": library.metadata_backup}
    configure_metadata_operations(params, kind, logger)
    logger.error.assert_not_called()


@pytest.mark.parametrize("kind", ["silo", "jellyfin", "emby"])
def test_native_backup_preserves_same_title_items_and_existing_attributes(kind):
    key_data = {"tmdb_id": 123, "year": 2000} if kind == "silo" else {"ProviderIds": {"Tmdb": "123"}, "ProductionYear": 2000}
    library, first = native_item(kind, **key_data)
    _, second = native_item(kind, **{**key_data, ("content_id" if kind == "silo" else "Id"): "second"})
    library.metadata_backup = {"path": "/tmp/backup.yml", "sync_tags": False}
    library.get_all = lambda: [first, second]
    library.reload = lambda item: item
    document = SimpleNamespace(data={"collections": {"Keep": {}}, "metadata": {123: {"url_poster": "https://example.com/poster.jpg", "genre.sync": ["Old"]}}}, save=MagicMock())
    backup_metadata(SimpleNamespace(Requests=SimpleNamespace(file_yaml=lambda *args, **kwargs: document)), library, MagicMock())
    records = document.data["metadata"]
    assert len(records) == 2
    assert records[123]["url_poster"] == "https://example.com/poster.jpg"
    assert records[123]["genre"] == "Drama"
    assert "genre.sync" not in records[123]
    assert records["Example (2000) [second]"]["match"] == {"title": "Example", "year": 2000}
    assert document.data["collections"] == {"Keep": {}}


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_regular_metadata_reader_restores_browser_backup(kind, monkeypatch):
    from modules import meta as meta_module
    from modules.meta import MetadataFile

    library, item = native_item(kind, People=[{"Name": "Old Director", "Type": "Director"}, {"Name": "Actor", "Type": "Actor"}], UserData={"Rating": 1})
    library.reload = lambda item: item
    metadata_file = MetadataFile.__new__(MetadataFile)
    metadata_file.library = library
    monkeypatch.setattr(meta_module, "logger", MagicMock())
    entry = {"original_title": "Restored", "summary": "Saved summary", "content_rating": "PG-13", "critic_rating": 8.5, "user_rating": 0, "genre.sync": [], "label": "New", "director.sync": ["New Director"]}
    metadata_file.update_metadata_item(item, 123, entry, {key: key for key in entry})
    writes = [call.args[1] for call in library.client.update_item.call_args_list]
    assert writes[0]["OriginalTitle"] == "Restored"
    assert writes[0]["OfficialRating"] == "PG-13"
    assert writes[0]["CriticRating"] == 85
    assert writes[1]["Genres"] == []
    assert writes[1]["Tags"] == ["Keep", "New"]
    assert writes[1]["People"] == [{"Name": "Actor", "Type": "Actor"}, {"Name": "New Director", "Type": "Director"}]
    library.client.update_user_data.assert_called_once_with(item.ratingKey, {"Rating": 0.0})


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_browser_restore_rejects_invalid_fields_before_writes(kind):
    from modules.native_metadata import restore_browser_metadata
    from modules.util import Failed

    library, item = native_item(kind)
    for entry in ({"summary": "Saved", "critic_rating": 101}, {"summary": "Saved", "genre": "A", "genre.sync": []}, {"summary": "Saved", "unsupported_option": True}):
        with pytest.raises(Failed):
            restore_browser_metadata(library, item, entry, MagicMock())
    library.client.update_item.assert_not_called()


@pytest.mark.parametrize("kind", ["jellyfin", "emby"])
def test_browser_restore_nested_season_and_episode_metadata(kind):
    from modules.native_metadata import restore_browser_metadata

    library, show = native_item(kind, Id="show", Type="Series")
    _, season = native_item(kind, Id="season", Type="Season", IndexNumber=1)
    _, episode = native_item(kind, Id="episode", Type="Episode", IndexNumber=2)
    items = {item.ratingKey: item for item in (show, season, episode)}
    library.client.update_item.side_effect = lambda key, fields: {**items[key].data, **fields}
    show.seasons = lambda: [season]
    season.episodes = lambda: [episode]
    library.reload = lambda item: item
    restore_browser_metadata(library, show, {"seasons": {1: {"title": "First Season", "episodes": {2: {"summary": "Episode restored", "label.sync": []}}}}}, MagicMock())
    assert season.title == "First Season"
    assert episode.summary == "Episode restored"
    assert episode.data["Tags"] == []
