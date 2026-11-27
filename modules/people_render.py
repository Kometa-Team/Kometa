import hashlib
import math
import os
import re
import unicodedata
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from modules import util
from modules.font_layout import FontMetrics
from modules.util import Failed

logger = util.logger

# Bump whenever a change to this module alters rendered output, so cached posters are regenerated.
RENDERER_VERSION = "1"

SIZE = (1000, 1500)
STYLES = ("bw", "diiivoy", "diiivoycolor", "rainier", "signature")
SUBJECT_TOP = 247
JPEG_QUALITY = 95

code_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
asset_dir = os.path.join(code_base, "defaults", "images", "people")
font_dir = os.path.join(code_base, "fonts")

COMFORTAA = os.path.join(font_dir, "Comfortaa-Medium.ttf")
MONTSERRAT_LIGHT = os.path.join(font_dir, "Montserrat-Light.ttf")
FUGGLES = os.path.join(font_dir, "people", "Fuggles-Regular.ttf")
INTER = os.path.join(font_dir, "people", "Inter-Light.ttf")
MONTSERRAT_SEMIBOLD = os.path.join(font_dir, "people", "Montserrat-SemiBold.ttf")

BASE_ARTWORK = os.path.join(asset_dir, "base.png")
STYLE_ARTWORK = {
    "diiivoy": os.path.join(asset_dir, "diiivoy.png"),
    "diiivoycolor": os.path.join(asset_dir, "diiivoy.png"),
    "rainier": os.path.join(asset_dir, "rainier.png"),
    "signature": os.path.join(asset_dir, "signature.png"),
}
NAME_FONTS = {"bw": COMFORTAA, "rainier": COMFORTAA, "signature": FUGGLES, "diiivoy": INTER, "diiivoycolor": INTER}
FALLBACK_FONT = INTER
SUBSTITUTIONS = {"\u02bb": "\u2019"}
COLLECTION_TEXT = {
    "signature": {"font": MONTSERRAT_SEMIBOLD, "size": 46, "tracking": 6.25, "stroke": 0, "x": 321, "y": 1395},
    "rainier": {"font": MONTSERRAT_LIGHT, "size": 55, "tracking": 9.0, "stroke": 0, "x": 100, "y": 404},
    "diiivoy": {"font": MONTSERRAT_SEMIBOLD, "size": 50, "tracking": 41.5, "stroke": 0.5, "x": 154, "y": 1428},
    "diiivoycolor": {"font": MONTSERRAT_SEMIBOLD, "size": 50, "tracking": 41.5, "stroke": 0.5, "x": 154, "y": 1428},
}
NAME_SIZE = 91.5
DIIIVOY_NAME_SIZE = 95
FULL_WIDTH = 950
RAINIER_WIDTH = 800


def style_files(style):
    files = [BASE_ARTWORK, NAME_FONTS[style], FALLBACK_FONT]
    if style in STYLE_ARTWORK:
        files.extend([STYLE_ARTWORK[style], COLLECTION_TEXT[style]["font"]])
    return list(dict.fromkeys(files))


def label_text(name):
    name = re.sub(r"\(\d+\)$", "", name.strip()).strip()
    return re.sub(r"\d+$", "", name).strip()


def normalize_cutout(image):
    rgba = image.convert("RGBA")
    if rgba.width != SIZE[0]:
        height = max(1, math.floor(rgba.height * SIZE[0] / rgba.width + 0.5))
        rgba = rgba.convert("RGBa").resize((SIZE[0], height), Image.Resampling.LANCZOS).convert("RGBA")
    if rgba.height > SIZE[1]:
        top = (rgba.height - SIZE[1]) // 2
        rgba = rgba.crop((0, top, SIZE[0], top + SIZE[1]))
    canvas = Image.new("RGBA", SIZE)
    canvas.alpha_composite(rgba, (0, (SIZE[1] - rgba.height) // 2))
    return canvas


def shifted_cutout(image):
    bounds = image.getchannel("A").getbbox()
    canvas = Image.new("RGBA", SIZE)
    canvas.alpha_composite(image, (0, max(0, SUBJECT_TOP - bounds[1])))
    return canvas


def gray(image):
    luminance = image.convert("RGB").convert("L", (0.212656, 0.715158, 0.072186, 0))
    if image.mode == "RGBA":
        result = luminance.convert("RGBA")
        result.putalpha(image.getchannel("A"))
        return result
    return luminance


class PeopleRenderer:
    def __init__(self):
        self._art = {}
        self._metrics = {}
        self._fonts = {}
        self._fingerprints = {}

    def fingerprint(self, style):
        """Hash of everything that determines a style's output; any change invalidates that style's cached posters."""
        if style not in self._fingerprints:
            digest = hashlib.sha256(f"{RENDERER_VERSION}:{style}:{SIZE}:{JPEG_QUALITY}".encode("utf-8"))
            for path in style_files(style):
                with open(path, "rb") as handle:
                    digest.update(hashlib.sha256(handle.read()).digest())
            self._fingerprints[style] = digest.hexdigest()[:16]
        return self._fingerprints[style]

    def _artwork(self, path):
        if path not in self._art:
            with Image.open(path) as image:
                self._art[path] = image.convert("RGBA")
        return self._art[path]

    def _font_metrics(self, path):
        if path not in self._metrics:
            self._metrics[path] = FontMetrics(path, shaping=path == INTER)
        return self._metrics[path]

    def _font(self, path, size):
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(BytesIO(self._font_metrics(path).font_data), size, layout_engine=ImageFont.Layout.BASIC)
        return self._fonts[key]

    def _width(self, text, path, size):
        return self._font_metrics(path).width(text, size)

    def _resolve_label(self, name, style):
        text = label_text(name)
        if style != "signature":
            text = text.upper()
        if not text:
            raise Failed(f"People Poster Error: No label text for {name}")
        primary = NAME_FONTS[style]

        def supported(label, path):
            try:
                metrics = self._font_metrics(path)
                for line in label.splitlines():
                    metrics.glyphs(line)
                    metrics.layout(line, 100)
                return True
            except Failed:
                return False

        candidates = [(text, primary)]
        for form in ("NFC", "NFD"):
            normalized = unicodedata.normalize(form, text)
            if normalized != text:
                candidates.append((normalized, primary))
        substituted = text
        for old, new in SUBSTITUTIONS.items():
            substituted = substituted.replace(old, new)
        if substituted != text:
            candidates.append((substituted, primary))
        if primary != FALLBACK_FONT:
            candidates.append((text, FALLBACK_FONT))
        for label, path in candidates:
            if supported(label, path):
                return label, path
        raise Failed(f"People Poster Error: No bundled font can draw the name {name}")

    def _collection(self, poster, style):
        config = COLLECTION_TEXT[style]
        font = self._font(config["font"], config["size"])
        text = "COLLECTION"
        padding = math.ceil(config["size"] + config["stroke"])
        advance = sum(font.getlength(c) for c in text) + config["tracking"] * (len(text) - 1)
        layer = Image.new("RGBA", (math.ceil(advance) + padding * 2, padding * 4))
        draw = ImageDraw.Draw(layer)
        x = float(padding)
        for character in text:
            draw.text((x, padding), character, font=font, fill="white", stroke_width=config["stroke"], stroke_fill="white")
            x += font.getlength(character) + config["tracking"]
        layer = layer.crop(layer.getchannel("A").getbbox())
        poster.alpha_composite(layer, (config["x"], config["y"]))

    def _label(self, text, path, box, size=None, align="center", vertical="center"):
        lines = text.splitlines()
        metrics = self._font_metrics(path)
        if size is None:
            # Fit in half-point steps, the same granularity as whole points at 2000 x 3000.
            low, high = 2, 3200
            while low < high:
                mid = (low + high + 1) // 2
                width, height = metrics.fitted_extent(text, mid / 2, self._font(path, mid / 2).font.height)
                if width <= box[0] and height <= box[1]:
                    low = mid
                else:
                    high = mid - 1
            size = max(1, low - 1) / 2
        font = self._font(path, size)
        ascent, _ = font.getmetrics()
        layouts = [metrics.layout(line, size) for line in lines]
        widths = [layout[1] for layout in layouts]
        line_height = font.font.height
        pad = math.ceil(size)
        mask = Image.new("RGBA", (max(1, math.ceil(max(widths))) + pad * 2, line_height * len(lines) + pad * 2))
        draw = ImageDraw.Draw(mask)
        for index, (glyphs, width) in enumerate(layouts):
            x = (max(widths) - width) / 2 if align == "center" else 0
            for character, offset, y_offset in glyphs:
                draw.text((pad + x + offset, pad + ascent + index * line_height + y_offset), character, font=font, fill="white", anchor="ls")
        bounds = mask.getchannel("A").getbbox()
        if bounds is None:
            raise Failed("People Poster Error: Font produced no visible label")
        cropped = mask.crop(bounds)
        result = Image.new("RGBA", box)
        x = (box[0] - cropped.width) // 2 if align == "center" else 0
        y = box[1] - cropped.height if vertical == "south" else (box[1] - cropped.height) // 2
        result.alpha_composite(cropped, (x, y))
        return result

    def _bw_label(self, title, path):
        if self._width(title, path, NAME_SIZE) <= FULL_WIDTH:
            return title, NAME_SIZE
        words = title.split(" ")
        if 2 <= len(words) <= 4:
            rest = " ".join(words[1:])
            return f"{words[0]}\n{rest}", NAME_SIZE if self._width(rest, path, NAME_SIZE) <= FULL_WIDTH else None
        return title, None

    def _rainier_label(self, title, path):
        words = title.split(" ")

        def fits(*parts):
            return max(self._width(p, path, NAME_SIZE) for p in parts) <= RAINIER_WIDTH

        if len(words) == 1:
            return title, NAME_SIZE if fits(title) else None
        if len(words) == 2:
            return "\n".join(words), NAME_SIZE if fits(words[1]) else None
        if len(words) == 3:
            if "JR." in title:
                first, second = words[0], " ".join(words[1:])
            else:
                first, second = " ".join(words[:2]), words[2]
            return f"{first}\n{second}", NAME_SIZE if fits(first, second) else None
        if len(words) == 4:
            return f"{' '.join(words[:2])}\n{' '.join(words[2:])}", NAME_SIZE if fits(" ".join(words[1:])) else None
        return title, None

    def render(self, source, name, style):
        """Renders a person's transparent cutout as a 1000 x 1500 poster in the given style."""
        if style not in STYLES:
            raise Failed(f"People Poster Error: Unknown style {style}")
        cutout = normalize_cutout(source)
        alpha = cutout.getchannel("A")
        if not alpha.getbbox() or alpha.getextrema()[0] == 255:
            raise Failed(f"People Poster Error: Source image for {name} is not a transparent cutout")
        text, path = self._resolve_label(name, style)
        base = self._artwork(BASE_ARTWORK)

        if style == "bw":
            title, size = self._bw_label(text, path)
            poster = gray(Image.alpha_composite(base, shifted_cutout(cutout))).convert("RGBA")
            poster.alpha_composite(self._label(title, path, (FULL_WIDTH, 250), size), (25, 0))
            return poster.convert("L")

        if style == "signature":
            poster = Image.alpha_composite(Image.alpha_composite(base, cutout), self._artwork(STYLE_ARTWORK[style]))
            self._collection(poster, style)
            poster.alpha_composite(self._label(text, path, (FULL_WIDTH, 300), vertical="south"), (25, 1075))
            return poster.convert("RGB")

        shifted = shifted_cutout(cutout)
        subject = gray(shifted) if style == "diiivoy" else shifted
        poster = Image.alpha_composite(Image.alpha_composite(base, subject), self._artwork(STYLE_ARTWORK[style]))
        self._collection(poster, style)
        if style == "rainier":
            title, size = self._rainier_label(text, path)
            poster.alpha_composite(self._label(title, path, (RAINIER_WIDTH, 290), size, align="west"), (100, 40))
        else:
            size = DIIIVOY_NAME_SIZE if self._width(text, path, DIIIVOY_NAME_SIZE) <= FULL_WIDTH else None
            poster.alpha_composite(self._label(text, path, (FULL_WIDTH, 290), size), (25, 40))
        return poster.convert("RGB")

    @staticmethod
    def save(image, path):
        """Writes the poster as a JPEG, replacing any existing file only once the new one is complete."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        temp_path = f"{path}.tmp"
        image.save(temp_path, "JPEG", quality=JPEG_QUALITY, subsampling=0)
        os.replace(temp_path, path)
