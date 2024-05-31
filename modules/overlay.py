import os, re, time
from datetime import datetime
from modules import util
from modules.util import Failed
from PIL import Image, ImageColor, ImageDraw, ImageFont
from plexapi.audio import Album
from plexapi.video import Episode

logger = util.logger

portrait_dim = (1000, 1500)
landscape_dim = (1920, 1080)
square_dim = (1000, 1000)
old_special_text = [f"{a}{s}" for a in ["audience_rating", "critic_rating", "user_rating"] for s in ["", "0", "%", "#"]]
rating_sources = [
    "tmdb_rating", "imdb_rating", "trakt_user_rating", "omdb_rating", "mdb_rating", "mdb_average_rating",
    "mdb_imdb_rating", "mdb_metacritic_rating", "mdb_metacriticuser_rating", "mdb_trakt_rating", "mdb_tomatoes_rating",
    "mdb_tomatoesaudience_rating", "mdb_tmdb_rating", "mdb_letterboxd_rating", "mdb_myanimelist_rating",
    "anidb_rating", "anidb_average_rating", "anidb_score_rating", "mal_rating"
]
float_vars = ["audience_rating", "critic_rating", "user_rating"] + rating_sources
int_vars = ["runtime", "season_number", "episode_number", "episode_count", "versions"]
date_vars = ["originally_available"]
types_for_var = {
    "movie_show_season_episode_artist_album": ["runtime", "user_rating", "title"],
    "movie_show_episode_album": ["critic_rating", "originally_available"],
    "movie_show_season_episode": ["tmdb_rating"],
    "show_season_artist_album": ["total_runtime"],
    "movie_show_episode": ["audience_rating", "content_rating", "tmdb_rating", "imdb_rating"],
    "movie_show": [
        "original_title", "trakt_user_rating", "omdb_rating", "mdb_rating", "mdb_average_rating", "mdb_imdb_rating",
        "mdb_metacritic_rating", "mdb_metacriticuser_rating", "mdb_trakt_rating", "mdb_tomatoes_rating",
        "mdb_tomatoesaudience_rating", "mdb_tmdb_rating", "mdb_letterboxd_rating", "mdb_myanimelist_rating",
        "anidb_rating", "anidb_average_rating", "anidb_score_rating", "mal_rating"
    ],
    "movie_episode": ["versions", "bitrate"],
    "season_episode": ["show_title", "season_number"],
    "show_season": ["episode_count"],
    "movie": ["edition"],
    "episode": ["season_title", "episode_number"]
}
var_mods = {
    "bitrate": ["", "H", "L"],
    "originally_available": ["", "["],
    "runtime": ["", "H", "M"],
    "total_runtime": ["", "H", "M"],
}
for mod in float_vars:
    var_mods[mod] = ["", "%", "#", "/"]
for mod in ["title", "content_rating", "original_title", "edition", "show_title", "season_title"]:
    var_mods[mod] = ["", "U", "L", "P"]
for mod in ["season_number", "episode_number", "episode_count", "versions"]:
    var_mods[mod] = ["", "W", "WU", "WL", "0", "00"]
single_mods = list(set([m for a, ms in var_mods.items() for m in ms if len(m) == 1]))
double_mods = list(set([m for a, ms in var_mods.items() for m in ms if len(m) == 2]))
vars_by_type = {
    "movie": [f"{item}{m}" for check, sub in types_for_var.items() for item in sub for m in var_mods[item] if "movie" in check],
    "show": [f"{item}{m}" for check, sub in types_for_var.items() for item in sub for m in var_mods[item] if "show" in check],
    "season": [f"{item}{m}" for check, sub in types_for_var.items() for item in sub for m in var_mods[item] if "season" in check],
    "episode": [f"{item}{m}" for check, sub in types_for_var.items() for item in sub for m in var_mods[item] if "episode" in check],
    "artist": [f"{item}{m}" for check, sub in types_for_var.items() for item in sub for m in var_mods[item] if "artist" in check],
    "album": [f"{item}{m}" for check, sub in types_for_var.items() for item in sub for m in var_mods[item] if "album" in check],
}

def get_canvas_size(item):
    if isinstance(item, Episode):
        return landscape_dim
    elif isinstance(item, Album):
        return square_dim
    else:
        return portrait_dim

class Overlay:
    def __init__(self, config, library, overlay_file, original_mapping_name, overlay_data, suppress, level):
        self.config = config
        self.requests = self.config.Requests
        self.cache = self.config.Cache
        self.library = library
        self.overlay_file = overlay_file
        self.original_mapping_name = original_mapping_name
        self.data = overlay_data
        self.level = level
        self.keys = []
        self.updated = False
        self.image = None
        self.backdrop_box = None
        self.backdrop_text = None
        self.group = None
        self.queue = None
        self.queue_name = None
        self.weight = None
        self.path = None
        self.font = None
        self.font_name = None
        self.font_size = 36
        self.font_color = None
        self.stroke_color = None
        self.stroke_width = 0
        self.addon_offset = 0
        self.addon_position = None
        self.back_width = None
        self.back_height = None
        self.special_text = None

        logger.debug("")
        logger.debug("Validating Method: overlay")
        logger.debug(f"Value: {self.data}")
        if not isinstance(self.data, dict):
            self.data = {"name": str(self.data)}
            logger.warning(f"Overlay Warning: No overlay attribute using mapping name {self.data} as the overlay name")
        if "name" not in self.data or not self.data["name"]:
            raise Failed(f"Overlay Error: overlay must have the name attribute")
        self.name = str(self.data["name"])

        self.prefix = f"Overlay File ({self.overlay_file.file_num}) "

        self.mapping_name = f"{self.prefix}{self.original_mapping_name}"
        self.suppress = [f"{self.prefix}{s}" for s in suppress]

        if "group" in self.data and self.data["group"]:
            self.group = str(self.data["group"])
        if "queue" in self.data and self.data["queue"]:
            self.queue_name = str(self.data["queue"])
            if self.queue_name not in self.overlay_file.queue_names:
                raise Failed(f"Overlay Error: queue: {self.queue_name} not found")
            self.queue = self.overlay_file.queue_names[self.queue_name]
        if "weight" in self.data:
            self.weight = util.parse("Overlay", "weight", self.data["weight"], datatype="int", parent="overlay", minimum=0)
        if "group" in self.data and (self.weight is None or not self.group):
            raise Failed(f"Overlay Error: overlay attribute's group requires the weight attribute")
        elif "queue" in self.data and (self.weight is None or not self.queue_name):
            raise Failed(f"Overlay Error: overlay attribute's queue requires the weight attribute")
        elif self.group and self.queue_name:
            raise Failed(f"Overlay Error: overlay attribute's group and queue cannot be used together")
        self.horizontal_offset, self.horizontal_align, self.vertical_offset, self.vertical_align = util.parse_cords(self.data, "overlay")

        if (self.horizontal_offset is None and self.vertical_offset is not None) or (self.vertical_offset is None and self.horizontal_offset is not None):
            raise Failed(f"Overlay Error: overlay attribute's horizontal_offset and vertical_offset must be used together")

        def color(attr):
            if attr in self.data and self.data[attr]:
                try:
                    return ImageColor.getcolor(self.data[attr], "RGBA")
                except ValueError:
                    raise Failed(f"Overlay Error: overlay {attr}: {self.data[attr]} invalid")
        self.back_color = color("back_color")
        self.back_radius = util.parse("Overlay", "back_radius", self.data["back_radius"], datatype="int", parent="overlay") if "back_radius" in self.data and self.data["back_radius"] else None
        self.back_line_width = util.parse("Overlay", "back_line_width", self.data["back_line_width"], datatype="int", parent="overlay") if "back_line_width" in self.data and self.data["back_line_width"] else None
        self.back_line_color = color("back_line_color")
        self.back_padding = util.parse("Overlay", "back_padding", self.data["back_padding"], datatype="int", parent="overlay", minimum=0, default=0) if "back_padding" in self.data else 0
        self.back_align = util.parse("Overlay", "back_align", self.data["back_align"], parent="overlay", default="center", options=["left", "right", "center", "top", "bottom"]) if "back_align" in self.data else "center"
        self.back_box = None
        back_width = util.parse("Overlay", "back_width", self.data["back_width"], datatype="int", parent="overlay", minimum=0) if "back_width" in self.data else -1
        back_height = util.parse("Overlay", "back_height", self.data["back_height"], datatype="int", parent="overlay", minimum=0) if "back_height" in self.data else -1
        if self.name == "backdrop":
            self.back_box = (back_width, back_height)
        elif self.back_align != "center" and back_width < 0:
            raise Failed(f"Overlay Error: overlay attribute back_align only works when back_width is used")
        elif back_width >= 0 or back_height >= 0:
            self.back_box = (back_width, back_height)
        self.has_back = True if self.back_color or self.back_line_color else False
        if self.name != "backdrop" and self.has_back and not self.has_coordinates() and not self.queue_name:
            raise Failed(f"Overlay Error: horizontal_offset and vertical_offset are required when using a backdrop")

        def get_and_save_image(image_url):
            response = self.requests.get(image_url)
            if response.status_code == 404:
                raise Failed(f"Overlay Error: Overlay Image not found at: {image_url}")
            if response.status_code >= 400:
                raise Failed(f"Overlay Error: Status {response.status_code} when attempting download of: {image_url}")
            if "Content-Type" not in response.headers or response.headers["Content-Type"] != "image/png":
                raise Failed(f"Overlay Error: Overlay Image not a png: {image_url}")
            if not os.path.exists(library.overlay_folder) or not os.path.isdir(library.overlay_folder):
                os.makedirs(library.overlay_folder, exist_ok=False)
                logger.info(f"Creating Overlay Folder found at: {library.overlay_folder}")
            clean_image_name, _ = util.validate_filename(self.name)
            image_path = os.path.join(library.overlay_folder, f"{clean_image_name}.png")
            if os.path.exists(image_path):
                os.remove(image_path)
            with open(image_path, "wb") as handler:
                handler.write(response.content)
            while util.is_locked(image_path):
                time.sleep(1)
            return image_path

        if not self.name.startswith(("blur", "backdrop")):
            if ("default" in self.data and self.data["default"]) or ("pmm" in self.data and self.data["pmm"]) or ("git" in self.data and self.data["git"] and self.data["git"].startswith("PMM/")):
                if "default" in self.data and self.data["default"]:
                    temp_path = self.data["default"]
                elif "pmm" in self.data and self.data["pmm"]:
                    temp_path = self.data["pmm"]
                else:
                    temp_path = self.data["git"][4:]
                if temp_path.startswith("overlays/images/"):
                    temp_path = temp_path[16:]
                if not temp_path.endswith(".png"):
                    temp_path = f"{temp_path}.png"
                images_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "defaults", "overlays", "images")
                if not os.path.exists(os.path.abspath(os.path.join(images_path, temp_path))):
                    raise Failed(f"Overlay Error: Overlay Image not found at: {os.path.abspath(os.path.join(images_path, temp_path))}")
                self.path = os.path.abspath(os.path.join(images_path, temp_path))
            elif "file" in self.data and self.data["file"]:
                self.path = self.data["file"]
            elif "git" in self.data and self.data["git"]:
                self.path = get_and_save_image(f"{self.config.GitHub.configs_url}{self.data['git']}.png")
            elif "repo" in self.data and self.data["repo"]:
                self.path = get_and_save_image(f"{self.config.custom_repo}{self.data['repo']}.png")
            elif "url" in self.data and self.data["url"]:
                self.path = get_and_save_image(self.data["url"])

        if "|" in self.name:
            raise Failed(f"Overlay Error: Overlay Name: {self.name} cannot contain '|'")
        elif self.name.startswith("blur"):
            try:
                match = re.search("\\(([^)]+)\\)", self.name)
                if not match or 0 >= int(match.group(1)) > 100:
                    raise ValueError
                self.name = f"blur({match.group(1)})"
            except ValueError:
                logger.error(f"Overlay Error: failed to parse overlay blur name: {self.name} defaulting to blur(50)")
                self.name = "blur(50)"
        elif self.name.startswith("text"):
            if not self.has_coordinates() and not self.queue_name:
                raise Failed(f"Overlay Error: overlay attribute's horizontal_offset and vertical_offset are required when using text")
            if self.path:
                if not os.path.exists(self.path):
                    raise Failed(f"Overlay Error: Text Overlay Addon Image not found at: {self.path}")
                self.addon_offset = util.parse("Overlay", "addon_offset", self.data["addon_offset"], datatype="int", parent="overlay") if "addon_offset" in self.data else 0
                self.addon_position = util.parse("Overlay", "addon_position", self.data["addon_position"], parent="overlay", options=["left", "right", "top", "bottom"]) if "addon_position" in self.data else "left"
                image_compare = None
                if self.cache:
                    _, image_compare, _ = self.cache.query_image_map(self.mapping_name, f"{self.library.image_table_name}_overlays")
                overlay_size = os.stat(self.path).st_size
                self.updated = not image_compare or str(overlay_size) != str(image_compare)
                try:
                    self.image = Image.open(self.path).convert("RGBA")
                    if self.cache:
                        self.cache.update_image_map(self.mapping_name, f"{self.library.image_table_name}_overlays", self.name, overlay_size)
                except OSError:
                    raise Failed(f"Overlay Error: overlay image {self.path} failed to load")
            match = re.search("\\(([^)]+)\\)", self.name)
            if not match:
                raise Failed(f"Overlay Error: failed to parse overlay text name: {self.name}")
            self.name = f"text({match.group(1)})"
            text = f"{match.group(1)}"
            code_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            font_base = os.path.join(code_base, "fonts")
            self.font_name = os.path.join(font_base, "Roboto-Medium.ttf")
            if "font_size" in self.data:
                self.font_size = util.parse("Overlay", "font_size", self.data["font_size"], datatype="int", parent="overlay", default=self.font_size)
            if "font" in self.data and self.data["font"]:
                font = str(self.data["font"])
                if not os.path.exists(font) and os.path.exists(os.path.join(code_base, font)):
                    font = os.path.join(code_base, font)
                if not os.path.exists(font):
                    kometa_fonts = os.listdir(font_base)
                    fonts = util.get_system_fonts() + kometa_fonts
                    if font not in fonts:
                        raise Failed(f"Overlay Error: font: {os.path.abspath(font)} not found. Options: {', '.join(fonts)}")
                    if font in kometa_fonts:
                        font = os.path.join(font_base, font)
                self.font_name = font
            self.font = ImageFont.truetype(self.font_name, self.font_size)
            if "font_style" in self.data and self.data["font_style"]:
                try:
                    variation_names = [n.decode("utf-8") for n in self.font.get_variation_names()]
                    if self.data["font_style"] in variation_names:
                        self.font.set_variation_by_name(self.data["font_style"])
                    else:
                        raise Failed(f"Overlay Error: Font Style {self.data['font_style']} not found. Options: {','.join(variation_names)}")
                except OSError:
                    logger.warning(f"Overlay Warning: font: {self.font} does not have variations")
            if "font_color" in self.data and self.data["font_color"]:
                try:
                    self.font_color = ImageColor.getcolor(self.data["font_color"], "RGBA")
                except ValueError:
                    raise Failed(f"Overlay Error: overlay font_color: {self.data['font_color']} invalid")
            if "stroke_width" in self.data:
                self.stroke_width = util.parse("Overlay", "stroke_width", self.data["stroke_width"], datatype="int", parent="overlay", default=self.stroke_width)
            if "stroke_color" in self.data and self.data["stroke_color"]:
                try:
                    self.stroke_color = ImageColor.getcolor(self.data["stroke_color"], "RGBA")
                except ValueError:
                    raise Failed(f"Overlay Error: overlay stroke_color: {self.data['stroke_color']} invalid")
            if text in old_special_text:
                text_mod = text[-1] if text[-1] in ["0", "%", "#"] else None
                text = text if text_mod is None else text[:-1]
                if text_mod is None:
                    self.name = f"text(<<{text}>>)"
                else:
                    self.name = f"text(<<{text}#>>)" if text_mod == "#" else f"text(<<{text}%>>{''  if text_mod == '0' else '%'})"
            if "<<originally_available[" in text:
                match = re.search("<<originally_available\\[(.+)]>>", text)
                if match:
                    try:
                        datetime.now().strftime(match.group(1))
                    except ValueError:
                        raise Failed("Overlay Error: originally_available date format not valid")
            box = self.image.size if self.image else None
            self.backdrop_box = box
            self.backdrop_text = self.name[5:-1]
        elif self.name.startswith("backdrop"):
            self.backdrop_box = self.back_box
            if self.horizontal_offset is None:
                self.horizontal_offset = 0
            if self.vertical_offset is None:
                self.vertical_offset = 0
        else:
            if not self.path:
                clean_name, _ = util.validate_filename(self.name)
                self.path = os.path.join(library.overlay_folder, f"{clean_name}.png")
            if not os.path.exists(self.path):
                raise Failed(f"Overlay Error: Overlay Image not found at: {self.path}")
            image_compare = None
            if self.cache:
                _, image_compare, _ = self.cache.query_image_map(self.mapping_name, f"{self.library.image_table_name}_overlays")
            overlay_size = os.stat(self.path).st_size
            self.updated = not image_compare or str(overlay_size) != str(image_compare)
            try:
                self.image = Image.open(self.path).convert("RGBA")
                if self.has_coordinates():
                    self.backdrop_box = self.image.size
                if self.cache:
                    self.cache.update_image_map(self.mapping_name, f"{self.library.image_table_name}_overlays", self.mapping_name, overlay_size)
            except OSError:
                raise Failed(f"Overlay Error: overlay image {self.path} failed to load")

    def get_backdrop(self, canvas_box, box=None, text=None, new_cords=None):
        overlay_image = None
        text_width = None
        text_height = None
        image_width, image_height = box if box else (None, None)
        if text is not None:
            _, _, text_width, text_height = self.get_text_size(text)
            if image_width is not None and self.addon_position in ["left", "right"]:
                box = (text_width + image_width + self.addon_offset, text_height if text_height > image_height else image_height)
            elif image_width is not None:
                box = (text_width if text_width > image_width else image_width, text_height + image_height + self.addon_offset)
            else:
                box = (text_width, text_height)
        box_width, box_height = box
        back_width, back_height = self.back_box if self.back_box else (None, None)
        if back_width == -1:
            back_width = canvas_box[0] if self.name == "backdrop" else box_width
        if back_height == -1:
            back_height = canvas_box[1] if self.name == "backdrop" else box_height
        start_x, start_y = self.get_coordinates(canvas_box, box, new_cords=new_cords)
        main_x = start_x
        main_y = start_y
        if text is not None or self.has_back:
            overlay_image = Image.new("RGBA", canvas_box, (255, 255, 255, 0))
            drawing = ImageDraw.Draw(overlay_image)
            if self.has_back:
                cords = (
                    start_x - self.back_padding,
                    start_y - self.back_padding,
                    start_x + (back_width if self.back_box else box_width) + self.back_padding,
                    start_y + (back_height if self.back_box else box_height) + self.back_padding
                )
                if self.back_radius:
                    drawing.rounded_rectangle(cords, fill=self.back_color, outline=self.back_line_color, width=self.back_line_width, radius=self.back_radius)
                else:
                    drawing.rectangle(cords, fill=self.back_color, outline=self.back_line_color, width=self.back_line_width)

            if self.back_box:
                if self.back_align in ["left", "right", "center", "bottom"]:
                    main_y = start_y + (back_height - box_height) // (1 if self.back_align == "bottom" else 2)
                if self.back_align in ["top", "bottom", "center", "right"]:
                    main_x = start_x + (back_width - box_width) // (1 if self.back_align == "right" else 2)

            addon_x = None
            addon_y = None
            if text is not None and image_width:
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

            if text is not None:
                drawing.text((int(main_x), int(main_y)), text, font=self.font, fill=self.font_color,
                             stroke_fill=self.stroke_color, stroke_width=self.stroke_width, anchor="lt")
            if addon_x is not None:
                main_x = addon_x
                main_y = addon_y
        return overlay_image, (int(main_x), int(main_y))

    def get_overlay_compare(self):
        output = f"{self.name}"
        if self.group:
            output += f"{self.group}{self.weight}"
        if self.has_coordinates():
            output += f"{self.horizontal_align}{self.horizontal_offset}{self.vertical_offset}{self.vertical_align}"
        if self.font_name:
            output += f"{self.font_name}{self.font_size}"
        if self.back_box:
            output += f"{self.back_box[0]}{self.back_box[1]}{self.back_align}"
        if self.addon_position is not None:
            output += f"{self.addon_position}{self.addon_offset}"
        for value in [self.font_color, self.back_color, self.back_radius, self.back_padding,
                      self.back_line_color, self.back_line_width, self.stroke_color, self.stroke_width]:
            if value is not None:
                output += f"{value}"
        return output

    def has_coordinates(self):
        return self.horizontal_offset is not None and self.vertical_offset is not None

    def get_text_size(self, text):
        return ImageDraw.Draw(Image.new("RGBA", (0, 0))).textbbox((0, 0), text, font=self.font, anchor='lt')

    def get_coordinates(self, canvas_box, box, new_cords=None):
        if new_cords is None and not self.has_coordinates():
            return 0, 0
        if self.back_box:
            bw, bh = box
            bbw, bbh = self.back_box
            box = (bbw if bbw >= 0 else bw, bbh if bbh >= 0 else bh)

        def get_cord(value, image_value, over_value, align):
            value = int(image_value * 0.01 * int(value[:-1])) if str(value).endswith("%") else value
            if align in ["right", "bottom"]:
                return image_value - over_value - value
            elif align == "center":
                return int(image_value / 2) - int(over_value / 2) + value
            else:
                return value

        ho = int(new_cords[0]) if new_cords and self.horizontal_offset is None else self.horizontal_offset
        ha = new_cords[1] if new_cords and self.horizontal_align is None else self.horizontal_align
        vo = int(new_cords[2]) if new_cords and self.vertical_offset is None else self.vertical_offset
        va = new_cords[3] if new_cords and self.vertical_align is None else self.vertical_align

        return get_cord(ho, canvas_box[0], box[0], ha), get_cord(vo, canvas_box[1], box[1], va)

    def get_canvas(self, item):
        if isinstance(item, Episode):
            canvas_size = landscape_dim
        elif isinstance(item, Album):
            canvas_size = square_dim
        else:
            canvas_size = portrait_dim
        return self.get_backdrop(canvas_size, box=self.backdrop_box, text=self.backdrop_text)
