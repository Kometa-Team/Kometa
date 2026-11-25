"""Tests for the unused assets report operation."""

from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PIL import Image
from plexapi.video import Episode, Movie, Season, Show

import modules.builder  # noqa: F401 - breaks circular imports
from modules import asset_audit
from modules.request import YAML
from modules.util import Failed
from tests.conftest import FakeLogger
from tests.factories import make_plex


def touch(path, size=(10, 15)):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in asset_audit.IMAGE_EXTENSIONS:
        Image.new("RGB", size).save(path, format="PNG")
    else:
        path.write_text("x")
    return path


def movie(title, folder):
    return MagicMock(spec=Movie, title=title, type="movie", locations=[f"/media/{folder}/{title}.mkv"])


def show(title, seasons):
    item = MagicMock(spec=Show, title=title, type="show", locations=[f"/media/{title}"])
    item.seasons.return_value = seasons
    return item


def season(number, episodes, parent):
    item = MagicMock(spec=Season, seasonNumber=number, parentTitle=parent, type="season")
    item.episodes.return_value = episodes
    return item


def episode(code, parent):
    return MagicMock(spec=Episode, seasonEpisode=code, grandparentTitle=parent, type="episode")


def library(root, items, name="Movies", collections=(), asset_folders=True, **attrs):
    lib = make_plex(
        name=name,
        asset_directory=[str(root)],
        asset_folders=asset_folders,
        asset_depth=attrs.pop("asset_depth", 0),
        create_asset_folders=attrs.pop("create_asset_folders", False),
        dimensional_asset_rename=attrs.pop("dimensional_asset_rename", False),
        **attrs,
    )
    lib.get_all = MagicMock(return_value=items)
    lib.get_all_collections = MagicMock(return_value=[SimpleNamespace(title=c) for c in collections])
    lib.query = lambda method: method()
    lib.unused_assets_report = {"path": str(root.parent / f"{name}_Unused_Assets.yml")}
    return lib


def make_audit_config(*libraries, playlist_names=()):
    return SimpleNamespace(
        libraries=list(libraries),
        playlist_names=list(playlist_names),
        playlist_files=[],
        Requests=SimpleNamespace(file_yaml=lambda path, **kwargs: YAML(path=path, **kwargs)),
    )


def run(config, lib, names=None):
    logger = FakeLogger()
    names = names or {}
    data = asset_audit.run_unused_assets_report(config, lib, lambda target: names.get(target.name, set()), logger)
    return data, logger


def reasons(data):
    return {os.path.relpath(entry["path"], data["asset_directories"][0]).replace(os.sep, "/"): entry["reason"] for entry in data["unused_folders"] + data["unused_files"]}


def test_folder_mode_reports_each_kind_of_unused_asset(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Movie A (2001)" / "poster.jpg")
    touch(root / "Movie A (2001)" / "background.jpg")
    touch(root / "Movie A (2001)" / "poster-old.jpg")
    touch(root / "Movie A (2001)" / "notes.txt")
    touch(root / "Movie A (2001)" / "extras" / "still.jpg")
    touch(root / "Old Movie (1999)" / "poster.jpg")
    touch(root / "Old Movie (1999)" / "fanart.png")
    touch(root / "Empty Folder" / "readme.txt")
    touch(root / "loose.jpg")
    touch(root / ".thumbs" / "x.jpg")
    touch(root / "@eaDir" / "x.jpg")
    lib = library(root, [movie("Movie A", "Movie A (2001)")])

    data, logger = run(make_audit_config(lib), lib)

    assert logger.error_messages == []
    assert reasons(data) == {
        "Movie A (2001)/extras": asset_audit.REASON_FOLDER,
        "Old Movie (1999)": asset_audit.REASON_FOLDER,
        "Movie A (2001)/poster-old.jpg": asset_audit.REASON_NAME,
        "loose.jpg": asset_audit.REASON_LOOSE,
    }
    old = next(f for f in data["unused_folders"] if f["path"].endswith("Old Movie (1999)"))
    assert old["files"] == 2
    assert data["summary"]["unused_folders"] == 2
    assert data["summary"]["unused_files"] == 2
    assert os.path.exists(lib.unused_assets_report["path"])


def test_duplicate_extension_names_the_file_that_is_used(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Movie A (2001)" / "poster.jpg")
    touch(root / "Movie A (2001)" / "poster.png")
    lib = library(root, [movie("Movie A", "Movie A (2001)")])

    data, _ = run(make_audit_config(lib), lib)

    (entry,) = data["unused_files"]
    used = "poster.png" if entry["path"].endswith("poster.jpg") else "poster.jpg"
    assert entry["reason"] == asset_audit.REASON_DUPLICATE.format(used=used)


def test_shared_directory_counts_assets_used_by_other_libraries(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Movie A (2001)" / "poster.jpg")
    touch(root / "Show B" / "poster.jpg")
    touch(root / "Show B" / "Season01.jpg")
    touch(root / "Show B" / "S01E01.jpg")
    touch(root / "Show B" / "Season02.jpg")
    touch(root / "Show B" / "S01E05.jpg")
    ep = episode("s01e01", "Show B")
    tv = library(root, [show("Show B", [season(1, [ep], "Show B")])], name="TV Shows", is_movie=False, is_show=True, type="Show")
    movies = library(root, [movie("Movie A", "Movie A (2001)")])
    unrelated = library(tmp_path / "elsewhere", [], name="Music")

    data, _ = run(make_audit_config(movies, tv, unrelated), movies)

    assert data["libraries_checked"] == ["Movies", "TV Shows"]
    assert reasons(data) == {"Show B/S01E05.jpg": asset_audit.REASON_SEASON, "Show B/Season02.jpg": asset_audit.REASON_SEASON}
    unrelated.get_all.assert_not_called()


def test_collections_and_playlists_keep_their_folders(tmp_path):
    root = tmp_path / "assets"
    for name in ["Configured", "Disabled Mapping", "On Server", "My Playlist", "Forgotten"]:
        touch(root / name / "poster.jpg")
    lib = library(root, [], collections=["On Server"])

    data, _ = run(make_audit_config(lib, playlist_names=["My Playlist"]), lib, names={"Movies": {"Configured", "Disabled Mapping"}})

    assert reasons(data) == {"Forgotten": asset_audit.REASON_FOLDER}


def test_nested_asset_folders_respect_asset_depth(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Group" / "Movie A (2001)" / "poster.jpg")
    touch(root / "Group" / "group-art.jpg")
    touch(root / "Dead Group" / "Gone (1990)" / "poster.jpg")
    lib = library(root, [movie("Movie A", "Movie A (2001)")], asset_depth=1)

    data, _ = run(make_audit_config(lib), lib)

    assert reasons(data) == {"Dead Group": asset_audit.REASON_FOLDER, "Group/group-art.jpg": asset_audit.REASON_LOOSE}


def test_flat_mode_matches_files_by_name(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Movie A (2001).jpg")
    touch(root / "Movie A (2001)_background.jpg")
    touch(root / "Gone (1990).jpg")
    touch(root / "sub" / "x.jpg")
    lib = library(root, [movie("Movie A", "Movie A (2001)")], asset_folders=False)

    data, _ = run(make_audit_config(lib), lib)

    assert reasons(data) == {"Gone (1990).jpg": asset_audit.REASON_FLAT, "sub": asset_audit.REASON_FOLDER}


@pytest.mark.parametrize("error", [Failed("server unavailable"), RuntimeError("boom")])
def test_any_loading_failure_writes_no_report(tmp_path, error):
    root = tmp_path / "assets"
    touch(root / "Show B" / "poster.jpg")
    movies = library(root, [])
    tv = library(root, [], name="TV Shows")
    tv.get_all.side_effect = error

    data, logger = run(make_audit_config(movies, tv), movies)

    assert data is None
    assert not os.path.exists(movies.unused_assets_report["path"])
    assert any("No report was written" in message for message in logger.error_messages)


def test_missing_asset_directory_writes_no_report(tmp_path):
    lib = library(tmp_path / "missing", [])

    data, logger = run(make_audit_config(lib), lib)

    assert data is None
    assert any("Asset directory not found" in message for message in logger.warning_messages)
    assert any("No asset directory to check" in message for message in logger.error_messages)


def test_report_never_creates_folders_or_renames_files(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Movie A (2001)" / "tall.jpg", size=(10, 15))
    touch(root / "Movie A (2001)" / "wide.jpg", size=(15, 10))
    lib = library(root, [movie("Movie A", "Movie A (2001)"), movie("No Folder", "No Folder (2020)")], create_asset_folders=True, dimensional_asset_rename=True)

    data, _ = run(make_audit_config(lib), lib)

    # Dimensional rename would use both files, so neither is unused, and neither was renamed.
    assert reasons(data) == {}
    assert sorted(os.listdir(root / "Movie A (2001)")) == ["tall.jpg", "wide.jpg"]
    assert not (root / "No Folder (2020)").exists()


def test_collection_folder_in_collection_directory_is_used_despite_same_named_item_folder(tmp_path):
    items_root = tmp_path / "assets"
    collections_root = tmp_path / "collection_assets"
    touch(items_root / "Doctor Who" / "poster.jpg")
    touch(collections_root / "Doctor Who" / "poster.jpg")
    lib = library(items_root, [show("Doctor Who", [])], collection_asset_directory=[str(collections_root)], is_show=True, type="Show")

    data, _ = run(make_audit_config(lib), lib, names={"Movies": {"Doctor Who"}})

    assert data["unused_folders"] == [] and data["unused_files"] == []


def test_library_with_a_nested_asset_directory_counts_as_sharing(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Movie A (2001)" / "poster.jpg")
    touch(root / "Shows" / "Show B" / "poster.jpg")
    movies = library(root, [movie("Movie A", "Movie A (2001)")])
    tv = library(root / "Shows", [show("Show B", [])], name="TV Shows", is_show=True, type="Show")

    data, _ = run(make_audit_config(movies, tv), movies)

    assert data["libraries_checked"] == ["Movies", "TV Shows"]
    assert reasons(data) == {}


def test_nested_scan_root_is_walked_on_its_own(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Group" / "Inner" / "Movie A (2001)" / "poster.jpg")
    touch(root / "Group" / "Inner" / "Gone (1990)" / "poster.jpg")
    lib = library(root, [movie("Movie A", "Movie A (2001)")])
    lib.asset_directory = [str(root), str(root / "Group" / "Inner")]

    data, _ = run(make_audit_config(lib), lib)

    assert reasons(data) == {"Group/Inner/Gone (1990)": asset_audit.REASON_FOLDER}


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_same_folder_through_a_symlink_counts_as_sharing(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Show B" / "poster.jpg")
    link = tmp_path / "linked"
    try:
        os.symlink(root, link, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks not permitted")
    movies = library(root, [])
    tv = library(link, [show("Show B", [])], name="TV Shows", is_show=True, type="Show")

    data, _ = run(make_audit_config(movies, tv), movies)

    assert reasons(data) == {}


def test_collection_file_override_directory_is_searched(tmp_path):
    root = tmp_path / "assets"
    touch(root / "collections" / "Marvel" / "poster.jpg")
    lib = library(root, [])
    lib.configured_collection_metadata_files = [SimpleNamespace(asset_directory=[str(root / "collections")], collection_asset_directory=[], collections={"Marvel": {}})]

    data, _ = run(make_audit_config(lib), lib, names={"Movies": {"Marvel"}})

    assert reasons(data) == {}


@pytest.mark.parametrize(
    ("config_attrs", "library_attrs", "expected"),
    [
        ({"requested_libraries": ["Movies"]}, {}, "--run-libraries"),
        ({"requested_servers": ["home"]}, {}, "--run-servers"),
        ({"failed_libraries": ["TV Shows"]}, {}, "failed to connect: TV Shows"),
        ({"incomplete_playlist_files": ["playlists.yml"]}, {}, "playlist files did not load: playlists.yml"),
        ({}, {"incomplete_collection_files": ["movies.yml"]}, "collection files for the Movies library did not load: movies.yml"),
    ],
)
def test_incomplete_runs_write_no_report(tmp_path, config_attrs, library_attrs, expected):
    root = tmp_path / "assets"
    touch(root / "Old" / "poster.jpg")
    lib = library(root, [], **library_attrs)
    config = make_audit_config(lib)
    for key, value in config_attrs.items():
        setattr(config, key, value)

    data, logger = run(config, lib)

    assert data is None
    assert not os.path.exists(lib.unused_assets_report["path"])
    assert any(expected in message and "No report was written" in message for message in logger.error_messages)
    lib.get_all.assert_not_called()


def test_name_mapping_is_an_asset_alias_only_when_asked():
    from modules.operations import _configured_collection_name_aliases

    metadata_file = MagicMock()
    metadata_file.apply_template.return_value = {"name_mapping": "From Template"}
    plain = {"name_mapping": "Mapped", "plex_search": {}}
    templated = {"template": {"name": "t"}}

    assert _configured_collection_name_aliases(MagicMock(), MagicMock(), metadata_file, "Coll", plain) == {"Coll"}
    assert _configured_collection_name_aliases(MagicMock(), MagicMock(), metadata_file, "Coll", plain, include_name_mapping=True) == {"Coll", "Mapped"}
    assert _configured_collection_name_aliases(MagicMock(), MagicMock(), metadata_file, "Coll", templated, include_name_mapping=True) == {"Coll", "From Template"}


def test_asset_names_raise_instead_of_skipping_unresolvable_collections(monkeypatch):
    import modules.operations as ops_module

    def broken(*args, **kwargs):
        raise RuntimeError("template missing")

    monkeypatch.setattr(ops_module, "_configured_collection_name_aliases", broken)
    monkeypatch.setattr(ops_module, "logger", FakeLogger())
    lib = SimpleNamespace(collection_names=[], configured_collection_metadata_files=[SimpleNamespace(collections={"Coll": {}})])
    operations = ops_module.Operations(MagicMock(), lib)

    assert operations._configured_collection_names() == set()
    with pytest.raises(Failed, match="could not resolve the names of collection Coll"):
        operations._configured_collection_names(for_assets=True)


@pytest.mark.parametrize("enabled", [True, False])
def test_operations_only_reads_scheduled_collection_names_for_the_report(tmp_path, monkeypatch, enabled):
    import modules.library as library_module
    from modules.util import NotScheduled

    loaded = []

    class FakeMetadataFile:
        def __init__(self, config, lib, file_type, path, temp_vars, asset_directory, kind, configured_names_only=False):
            loaded.append(path)
            if path == "broken.yml":
                raise Failed("bad file")
            if path == "later.yml":
                raise NotScheduled("later")
            self.collections = {f"{path} collection": {}}

    monkeypatch.setattr(library_module, "MetadataFile", FakeMetadataFile)
    monkeypatch.setattr(library_module, "logger", FakeLogger())
    entries = [("File", name, {}, None) for name in ["scheduled.yml", "unscheduled.yml", "broken.yml", "later.yml"]]
    lib = library(tmp_path / "assets", [])
    lib.configured_collection_files = entries
    lib.scanned_collection_files = [entries[0], entries[2]]
    lib.configured_collection_metadata_files = []
    lib.incomplete_collection_files = []
    lib.collection_names = []
    lib.unused_assets_report = {"path": "x"} if enabled else None

    lib.scan_files(operations_only=True, overlays_only=False, collection_only=False, metadata_only=False)

    if enabled:
        assert sorted(loaded) == ["broken.yml", "later.yml", "scheduled.yml", "unscheduled.yml"]
        assert set(lib.collection_names) == {"scheduled.yml collection", "unscheduled.yml collection"}
        assert sorted(lib.incomplete_collection_files) == ["broken.yml", "later.yml"]
    else:
        assert sorted(loaded) == ["later.yml", "unscheduled.yml"]
        assert lib.collection_names == ["unscheduled.yml collection"]


def test_scheduled_out_playlists_and_their_name_mapping_are_used(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Weekly Mix" / "poster.jpg")
    touch(root / "weekly-art" / "poster.jpg")
    lib = library(root, [])
    config = make_audit_config(lib)
    config.unscheduled_playlist_files = [SimpleNamespace(playlists={"Weekly Mix": {"name_mapping": "weekly-art"}})]

    data, _ = run(config, lib)

    assert reasons(data) == {}


def test_definition_asset_directory_is_read_in_any_case_and_from_templates(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Upper" / "Marvel" / "poster.jpg")
    touch(root / "Templated" / "DC" / "poster.jpg")
    metadata_file = MagicMock(asset_directory=[], collection_asset_directory=[])
    metadata_file.collections = {"Marvel": {"Asset_Directory": str(root / "Upper")}, "DC": {"template": {"name": "t"}}}
    metadata_file.apply_template.return_value = {"asset_directory": str(root / "Templated")}
    lib = library(root, [])
    lib.configured_collection_metadata_files = [metadata_file]

    data, _ = run(make_audit_config(lib), lib, names={"Movies": {"Marvel", "DC"}})

    assert reasons(data) == {}


def test_failed_template_expansion_writes_no_report(tmp_path):
    root = tmp_path / "assets"
    touch(root / "Old" / "poster.jpg")
    metadata_file = MagicMock(asset_directory=[], collection_asset_directory=[], collections={"DC": {"template": {"name": "t"}}})
    metadata_file.apply_template.side_effect = Failed("missing variable")
    lib = library(root, [])
    lib.configured_collection_metadata_files = [metadata_file]

    data, logger = run(make_audit_config(lib), lib)

    assert data is None
    assert any("could not expand the templates of DC" in message and "No report was written" in message for message in logger.error_messages)


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_folder_holding_a_symlinked_asset_folder_is_not_reported(tmp_path):
    root = tmp_path / "assets"
    target = tmp_path / "elsewhere" / "Movie A (2001)"
    touch(target / "poster.jpg")
    (root / "Links").mkdir(parents=True)
    touch(root / "Links" / "stray.jpg")
    try:
        os.symlink(target, root / "Links" / "Movie A (2001)", target_is_directory=True)
    except OSError:
        pytest.skip("symlinks not permitted")
    lib = library(root, [movie("Movie A", "Movie A (2001)")], asset_depth=1)

    data, _ = run(make_audit_config(lib), lib)

    assert reasons(data) == {"Links/stray.jpg": asset_audit.REASON_LOOSE}
