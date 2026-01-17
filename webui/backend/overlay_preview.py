"""
Overlay Preview Manager for Kometa Web UI

Parses overlay configurations and generates preview data for visualization.
"""

import os
import re
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from ruamel.yaml import YAML

from .template_processor import TemplateProcessor


# Standard canvas dimensions
CANVAS_PORTRAIT = (1000, 1500)   # Movies, shows, seasons
CANVAS_LANDSCAPE = (1920, 1080)  # Episodes
CANVAS_SQUARE = (1000, 1000)     # Albums

# Default overlay properties
DEFAULTS = {
    "font_size": 36,
    "font_color": "#FFFFFF",
    "stroke_width": 0,
    "stroke_color": "#000000",
    "back_radius": 0,
    "back_padding": 0,
    "horizontal_align": "left",
    "vertical_align": "top",
    "horizontal_offset": 0,
    "vertical_offset": 0,
}


class OverlayPreviewManager:
    """Manages overlay preview generation."""

    def __init__(self, config_dir: Path, kometa_root: Path):
        self.config_dir = Path(config_dir)
        self.kometa_root = Path(kometa_root)
        self.defaults_dir = self.kometa_root / "defaults" / "overlays"
        self.images_dir = self.defaults_dir / "images"
        self.fonts_dir = self.kometa_root / "fonts"

        self.yaml = YAML()
        self.yaml.preserve_quotes = True

        # Initialize template processor for handling Kometa templates
        self.template_processor = TemplateProcessor(kometa_root)

    def get_available_overlays(self) -> Dict[str, Any]:
        """Get list of available overlay configurations."""
        overlays = {
            "default": [],
            "custom": []
        }

        # Scan default overlays
        if self.defaults_dir.exists():
            for yml_file in self.defaults_dir.glob("*.yml"):
                if yml_file.name not in ["templates.yml"]:
                    overlays["default"].append({
                        "name": yml_file.stem,
                        "path": str(yml_file),
                        "type": "default"
                    })

        # Scan custom overlays in config directory
        config_overlays_dir = self.config_dir / "overlays"
        if config_overlays_dir.exists():
            for yml_file in config_overlays_dir.glob("*.yml"):
                overlays["custom"].append({
                    "name": yml_file.stem,
                    "path": str(yml_file),
                    "type": "custom"
                })

        return overlays

    def parse_overlay_file(
        self,
        file_path: str,
        template_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse an overlay YAML file and extract overlay definitions.

        Args:
            file_path: Path to the overlay YAML file
            template_variables: Optional user-provided template variables to apply

        Returns:
            Dictionary with parsed overlays, queues, and metadata
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Overlay file not found: {file_path}")

        with open(path, encoding="utf-8") as f:
            data = self.yaml.load(f)

        if not data:
            return {"overlays": [], "queues": [], "has_templates": False}

        result = {
            "overlays": [],
            "queues": [],
            "groups": {},  # Group name -> list of overlay names
            "has_templates": False,
            "template_info": {}
        }

        # Check if file uses templates
        has_external_templates = "external_templates" in data
        has_local_templates = "templates" in data and data["templates"]
        result["has_templates"] = has_external_templates or has_local_templates

        if has_external_templates:
            result["template_info"]["external"] = data["external_templates"]
        if has_local_templates:
            result["template_info"]["local_count"] = len(data["templates"])

        # Extract queues
        if "queues" in data:
            for queue_name, queue_data in data["queues"].items():
                result["queues"].append({
                    "name": queue_name,
                    "positions": queue_data.get("settings", {}).get("position", [])
                })

        # Process overlays - use template expansion if templates are present
        if result["has_templates"]:
            # Use the template processor to expand all overlays
            expanded = self.template_processor.expand_overlay_file(
                file_path,
                template_variables
            )

            for overlay_config in expanded:
                if overlay_config:
                    # Extract the overlay name
                    original_name = overlay_config.pop("_original_name", "unknown")
                    overlay_config.pop("_template", None)
                    overlay_config.pop("_direct", None)

                    parsed = self._parse_overlay_config(original_name, overlay_config)
                    result["overlays"].append(parsed)

        # Also process any direct overlay definitions (non-templated)
        if "overlays" in data:
            for overlay_name, overlay_data in data["overlays"].items():
                if overlay_data and isinstance(overlay_data, dict):
                    # Skip if already processed via template
                    if result["has_templates"] and "template" in overlay_data:
                        continue

                    overlay_config = overlay_data.get("overlay", {})
                    if overlay_config:
                        parsed = self._parse_overlay_config(overlay_name, overlay_config)
                        parsed["filters"] = overlay_data.get("filters", [])
                        parsed["plex_all"] = overlay_data.get("plex_all", False)
                        parsed["builder_level"] = overlay_data.get("builder_level", "item")
                        result["overlays"].append(parsed)

        # Build groups dictionary from parsed overlays
        for overlay in result["overlays"]:
            group = overlay.get("group")
            if group:
                if group not in result["groups"]:
                    result["groups"][group] = []
                result["groups"][group].append({
                    "name": overlay["name"],
                    "weight": overlay.get("weight", 0)
                })

        # Sort overlays within each group by weight
        for group_name in result["groups"]:
            result["groups"][group_name].sort(key=lambda x: x.get("weight", 0), reverse=True)

        return result

    def _parse_overlay_config(self, name: str, config: Dict) -> Dict[str, Any]:
        """Parse a single overlay configuration."""
        overlay_name = config.get("name", name)

        # Determine overlay type
        overlay_type = "image"
        text_content = None
        blur_amount = None

        if isinstance(overlay_name, str):
            if overlay_name.startswith("text(") and overlay_name.endswith(")"):
                overlay_type = "text"
                text_content = overlay_name[5:-1]  # Extract text content
            elif overlay_name.startswith("blur("):
                overlay_type = "blur"
                # Extract blur amount if specified
                try:
                    blur_amount = int(overlay_name[5:-1])
                except (ValueError, IndexError):
                    blur_amount = 50  # Default blur
            elif overlay_name == "backdrop":
                overlay_type = "backdrop"

        # Extract suppress_overlays info
        suppress_overlays = config.get("suppress_overlays")

        return {
            "name": name,
            "display_name": overlay_name,
            "type": overlay_type,
            "text_content": text_content,
            "blur_amount": blur_amount,

            # Positioning
            "horizontal_align": config.get("horizontal_align", DEFAULTS["horizontal_align"]),
            "horizontal_offset": config.get("horizontal_offset", DEFAULTS["horizontal_offset"]),
            "vertical_align": config.get("vertical_align", DEFAULTS["vertical_align"]),
            "vertical_offset": config.get("vertical_offset", DEFAULTS["vertical_offset"]),

            # Text styling
            "font": config.get("font", "fonts/Roboto-Medium.ttf"),
            "font_size": config.get("font_size", DEFAULTS["font_size"]),
            "font_color": config.get("font_color", DEFAULTS["font_color"]),
            "stroke_width": config.get("stroke_width", DEFAULTS["stroke_width"]),
            "stroke_color": config.get("stroke_color", DEFAULTS["stroke_color"]),

            # Background
            "back_color": config.get("back_color"),
            "back_width": config.get("back_width"),
            "back_height": config.get("back_height"),
            "back_radius": config.get("back_radius", DEFAULTS["back_radius"]),
            "back_padding": config.get("back_padding", DEFAULTS["back_padding"]),
            "back_align": config.get("back_align", "center"),
            "back_line_color": config.get("back_line_color"),
            "back_line_width": config.get("back_line_width"),

            # Image
            "file": config.get("file"),
            "url": config.get("url"),
            "default": config.get("default"),
            "scale_width": config.get("scale_width"),
            "scale_height": config.get("scale_height"),

            # Grouping
            "group": config.get("group"),
            "weight": config.get("weight", 0),
            "queue": config.get("queue"),
            "suppress_overlays": suppress_overlays,

            # Addon
            "addon_position": config.get("addon_position"),
            "addon_offset": config.get("addon_offset", 0),
        }

    def calculate_position(
        self,
        canvas_size: Tuple[int, int],
        overlay_size: Tuple[int, int],
        h_align: str,
        h_offset: Any,
        v_align: str,
        v_offset: Any
    ) -> Tuple[int, int]:
        """Calculate the actual X, Y position for an overlay."""
        canvas_w, canvas_h = canvas_size
        overlay_w, overlay_h = overlay_size

        # Parse offsets (can be int or percentage string)
        h_off = self._parse_offset(h_offset, canvas_w)
        v_off = self._parse_offset(v_offset, canvas_h)

        # Calculate X position
        if h_align == "left":
            x = h_off
        elif h_align == "right":
            x = canvas_w - overlay_w - h_off
        else:  # center
            x = (canvas_w - overlay_w) // 2 + h_off

        # Calculate Y position
        if v_align == "top":
            y = v_off
        elif v_align == "bottom":
            y = canvas_h - overlay_h - v_off
        else:  # center
            y = (canvas_h - overlay_h) // 2 + v_off

        return (max(0, x), max(0, y))

    def _parse_offset(self, offset: Any, dimension: int) -> int:
        """Parse an offset value (int or percentage string)."""
        if offset is None:
            return 0
        if isinstance(offset, int):
            return offset
        if isinstance(offset, str) and offset.endswith("%"):
            try:
                pct = float(offset[:-1])
                return int(dimension * pct / 100)
            except ValueError:
                return 0
        try:
            return int(offset)
        except (ValueError, TypeError):
            return 0

    def get_overlay_image_path(self, overlay: Dict) -> Optional[Path]:
        """
        Get the path to an overlay image file.

        Searches in multiple locations with various naming conventions:
        - Direct path from 'file' attribute
        - Default images directory with 'default' attribute
        - Subdirectories organized by type (resolution, ribbon, streaming, etc.)
        - Various case and format variations
        """
        # Helper to normalize names for file searching
        def normalize_name(name: str) -> List[str]:
            """Generate variations of a name for file searching."""
            variations = set()
            variations.add(name)

            # Remove common suffixes like -Dovetail
            base_name = name
            if "-Dovetail" in name:
                base_name = name.replace("-Dovetail", "")
                variations.add(base_name)

            # Add lowercase version
            variations.add(name.lower())
            variations.add(base_name.lower())

            # Remove hyphens and convert to lowercase
            no_hyphen = base_name.replace("-", "").lower()
            variations.add(no_hyphen)

            # Handle resolution format: "4K-DV-HDR-Plus" -> "4kdvhdrplus"
            # Also handle "Plus" -> "plus"
            compact = base_name.replace("-", "").replace("P", "p").lower()
            variations.add(compact)

            # Another variation: remove "P" suffix for resolutions
            # "1080P" -> "1080p"
            for res in ["4K", "1080P", "720P", "480P", "576P"]:
                if res in base_name:
                    alt = base_name.replace(res, res.lower())
                    variations.add(alt.replace("-", "").lower())

            # Convert list for ordered iteration
            return list(variations)

        # Check file path first (explicit path takes priority)
        if overlay.get("file"):
            file_path = overlay["file"]
            path = Path(file_path)
            if not path.is_absolute():
                path = self.config_dir / file_path
            if path.exists():
                return path

        # Check default attribute (e.g., "default: resolution/4k")
        if overlay.get("default"):
            default_val = overlay["default"]

            # Handle paths with subdirectories
            if "/" in default_val:
                path = self.images_dir / f"{default_val}.png"
                if path.exists():
                    return path

            # Try direct name in images root
            path = self.images_dir / f"{default_val}.png"
            if path.exists():
                return path

            # Try in known subdirectories
            for subdir in self.images_dir.iterdir():
                if subdir.is_dir():
                    path = subdir / f"{default_val}.png"
                    if path.exists():
                        return path
                    # Try in nested subdirectories (e.g., ribbon/red/)
                    for nested in subdir.iterdir():
                        if nested.is_dir():
                            path = nested / f"{default_val}.png"
                            if path.exists():
                                return path

        # Check for image by overlay name
        name = overlay.get("display_name", overlay.get("name", ""))
        if name and not name.startswith(("text(", "blur(", "backdrop")):
            name_variations = normalize_name(name)

            for variation in name_variations:
                # Try direct name in images root
                path = self.images_dir / f"{variation}.png"
                if path.exists():
                    return path

                # Try in subdirectories
                for subdir in self.images_dir.iterdir():
                    if subdir.is_dir():
                        path = subdir / f"{variation}.png"
                        if path.exists():
                            return path

                        # Try nested subdirectories (e.g., ribbon/red/, streaming/...)
                        for nested in subdir.iterdir():
                            if nested.is_dir():
                                path = nested / f"{variation}.png"
                                if path.exists():
                                    return path

        # Last resort: try to infer category from overlay name and search there
        category_map = {
            "resolution": ["4K", "1080", "720", "480", "576", "DV", "HDR"],
            "audio_codec": ["Atmos", "DTS", "TrueHD", "AAC", "Dolby"],
            "ribbon": ["Emmy", "Oscar", "Golden", "BAFTA", "IMDb", "Rotten"],
            "streaming": ["Netflix", "Amazon", "Disney", "Hulu", "HBO", "Apple"],
            "network": ["ABC", "CBS", "NBC", "FOX", "BBC", "AMC"],
            "studio": ["Marvel", "Warner", "Sony", "Universal", "Paramount"],
        }

        for category, keywords in category_map.items():
            if any(kw.lower() in name.lower() for kw in keywords):
                category_dir = self.images_dir / category
                if category_dir.exists():
                    for variation in normalize_name(name):
                        path = category_dir / f"{variation}.png"
                        if path.exists():
                            return path
                        # Check nested dirs
                        for nested in category_dir.iterdir():
                            if nested.is_dir():
                                path = nested / f"{variation}.png"
                                if path.exists():
                                    return path

        return None

    def generate_preview(
        self,
        overlays: List[Dict],
        canvas_type: str = "portrait",
        sample_poster: Optional[str] = None,
        media_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a preview of overlays on a canvas.

        Args:
            overlays: List of overlay configurations to render
            canvas_type: "portrait", "landscape", or "square"
            sample_poster: Optional path to a poster image file
            media_metadata: Optional metadata from Plex item for text substitution

        Returns preview data including:
        - Base64 encoded preview image
        - Overlay positions and dimensions
        - Warnings/errors
        """
        # Store media metadata for text substitution
        self._current_media_metadata = media_metadata or {}
        if not HAS_PIL:
            return {
                "error": "PIL/Pillow not available for image generation",
                "overlays": overlays
            }

        # Select canvas size
        if canvas_type == "landscape":
            canvas_size = CANVAS_LANDSCAPE
        elif canvas_type == "square":
            canvas_size = CANVAS_SQUARE
        else:
            canvas_size = CANVAS_PORTRAIT

        # Create canvas
        if sample_poster:
            try:
                canvas = Image.open(sample_poster).convert("RGBA")
                canvas = canvas.resize(canvas_size, Image.Resampling.LANCZOS)
            except Exception:
                canvas = self._create_sample_canvas(canvas_size)
        else:
            canvas = self._create_sample_canvas(canvas_size)

        preview_overlays = []
        warnings = []

        for overlay in overlays:
            try:
                result = self._render_overlay(canvas, overlay)
                preview_overlays.append(result)
            except Exception as e:
                warnings.append(f"Failed to render {overlay.get('name', 'unknown')}: {str(e)}")

        # Convert to base64
        buffer = BytesIO()
        canvas.save(buffer, format="PNG")
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "image": f"data:image/png;base64,{base64_image}",
            "canvas_size": canvas_size,
            "overlays": preview_overlays,
            "warnings": warnings
        }

    def _create_sample_canvas(self, size: Tuple[int, int]) -> Image.Image:
        """Create a sample poster canvas with gradient background."""
        canvas = Image.new("RGBA", size, (30, 30, 50, 255))
        draw = ImageDraw.Draw(canvas)

        # Add gradient effect
        for i in range(size[1]):
            alpha = int(255 * (1 - i / size[1] * 0.3))
            draw.line([(0, i), (size[0], i)], fill=(40, 40, 70, alpha))

        # Add sample text
        try:
            font = ImageFont.truetype(str(self.fonts_dir / "Roboto-Medium.ttf"), 48)
        except Exception:
            font = ImageFont.load_default()

        text = "Sample Poster"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2

        draw.text((x, y), text, fill=(100, 100, 120, 200), font=font)

        return canvas

    def _render_overlay(self, canvas: Image.Image, overlay: Dict) -> Dict[str, Any]:
        """Render a single overlay on the canvas."""
        canvas_size = canvas.size
        draw = ImageDraw.Draw(canvas)

        overlay_type = overlay.get("type", "image")
        result = {
            "name": overlay.get("name"),
            "type": overlay_type,
            "position": None,
            "size": None,
            "rendered": False
        }

        if overlay_type == "text":
            self._render_text_overlay(canvas, draw, overlay, result)
        elif overlay_type == "image":
            self._render_image_overlay(canvas, overlay, result)
        elif overlay_type == "backdrop":
            self._render_backdrop_overlay(canvas, draw, overlay, result)
        elif overlay_type == "blur":
            self._render_blur_overlay(canvas, overlay, result)

        return result

    def _render_text_overlay(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        overlay: Dict,
        result: Dict
    ):
        """Render a text overlay."""
        text = overlay.get("text_content", "Sample Text")

        # Substitute sample values for variables
        text = self._substitute_variables(text)

        # Load font
        font_size = overlay.get("font_size", 36)
        try:
            font_path = overlay.get("font", "fonts/Roboto-Medium.ttf")
            if not Path(font_path).is_absolute():
                font_path = self.kometa_root / font_path
            font = ImageFont.truetype(str(font_path), font_size)
        except Exception:
            font = ImageFont.load_default()

        # Calculate text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate background size
        back_padding = overlay.get("back_padding", 0)
        back_width = overlay.get("back_width") or (text_width + back_padding * 2)
        back_height = overlay.get("back_height") or (text_height + back_padding * 2)

        if back_width == -1:
            back_width = text_width + back_padding * 2
        if back_height == -1:
            back_height = text_height + back_padding * 2

        # Calculate position
        x, y = self.calculate_position(
            canvas.size,
            (back_width, back_height),
            overlay.get("horizontal_align", "left"),
            overlay.get("horizontal_offset", 0),
            overlay.get("vertical_align", "top"),
            overlay.get("vertical_offset", 0)
        )

        result["position"] = (x, y)
        result["size"] = (back_width, back_height)

        # Draw background
        back_color = overlay.get("back_color")
        if back_color:
            rgba = self._parse_color(back_color)
            radius = overlay.get("back_radius", 0)
            self._draw_rounded_rect(draw, (x, y, x + back_width, y + back_height), radius, rgba)

        # Draw text
        font_color = self._parse_color(overlay.get("font_color", "#FFFFFF"))
        text_x = x + (back_width - text_width) // 2
        text_y = y + (back_height - text_height) // 2

        # Stroke
        stroke_width = overlay.get("stroke_width", 0)
        stroke_color = self._parse_color(overlay.get("stroke_color", "#000000")) if stroke_width else None

        draw.text(
            (text_x, text_y),
            text,
            fill=font_color,
            font=font,
            stroke_width=stroke_width,
            stroke_fill=stroke_color
        )

        result["rendered"] = True

    def _render_image_overlay(self, canvas: Image.Image, overlay: Dict, result: Dict):
        """Render an image overlay."""
        image_path = self.get_overlay_image_path(overlay)

        if not image_path:
            # Create placeholder
            size = (150, 100)
            overlay_img = Image.new("RGBA", size, (100, 100, 100, 200))
            draw = ImageDraw.Draw(overlay_img)
            draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(150, 150, 150, 255))
        else:
            overlay_img = Image.open(image_path).convert("RGBA")

        # Scale if specified
        scale_w = overlay.get("scale_width")
        scale_h = overlay.get("scale_height")

        if scale_w or scale_h:
            orig_w, orig_h = overlay_img.size

            if isinstance(scale_w, str) and scale_w.endswith("%"):
                scale_w = int(orig_w * float(scale_w[:-1]) / 100)
            if isinstance(scale_h, str) and scale_h.endswith("%"):
                scale_h = int(orig_h * float(scale_h[:-1]) / 100)

            if scale_w and not scale_h:
                scale_h = int(orig_h * scale_w / orig_w)
            elif scale_h and not scale_w:
                scale_w = int(orig_w * scale_h / orig_h)

            if scale_w and scale_h:
                overlay_img = overlay_img.resize((int(scale_w), int(scale_h)), Image.Resampling.LANCZOS)

        # Calculate position
        x, y = self.calculate_position(
            canvas.size,
            overlay_img.size,
            overlay.get("horizontal_align", "left"),
            overlay.get("horizontal_offset", 0),
            overlay.get("vertical_align", "top"),
            overlay.get("vertical_offset", 0)
        )

        result["position"] = (x, y)
        result["size"] = overlay_img.size

        # Paste overlay
        canvas.paste(overlay_img, (x, y), overlay_img)
        result["rendered"] = True

    def _render_backdrop_overlay(
        self,
        canvas: Image.Image,
        draw: ImageDraw.Draw,
        overlay: Dict,
        result: Dict
    ):
        """Render a backdrop overlay."""
        back_color = overlay.get("back_color", "#000000AA")
        rgba = self._parse_color(back_color)

        back_width = overlay.get("back_width") or canvas.size[0]
        back_height = overlay.get("back_height") or canvas.size[1]

        x, y = self.calculate_position(
            canvas.size,
            (back_width, back_height),
            overlay.get("horizontal_align", "left"),
            overlay.get("horizontal_offset", 0),
            overlay.get("vertical_align", "top"),
            overlay.get("vertical_offset", 0)
        )

        result["position"] = (x, y)
        result["size"] = (back_width, back_height)

        radius = overlay.get("back_radius", 0)
        self._draw_rounded_rect(draw, (x, y, x + back_width, y + back_height), radius, rgba)

        result["rendered"] = True

    def _render_blur_overlay(self, canvas: Image.Image, overlay: Dict, result: Dict):
        """Render a blur overlay on a region of the canvas."""
        try:
            from PIL import ImageFilter
        except ImportError:
            result["rendered"] = False
            return

        # Get blur amount (percentage translates to blur radius)
        blur_amount = overlay.get("blur_amount", 50)
        blur_radius = max(1, int(blur_amount / 5))  # Convert percentage to radius

        # Determine blur region
        back_width = overlay.get("back_width") or canvas.size[0]
        back_height = overlay.get("back_height") or canvas.size[1]

        x, y = self.calculate_position(
            canvas.size,
            (back_width, back_height),
            overlay.get("horizontal_align", "left"),
            overlay.get("horizontal_offset", 0),
            overlay.get("vertical_align", "top"),
            overlay.get("vertical_offset", 0)
        )

        result["position"] = (x, y)
        result["size"] = (back_width, back_height)

        # Extract region, blur it, paste back
        region = canvas.crop((x, y, x + back_width, y + back_height))
        blurred = region.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        canvas.paste(blurred, (x, y))

        result["rendered"] = True

    def _substitute_variables(self, text: str) -> str:
        """
        Substitute variables in text with actual metadata values when available,
        or sample values as fallback.
        """
        # Get metadata from current preview context
        metadata = getattr(self, '_current_media_metadata', {})

        # Map Kometa variables to Plex metadata fields
        metadata_mapping = {
            "<<runtime>>": ("duration", lambda x: str(x) if x else "7200000"),
            "<<runtime H>>": ("duration", lambda x: str(int(x / 3600000)) if x else "2"),
            "<<runtime M>>": ("duration", lambda x: str(int((x % 3600000) / 60000)).zfill(2) if x else "00"),
            "<<audience_rating>>": ("audienceRating", lambda x: f"{x:.1f}" if x else "8.5"),
            "<<critic_rating>>": ("rating", lambda x: str(int(x * 10)) if x else "92"),
            "<<user_rating>>": ("userRating", lambda x: f"{x:.1f}" if x else "9.0"),
            "<<imdb_rating>>": ("audienceRating", lambda x: f"{x:.1f}" if x else "8.2"),
            "<<tmdb_rating>>": ("audienceRating", lambda x: f"{x:.1f}" if x else "8.1"),
            "<<title>>": ("title", lambda x: x if x else "Sample Title"),
            "<<content_rating>>": ("contentRating", lambda x: x if x else "PG-13"),
            "<<edition>>": ("editionTitle", lambda x: x if x else "Director's Cut"),
            "<<year>>": ("year", lambda x: str(x) if x else "2024"),
            "<<originally_available>>": ("originallyAvailableAt", lambda x: x if x else "2024-01-15"),
            "<<studio>>": ("studio", lambda x: x if x else "Studio"),
            "<<genres>>": ("genres", lambda x: ", ".join(x[:3]) if x else "Drama, Action"),
        }

        # Season/episode specific
        season_episode_mapping = {
            "<<season_number>>": ("parentIndex", lambda x: str(x) if x else "1"),
            "<<season_number0>>": ("parentIndex", lambda x: str(x).zfill(2) if x else "01"),
            "<<episode_number>>": ("index", lambda x: str(x) if x else "5"),
            "<<episode_number0>>": ("index", lambda x: str(x).zfill(2) if x else "05"),
            "<<episode_number00>>": ("index", lambda x: str(x).zfill(3) if x else "005"),
        }

        # Static sample values for less common variables
        static_substitutions = {
            "<<bitrate>>": "15000",
            "<<versions>>": "2",
            "<<video_resolution>>": "4K",
            "<<audio_codec>>": "TrueHD Atmos",
            "<<video_codec>>": "HEVC",
        }

        # Apply metadata-based substitutions
        for var, (field, formatter) in {**metadata_mapping, **season_episode_mapping}.items():
            if var in text:
                value = metadata.get(field)
                text = text.replace(var, formatter(value))

        # Apply static substitutions
        for var, value in static_substitutions.items():
            text = text.replace(var, value)

        # Handle any remaining variables with placeholder
        text = re.sub(r"<<[^>]+>>", "???", text)

        return text

    def _parse_color(self, color: str) -> Tuple[int, int, int, int]:
        """Parse a hex color string to RGBA tuple."""
        if not color:
            return (255, 255, 255, 255)

        color = color.lstrip("#")

        if len(color) == 6:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            a = 255
        elif len(color) == 8:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            a = int(color[6:8], 16)
        else:
            return (255, 255, 255, 255)

        return (r, g, b, a)

    def _draw_rounded_rect(
        self,
        draw: ImageDraw.Draw,
        bbox: Tuple[int, int, int, int],
        radius: int,
        fill: Tuple[int, int, int, int]
    ):
        """Draw a rounded rectangle."""
        x1, y1, x2, y2 = bbox

        if radius <= 0:
            draw.rectangle(bbox, fill=fill)
            return

        # Draw rounded corners using ellipses
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)

    def get_overlay_images_list(self) -> Dict[str, List[str]]:
        """Get list of available overlay images organized by category."""
        images = {}

        if not self.images_dir.exists():
            return images

        for item in self.images_dir.iterdir():
            if item.is_dir():
                category = item.name
                images[category] = []
                for img in item.rglob("*.png"):
                    rel_path = img.relative_to(self.images_dir)
                    images[category].append(str(rel_path).replace(".png", ""))
            elif item.suffix == ".png":
                if "root" not in images:
                    images["root"] = []
                images["root"].append(item.stem)

        return images
