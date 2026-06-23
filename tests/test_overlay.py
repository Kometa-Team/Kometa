"""Tests for modules/overlay.py — the Overlay class.

Focuses on overlay configuration parsing, coordinate calculations,
and comparison-string generation that can be tested without a full
Plex/Pillow rendering pipeline.
"""

from __future__ import annotations

import pytest

from modules.overlay import Overlay
from tests.conftest import FakeLogger

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def make_overlay(**attrs) -> Overlay:
    """Create a minimal Overlay via ``Overlay.__new__``."""
    ov = Overlay.__new__(Overlay)
    defaults = {
        "name": "Test Overlay",
        "mapping_name": "Test Overlay",
        "group": None,
        "weight": None,
        "font_name": None,
        "font_size": 36,
        "font_color": None,
        "stroke_color": None,
        "stroke_width": 0,
        "back_box": None,
        "back_color": None,
        "back_align": None,
        "back_radius": None,
        "back_padding": None,
        "back_line_color": None,
        "back_line_width": None,
        "scale_width": None,
        "scale_height": None,
        "addon_position": None,
        "addon_offset": 0,
        "horizontal_offset": None,
        "vertical_offset": None,
        "horizontal_align": None,
        "vertical_align": None,
        "backdrop_box": None,
        "backdrop_text": None,
        "prefix": "",
        "suppress": [],
        "keys": [],
        "updated": False,
        "image": None,
        "font": None,
        "path": None,
        "config": None,
        "library": None,
    }
    defaults.update(attrs)
    for key, value in defaults.items():
        setattr(ov, key, value)
    return ov


# ═══════════════════════════════════════════════════════════════════════
# has_coordinates
# ═══════════════════════════════════════════════════════════════════════


class TestHasCoordinates:
    def test_true_when_both_offsets_set(self):
        ov = make_overlay(horizontal_offset=10, vertical_offset=20)
        assert ov.has_coordinates() is True

    def test_false_when_horizontal_missing(self):
        ov = make_overlay(horizontal_offset=None, vertical_offset=20)
        assert ov.has_coordinates() is False

    def test_false_when_vertical_missing(self):
        ov = make_overlay(horizontal_offset=10, vertical_offset=None)
        assert ov.has_coordinates() is False

    def test_false_when_both_missing(self):
        ov = make_overlay(horizontal_offset=None, vertical_offset=None)
        assert ov.has_coordinates() is False


# ═══════════════════════════════════════════════════════════════════════
# get_overlay_compare
# ═══════════════════════════════════════════════════════════════════════


class TestGetOverlayCompare:
    def test_basic_name_only(self):
        """Stroke width (default 0) is appended because 0 is not None."""
        ov = make_overlay(name="Rating")
        assert ov.get_overlay_compare() == "Rating0"

    def test_with_group_and_weight(self):
        ov = make_overlay(name="Rating", group="Top", weight=100)
        result = ov.get_overlay_compare()
        assert result.startswith("RatingTop100")

    def test_with_coordinates(self):
        ov = make_overlay(name="Rating", horizontal_offset=10, vertical_offset=20, horizontal_align="left", vertical_align="top")
        # Order: h_align, h_offset, v_offset, v_align (not h_offset, h_align, v_offset, v_align)
        result = ov.get_overlay_compare()
        assert "left10" in result
        assert "20top" in result

    def test_with_font(self):
        ov = make_overlay(name="Rating", font_name="Arial", font_size=24)
        result = ov.get_overlay_compare()
        assert "Arial" in result
        assert "24" in result


# ═══════════════════════════════════════════════════════════════════════
# get_coordinates
# ═══════════════════════════════════════════════════════════════════════


class TestGetCoordinates:
    def test_returns_origin_when_no_coords_and_no_new_cords(self):
        ov = make_overlay()
        x, y = ov.get_coordinates((100, 100), (50, 50))
        assert x == 0
        assert y == 0

    def test_left_top_alignment(self):
        ov = make_overlay(horizontal_offset=10, vertical_offset=20, horizontal_align="left", vertical_align="top")
        x, y = ov.get_coordinates((100, 100), (50, 50))
        assert x == 10
        assert y == 20

    def test_right_alignment(self):
        ov = make_overlay(horizontal_offset=10, vertical_offset=20, horizontal_align="right", vertical_align="top")
        x, y = ov.get_coordinates((100, 100), (50, 50))
        # right: image_value (100) - over_value (50) - offset (10)
        assert x == 40
        assert y == 20

    def test_center_alignment(self):
        ov = make_overlay(horizontal_offset=5, vertical_offset=5, horizontal_align="center", vertical_align="center")
        x, y = ov.get_coordinates((100, 100), (50, 50))
        # center: int(image_value/2) - int(over_value/2) + offset
        # int(100/2) - int(50/2) + 5 = 50 - 25 + 5 = 30
        assert x == 30
        assert y == 30

    def test_bottom_alignment(self):
        ov = make_overlay(horizontal_offset=5, vertical_offset=5, horizontal_align="left", vertical_align="bottom")
        x, y = ov.get_coordinates((100, 100), (50, 50))
        # bottom: image_value (100) - over_value (50) - offset (5) = 45
        assert x == 5
        assert y == 45

    def test_percentage_offset(self):
        ov = make_overlay(horizontal_offset="50%", vertical_offset="25%", horizontal_align="left", vertical_align="top")
        x, y = ov.get_coordinates((100, 100), (50, 50))
        # 50% of 100 = 50, 25% of 100 = 25
        assert x == 50
        assert y == 25


# ═══════════════════════════════════════════════════════════════════════
# get_text_size
# ═══════════════════════════════════════════════════════════════════════


class TestGetTextSize:
    def test_returns_text_bounding_box(self):
        """get_text_size returns a tuple of 4 ints from PIL textbbox."""
        import PIL.Image as PILImage
        import PIL.ImageDraw as PILImageDraw

        ov = make_overlay(font=PILImageDraw.Draw(PILImage.new("RGBA", (100, 100))).getfont())
        bbox = ov.get_text_size("Hello")
        assert isinstance(bbox, tuple)
        assert len(bbox) == 4
        assert all(isinstance(v, int) for v in bbox)
