import os
import shutil

import pytest
from PIL import Image, ImageDraw

from modules import people_render
from modules.people_render import SIZE, STYLES, PeopleRenderer, label_text
from modules.util import Failed


def _cutout(top=100, color=(200, 60, 40)):
    image = Image.new("RGBA", SIZE)
    draw = ImageDraw.Draw(image)
    draw.ellipse((250, top, 750, top + 700), fill=(*color, 255))
    draw.rectangle((150, top + 600, 850, SIZE[1]), fill=(*color, 255))
    return image


def _is_gray(pixel):
    return max(pixel[:3]) - min(pixel[:3]) <= 2


@pytest.fixture(scope="module")
def renderer():
    return PeopleRenderer()


@pytest.mark.parametrize("style", STYLES)
def test_every_style_renders_full_size_poster(renderer, style):
    poster = renderer.render(_cutout(), "Tom Hanks", style)
    assert poster.size == SIZE
    assert poster.mode == ("L" if style == "bw" else "RGB")


def test_diiivoy_subject_is_gray_and_diiivoycolor_keeps_color(renderer):
    gray_poster = renderer.render(_cutout(), "Tom Hanks", "diiivoy")
    color_poster = renderer.render(_cutout(), "Tom Hanks", "diiivoycolor")
    assert _is_gray(gray_poster.getpixel((500, 900)))
    assert not _is_gray(color_poster.getpixel((500, 900)))


@pytest.mark.parametrize("style", ["diiivoycolor", "rainier"])
def test_color_styles_keep_color_when_subject_starts_low(renderer, style):
    poster = renderer.render(_cutout(top=400), "Tom Hanks", style)
    assert not _is_gray(poster.getpixel((500, 900)))


@pytest.mark.parametrize("top, expected", [(20, people_render.SUBJECT_TOP), (400, 400)])
def test_subject_is_moved_down_to_fixed_top(top, expected):
    assert people_render.shifted_cutout(_cutout(top=top)).getchannel("A").getbbox()[1] == expected


def test_signature_subject_is_not_moved(renderer):
    poster = renderer.render(_cutout(top=500, color=(255, 255, 255)), "Tom Hanks", "signature")
    assert min(poster.getpixel((500, 520))) > 240


@pytest.mark.parametrize(
    "name, expected",
    [("Tom Hanks", "Tom Hanks"), ("Tom Hanks (2)", "Tom Hanks"), ("Tom Hanks 2", "Tom Hanks"), ("  Tom Hanks  ", "Tom Hanks")],
)
def test_label_text_strips_disambiguation(name, expected):
    assert label_text(name) == expected


def test_bw_label_wraps_long_names_after_first_word(renderer):
    label, size = renderer._bw_label("SAMUEL L. JACKSON", people_render.COMFORTAA)
    assert label == "SAMUEL\nL. JACKSON"
    assert size == people_render.NAME_SIZE


def test_bw_label_keeps_short_names_on_one_line(renderer):
    assert renderer._bw_label("TOM HANKS", people_render.COMFORTAA) == ("TOM HANKS", people_render.NAME_SIZE)


@pytest.mark.parametrize(
    "title, expected",
    [
        ("CHER", "CHER"),
        ("TOM HANKS", "TOM\nHANKS"),
        ("ROBERT DOWNEY JR.", "ROBERT\nDOWNEY JR."),
        ("SAMUEL L. JACKSON", "SAMUEL L.\nJACKSON"),
        ("ANNA MARIA DE FREITAS", "ANNA MARIA\nDE FREITAS"),
    ],
)
def test_rainier_label_wrapping(renderer, title, expected):
    assert renderer._rainier_label(title, people_render.COMFORTAA)[0] == expected


def test_long_names_are_fitted_inside_the_label_box(renderer):
    name = "Maximiliano Bartholomew Featherstonehaugh-Worthington"
    for style in STYLES:
        assert renderer.render(_cutout(), name, style).size == SIZE


def test_labels_are_uppercase_except_signature(renderer):
    assert renderer._resolve_label("Tom Hanks", "bw")[0] == "TOM HANKS"
    assert renderer._resolve_label("Tom Hanks", "signature")[0] == "Tom Hanks"


def test_label_falls_back_to_inter_when_style_font_lacks_glyphs(renderer):
    comfortaa = renderer._font_metrics(people_render.COMFORTAA).cmap
    inter = renderer._font_metrics(people_render.INTER).cmap
    missing = next(chr(c) for c in range(0x100, 0x2000) if chr(c).isalpha() and chr(c).upper() == chr(c) and c not in comfortaa and c in inter)
    assert renderer._resolve_label(f"Tom {missing}", "bw") == (f"TOM {missing}", people_render.INTER)


def test_unsupported_name_fails(renderer):
    with pytest.raises(Failed):
        renderer.render(_cutout(), "山田太郎", "bw")


def test_opaque_source_fails(renderer):
    with pytest.raises(Failed):
        renderer.render(Image.new("RGB", SIZE, "red"), "Tom Hanks", "bw")


def test_source_is_normalized_to_poster_size(renderer):
    large = _cutout().resize((2000, 3000))
    assert renderer.render(large, "Tom Hanks", "rainier").size == SIZE


def test_fingerprint_is_stable_and_differs_per_style(renderer):
    assert renderer.fingerprint("bw") == PeopleRenderer().fingerprint("bw")
    assert len({renderer.fingerprint(style) for style in STYLES}) == len(STYLES)


def test_fingerprint_changes_with_renderer_version(monkeypatch, renderer):
    before = renderer.fingerprint("rainier")
    monkeypatch.setattr(people_render, "RENDERER_VERSION", "test")
    assert PeopleRenderer().fingerprint("rainier") != before


def test_fingerprint_changes_with_artwork(monkeypatch, tmp_path, renderer):
    before = renderer.fingerprint("rainier")
    artwork = tmp_path / "rainier.png"
    shutil.copyfile(people_render.STYLE_ARTWORK["rainier"], artwork)
    with open(artwork, "ab") as handle:
        handle.write(b"\0")
    monkeypatch.setitem(people_render.STYLE_ARTWORK, "rainier", str(artwork))
    assert PeopleRenderer().fingerprint("rainier") != before
    assert PeopleRenderer().fingerprint("bw") == renderer.fingerprint("bw")


def test_save_writes_jpeg_without_leaving_temp_file(renderer, tmp_path):
    path = tmp_path / "rainier" / "T" / "Tom Hanks.jpg"
    renderer.save(renderer.render(_cutout(), "Tom Hanks", "rainier"), str(path))
    with Image.open(path) as saved:
        assert saved.format == "JPEG"
        assert saved.size == SIZE
    assert os.listdir(path.parent) == ["Tom Hanks.jpg"]
