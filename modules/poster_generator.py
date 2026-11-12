"""Procedural backgrounds and foreground layout for generated Kometa posters."""

from __future__ import annotations

import colorsys
import random
import re
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont

SIZE = (1000, 1500)
FADES = ("top", "bottom", "middle")
BREAKER_WORDS = {"the", "a", "and"}


def fade_overlay(size: tuple[int, int], style: str) -> Image.Image:
    """Procedurally recreate the soft black overlays in the reference posters."""
    w, h = size
    small_w = max(96, round(w / 8))
    small_h = max(144, round(h / 8))
    alpha = Image.new("L", (small_w, small_h))
    px = alpha.load()
    assert px is not None
    for y in range(small_h):
        v = y / max(1, small_h - 1)
        for x in range(small_w):
            u = x / max(1, small_w - 1)
            if style == "top":
                amount = 0.36 + 0.39 * (1 - v) ** 1.45
            elif style == "bottom":
                amount = 0.36 + 0.39 * v**1.45
            elif style == "middle":
                vertical = abs(v - 0.46) / 0.54
                horizontal = abs(u - 0.54) / 0.75
                radial = min(1.0, (vertical**2 + 0.30 * horizontal**2) ** 0.5)
                amount = 0.31 + 0.44 * min(1.0, radial**1.3)
            else:
                raise ValueError(f"Unknown fade: {style}")
            px[x, y] = round(max(0.0, min(1.0, amount)) * 255)
    alpha = alpha.resize(size, Image.Resampling.BICUBIC)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    overlay.putalpha(alpha)
    return overlay


def random_colour(rng: random.Random) -> str:
    # Saturated, medium-bright jewel tones like the example posters.
    h = rng.random()
    s = rng.uniform(0.65, 0.98)
    v = rng.uniform(0.46, 0.80)
    rgb = colorsys.hsv_to_rgb(h, s, v)
    return "#" + "".join(f"{round(c * 255):02X}" for c in rgb)


COLOUR_FAMILIES: dict[str, tuple[float, float]] = {
    "red": (0.97, 0.03),
    "orange": (0.05, 0.10),
    "yellow": (0.12, 0.17),
    "lime": (0.18, 0.26),
    "green": (0.26, 0.40),
    "teal": (0.42, 0.50),
    "cyan": (0.48, 0.56),
    "blue": (0.56, 0.68),
    "indigo": (0.68, 0.74),
    "purple": (0.74, 0.84),
    "pink": (0.86, 0.96),
    "magenta": (0.88, 0.96),
}


def normalise_hex_colour(value: str) -> str:
    return "#" + bytes(parse_hex_colour(value, "colour")).hex().upper()


def family_hue(rng: random.Random, family: str) -> float:
    family = family.lower()
    if family not in COLOUR_FAMILIES:
        supported = ", ".join(sorted(COLOUR_FAMILIES))
        raise ValueError(f"Unknown colour family {family!r}. Supported families: {supported}")
    start, end = COLOUR_FAMILIES[family]
    if start <= end:
        hue = rng.uniform(start, end)
    else:
        span = (1.0 - start) + end
        hue = (start + rng.random() * span) % 1.0
    return hue


def random_colour_from_family(rng: random.Random, family: str | None = None) -> str:
    # Saturated, medium-bright jewel tones. If a family is provided, keep the
    # hue within that range while still randomising the shade.
    if family:
        h = family_hue(rng, family)
    else:
        h = rng.random()
    s = rng.uniform(0.62, 0.98)
    v = rng.uniform(0.44, 0.84)
    rgb = colorsys.hsv_to_rgb(h, s, v)
    return "#" + "".join(f"{round(c * 255):02X}" for c in rgb)


def parse_style(style: str) -> tuple[str, tuple[str | None, str | None]]:
    style = (style or "single").strip()
    if style == "single":
        return "single", (None, None)
    if style == "dual":
        return "dual", (None, None)
    match = re.fullmatch(r"dual\(([^:()]+):([^:()]+)\)", style, flags=re.IGNORECASE)
    if match:
        left = match.group(1).strip()
        right = match.group(2).strip()
        return "dual", (left, right)
    raise ValueError("style must be one of: single, dual, dual(family1:family2) or dual(#RRGGBB:#RRGGBB)")


def resolve_tone(rng: random.Random, token: str | None) -> str:
    if token is None:
        return random_colour(rng)
    token = token.strip()
    if re.fullmatch(r"#[0-9A-Fa-f]{6}", token):
        return normalise_hex_colour(token)
    return random_colour_from_family(rng, token)


def build_background_base(rng: random.Random, canvas_size: tuple[int, int], style: str, explicit_color: str | None = None) -> tuple[Image.Image, str]:
    mode, tokens = parse_style(style)
    if explicit_color and mode != "single":
        raise ValueError("--color can only be used with --style single")

    if mode == "single":
        colour = normalise_hex_colour(explicit_color) if explicit_color else random_colour(rng)
        rgb = parse_hex_colour(colour, "color")
        return Image.new("RGB", canvas_size, rgb), colour

    colour_a = resolve_tone(rng, tokens[0])
    colour_b = resolve_tone(rng, tokens[1])
    rgb_a = parse_hex_colour(colour_a, "color_a")
    rgb_b = parse_hex_colour(colour_b, "color_b")

    width, height = canvas_size
    direction = rng.choice(("vertical", "horizontal", "diagonal_down", "diagonal_up"))
    base = Image.new("RGB", canvas_size)
    px = base.load()
    assert px is not None

    for y in range(height):
        for x in range(width):
            if direction == "vertical":
                t = y / max(1, height - 1)
            elif direction == "horizontal":
                t = x / max(1, width - 1)
            elif direction == "diagonal_down":
                t = (x + y) / max(1, (width - 1) + (height - 1))
            else:  # diagonal_up
                t = (x + (height - 1 - y)) / max(1, (width - 1) + (height - 1))
            px[x, y] = tuple(round(rgb_a[i] + (rgb_b[i] - rgb_a[i]) * t) for i in range(3))

    return base, f"{colour_a}->{colour_b} ({direction})"


def jpeg_roundtrip(image: Image.Image, quality: int = 92) -> Image.Image:
    with BytesIO() as stream:
        image.convert("RGB").save(stream, "JPEG", quality=quality, subsampling=0)
        stream.seek(0)
        with Image.open(stream) as decoded:
            return decoded.convert("RGB")


def parse_hex_colour(value: str, name: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value or ""):
        raise ValueError(f"{name} must be in #RRGGBB format")
    r, g, b = bytes.fromhex(value[1:])
    return r, g, b


def border_palette(value: str | list[str]) -> list[tuple[int, int, int]]:
    """Validate a solid colour, an ordered palette, or the rainbow keyword."""

    def rgb_colour(colour: str) -> tuple[int, int, int]:
        rgb = ImageColor.getcolor(colour, "RGB")
        if not isinstance(rgb, tuple) or len(rgb) != 3:
            raise ValueError(f"Expected an RGB colour: {colour}")
        return rgb[0], rgb[1], rgb[2]

    if isinstance(value, str):
        value = value.strip()
        if value.lower() == "rainbow":
            return []
        # Preserve colour functions such as rgb(255, 0, 0).
        try:
            return [rgb_colour(value)]
        except ValueError:
            values = [colour.strip() for colour in value.split(",")]
    else:
        values = value if isinstance(value, list) else [value]
    if not values or any(not isinstance(colour, str) for colour in values):
        raise ValueError("border_color must be a colour, a nonempty list of colours, or rainbow")
    return [rgb_colour(colour) for colour in values]


def draw_border(image: Image.Image, width: int, colour: str | list[str]) -> None:
    palette = border_palette(colour)
    if len(palette) == 1:
        ImageDraw.Draw(image).rectangle((0, 0, image.width - 1, image.height - 1), outline=palette[0], width=width)
        return
    pixels = image.load()
    if pixels is None:
        raise ValueError("Cannot draw a border without image pixels")
    for inset in range(min(width, (min(image.size) + 1) // 2)):
        left, top = inset, inset
        right, bottom = image.width - 1 - inset, image.height - 1 - inset
        perimeter = max(1, 2 * (right - left + bottom - top))

        def paint(x, y, distance):
            fraction = distance / perimeter
            if palette:
                position = fraction * len(palette)
                index = int(position)
                blend = position - index
                start, end = palette[index % len(palette)], palette[(index + 1) % len(palette)]
                rgb = tuple(round(a + (b - a) * blend) for a, b in zip(start, end))
            else:
                rgb = tuple(round(channel * 255) for channel in colorsys.hsv_to_rgb(fraction, 1, 1))
            pixels[x, y] = rgb

        for x in range(left, right + 1):
            paint(x, top, x - left)
            paint(x, bottom, right - left + bottom - top + right - x)
        for y in range(top + 1, bottom):
            paint(right, y, right - left + y - top)
            paint(left, y, 2 * (right - left) + bottom - top + bottom - y)


def decorated_font(font_path: Path, *, bold: bool, italic: bool) -> tuple[Path, bool, bool]:
    """Prefer a matching face; synthesise only styles absent from the font family."""
    face = ImageFont.truetype(str(font_path), 12)
    family, current_style = face.getname()
    current_style = current_style or ""
    want_bold = bold or "bold" in current_style.lower()
    want_italic = italic or any(value in current_style.lower() for value in ("italic", "oblique"))
    candidates = []
    for path in sorted(font_path.parent.iterdir(), key=lambda path: (path != font_path, path.name)):
        if path.suffix.lower() not in (".ttf", ".otf"):
            continue
        try:
            candidate_family, style = ImageFont.truetype(str(path), 12).getname()
        except OSError:
            continue
        if candidate_family != family:
            continue
        style = style or ""
        is_bold = "bold" in style.lower()
        is_italic = any(value in style.lower() for value in ("italic", "oblique"))
        if (is_bold and not want_bold) or (is_italic and not want_italic):
            continue
        score = int(is_bold == want_bold) + int(is_italic == want_italic)
        candidates.append((score, path, want_bold and not is_bold, want_italic and not is_italic))
    if candidates:
        _, path, synthetic_bold, synthetic_italic = max(candidates, key=lambda candidate: candidate[0])
        return path, synthetic_bold, synthetic_italic
    return font_path, bold, italic


def load_font(font_path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not font_path.is_file():
        raise FileNotFoundError(f"Font not found: {font_path}")
    return ImageFont.truetype(str(font_path), size=size)


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return round(right - left), round(bottom - top)


def wrap_text(words: list[str], draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text, preferring breaker words at the end of a line when possible."""
    lines: list[str] = []
    current: list[str] = []
    i = 0

    while i < len(words):
        word = words[i]
        candidate = " ".join(current + [word]) if current else word
        candidate_width, _ = text_bbox(draw, candidate, font)

        if candidate_width <= max_width:
            current.append(word)
            i += 1
            continue

        if current:
            # If the previous word is a breaker and adding it still fits, keep it on this line.
            if word.lower() in BREAKER_WORDS:
                breaker_candidate = " ".join(current + [word])
                breaker_width, _ = text_bbox(draw, breaker_candidate, font)
                if breaker_width <= max_width:
                    current.append(word)
                    i += 1
            lines.append(" ".join(current))
            current = []
        else:
            # Single long word; keep it as its own line and scale that line later.
            lines.append(word)
            i += 1

    if current:
        lines.append(" ".join(current))
    return lines


def measure_wrapped_text(text: str, font_path: Path, base_font_size: int, max_width: int, max_height: int, line_spacing_ratio: float = 0.18, min_font_size: int = 16) -> list[dict[str, Any]]:
    """Measure wrapped text and shrink the overall font if the block is too tall.

    Long single-word lines are individually downscaled to fit the max width.
    """
    scratch = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(scratch)
    paragraphs = [line.split() for line in text.split("\n")]
    if not any(paragraphs):
        return []

    font_size = max(1, base_font_size)
    # The fitting floor must not reject an explicitly requested smaller font.
    min_font_size = min(font_size, max(1, min_font_size))
    while font_size >= min_font_size:
        base_font = load_font(font_path, font_size)
        lines = [line for words in paragraphs for line in (wrap_text(words, draw, base_font, max_width) if words else [""])]
        gap = max(1, round(font_size * line_spacing_ratio))
        rendered: list[dict[str, Any]] = []
        total_height = 0

        for index, line in enumerate(lines):
            line_font_size = font_size
            line_font = base_font
            line_width, line_height = text_bbox(draw, line, line_font)
            if not line:
                line_height = text_bbox(draw, "Ag", line_font)[1]

            if line_width > max_width:
                scale = max_width / line_width
                line_font_size = max(1, int(font_size * scale))
                while line_font_size > 1 and text_bbox(draw, line, load_font(font_path, line_font_size))[0] > max_width:
                    line_font_size -= 1
                line_font = load_font(font_path, line_font_size)
                line_width, line_height = text_bbox(draw, line, line_font)

            rendered.append(
                {
                    "text": line,
                    "font": line_font,
                    "font_size": line_font_size,
                    "width": line_width,
                    "height": line_height,
                    "gap_after": gap if index < len(lines) - 1 else 0,
                }
            )
            total_height += line_height + (gap if index < len(lines) - 1 else 0)

        if total_height <= max_height:
            return rendered

        next_size = int(font_size * 0.92)
        if next_size >= font_size:
            next_size = font_size - 1
        font_size = next_size

    raise ValueError("Text could not be fitted into the available poster area")


def _decode_overlay(data: bytes, source: str) -> Image.Image:
    """Read a raster image or convert SVG vector markup to a transparent PNG."""
    is_svg = source.lower().split("?")[0].endswith(".svg") or b"<svg" in data[:4096].lower()
    if is_svg:
        try:
            import resvg_py
        except ImportError as exc:
            raise RuntimeError("SVG support requires resvg-py. Install it with: pip install resvg-py") from exc
        # Render vector at poster-relevant resolution, preserving aspect ratio.
        data = resvg_py.svg_to_bytes(svg_string=data.decode("utf-8-sig"), width=1500)

    try:
        with Image.open(BytesIO(data)) as image:
            image.load()
            if image.width * image.height > 40_000_000:
                raise ValueError("Image exceeds 40 million pixels")
            return image.convert("RGBA")
    except Exception as exc:
        raise ValueError(f"Could not decode image from {source!r}. " "Supply a direct image URL (not a web page or Markdown link).") from exc


@lru_cache(maxsize=8)
def load_overlay_source(source: str) -> Image.Image:
    """Load local or remote images, including SVG (requires resvg-py)."""
    # A markdown link like [https://...](https://...) is not a bare URL.
    if source.startswith("[") and "](" in source:
        raise ValueError("Pass a plain URL in image, not a Markdown-formatted link.")
    scheme = urlsplit(source).scheme.lower()
    if scheme in ("http", "https"):
        # Some image hosts reject downloads without a browser agent and referrer.
        parsed = urlsplit(source)
        headers = {"User-Agent": "Mozilla/5.0", "Referer": f"{parsed.scheme}://{parsed.netloc}/"}
        limit = 20 * 1024 * 1024
        with requests.get(source, headers=headers, timeout=20, stream=True) as response:
            response.raise_for_status()
            if urlsplit(response.url).scheme.lower() not in ("http", "https"):
                raise ValueError("Image URL redirected to a non-HTTP(S) location")
            data = bytearray()
            for chunk in response.iter_content(chunk_size=65536):
                data.extend(chunk)
                if len(data) > limit:
                    raise ValueError("Image URL exceeds the 20 MB download limit")
        return _decode_overlay(bytes(data), source)

    # Windows drive paths such as C:\\images\\logo.png still work.
    if scheme and not re.match(r"^[A-Za-z]:[\\/]", source):
        raise ValueError("Only local paths and HTTP(S) image URLs are supported")
    path = Path(source)
    if not path.is_file():
        raise FileNotFoundError(f"Overlay image not found: {path}")
    if path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError("Image exceeds the 20 MB file limit")
    return _decode_overlay(path.read_bytes(), source)


def prepare_overlay_image(image_path: str | Path, canvas_size: tuple[int, int], max_width_ratio: float = 0.75, max_height_ratio: float = 1 / 3, forced_max_height: int | None = None) -> Image.Image:
    overlay = load_overlay_source(str(image_path)).copy()

    max_width = round(canvas_size[0] * max_width_ratio)
    max_height = round(canvas_size[1] * max_height_ratio)
    if forced_max_height is not None:
        max_height = min(max_height, forced_max_height)

    if max_width < 1 or max_height < 1:
        raise ValueError("No space available for the overlay image")

    scale = min(max_width / overlay.width, max_height / overlay.height, 1.0)
    if scale < 1.0:
        new_size = (
            max(1, round(overlay.width * scale)),
            max(1, round(overlay.height * scale)),
        )
        overlay = overlay.resize(new_size, Image.Resampling.LANCZOS)
    return overlay


def sentence_case(text: str) -> str:
    return re.sub(r"(^|[.!?]\s+|\n)([^\W\d_])", lambda match: match[1] + match[2].upper(), text.lower())


def decorated_caption(text, font, fill, decorations, outline_color, outline_width, shadow_color, shadow_offset, synthetic_bold, synthetic_italic):
    """Render one line to a tightly bounded layer, including all text effects."""
    small = ImageFont.truetype(font.path, max(1, round(font.size * 0.75)))
    glyphs = [(char.upper(), small if char.islower() else font) for char in text] if "small_caps" in decorations else [(text, font)]
    ascent = max(face.getmetrics()[0] for _, face in glyphs)
    descent = max(face.getmetrics()[1] for _, face in glyphs)
    stroke = max(1, round(font.size / 40)) if synthetic_bold else 0
    padding = font.size + stroke
    mask = Image.new("L", (max(1, round(sum(face.getlength(char) for char, face in glyphs))) + padding * 2, ascent + descent + padding * 2))
    draw = ImageDraw.Draw(mask)
    x = padding
    for char, face in glyphs:
        draw.text((x, padding + ascent), char, font=face, anchor="ls", fill=255, stroke_width=stroke)
        x += face.getlength(char)
    thickness = max(1, round(font.size / 18))
    for name, y in (("underline", padding + ascent + thickness), ("strike", padding + ascent - round(font.size * 0.3))):
        if name in decorations:
            draw.line((padding, y, x, y), fill=255, width=thickness)
    if synthetic_italic:
        shift = round(mask.height * 0.22)
        mask = mask.transform((mask.width + shift, mask.height), Image.Transform.AFFINE, (1, 0.22, -shift, 0, 1, 0), resample=Image.Resampling.BICUBIC)
    box = mask.getbbox()
    if box:
        mask = mask.crop(box)
    outline = outline_width if "outline" in decorations else 0
    offset = shadow_offset if "shadow" in decorations else 0
    expanded = Image.new("L", (mask.width + 2 * outline + offset, mask.height + 2 * outline + offset))
    expanded.paste(mask, (outline, outline))
    layer = Image.new("RGBA", expanded.size)
    if "shadow" in decorations:
        shadow = Image.new("L", expanded.size)
        shadow.paste(expanded, (offset, offset))
        layer.paste(ImageColor.getrgb(shadow_color), (0, 0), shadow)
    if outline:
        edge = expanded.filter(ImageFilter.MaxFilter(2 * outline + 1))
        ink = Image.new("RGBA", expanded.size, outline_color)
        ink.putalpha(edge)
        layer.alpha_composite(ink)
    ink = Image.new("RGBA", expanded.size, fill)
    ink.putalpha(expanded)
    layer.alpha_composite(ink)
    return layer


def compose_foreground(
    background: Image.Image,
    *,
    text: str | None,
    font_path: Path | None,
    font_size: int,
    text_color: str,
    image_path: str | Path | None,
    top_margin_ratio: float = 0.05,
    bottom_gap_ratio: float = 0.05,
    image_text_gap_ratio: float = 0.05,
    text_width_ratio: float = 0.75,
    image_width_ratio: float = 0.85,
    image_height_ratio: float = 0.45,
    decorations: tuple[str, ...] = (),
    outline_color: str = "#000000",
    outline_width: int = 2,
    shadow_color: str = "#000000",
    shadow_offset: int = 4,
    synthetic_bold: bool = False,
    synthetic_italic: bool = False,
) -> Image.Image:
    """Place optional centred image and centred text as one content block.

    When both image and text are present, they are scaled down together as a
    single block so the image is not disproportionately squeezed just to keep
    the original text size.
    """
    if not (text and text.strip()) and image_path is None:
        return background

    canvas = background.convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    fill = parse_hex_colour(text_color, "text_color")

    safe_top = round(canvas.height * top_margin_ratio)
    safe_bottom = canvas.height - round(canvas.height * bottom_gap_ratio)
    if safe_bottom <= safe_top:
        raise ValueError("No content area remains after margins")

    area_height = safe_bottom - safe_top
    text_max_width = round(canvas.width * text_width_ratio)
    min_font_size = max(1, round(canvas.width * 0.016))
    base_gap = round(canvas.height * image_text_gap_ratio)

    def build_block(scale: float):
        scaled_font_size = max(1, round(font_size * scale))
        scaled_gap = round(base_gap * scale) if (image_path is not None and text and text.strip()) else 0

        text_lines: list[dict[str, Any]] = []
        text_height = 0
        if text and text.strip():
            if font_path is None:
                raise ValueError("A font path is required when using text")
            # Give the measurer the full safe height; overall fit is checked below.
            text_lines = measure_wrapped_text(
                text.strip(),
                font_path,
                scaled_font_size,
                text_max_width,
                area_height,
                min_font_size=min_font_size,
            )
            if set(decorations) & {"underline", "strike", "small_caps", "outline", "shadow"}:
                for entry in text_lines:
                    layer = decorated_caption(entry["text"], entry["font"], fill, decorations, outline_color, outline_width, shadow_color, shadow_offset, synthetic_bold, synthetic_italic)
                    if layer.width > text_max_width:
                        layer = layer.resize((text_max_width, max(1, round(layer.height * text_max_width / layer.width))), Image.Resampling.LANCZOS)
                    entry["layer"] = layer
                    entry["height"] = layer.height
            text_height = sum(int(entry["height"]) + int(entry["gap_after"]) for entry in text_lines)
            if text_height > area_height and text_lines and "layer" in text_lines[0]:
                fit = area_height / text_height
                for entry in text_lines:
                    layer = entry["layer"]
                    layer = layer.resize((max(1, int(layer.width * fit)), max(1, int(layer.height * fit))), Image.Resampling.LANCZOS)
                    entry.update(layer=layer, height=layer.height, gap_after=int(entry["gap_after"] * fit))
                text_height = sum(int(entry["height"]) + int(entry["gap_after"]) for entry in text_lines)

        overlay_image: Image.Image | None = None
        overlay_width = 0
        overlay_height = 0
        if image_path is not None:
            overlay_image = prepare_overlay_image(
                image_path,
                canvas.size,
                max_width_ratio=image_width_ratio * scale,
                max_height_ratio=image_height_ratio * scale,
            )
            overlay_width, overlay_height = overlay_image.size

        total_height = overlay_height + (scaled_gap if overlay_image is not None and text_lines else 0) + text_height
        return {
            "scale": scale,
            "text_lines": text_lines,
            "text_height": text_height,
            "overlay_image": overlay_image,
            "overlay_width": overlay_width,
            "overlay_height": overlay_height,
            "gap": scaled_gap if overlay_image is not None and text_lines else 0,
            "total_height": total_height,
        }

    # If only one element is present, let its dedicated sizing logic do the work.
    # If both are present, shrink both together until the combined block fits.
    has_text = bool(text and text.strip())
    has_image = image_path is not None

    block = None
    if has_text and has_image:
        scale = 1.0
        while scale >= 0.12:
            candidate = build_block(scale)
            if candidate["total_height"] <= area_height:
                block = candidate
                break
            next_scale = scale * 0.94
            if next_scale >= scale:
                next_scale = scale - 0.01
            scale = next_scale
        if block is None:
            raise ValueError("Image and text could not be fitted into the safe poster area")
    else:
        block = build_block(1.0)
        if block["total_height"] > area_height:
            raise ValueError("Content could not be fitted into the safe poster area")

    y = safe_top + (area_height - int(block["total_height"])) // 2

    overlay_image = block["overlay_image"]
    if overlay_image is not None:
        x = (canvas.width - int(block["overlay_width"])) // 2
        canvas.alpha_composite(overlay_image, (x, y))
        y += int(block["overlay_height"]) + int(block["gap"])

    for entry in block["text_lines"]:
        line = str(entry["text"])
        line_font = entry["font"]
        line_width = int(entry["width"])
        line_height = int(entry["height"])
        x = (canvas.width - line_width) // 2
        if "layer" in entry:
            layer = entry["layer"]
            canvas.alpha_composite(layer, ((canvas.width - layer.width) // 2, y))
        elif synthetic_bold or synthetic_italic:
            stroke = max(1, round(line_font.size / 40)) if synthetic_bold else 0
            left, top, right, bottom = line_font.getbbox(line, stroke_width=stroke)
            layer = Image.new("RGBA", (max(1, right - left), max(1, bottom - top)))
            ImageDraw.Draw(layer).text((-left, -top), line, font=line_font, fill=fill, stroke_width=stroke, stroke_fill=fill)
            if synthetic_italic:
                skew = 0.22
                shift = round(layer.height * skew)
                layer = layer.transform((layer.width + shift, layer.height), Image.Transform.AFFINE, (1, skew, -shift, 0, 1, 0), resample=Image.Resampling.BICUBIC)
            if layer.width > text_max_width:
                layer = layer.resize((text_max_width, max(1, round(layer.height * text_max_width / layer.width))), Image.Resampling.LANCZOS)
            canvas.alpha_composite(layer, ((canvas.width - layer.width) // 2, y))
        else:
            draw.text((x, y), line, font=line_font, fill=fill)
        y += line_height + int(entry["gap_after"])

    return canvas.convert("RGB")


def generate(
    seed: int,
    output: Path,
    fade_name: str | None = None,
    base_color: str | None = None,
    style: str = "single",
    text: str | None = None,
    font_path: Path | None = None,
    font_size: int = 120,
    text_color: str = "#FFFFFF",
    image_path: str | Path | None = None,
    image_text_gap: float = 0.05,
    text_width: float = 0.75,
    image_width: float = 0.85,
    image_height: float = 0.45,
    top_margin: float = 0.05,
    bottom_margin: float = 0.05,
    canvas_size: tuple[int, int] = SIZE,
    decorations: tuple[str, ...] = (),
    outline_color: str = "#000000",
    outline_width: int = 2,
    shadow_color: str = "#000000",
    shadow_offset: int = 4,
    synthetic_bold: bool = False,
    synthetic_italic: bool = False,
    border_width: int = 0,
    border_color: str | list[str] = "#FFFFFF",
) -> tuple[str, str, str]:
    # Repeatable artwork does not require cryptographic randomness.
    rng = random.Random(seed)  # nosec B311
    fade = fade_name or rng.choice(tuple(FADES))
    overlay = fade_overlay(canvas_size, fade)

    # Match the source composer's background construction.
    background_base, palette = build_background_base(rng, canvas_size, style, base_color)
    base = jpeg_roundtrip(background_base, 92)
    composite = base.convert("RGBA")
    composite.alpha_composite(overlay)
    result = jpeg_roundtrip(composite.convert("RGB"), 92)

    if (text and text.strip()) or image_path is not None:
        if text and text.strip() and font_path is None:
            raise ValueError("A font path is required when using text")
        result = compose_foreground(
            result,
            text=text,
            font_path=font_path,
            font_size=font_size,
            text_color=text_color,
            image_path=image_path,
            image_text_gap_ratio=image_text_gap,
            text_width_ratio=text_width,
            image_width_ratio=image_width,
            image_height_ratio=image_height,
            top_margin_ratio=top_margin,
            bottom_gap_ratio=bottom_margin,
            decorations=decorations,
            outline_color=outline_color,
            outline_width=outline_width,
            shadow_color=shadow_color,
            shadow_offset=shadow_offset,
            synthetic_bold=synthetic_bold,
            synthetic_italic=synthetic_italic,
        )

    if border_width:
        draw_border(result, border_width, border_color)

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() in (".jpg", ".jpeg"):
        result.save(output, "JPEG", quality=100, subsampling=0)
    elif output.suffix.lower() == ".png":
        result.save(output, "PNG")
    else:
        raise ValueError("Output file must end in .jpg, .jpeg or .png")
    return palette, fade, style
