"""Selecting People Posters: the people_poster attribute and legacy People-Images-<style> URLs resolve through the local generator."""

import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.poster import ImageData
from modules.util import Failed
from tests.factories import make_builder, make_image_requests, make_plex

LEGACY_URL = "https://raw.githubusercontent.com/Kometa-Team/People-Images-rainier/master/T/Images/Tom%20Hanks%20(2).jpg"
TMDB_URL = "https://image.tmdb.org/t/p/original/person.jpg"


class Generator:
    def __init__(self, result="render", tmp_path=None):
        self.result = result
        self.tmp_path = tmp_path
        self.specs = []

    def image(self, spec):
        self.specs.append(spec)
        if self.result == "missing":
            raise Failed(f"People Posters Error: No image for {spec['name']}")
        if self.result == "limit":
            return None
        if self.result == "url":
            return ImageData("people_poster", "https://raw.githubusercontent.com/Kometa-Team/People-Images-1500/HEAD/T/Images/Tom%20Hanks.jpg")
        path = os.path.join(str(self.tmp_path), f"{spec['style']}.jpg")
        with open(path, "wb") as handle:
            handle.write(b"jpeg")
        return ImageData("people_poster", path, is_url=False, compare=f"sha:{spec['style']}")


@pytest.fixture
def logger(monkeypatch):
    test_logger = MagicMock()
    monkeypatch.setattr("modules.library.logger", test_logger)
    monkeypatch.setattr("modules.builder.logger", test_logger)
    return test_logger


def _library(generator):
    requests, _, mock_head = make_image_requests()
    return make_plex(config=SimpleNamespace(Requests=requests, PeoplePosters=generator)), requests, mock_head


def test_people_poster_renders(tmp_path, logger):
    generator = Generator(tmp_path=tmp_path)
    library, _, _ = _library(generator)
    image = library.pick_image("Tom Hanks", {"people_poster": {"name": "Tom Hanks", "style": "bw"}, "tmdb_person": TMDB_URL}, False, False, None)
    assert image.attribute == "people_poster" and image.compare == "sha:bw"
    assert generator.specs == [{"name": "Tom Hanks", "style": "bw"}]


def test_missing_person_falls_back_to_tmdb(logger):
    library, _, _ = _library(Generator("missing"))
    image = library.pick_image("Tom Hanks", {"people_poster": {"name": "Tom Hanks", "style": "bw"}, "tmdb_person": TMDB_URL}, False, False, None)
    assert image.attribute == "tmdb_person" and image.location == TMDB_URL
    logger.warning.assert_called_once()


def test_render_limit_leaves_current_poster_unchanged(logger):
    library, _, _ = _library(Generator("limit"))
    assert library.pick_image("Tom Hanks", {"people_poster": {"name": "Tom Hanks", "style": "bw"}, "tmdb_person": TMDB_URL}, False, False, None) is None


def test_explicit_poster_wins_without_rendering(tmp_path, logger):
    generator = Generator(tmp_path=tmp_path)
    library, _, _ = _library(generator)
    image = library.pick_image("Tom Hanks", {"url_poster": "https://example.com/p.jpg", "people_poster": {"name": "Tom Hanks", "style": "bw"}}, False, False, None)
    assert image.location == "https://example.com/p.jpg"
    assert generator.specs == []


def test_legacy_url_is_generated_locally(tmp_path, logger):
    generator = Generator(tmp_path=tmp_path)
    library, _, _ = _library(generator)
    image = library.pick_image("Tom Hanks", {"url_poster": LEGACY_URL, "tmdb_person": TMDB_URL}, False, False, None)
    assert generator.specs == [{"name": "Tom Hanks (2)", "style": "rainier"}]
    assert image.attribute == "people_poster" and not image.is_url


def test_legacy_url_untouched_when_people_posters_unavailable(logger):
    library, _, _ = _library(None)
    image = library.pick_image("Tom Hanks", {"url_poster": LEGACY_URL}, False, False, None)
    assert image.attribute == "url_poster" and image.location == LEGACY_URL


def test_people_poster_skipped_when_people_posters_unavailable(logger):
    library, _, _ = _library(None)
    image = library.pick_image("Tom Hanks", {"people_poster": {"name": "Tom Hanks", "style": "bw"}, "tmdb_person": TMDB_URL}, False, False, None)
    assert image.attribute == "tmdb_person"
    logger.error.assert_called_once()


def test_original_style_uses_url_path(logger):
    library, _, _ = _library(Generator("url"))
    image = library.pick_image("Tom Hanks", {"people_poster": {"name": "Tom Hanks", "style": "original"}}, False, False, None)
    assert image.is_url and image.location.endswith("Tom%20Hanks.jpg")


def test_generated_poster_is_copied_to_asset_folder(tmp_path, logger):
    library, _, _ = _library(Generator(tmp_path=tmp_path))
    assets = tmp_path / "assets"
    assets.mkdir()
    image = library.pick_image("Tom Hanks", {"people_poster": {"name": "Tom Hanks", "style": "bw"}}, False, True, str(assets), image_name="poster")
    assert image.attribute == "asset_directory"
    assert image.location == str(assets / "poster.jpg")
    assert (assets / "poster.jpg").read_bytes() == b"jpeg"


def test_existing_asset_wins_over_generated_copy(tmp_path, logger):
    library, _, _ = _library(Generator(tmp_path=tmp_path))
    asset = ImageData("asset_directory", str(tmp_path / "existing.jpg"), is_url=False, compare="x")
    images = {"people_poster": {"name": "Tom Hanks", "style": "bw"}, "asset_directory": asset}
    assert library.pick_image("Tom Hanks", images, False, True, str(tmp_path), image_name="poster") is asset


def test_builder_skips_validation_for_generated_legacy_url(logger):
    requests, _, mock_head = make_image_requests()
    builder = make_builder(config=SimpleNamespace(Requests=requests, PeoplePosters=Generator()), posters={})
    builder._poster("url_poster", LEGACY_URL)
    assert builder.posters == {"url_poster": LEGACY_URL}
    mock_head.assert_not_called()


def test_builder_stores_people_poster_spec(logger):
    builder = make_builder(config=SimpleNamespace(PeoplePosters=Generator()), posters={})
    builder._poster("people_poster", {"Name": "Tom Hanks", "Style": "Signature"})
    assert builder.posters == {"people_poster": {"name": "Tom Hanks", "style": "signature"}}


def test_builder_rejects_invalid_people_poster(logger):
    builder = make_builder(config=SimpleNamespace(PeoplePosters=Generator()), posters={})
    with pytest.raises(Failed, match="style sepia is invalid"):
        builder._poster("people_poster", {"name": "Tom Hanks", "style": "sepia"})
