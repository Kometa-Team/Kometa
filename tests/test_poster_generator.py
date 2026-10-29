import os
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

import modules.builder  # noqa: F401
from modules.poster import KometaImage
from modules.util import Failed


@pytest.mark.parametrize("options", [{}, {"style": "dual"}, {"style": "dual(red:blue)", "fade": "middle"}])
def test_generated_poster_is_stable(options):
    poster = KometaImage(None, {**options, "width": 120, "height": 180}, "kometa_poster")
    first = poster.save({"title": "A Collection"})
    second = poster.save({"title": "A Collection"})
    try:
        assert first.compare == second.compare
        with Image.open(first.location) as image:
            assert image.size == (120, 180)
    finally:
        os.remove(first.location)
        os.remove(second.location)


@pytest.mark.parametrize("options", [{}, True])
def test_default_text_and_placeholder(options):
    poster = KometaImage(None, options, "kometa_poster")
    with patch("modules.poster_generator.generate") as generate:
        result = poster.save({"title": "Pixar"})
    os.remove(result.location)
    assert generate.call_args.kwargs["text"] == "Pixar"
    assert poster.generator_options["text"] == "<<collection_name>>"
    assert poster.generator_options["font_path"].name == "Comfortaa-Medium.ttf"


@pytest.mark.parametrize("options", [None, False, {"style": "bad"}, {"fade": "bad"}, {"width": 0}, {"font_size": 0}, {"top_margin": 0.7, "bottom_margin": 0.4}, {"image_width": False}, {"font": "missing.ttf"}, {"typo": 1}])
def test_invalid_options(options):
    with pytest.raises(Failed):
        KometaImage(None, options, "kometa_poster")


def test_local_svg(tmp_path):
    path = tmp_path / "logo.svg"
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20" fill="red"/></svg>')
    poster = KometaImage(None, {"image": str(path), "text": "", "width": 100, "height": 150}, "kometa_poster")
    result = poster.save({"title": "Test"})
    try:
        with Image.open(result.location) as image:
            assert image.getpixel((50, 75))[0] > 200
    finally:
        os.remove(result.location)


def test_legacy_components():
    with patch("modules.poster.os.listdir", return_value=[]), patch("modules.poster.Component"):
        poster = KometaImage(None, {"components": [{"text": "<<title>>"}]}, "kometa_poster")
    assert not poster.generated


def test_picker_selects_generated_poster():
    from types import SimpleNamespace

    from modules.library import Library

    obj = SimpleNamespace()
    poster = KometaImage(None, {}, "kometa_poster")
    with patch("modules.library.logger", MagicMock()):
        assert Library.pick_image(obj, "Test", {"kometa_poster": poster}, False, False, None) is poster


def test_remote_svg_uses_browser_headers():
    from modules.poster_generator import load_overlay_source

    source = "https://example.com/logo.svg"
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20" fill="red"/></svg>'
    response = MagicMock()
    response.url = source
    response.iter_content.return_value = [svg]
    response.__enter__.return_value = response
    load_overlay_source.cache_clear()
    with patch("modules.poster_generator.requests.get", return_value=response) as get:
        image = load_overlay_source(source)
    assert image.getpixel((0, 0)) == (255, 0, 0, 255)
    assert get.call_args.kwargs["headers"] == {"User-Agent": "Mozilla/5.0", "Referer": "https://example.com/"}
    assert get.call_args.kwargs["stream"] is True
    response.raise_for_status.assert_called_once()
    load_overlay_source.cache_clear()


def test_remote_image_rejects_http_errors():
    import requests

    from modules.poster_generator import load_overlay_source

    response = MagicMock()
    response.__enter__.return_value = response
    response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
    with patch("modules.poster_generator.requests.get", return_value=response):
        with pytest.raises(requests.HTTPError):
            load_overlay_source("https://example.com/forbidden.svg")
    response.iter_content.assert_not_called()


@pytest.mark.parametrize("decoration,expected", [("upper", "WOW PIXAR"), ("lower", "wow pixar"), ("title", "Wow Pixar"), (" upper, lower, title ", "Wow Pixar"), ("bold, italic, upper", "WOW PIXAR")])
def test_decoration_applies_after_placeholders(decoration, expected):
    poster = KometaImage(None, {"text": "wow <<collection_name>>", "decoration": decoration}, "kometa_poster")
    with patch("modules.poster_generator.generate") as generate:
        result = poster.save({"title": "Pixar"})
    os.remove(result.location)
    assert generate.call_args.kwargs["text"] == expected


@pytest.mark.parametrize("decoration", ["bold", "italic", "bold, italic"])
def test_decorated_poster_renders(decoration):
    poster = KometaImage(None, {"decoration": decoration, "width": 160, "height": 240}, "kometa_poster")
    result = poster.save({"title": "Example"})
    try:
        with Image.open(result.location) as image:
            assert image.size == (160, 240)
    finally:
        os.remove(result.location)


def test_decoration_selects_matching_font_face():
    poster = KometaImage(None, {"font": "Roboto-Regular.ttf", "decoration": "bold, italic"}, "kometa_poster")
    assert poster.generator_options["font_path"].name == "Roboto-BoldItalic.ttf"
    assert poster.generator_options["synthetic_bold"] is False
    assert poster.generator_options["synthetic_italic"] is False


@pytest.mark.parametrize("decoration", ["unknown", "bold, typo", True, None, ["bold"]])
def test_invalid_decoration(decoration):
    with pytest.raises(Failed):
        KometaImage(None, {"decoration": decoration}, "kometa_poster")


@pytest.mark.parametrize("font_size", [1, 5, 10, 16, 32])
def test_explicit_small_font_size_is_respected(font_size):
    from pathlib import Path

    from modules.poster_generator import measure_wrapped_text

    font = Path(__file__).parents[1] / "fonts" / "Roboto-Regular.ttf"
    lines = measure_wrapped_text("Small text", font, font_size, 1000, 1500)
    assert [line["font_size"] for line in lines] == [font_size]


def test_small_font_size_renders_instead_of_leaving_previous_poster():
    poster = KometaImage(None, {"text": "Small text", "font_size": 10}, "kometa_poster")
    result = poster.save({"title": "Test"})
    try:
        with Image.open(result.location) as image:
            assert image.size == (1000, 1500)
    finally:
        os.remove(result.location)


def test_explicit_line_breaks_and_blank_lines_are_preserved():
    from pathlib import Path

    from modules.poster_generator import measure_wrapped_text

    font = Path(__file__).parents[1] / "fonts" / "Roboto-Regular.ttf"
    lines = measure_wrapped_text("Movie\nnight\n\nSomething for everyone", font, 30, 1000, 1500)
    assert [line["text"] for line in lines] == ["Movie", "night", "", "Something for everyone"]
    assert lines[2]["height"] > 0


@pytest.mark.parametrize("width", [500, 1000])
def test_font_size_is_pixels_independent_of_canvas_width(width):
    import tempfile
    from pathlib import Path

    from modules.poster_generator import generate

    font = Path(__file__).parents[1] / "fonts" / "Roboto-Regular.ttf"
    with tempfile.TemporaryDirectory() as directory:
        with patch("modules.poster_generator.compose_foreground", return_value=Image.new("RGB", (width, 750))) as compose:
            generate(1, Path(directory) / "test.png", text="Example", font_path=font, font_size=10, canvas_size=(width, 750))
        assert compose.call_args.kwargs["font_size"] == 10


@pytest.mark.parametrize("builders,filename", [(["imdb_chart"], "IMDb.png"), (["tmdb_trending_daily"], "TMDb.png"), (["plex_search"], "Plex.png"), (["smart_filter", "imdb_chart"], "IMDb.png"), (["tautulli_popular"], "Tautulli.png")])
def test_default_builder_logo_mapping(builders, filename):
    from modules.poster import default_builder_logo

    assert default_builder_logo(builders).endswith("/" + filename)


def test_unmapped_builder_does_not_get_logo():
    from modules.poster import default_builder_logo

    assert default_builder_logo(["label"]) is None


@pytest.mark.parametrize("data", [True, {}, {"text": "Chart"}])
def test_generated_chart_poster_gets_default_image(data):
    poster = KometaImage(None, data, "kometa_poster", builders=["imdb_chart"])
    assert poster.generator_options["image_path"].endswith("/IMDb.png")


@pytest.mark.parametrize("image", [None, "custom.png"])
def test_explicit_image_overrides_builder_logo(image):
    poster = KometaImage(None, {"image": image}, "kometa_poster", builders=["imdb_chart"])
    assert poster.generator_options["image_path"] == image
    assert poster.default_image is None


def test_unavailable_default_logo_falls_back_to_text():
    poster = KometaImage(None, True, "kometa_poster", builders=["imdb_chart"])
    with patch("modules.poster_generator.load_overlay_source", side_effect=ValueError("unavailable")), patch("modules.poster_generator.generate") as generate:
        result = poster.save({"title": "Chart"})
    os.remove(result.location)
    assert generate.call_args.kwargs["image_path"] is None
    assert generate.call_args.kwargs["text"] == "Chart"


@pytest.mark.parametrize("width", [0, 1, 7, 100])
def test_generated_border_draws_inwards(tmp_path, width):
    from modules.poster_generator import generate

    plain = tmp_path / "plain.png"
    bordered = tmp_path / "bordered.png"
    generate(42, plain, canvas_size=(60, 90))
    generate(42, bordered, canvas_size=(60, 90), border_width=width, border_color="#123456")
    with Image.open(plain) as original, Image.open(bordered) as result:
        assert result.size == original.size == (60, 90)
        for y in range(90):
            for x in range(60):
                edge = min(x, y, 59 - x, 89 - y) < width
                assert result.getpixel((x, y)) == ((18, 52, 86) if edge else original.getpixel((x, y)))


@pytest.mark.parametrize("options", [{"border_width": -1}, {"border_width": True}, {"border_width": 1.5}, {"border_width": None}, {"border_color": "invalid"}, {"border_color": None}])
def test_invalid_generated_border_options(options):
    with pytest.raises(Failed):
        KometaImage(None, options, "kometa_poster")


def test_generated_border_options_pass_to_renderer():
    poster = KometaImage(None, {"border_width": 12, "border_color": "#123456"}, "kometa_poster")
    with patch("modules.poster_generator.generate") as generate:
        result = poster.save({"title": "Test"})
    os.remove(result.location)
    assert generate.call_args.kwargs["border_width"] == 12
    assert generate.call_args.kwargs["border_color"] == "#123456"


@pytest.mark.parametrize("colour", ["white", ["red", "white", "blue"], "rainbow"])
def test_named_palette_and_rainbow_borders(tmp_path, colour):
    from modules.poster_generator import generate

    poster = KometaImage(None, {"border_width": 3, "border_color": colour}, "kometa_poster")
    assert poster.generator_options["border_color"] == colour
    plain = tmp_path / "plain.png"
    bordered = tmp_path / "border.png"
    generate(42, plain, canvas_size=(60, 90))
    generate(42, bordered, canvas_size=(60, 90), border_width=3, border_color=colour)
    with Image.open(plain) as original, Image.open(bordered) as result:
        assert result.size == (60, 90)
        assert result.crop((3, 3, 57, 87)).tobytes() == original.crop((3, 3, 57, 87)).tobytes()
        colours = {result.getpixel((x, 0)) for x in range(60)} | {result.getpixel((x, 89)) for x in range(60)}
        if colour == "white":
            assert colours == {(255, 255, 255)}
        elif isinstance(colour, list):
            assert len(colours) > 50
            assert result.getpixel((0, 0)) == (255, 0, 0)
        else:
            assert len(colours) > 50
            assert result.getpixel((0, 0)) == (255, 0, 0)


@pytest.mark.parametrize("colour", [[], ["white", "invalid"], [42], 42])
def test_invalid_border_palettes(colour):
    with pytest.raises(Failed):
        KometaImage(None, {"border_color": colour}, "kometa_poster")


@pytest.mark.parametrize("value", ["red, white, blue", " red ,white, blue "])
def test_comma_separated_border_matches_list(tmp_path, value):
    from modules.poster_generator import generate

    KometaImage(None, {"border_color": value}, "kometa_poster")
    first = tmp_path / "string.png"
    second = tmp_path / "list.png"
    generate(42, first, canvas_size=(60, 90), border_width=4, border_color=value)
    generate(42, second, canvas_size=(60, 90), border_width=4, border_color=["red", "white", "blue"])
    assert first.read_bytes() == second.read_bytes()


@pytest.mark.parametrize("value", ["red,,blue", "red,", ",", "red,invalid"])
def test_invalid_comma_separated_border(value):
    with pytest.raises(Failed):
        KometaImage(None, {"border_color": value}, "kometa_poster")


def test_border_rgb_function_remains_supported():
    from modules.poster_generator import border_palette

    assert border_palette("rgb(255, 0, 0)") == [(255, 0, 0)]


@pytest.mark.parametrize("colour", [["red", "blue"], "red, blue"])
def test_border_blends_colours_and_wraps_smoothly(colour):
    from modules.poster_generator import draw_border

    image = Image.new("RGB", (101, 101), "white")
    draw_border(image, 3, colour)
    assert image.getpixel((0, 0)) == (255, 0, 0)
    assert image.getpixel((100, 0)) == (128, 0, 128)
    assert image.getpixel((100, 100)) == (0, 0, 255)
    assert image.getpixel((0, 100)) == (128, 0, 128)
    assert image.getpixel((0, 1)) == (254, 0, 1)
    assert image.getpixel((50, 50)) == (255, 255, 255)


@pytest.mark.parametrize("decoration", ["underline", "strike", "sentence", "small_caps", "outline", "shadow", "bold, italic, small_caps, underline, strike, outline, shadow"])
def test_new_decorations_render_stably(decoration):
    poster = KometaImage(None, {"text": "Movie Night", "decoration": decoration, "width": 200, "height": 300, "font_size": 28}, "kometa_poster")
    first = poster.save({})
    second = poster.save({})
    try:
        assert first.compare == second.compare
        with Image.open(first.location) as image:
            assert image.size == (200, 300)
    finally:
        os.remove(first.location)
        os.remove(second.location)


def test_sentence_case_after_placeholder_substitution():
    poster = KometaImage(None, {"text": "<<title>>. ANOTHER sentence! NEXT? yes\nNEW LINE", "decoration": "sentence"}, "kometa_poster")
    with patch("modules.poster_generator.generate") as generate:
        image = poster.save({"title": "MOVIE NIGHT"})
    os.remove(image.location)
    assert generate.call_args.kwargs["text"] == "Movie night. Another sentence! Next? Yes\nNew line"


@pytest.mark.parametrize("options", [{"outline_width": -1}, {"outline_width": True}, {"outline_width": 101}, {"shadow_offset": 1.5}, {"shadow_offset": None}, {"outline_color": "invalid"}, {"shadow_color": []}])
def test_invalid_text_effect_options(options):
    with pytest.raises(Failed):
        KometaImage(None, options, "kometa_poster")


def test_caption_effect_pixels():
    from pathlib import Path

    from PIL import ImageFont

    from modules.poster_generator import decorated_caption

    font = ImageFont.truetype(str(Path("fonts/Comfortaa-Medium.ttf")), 40)

    def render(effects):
        return decorated_caption("Movie Night", font, (255, 255, 255), effects, "red", 2, "blue", 4, False, False)

    plain = render(())
    for effect in ("underline", "strike", "small_caps", "outline", "shadow"):
        result = render((effect,))
        assert result.tobytes() != plain.tobytes()
    outlined = render(("outline",))
    shadowed = render(("shadow",))
    assert any(pixel == (255, 0, 0, 255) for _, pixel in outlined.getcolors(outlined.width * outlined.height))
    assert any(pixel == (0, 0, 255, 255) for _, pixel in shadowed.getcolors(shadowed.width * shadowed.height))
    assert render(("small_caps",)).width < plain.width * 1.2
