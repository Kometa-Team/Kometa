import hashlib
import json
import os
import tempfile
import time
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import quote

from PIL import Image, ImageColor, ImageDraw, ImageFont

from modules import util
from modules.util import Failed

logger = util.logger


class ImageData:
    def __init__(self, attribute, location, prefix="", image_type="poster", is_url=True, compare=None):
        self.attribute = attribute
        self.location = location
        self.prefix = prefix
        self.is_poster = image_type == "poster"
        self.is_background = image_type == "background"
        self.is_logo = image_type == "logo"
        self.is_square_art = image_type == "square_art"
        self.is_url = is_url
        if compare:
            self.compare = compare
        elif is_url:
            self.compare = location
        else:
            file_stat = os.stat(location)
            self.compare = f"{os.path.abspath(location)}:{file_stat.st_size}:{file_stat.st_mtime_ns}"
        self.message = f"{prefix}{image_type} to [{'URL' if is_url else 'File'}] {location}"

    def __str__(self):
        return str(self.__dict__)


class ImageBase:
    def __init__(self, config, data):
        self.config = config
        self.data = data
        self.methods = {str(m).lower(): m for m in self.data}
        self.code_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.images_dir = os.path.join(self.code_base, "defaults", "images")

    def check_data(self, attr):
        if attr not in self.methods or not self.data[self.methods[attr]]:
            return None
        return self.data[self.methods[attr]]

    def check_file(self, attr, pmm_items, local=False, required=False):
        if attr not in self.methods or not self.data[self.methods[attr]]:
            if required:
                raise Failed(f"Posters Error: {attr} not found or is blank")
            return None, None
        file_data = self.data[self.methods[attr]]
        if isinstance(file_data, list):
            file_data = file_data[0]
        if not isinstance(file_data, dict):
            file_data = {"pmm": str(file_data)}
        if "pmm" in file_data and file_data["pmm"]:
            file_path = pmm_items[file_data["pmm"]] if file_data["pmm"] in pmm_items else file_data["pmm"]
            if os.path.exists(file_path):
                return file_path, os.path.getsize(file_path)
            raise Failed(f"Poster Error: {attr} pmm invalid. Options: {', '.join(pmm_items.keys())}")
        elif "file" in file_data and file_data["file"]:
            if os.path.exists(file_data["file"]):
                return file_data["file"], os.path.getsize(file_data["file"])
            raise Failed(f"Poster Error: {attr} file not found: {os.path.abspath(file_data['file'])}")
        elif local:
            return None, None
        elif "git" in file_data and file_data["git"]:
            url = f"{self.config.GitHub.configs_url}{file_data['git']}"
        elif "repo" in file_data and file_data["repo"]:
            url = f"{self.config.custom_repo}{file_data['repo']}"
        elif "url" in file_data and file_data["url"]:
            url = file_data["url"]
        else:
            return None, None

        response = self.config.Requests.get(url)
        if response.status_code >= 400:
            raise Failed(f"Poster Error: {attr} not found at: {url}")
        if "Content-Type" not in response.headers or response.headers["Content-Type"] not in self.config.Requests.image_content_types:
            raise Failed(f"Poster Error: {attr} not a png, jpg, or webp: {url}")
        if response.headers["Content-Type"] == "image/jpeg":
            ext = "jpg"
        elif response.headers["Content-Type"] == "image/webp":
            ext = "webp"
        else:
            ext = "png"
        num = ""
        image_path = os.path.join(self.images_dir, f"temp{num}.{ext}")
        while os.path.exists(image_path):
            num = 1 if not num else num + 1
            image_path = os.path.join(self.images_dir, f"temp{num}.{ext}")
        with open(image_path, "wb") as handler:
            handler.write(response.content)
        # Wait for file to be unlocked (up to 10 seconds)
        timeout = 10
        elapsed = 0
        while util.is_locked(image_path) and elapsed < timeout:
            time.sleep(0.1)
            elapsed += 0.1
        return image_path, url

    def check_color(self, attr):
        if attr not in self.methods or not self.data[self.methods[attr]]:
            return None
        try:
            return ImageColor.getcolor(self.data[self.methods[attr]], "RGBA")
        except ValueError:
            raise Failed(f"Poster Error: {attr}: {self.data[self.methods[attr]]} invalid")


class Component(ImageBase):
    def __init__(self, config, data):
        super().__init__(config, data)
        self.draw = ImageDraw.Draw(Image.new("RGBA", (0, 0)))
        self.back_color = self.check_color("back_color")
        self.back_radius = util.parse("Posters", "back_radius", self.data, datatype="int", methods=self.methods, default=0, minimum=0) if "back_radius" in self.methods else 0
        self.back_line_width = util.parse("Posters", "back_line_width", self.data, datatype="int", methods=self.methods, default=0, minimum=0) if "back_line_width" in self.methods else 0
        self.back_line_color = self.check_color("back_line_color")
        self.back_padding = util.parse("Posters", "back_padding", self.data, datatype="int", methods=self.methods, default=0, minimum=0) if "back_padding" in self.methods else 0
        self.back_align = util.parse("Posters", "back_align", self.data, methods=self.methods, default="center", options=["left", "right", "center", "top", "bottom"]) if "back_align" in self.methods else "center"

        self.back_width = 0
        if "back_width" in self.methods:
            if str(self.methods["back_width"]).lower() == "max":
                self.back_width = "max"
            else:
                self.back_width = util.parse("Posters", "back_width", self.data, methods=self.methods, datatype="int", minimum=0)
        self.back_height = 0
        if "back_height" in self.methods:
            if str(self.methods["back_height"]).lower() == "max":
                self.back_height = "max"
            else:
                self.back_height = util.parse("Posters", "back_height", self.data, methods=self.methods, datatype="int", minimum=0)
        self.has_back = True if self.back_color or self.back_line_width else False
        self.horizontal_offset, self.horizontal_align, self.vertical_offset, self.vertical_align = util.parse_cords(self.data, "component", err_type="Posters", default=(0, "center", 0, "center"))

        old_images_dir = os.path.join(self.images_dir, "images")
        self.pmm_images = {k[:-4]: os.path.join(old_images_dir, k) for k in os.listdir(old_images_dir)}
        self.image, self.image_compare = self.check_file("image", self.pmm_images)
        self.image_width = util.parse("Posters", "image_width", self.data, datatype="int", methods=self.methods, default=0, minimum=0, maximum=2000) if "image_width" in self.methods else 0
        self.image_color = self.check_color("image_color")

        self.text = None
        self.font_name = None
        self.font = None
        self.font_style = None
        self.addon_position = None
        self.text_align = util.parse("Posters", "text_align", self.data, methods=self.methods, default="center", options=["left", "right", "center"]) if "text_align" in self.methods else "center"
        self.font_size = util.parse("Posters", "font_size", self.data, datatype="int", methods=self.methods, default=163, minimum=1) if "font_size" in self.methods else 163
        self.font_color = self.check_color("font_color")
        self.stroke_color = self.check_color("stroke_color")
        self.stroke_width = util.parse("Posters", "stroke_width", self.data, datatype="int", methods=self.methods, default=0, minimum=0) if "stroke_width" in self.methods else 0
        self.addon_offset = util.parse("Posters", "addon_offset", self.data, datatype="int", methods=self.methods, default=0, minimum=0) if "stroke_width" in self.methods else 0
        if "text" in self.methods:
            font_base = os.path.join(self.code_base, "fonts")
            kometa_fonts = os.listdir(font_base)
            all_fonts = {s: s for s in util.get_system_fonts()}
            for font_name in kometa_fonts:
                all_fonts[font_name] = os.path.join(font_base, font_name)
            self.text = util.parse("Posters", "text", self.data, methods=self.methods, default="<<title>>")
            self.font_name, self.font_compare = self.check_file("font", all_fonts, local=True)
            if not self.font_name:
                self.font_name = all_fonts["Roboto-Medium.ttf"]
            self.font = ImageFont.truetype(self.font_name, self.font_size)
            if "font_style" in self.methods and self.data[self.methods["font_style"]]:
                try:
                    variation_names = [n.decode("utf-8") for n in self.font.get_variation_names()]
                    if self.data[self.methods["font_style"]] in variation_names:
                        self.font.set_variation_by_name(self.data[self.methods["font_style"]])
                        self.font_style = self.data[self.methods["font_style"]]
                    else:
                        raise Failed(f"Posters Error: Font Style {self.data[self.methods['font_style']]} not found. Options: {','.join(variation_names)}")
                except OSError:
                    raise Failed(f"Posters Warning: font: {self.font} does not have variations")
            self.addon_position = util.parse("Posters", "addon_position", self.data, methods=self.methods, options=["left", "right", "top", "bottom"]) if "addon_position" in self.methods else "left"

        if not self.image and not self.text:
            raise Failed("Posters Error: An image or text is required for each component")

    def apply_vars(self, item_vars):
        if self.text is None:
            return
        for var_key, var_data in item_vars.items():
            self.text = self.text.replace(f"<<{var_key}>>", str(var_data))

    def adjust_text_width(self, max_width):
        if self.text is None:
            return
        lines = []
        for line in self.text.split("\n"):
            for word in line.split(" "):
                word_length = self.draw.textlength(word, font=self.font)
                while word_length > max_width:
                    self.font_size -= 1
                    self.font = ImageFont.truetype(self.font_name, self.font_size)  # type: ignore[arg-type]
                    word_length = self.draw.textlength(word, font=self.font)
        for line in self.text.split("\n"):
            line_length = self.draw.textlength(line, font=self.font)
            if line_length <= max_width:
                lines.append(line)
                continue
            current_line = ""
            line_length = 0
            for word in line.split(" "):
                if current_line:
                    word = f" {word}"
                word_length = self.draw.textlength(word, font=self.font)
                if line_length + word_length <= max_width:
                    current_line += word
                    line_length += word_length
                else:
                    if current_line:
                        lines.append(current_line)
                    word = word.strip()
                    word_length = self.draw.textlength(word, font=self.font)
                    current_line = word
                    line_length = word_length
            if current_line:
                lines.append(current_line)
        self.text = "\n".join(lines)

    def get_compare_string(self):
        output = ""
        if self.text:
            output += f"{self.text} {self.text_align} {self.font_compare}"
            output += str(self.font_size)
            for value in [self.font_color, self.font_style, self.stroke_color, self.stroke_width]:
                if value:
                    output += f"{value}"
            if self.image:
                output += f"{self.addon_position} {self.addon_offset}"

        if self.image:
            output += str(self.image_compare)
            for value in [self.image_width, self.image_color]:
                if value:
                    output += str(value)

        output += f"({self.horizontal_offset},{self.horizontal_align},{self.vertical_offset},{self.vertical_align})"
        if self.has_back:
            for value in [self.back_color, self.back_radius, self.back_padding, self.back_align, self.back_width, self.back_height, self.back_line_color, self.back_line_width]:
                if value is not None:
                    output += f"{value}"
        return output

    def get_text_size(self, text):
        return self.draw.multiline_textbbox((0, 0), text, font=self.font)

    def get_coordinates(self, canvas_box, box, new_cords=None):
        canvas_width, canvas_height = canvas_box
        box_width, box_height = box

        def get_cord(value, image_value, over_value, align):
            value = int(image_value * 0.01 * int(value[:-1])) if str(value).endswith("%") else int(value)
            if align in ["right", "bottom"]:
                return image_value - over_value - value
            elif align == "center":
                return int(image_value / 2) - int(over_value / 2) + value
            else:
                return value

        if new_cords:
            ho, ha, vo, va = new_cords
        else:
            ho, ha, vo, va = self.horizontal_offset, self.horizontal_align, self.vertical_offset, self.vertical_align

        return get_cord(ho, canvas_width, box_width, ha), get_cord(vo, canvas_height, box_height, va)

    def get_generated_layer(self, canvas_box, new_cords=None):
        canvas_width, canvas_height = canvas_box
        generated_layer = None
        text_width, text_height = None, None
        if self.image:
            # Use context manager to ensure file descriptor is closed
            with Image.open(self.image) as img:
                image = img.copy()  # Copy to ensure data persists after context closes
            image_width, image_height = image.size
            if self.image_width:
                image_height = int(float(image_height) * float(self.image_width / float(image_width)))
                image_width = self.image_width
                image = image.resize((image_width, image_height), Image.Resampling.LANCZOS)  # noqa
            if self.image_color:
                r, g, b = self.image_color  # type: ignore[misc]
                pixels = image.load()
                if pixels is None:
                    raise Failed(f"Posters Error: failed to load pixels from image: {self.image}")
                for x in range(image_width):
                    for y in range(image_height):
                        if pixels[x, y][3] > 0:  # type: ignore[index] # noqa
                            pixels[x, y] = (r, g, b, pixels[x, y][3])  # type: ignore[index] # noqa
        else:
            image, image_width, image_height = None, 0, 0
        if self.text is not None:
            _, _, text_width, text_height = self.get_text_size(self.text)
            if image_width and self.addon_position in ["left", "right"]:
                box = (text_width + image_width + self.addon_offset, text_height if text_height > image_height else image_height)
            elif image_width:
                box = (text_width if text_width > image_width else image_width, text_height + image_height + self.addon_offset)
            else:
                box = (text_width, text_height)
        else:
            box = (image_width, image_height)
        box_width, box_height = box
        back_width = canvas_width if self.back_width == "max" else self.back_width if self.back_width else box_width
        back_height = canvas_height if self.back_height == "max" else self.back_height if self.back_height else box_height
        main_point = self.get_coordinates(canvas_box, (back_width, back_height), new_cords=new_cords)
        start_x, start_y = main_point

        if self.text is not None or self.has_back:
            generated_layer = Image.new("RGBA", canvas_box, (255, 255, 255, 0))
            drawing = ImageDraw.Draw(generated_layer)
            if self.has_back:
                cords = (start_x - self.back_padding, start_y - self.back_padding, start_x + back_width + self.back_padding, start_y + back_height + self.back_padding)  # type: ignore[operator]
                if self.back_radius:
                    drawing.rounded_rectangle(cords, fill=self.back_color, outline=self.back_line_color, width=self.back_line_width, radius=self.back_radius)
                else:
                    drawing.rectangle(cords, fill=self.back_color, outline=self.back_line_color, width=self.back_line_width)

            main_x, main_y = main_point
            if self.back_height and self.back_align in ["left", "right", "center", "bottom"]:
                main_y = start_y + (back_height - box_height) // (1 if self.back_align == "bottom" else 2)  # type: ignore[operator]
            if self.back_width and self.back_align in ["top", "bottom", "center", "right"]:
                main_x = start_x + (back_width - box_width) // (1 if self.back_align == "right" else 2)  # type: ignore[operator]

            addon_x = None
            addon_y = None
            if self.text is not None and self.image:
                # text_width and text_height are guaranteed set by the
                # `if self.text is not None:` block above; restate the
                # invariant for the type checker.
                if text_width is None or text_height is None:
                    raise Failed("Posters Error: text dimensions not computed")
                addon_x = main_x
                addon_y = main_y
                if self.addon_position == "left":
                    main_x = main_x + image_width + self.addon_offset
                elif self.addon_position == "right":
                    addon_x = main_x + text_width + self.addon_offset
                elif text_width < image_width:
                    main_x = main_x + ((image_width - text_width) / 2)
                elif text_width > image_width:
                    addon_x = main_x + ((text_width - image_width) / 2)

                if self.addon_position == "top":
                    main_y = main_y + image_height + self.addon_offset
                elif self.addon_position == "bottom":
                    addon_y = main_y + text_height + self.addon_offset
                elif text_height < image_height:
                    main_y = main_y + ((image_height - text_height) / 2)
                elif text_height > image_height:
                    addon_y = main_y + ((text_height - image_height) / 2)
            main_point = (int(main_x), int(main_y))

            if self.text is not None:
                drawing.multiline_text(main_point, self.text, font=self.font, fill=self.font_color, align=self.text_align, stroke_fill=self.stroke_color, stroke_width=self.stroke_width)
            if addon_x is not None:
                main_point = (addon_x, addon_y)

        return generated_layer, main_point, image


@lru_cache(maxsize=1)
def poster_builder_logos():
    """Ordered builder-to-logo mapping, stored separately for easy maintenance."""
    path = Path(__file__).resolve().parents[1] / "defaults" / "poster_builder_logos.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def default_builder_logo(builders):
    methods = {str(builder).lower() for builder in builders}
    for builder, image in poster_builder_logos().items():
        if builder in methods and image:
            return "https://raw.githubusercontent.com/Kometa-Team/Default-Images/master/chart/logos/" + quote(image, safe="/")
    return None


class KometaImage(ImageBase):
    def __init__(self, config, data, image_attr, playlist=False, builders=None):
        if data is True:
            data = {}
        if not isinstance(data, dict):
            raise Failed("Posters Error: kometa_poster must be true or a dictionary")
        super().__init__(config, data)
        self.generated = "components" not in self.methods
        if self.generated:
            self.default_image = default_builder_logo(builders) if builders and "image" not in self.methods else None
            self.generator_options = self._generator_options(playlist)
            if self.default_image:
                self.generator_options["image_path"] = self.default_image
            self.image_attr = image_attr
            return
        self.image_attr = image_attr
        self.backgrounds_dir = os.path.join(self.images_dir, "backgrounds")
        self.playlist = playlist
        self.pmm_backgrounds = {k[:-4]: os.path.join(self.backgrounds_dir, k) for k in os.listdir(self.backgrounds_dir)}

        self.background_image, self.background_compare = self.check_file("background_image", self.pmm_backgrounds)
        self.background_color = self.check_color("background_color")
        self.border_width = util.parse("Posters", "border_width", self.data, datatype="int", methods=self.methods, default=0, minimum=0) if "border_width" in self.methods else 0
        self.border_color = self.check_color("border_color")
        if "components" not in self.methods or not self.data[self.methods["components"]]:
            raise Failed("Posters Error: components attribute is required")
        self.components = [Component(self.config, d) for d in util.parse("Posters", "components", self.data, datatype="listdict", methods=self.methods)]

    def _generator_options(self, playlist):
        from modules import poster_generator as generator

        defaults = dict(
            text="<<collection_name>>",
            decoration="",
            style="single",
            image=None,
            font="Comfortaa-Medium.ttf",
            font_size=120,
            outline_color="#000000",
            outline_width=2,
            shadow_color="#000000",
            shadow_offset=4,
            border_width=0,
            border_color="#FFFFFF",
            text_color="#FFFFFF",
            text_width=0.75,
            image_text_gap=0.05,
            image_width=0.85,
            image_height=0.45,
            top_margin=0.05,
            bottom_margin=0.05,
            width=1000,
            height=1000 if playlist else 1500,
            seed=None,
            fade=None,
            color=None,
        )
        try:
            unknown = set(self.methods) - set(defaults)
            if unknown:
                raise ValueError(f"Unknown attributes: {', '.join(sorted(unknown))}")
            options: dict[str, Any] = {key: self.data[self.methods[key]] if key in self.methods else value for key, value in defaults.items()}
            for key in ("text", "image", "font", "style", "text_color", "fade", "color", "decoration"):
                if options[key] is not None and not isinstance(options[key], str):
                    raise ValueError(f"{key} must be a string")
            for key in ("width", "height", "seed", "font_size", "border_width"):
                value = options[key]
                if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
                    raise ValueError(f"{key} must be an integer")
            if options["border_width"] is None or options["border_width"] < 0:
                raise ValueError("border_width must be a nonnegative integer in pixels")
            generator.border_palette(options["border_color"])
            for key in ("outline_color", "shadow_color"):
                if not isinstance(options[key], str):
                    raise ValueError(f"{key} must be a colour string")
                ImageColor.getcolor(options[key], "RGB")
            for key in ("outline_width", "shadow_offset"):
                value = options[key]
                if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
                    raise ValueError(f"{key} must be an integer from 0 to 100 pixels")
            if options["font_size"] is None or options["font_size"] < 1:
                raise ValueError("font_size must be a positive integer in pixels")
            if options["width"] < 1 or options["height"] < 1 or options["width"] * options["height"] > 40_000_000:
                raise ValueError("Invalid canvas dimensions (maximum 40 million pixels)")
            for key in ("text_width", "image_width", "image_height", "image_text_gap", "top_margin", "bottom_margin"):
                value = options[key]
                allow_zero = key in ("image_text_gap", "top_margin", "bottom_margin")
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not (0 <= value < 1 if allow_zero else 0 < value <= 1):
                    raise ValueError(f"{key} must be a decimal fraction {'from 0 to less than 1' if allow_zero else 'greater than 0 and at most 1'}")
            if options["top_margin"] + options["bottom_margin"] >= 1:
                raise ValueError("Top and bottom margins must total less than 1")
            _, tones = generator.parse_style(options["style"])
            for tone in tones:
                generator.resolve_tone(generator.random.Random(0), tone)
            if options["fade"] is not None and options["fade"] not in generator.FADES:
                raise ValueError("fade must be top, bottom or middle")
            for key in ("color", "text_color"):
                if options[key] is not None:
                    generator.parse_hex_colour(options[key], key)
            decoration = options.pop("decoration")
            if not isinstance(decoration, str):
                raise ValueError("decoration must be a comma-separated string")
            self.decorations = [value.strip().lower() for value in decoration.split(",") if value.strip()]
            invalid = set(self.decorations) - {"bold", "italic", "upper", "lower", "title", "underline", "strike", "sentence", "small_caps", "outline", "shadow"}
            if invalid:
                raise ValueError(f"Unknown decoration: {', '.join(sorted(invalid))}")
            options["decorations"] = tuple(self.decorations)
            font = Path(options.pop("font"))
            if not font.is_file():
                font = Path(self.code_base) / "fonts" / font
            ImageFont.truetype(str(font), 12)
            if "bold" in self.decorations or "italic" in self.decorations:
                font, options["synthetic_bold"], options["synthetic_italic"] = generator.decorated_font(font, bold="bold" in self.decorations, italic="italic" in self.decorations)
            options["font_path"] = font
            options["image_path"] = options.pop("image")
            options["base_color"] = options.pop("color")
            options["fade_name"] = options.pop("fade")
            options["canvas_size"] = (options.pop("width"), options.pop("height"))
            return options
        except (ValueError, TypeError, OSError) as error:
            raise Failed(f"Posters Error: {error}") from error

    def _save_generated(self, item_vars):
        from modules.poster_generator import generate

        options = self.generator_options.copy()
        text = options["text"] or ""
        for key, value in {**item_vars, "collection_name": item_vars.get("collection_name", item_vars.get("title", ""))}.items():
            text = text.replace(f"<<{key}>>", str(value))
        for decoration in self.decorations:
            if decoration in ("upper", "lower", "title"):
                text = getattr(text, decoration)()
            elif decoration == "sentence":
                from modules.poster_generator import sentence_case

                text = sentence_case(text)
        options["text"] = text
        if self.default_image:
            from modules.poster_generator import load_overlay_source

            try:
                load_overlay_source(self.default_image)
            except Exception as error:
                if logger:
                    logger.warning(f"Posters Warning: Default builder logo unavailable ({error}); generating without an image")
                options["image_path"] = None
        # Stable defaults prevent random artwork changes on every run.
        signature = json.dumps(options, sort_keys=True, default=str)
        if options["seed"] is None:
            options["seed"] = int(hashlib.sha256(signature.encode()).hexdigest()[:16], 16)
        descriptor, path = tempfile.mkstemp(prefix="kometa_poster_", suffix=".png")
        os.close(descriptor)
        try:
            generate(output=Path(path), **options)
            # Compare rendered bytes so changes to local or remote assets are detected.
            compare = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            return ImageData(self.image_attr, path, is_url=False, compare=compare)
        except Exception as error:
            os.remove(path)
            raise Failed(f"Posters Error: {error}") from error

    def get_compare_string(self):
        output = ""
        for value in [self.background_compare, self.background_color, self.border_width, self.border_color]:
            if value:
                output += f"{value}"
        for component in self.components:
            output += component.get_compare_string()
        return output

    def save(self, item_vars):
        if self.generated:
            return self._save_generated(item_vars)
        image_path = os.path.join(self.images_dir, "temp_poster.png")
        if os.path.exists(image_path):
            os.remove(image_path)
        canvas_width = 1000
        canvas_height = 1000 if self.playlist else 1500
        canvas_box = (canvas_width, canvas_height)

        pmm_image = Image.new(mode="RGB", size=canvas_box, color=self.background_color)
        if self.background_image:
            with Image.open(self.background_image) as bkg_img:
                bkg_image = bkg_img.resize(canvas_box, Image.Resampling.LANCZOS)  # noqa
                pmm_image.paste(bkg_image, (0, 0), bkg_image)

        if self.border_width:
            draw = ImageDraw.Draw(pmm_image)
            draw.rectangle(((0, 0), canvas_box), outline=self.border_color, width=self.border_width)

        max_border_width = canvas_width - self.border_width - 100

        for component in self.components:
            if component.text:
                component.apply_vars(item_vars)
                component.adjust_text_width(component.back_width if component.back_width and component.back_width != "max" else max_border_width)
            generated_layer, image_point, image = component.get_generated_layer(canvas_box)
            if generated_layer:
                pmm_image.paste(generated_layer, (0, 0), generated_layer)
            if image:
                pmm_image.paste(image, image_point, image)

        pmm_image.save(image_path)

        return ImageData(self.image_attr, image_path, is_url=False, image_type="poster", compare=self.get_compare_string())
