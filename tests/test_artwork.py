import os
import sqlite3
import tempfile
from types import SimpleNamespace

from PIL import Image

import modules.builder as builder_module
import modules.cache as cache_module
import modules.plex as plex_module
from modules.builder import CollectionBuilder, collectionless_details, playlist_attributes
from modules.poster import ImageData
from modules.util import get_image_dicts


class FakeLogger:
    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def separator(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class FakeUploadItem:
    def __init__(self):
        self.calls = []

    def uploadPoster(self, **kwargs):
        self.calls.append(("poster", kwargs))

    def uploadArt(self, **kwargs):
        self.calls.append(("background", kwargs))

    def uploadLogo(self, **kwargs):
        self.calls.append(("logo", kwargs))

    def uploadSquareArt(self, **kwargs):
        self.calls.append(("square", kwargs))

    def refresh(self):
        pass


class FakeArtworkLibrary:
    def __init__(self):
        self.collection_images = {
            "Test Playlist": {
                "url_logo": "https://example.com/logo.png",
                "url_square": "https://example.com/square.png",
            }
        }
        self.prioritize_assets = False
        self.download_url_assets = False
        self.asset_folders = False
        self.show_missing_assets = False
        self.create_asset_folders = False
        self.upload_calls = []

    def find_item_assets(self, *args, **kwargs):
        return None, None, None, None, None, None

    def pick_image(self, title, images, prioritize_assets, download_url_assets, asset_location, image_type="poster", image_name=None):
        return images.get("style_data")

    def upload_images(self, obj, poster=None, background=None, logo=None, square=None, overlay=False):
        self.upload_calls.append({"poster": poster, "background": background, "logo": logo, "square": square, "overlay": overlay})
        return False, False, bool(logo), bool(square)


def _build_asset_plex(asset_directory, asset_folders=True, dimensional_asset_rename=False):
    plex = plex_module.Plex.__new__(plex_module.Plex)
    plex.asset_directory = [asset_directory]
    plex.asset_folders = asset_folders
    plex.asset_depth = 0
    plex.create_asset_folders = False
    plex.dimensional_asset_rename = dimensional_asset_rename
    return plex


def test_get_image_dicts_splits_logo_and_square():
    posters, backgrounds, logos, squares = get_image_dicts(
        {
            "poster": "https://example.com/poster.png",
            "background": "https://example.com/background.png",
            "logo": "https://example.com/logo.png",
            "square": "https://example.com/square.png",
        },
        {
            "url_poster": "poster",
            "url_background": "background",
            "url_logo": "logo",
            "url_square": "square",
        },
    )

    assert posters == {"url_poster": "https://example.com/poster.png"}
    assert backgrounds == {"url_background": "https://example.com/background.png"}
    assert logos == {"url_logo": "https://example.com/logo.png"}
    assert squares == {"url_square": "https://example.com/square.png"}


def test_cache_creates_and_updates_square_tables(monkeypatch):
    monkeypatch.setattr(cache_module, "logger", FakeLogger())

    with tempfile.TemporaryDirectory() as tempdir:
        config_path = os.path.join(tempdir, "config.yml")
        with open(config_path, "w", encoding="utf-8"):
            pass

        cache = cache_module.Cache(config_path, 60)
        table_name = cache.get_image_table_name("Test Library")
        cache.get_image_table_name("Test Library")
        cache.update_image_map("1", f"{table_name}_squares", "/tmp/square.png", "compare")

        assert cache.query_image_map("1", f"{table_name}_squares") == ("/tmp/square.png", "compare", "")

        with sqlite3.connect(cache.cache_path) as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}

        assert f"{table_name}_squares" in tables


def test_upload_image_dispatches_supported_artwork_types():
    plex = plex_module.Plex.__new__(plex_module.Plex)
    plex.config = SimpleNamespace(tpdb_timer=None)
    plex.validate_image_size = lambda image: True
    plex.reload = lambda item, force=False: None

    cases = [
        ("poster", "poster", {"url": "https://example.com/poster.png"}),
        ("background", "background", {"url": "https://example.com/background.png"}),
        ("logo", "logo", {"url": "https://example.com/logo.png"}),
        ("square", "square", {"url": "https://example.com/square.png"}),
    ]

    for expected_type, image_type, expected_kwargs in cases:
        item = FakeUploadItem()
        image = ImageData("test", expected_kwargs["url"], image_type=image_type)

        assert plex._upload_image(item, image) is True
        assert item.calls == [(expected_type, expected_kwargs)]


def test_find_item_assets_reads_top_level_logo_and_square():
    with tempfile.TemporaryDirectory() as tempdir:
        item_dir = os.path.join(tempdir, "Sample")
        os.makedirs(item_dir)
        for filename in ["poster.png", "background.png", "logo.png", "square.png"]:
            with open(os.path.join(item_dir, filename), "wb") as handle:
                handle.write(b"test")

        plex = _build_asset_plex(tempdir)
        poster, background, logo, square, item_asset_directory, folder_name = plex.find_item_assets("Sample")

        assert poster.location.endswith("poster.png")
        assert background.location.endswith("background.png")
        assert logo.location.endswith("logo.png")
        assert square.location.endswith("square.png")
        assert item_asset_directory == item_dir
        assert folder_name == "Sample"


def test_find_item_assets_reads_flat_square_without_poster():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, "Sample_square.png"), "wb") as handle:
            handle.write(b"test")

        plex = _build_asset_plex(tempdir, asset_folders=False)
        poster, background, logo, square, item_asset_directory, folder_name = plex.find_item_assets("Sample")

        assert poster is None
        assert background is None
        assert logo is None
        assert square.location.endswith("Sample_square.png")
        assert item_asset_directory == tempdir
        assert folder_name == "Sample"


def test_find_item_assets_keeps_one_to_one_art_as_poster():
    with tempfile.TemporaryDirectory() as tempdir:
        item_dir = os.path.join(tempdir, "Sample")
        os.makedirs(item_dir)
        Image.new("RGB", (100, 100), color="white").save(os.path.join(item_dir, "cover.png"))

        plex = _build_asset_plex(tempdir, dimensional_asset_rename=True)
        poster, background, logo, square, _, _ = plex.find_item_assets("Sample")

        assert poster.location.endswith("poster.png")
        assert background is None
        assert logo is None
        assert square is None
        assert os.path.exists(os.path.join(item_dir, "poster.png"))
        assert not os.path.exists(os.path.join(item_dir, "square.png"))


def test_builder_lists_accept_logo_and_square_for_playlists_and_collectionless():
    for attribute in ["url_logo", "file_logo", "url_square", "file_square"]:
        assert attribute in playlist_attributes
        assert attribute in collectionless_details


def test_playlist_update_details_uploads_logo_and_square(monkeypatch):
    monkeypatch.setattr(builder_module, "logger", FakeLogger())

    fake_library = FakeArtworkLibrary()
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.name = "Test Playlist"
    builder.Type = "Playlist"
    builder.playlist = True
    builder.obj = SimpleNamespace(title="Test Playlist")
    builder.summaries = {}
    builder.details = {}
    builder.asset_directory = ["/tmp/assets"]
    builder.mapping_name = "Test Playlist"
    builder.library = fake_library
    builder.posters = {}
    builder.backgrounds = {}
    builder.logos = {}
    builder.squares = {}
    builder.url_theme = None
    builder.file_theme = None

    updated_details = builder.update_details()

    assert updated_details == ["Image"]
    assert fake_library.upload_calls == [
        {
            "poster": None,
            "background": None,
            "logo": "https://example.com/logo.png",
            "square": "https://example.com/square.png",
            "overlay": False,
        }
    ]
