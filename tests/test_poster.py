"""Tests for modules/poster.py — ImageData and friends."""

from __future__ import annotations

import modules.builder  # noqa: F401


class TestImageData:
    def test_stores_attributes(self, tmp_path):
        from modules.poster import ImageData

        path = tmp_path / "test.jpg"
        path.write_bytes(b"data")
        d = ImageData(
            "poster",
            str(path),
            prefix="test",
            image_type="poster",
            is_url=False,
            compare="abc",
        )
        assert d.attribute == "poster"
        assert d.compare == "abc"

    def test_url_mode_skips_file_check(self):
        from modules.poster import ImageData

        d = ImageData("poster", "http://example.com/poster.jpg", is_url=True)
        assert d.location == "http://example.com/poster.jpg"

    def test_str_lists_the_image_attributes(self, tmp_path):
        from modules.poster import ImageData

        path = tmp_path / "test.jpg"
        path.write_bytes(b"data")
        d = ImageData("poster", str(path))
        text = str(d)
        assert "'attribute': 'poster'" in text
        assert "test.jpg" in text


class TestKometaPoster:
    @staticmethod
    def config():
        import io
        from types import SimpleNamespace
        from unittest.mock import MagicMock

        from PIL import Image

        content = io.BytesIO()
        Image.new("RGBA", (10, 10), "red").save(content, format="PNG")
        requests = MagicMock()
        requests.image_content_types = ["image/png"]
        requests.get.return_value = SimpleNamespace(status_code=200, headers={"Content-Type": "image/png"}, content=content.getvalue())
        return SimpleNamespace(Requests=requests, GitHub=SimpleNamespace(configs_url="https://example.com/"), custom_repo="https://repo.example.com/")

    def test_text_only_without_bundled_images(self, tmp_path, monkeypatch):
        from pathlib import Path

        from PIL import Image

        from modules import poster

        source = Path(poster.__file__).resolve().parent.parent
        (tmp_path / "fonts").symlink_to(source / "fonts", target_is_directory=True)
        monkeypatch.setattr(poster, "__file__", str(tmp_path / "modules" / "poster.py"))
        monkeypatch.setattr(poster.util, "get_system_fonts", lambda: [])
        image = poster.KometaImage(self.config(), {"background_color": "#0B1F3A", "components": [{"text": "WEEK 7", "font_size": 260, "font_color": "#FFFFFF"}]}, "kometa_poster")
        try:
            result = image.save({"title": "Week 7"})
            path = Path(result.location)
            with Image.open(path) as rendered:
                assert rendered.size == (1000, 1500)
                assert rendered.getpixel((0, 0)) == (11, 31, 58)
            assert image.pmm_backgrounds == {}
            assert image.components[0].pmm_images == {}
            assert not (tmp_path / "defaults").exists()
        finally:
            image.cleanup()
        assert not path.exists()

    def test_remote_images_survive_until_cleanup(self):
        from pathlib import Path

        from PIL import Image

        from modules.poster import KometaImage

        image = KometaImage(self.config(), {"background_image": {"url": "https://example.com/bg.png"}, "components": [{"image": {"git": "image.png"}}]}, "kometa_poster", playlist=True)
        downloads = [Path(image.background_image), Path(image.components[0].image)]
        result = image.save({})
        with Image.open(result.location) as rendered:
            assert rendered.size == (1000, 1000)
        assert all(path.exists() for path in downloads)
        image.cleanup()
        assert not Path(result.location).exists()
        assert all(not path.exists() for path in downloads)

    def test_unknown_bundled_image_reports_validation_error(self):
        import pytest

        from modules.poster import KometaImage
        from modules.util import Failed

        with pytest.raises(Failed, match="pmm invalid"):
            KometaImage(self.config(), {"background_image": {"pmm": "missing"}, "components": [{"text": "Test"}]}, "kometa_poster")


class TestGeneratedPosterUpload:
    def test_upload_and_cleanup(self, monkeypatch):
        self.run_upload(monkeypatch, fail=False)

    def test_cleanup_after_upload_failure(self, monkeypatch):
        self.run_upload(monkeypatch, fail=True)

    @staticmethod
    def run_upload(monkeypatch, fail):
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import MagicMock

        import pytest

        from modules.builder import CollectionBuilder
        from modules.poster import KometaImage
        from tests.factories import make_builder

        monkeypatch.setattr("modules.builder.logger", MagicMock())
        image = KometaImage(TestKometaPoster.config(), {"background_color": "#0B1F3A", "components": [{"image": {"repo": "image.png"}}]}, "kometa_poster", playlist=True)
        paths = [Path(image.components[0].image)]
        library = MagicMock()
        library.collection_images = {}

        def upload(obj, poster, **kwargs):
            paths.append(Path(poster.location))
            assert all(path.exists() for path in paths)
            assert poster.attribute == "kometa_poster"
            assert not poster.is_url
            if fail:
                raise RuntimeError("upload failed")
            return True, False, False, False

        library.upload_images.side_effect = upload
        builder = make_builder(
            playlist=True,
            library=library,
            obj=SimpleNamespace(title="Week 7"),
            name="Week 7",
            mapping_name="Week 7",
            summaries={},
            collection_poster=image,
            backgrounds={},
            logos={},
            square_arts={},
            collection_logo=None,
            collection_square_art=None,
            url_theme=None,
            file_theme=None,
        )
        monkeypatch.setattr(builder, "_load_collection_assets", lambda: (None, None))
        monkeypatch.setattr(builder, "_pick_collection_artwork", lambda *args: None)
        if fail:
            with pytest.raises(RuntimeError, match="upload failed"):
                CollectionBuilder.update_details(builder)
        else:
            assert CollectionBuilder.update_details(builder) == ["Image"]
        library.upload_images.assert_called_once()
        assert len(paths) == 2
        assert all(not path.exists() for path in paths)
