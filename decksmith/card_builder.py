"""
This module contains the CardBuilder class,
which is used to create card images based on a JSON specification.
"""

import operator
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from decksmith.logger import logger
from decksmith.utils import apply_anchor, get_wrapped_text
from decksmith.validate import transform_card, validate_card


class CardBuilder:
    """
    A class to build a card image based on a JSON specification.
    Attributes:
        spec (Dict[str, Any]): The JSON specification for the card.
        card (Image.Image): The PIL Image object representing the card.
        draw (ImageDraw.ImageDraw): The PIL ImageDraw object for drawing on the card.
        element_positions (Dict[str, Tuple[int, int, int, int]]):
            A dictionary mapping element IDs to their bounding boxes.
    """

    def __init__(self, spec: Dict[str, Any], base_path: Optional[Path] = None):
        """
        Initializes the CardBuilder with a JSON specification.
        Args:
            spec (Dict[str, Any]): The JSON specification for the card.
            base_path (Optional[Path]): The base path for resolving relative file paths.
        """
        self.spec = spec
        self.base_path = base_path
        width = self.spec.get("width", 250)
        height = self.spec.get("height", 350)
        bg_color = tuple(self.spec.get("background_color", (255, 255, 255, 0)))
        self.card: Image.Image = Image.new("RGBA", (width, height), bg_color)
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.card, "RGBA")
        self.element_positions: Dict[str, Tuple[int, int, int, int]] = {}
        if "id" in spec:
            self.element_positions[self.spec["id"]] = (0, 0, width, height)

    def _calculate_absolute_position(self, element: Dict[str, Any]) -> Tuple[int, int]:
        """
        Calculates the absolute position of an element,
        resolving relative positioning.
        Args:
            element (dict): The element dictionary.
        Returns:
            tuple: The absolute (x, y) position of the element.
        """
        # If the element has no 'relative_to', return its position directly
        if "relative_to" not in element:
            return tuple(element.get("position", [0, 0]))

        # If the element has 'relative_to', resolve based on the reference element and anchor
        relative_id, anchor = element["relative_to"]
        if relative_id not in self.element_positions:
            raise ValueError(
                f"Element with id '{relative_id}' not found for relative positioning."
            )

        parent_bbox = self.element_positions[relative_id]
        anchor_point = apply_anchor(parent_bbox, anchor)

        offset = tuple(element.get("position", [0, 0]))
        return tuple(map(operator.add, anchor_point, offset))

    def _prepare_text_element(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Prepares text element properties."""
        if pd.isna(element["text"]):
            element["text"] = " "

        # Font setup
        font_size = element.pop("font_size", 10)
        if font_path := element.pop("font_path", False):
            # Resolve font path relative to base_path if provided
            if self.base_path and not Path(font_path).is_absolute():
                potential_path = self.base_path / font_path
                if potential_path.exists():
                    font_path = str(potential_path)

            try:
                element["font"] = ImageFont.truetype(
                    font_path, font_size, encoding="unic"
                )
            except OSError:
                logger.error(f"Could not load font: {font_path}. Using default.")
                element["font"] = ImageFont.load_default(font_size)
        else:
            element["font"] = ImageFont.load_default(font_size)

        if font_variant := element.pop("font_variant", None):
            try:
                element["font"].set_variation_by_name(font_variant)
            except AttributeError:
                logger.warning(
                    f"Font variant '{font_variant}' not supported for this font."
                )

        # Text wrapping
        if line_length := element.pop("width", False):
            element["text"] = get_wrapped_text(
                element["text"], element["font"], line_length
            )

        # Colors and position
        if position := element.pop("position", [0, 0]):
            element["position"] = tuple(position)
        if color := element.pop("color", [0, 0, 0]):
            element["color"] = tuple(color)
        if stroke_color := element.pop("stroke_color", None):
            element["stroke_color"] = tuple(stroke_color)

        return element

    def _draw_text(self, element: Dict[str, Any]):
        """Draws text on the card."""
        assert element.pop("type") == "text", "Element type must be 'text'"

        element = self._prepare_text_element(element)

        original_pos = self._calculate_absolute_position(element)
        element["position"] = original_pos

        # Calculate anchor offset if needed
        if "anchor" in element:
            bbox = self.draw.textbbox(
                xy=(0, 0),
                text=element.get("text"),
                font=element["font"],
                spacing=element.get("line_spacing", 4),
                align=element.get("align", "left"),
            )
            anchor_point = apply_anchor(bbox, element.pop("anchor"))
            element["position"] = tuple(map(operator.sub, original_pos, anchor_point))

        # Draw text
        self.draw.text(
            xy=element.get("position"),
            text=element.get("text"),
            fill=element.get("color", None),
            font=element["font"],
            spacing=element.get("line_spacing", 4),
            align=element.get("align", "left"),
            stroke_width=element.get("stroke_width", 0),
            stroke_fill=element.get("stroke_color", None),
        )

        # Store position
        if "id" in element:
            bbox = self.draw.textbbox(
                xy=element.get("position"),
                text=element.get("text"),
                font=element["font"],
                spacing=element.get("line_spacing", 4),
                align=element.get("align", "left"),
            )
            self.element_positions[element["id"]] = bbox

    def _apply_image_filters(
        self, img: Image.Image, filters: Dict[str, Any]
    ) -> Image.Image:
        for filter_name, filter_value in filters.items():
            filter_method_name = f"_filter_{filter_name}"
            filter_method = getattr(self, filter_method_name, self._filter_unsupported)
            img = filter_method(img, filter_value)
        return img

    def _filter_unsupported(self, img: Image.Image, _: Any) -> Image.Image:
        return img

    def _filter_crop(self, img: Image.Image, crop_values: List[int]) -> Image.Image:
        return img.crop(tuple(crop_values))

    def _filter_crop_top(self, img: Image.Image, value: int) -> Image.Image:
        if value < 0:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", (img.width, img.height - value), (0, 0, 0, 0))
            new_img.paste(img, (0, -value))
            return new_img
        return img.crop((0, value, img.width, img.height))

    def _filter_crop_bottom(self, img: Image.Image, value: int) -> Image.Image:
        if value < 0:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", (img.width, img.height - value), (0, 0, 0, 0))
            new_img.paste(img, (0, 0))
            return new_img
        return img.crop((0, 0, img.width, img.height - value))

    def _filter_crop_left(self, img: Image.Image, value: int) -> Image.Image:
        if value < 0:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", (img.width - value, img.height), (0, 0, 0, 0))
            new_img.paste(img, (-value, 0))
            return new_img
        return img.crop((value, 0, img.width, img.height))

    def _filter_crop_right(self, img: Image.Image, value: int) -> Image.Image:
        if value < 0:
            img = img.convert("RGBA")
            new_img = Image.new("RGBA", (img.width - value, img.height), (0, 0, 0, 0))
            new_img.paste(img, (0, 0))
            return new_img
        return img.crop((0, 0, img.width - value, img.height))

    def _filter_crop_box(self, img: Image.Image, box: List[int]) -> Image.Image:
        img = img.convert("RGBA")
        x, y, w, h = box
        new_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        src_x1 = max(0, x)
        src_y1 = max(0, y)
        src_x2 = min(img.width, x + w)
        src_y2 = min(img.height, y + h)
        if src_x1 < src_x2 and src_y1 < src_y2:
            src_w = src_x2 - src_x1
            src_h = src_y2 - src_y1
            src_img = img.crop((src_x1, src_y1, src_x1 + src_w, src_y1 + src_h))
            dst_x = src_x1 - x
            dst_y = src_y1 - y
            new_img.paste(src_img, (dst_x, dst_y))
        return new_img

    def _filter_resize(self, img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        new_width, new_height = size
        if new_width is None and new_height is None:
            return img
        if new_width is None or new_height is None:
            original_width, original_height = img.size
            aspect_ratio = original_width / float(original_height)
            if new_width is None:
                new_width = int(new_height * aspect_ratio)
            else:
                new_height = int(new_width / aspect_ratio)
        return img.resize((new_width, new_height))

    def _filter_rotate(self, img: Image.Image, angle: float) -> Image.Image:
        return img.rotate(angle, expand=True)

    def _filter_flip(self, img: Image.Image, direction: str) -> Image.Image:
        if direction == "horizontal":
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        if direction == "vertical":
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        return img

    def _draw_image(self, element: Dict[str, Any]):
        """Draws an image on the card."""
        assert element.pop("type") == "image", "Element type must be 'image'"

        path_str = element["path"]
        path = Path(path_str)

        if not path.is_absolute() and self.base_path:
            potential_path = self.base_path / path
            if potential_path.exists():
                path = potential_path

        try:
            img = Image.open(path)
        except FileNotFoundError:
            logger.error(f"Image not found: {path}")
            return

        img = self._apply_image_filters(img, element.get("filters", {}))

        position = self._calculate_absolute_position(element)
        if "anchor" in element:
            anchor_point = apply_anchor((img.width, img.height), element.pop("anchor"))
            position = tuple(map(operator.sub, position, anchor_point))

        if img.mode == "RGBA":
            self.card.paste(img, position, mask=img)
        else:
            self.card.paste(img, position)

        if "id" in element:
            self.element_positions[element["id"]] = (
                position[0],
                position[1],
                position[0] + img.width,
                position[1] + img.height,
            )

    def _draw_shape_generic(self, element: Dict[str, Any], draw_func, size_func):
        """Generic method to draw shapes."""
        size = size_func(element)
        absolute_pos = self._calculate_absolute_position(element)

        if "color" in element:
            element["fill"] = tuple(element["color"])
        if "outline_color" in element:
            element["outline_color"] = tuple(element["outline_color"])

        if "anchor" in element:
            anchor_offset = apply_anchor(size, element.pop("anchor"))
            absolute_pos = tuple(map(operator.sub, absolute_pos, anchor_offset))

        layer = Image.new("RGBA", self.card.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")

        draw_func(layer_draw, absolute_pos, element)

        self.card = Image.alpha_composite(self.card, layer)
        self.draw = ImageDraw.Draw(self.card, "RGBA")

        if "id" in element:
            self.element_positions[element["id"]] = (
                absolute_pos[0],
                absolute_pos[1],
                absolute_pos[0] + size[0],
                absolute_pos[1] + size[1],
            )

    def _draw_shape_circle(self, element: Dict[str, Any]):
        assert element.pop("type") == "circle", "Element type must be 'circle'"
        radius = element["radius"]

        def draw(layer_draw, pos, el):
            center_pos = (pos[0] + radius, pos[1] + radius)
            layer_draw.circle(
                center_pos,
                radius,
                fill=el.get("fill", None),
                outline=el.get("outline_color", None),
                width=el.get("outline_width", 1),
            )

        self._draw_shape_generic(element, draw, lambda _: (radius * 2, radius * 2))

    def _draw_shape_ellipse(self, element: Dict[str, Any]):
        assert element.pop("type") == "ellipse", "Element type must be 'ellipse'"
        size = element["size"]

        def draw(layer_draw, pos, el):
            bbox = (pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
            layer_draw.ellipse(
                bbox,
                fill=el.get("fill", None),
                outline=el.get("outline_color", None),
                width=el.get("outline_width", 1),
            )

        self._draw_shape_generic(element, draw, lambda _: size)

    def _draw_shape_polygon(self, element: Dict[str, Any]):
        assert element.pop("type") == "polygon", "Element type must be 'polygon'"
        points = [tuple(p) for p in element.get("points", [])]
        if not points:
            return

        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        bbox_size = (max_x - min_x, max_y - min_y)

        def draw(layer_draw, pos, el):
            # pos is the top-left of the bounding box
            # We need to shift points so that (min_x, min_y) aligns with pos
            offset_x = pos[0] - min_x
            offset_y = pos[1] - min_y
            final_points = [(p[0] + offset_x, p[1] + offset_y) for p in points]

            layer_draw.polygon(
                final_points,
                fill=el.get("fill", None),
                outline=el.get("outline_color", None),
                width=el.get("outline_width", 1),
            )

        self._draw_shape_generic(element, draw, lambda _: bbox_size)

    def _draw_shape_regular_polygon(self, element: Dict[str, Any]):
        assert element.pop("type") == "regular-polygon", (
            "Element type must be 'regular-polygon'"
        )
        radius = element["radius"]

        def draw(layer_draw, pos, el):
            center_pos = (pos[0] + radius, pos[1] + radius)
            layer_draw.regular_polygon(
                (center_pos[0], center_pos[1], radius),
                n_sides=el["sides"],
                rotation=el.get("rotation", 0),
                fill=el.get("fill", None),
                outline=el.get("outline_color", None),
                width=el.get("outline_width", 1),
            )

        self._draw_shape_generic(element, draw, lambda _: (radius * 2, radius * 2))

    def _draw_shape_rectangle(self, element: Dict[str, Any]):
        assert element.pop("type") == "rectangle", "Element type must be 'rectangle'"
        size = element["size"]
        if "corners" in element:
            element["corners"] = tuple(element["corners"])

        def draw(layer_draw, pos, el):
            bbox = (pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
            layer_draw.rounded_rectangle(
                bbox,
                radius=el.get("corner_radius", 0),
                fill=el.get("fill", None),
                outline=el.get("outline_color", None),
                width=el.get("outline_width", 1),
                corners=el.get("corners", None),
            )

        self._draw_shape_generic(element, draw, lambda _: size)

    def render(self) -> Image.Image:
        """
        Renders the card image by drawing all elements specified in the JSON.
        Returns:
            Image.Image: The rendered card image.
        """
        self.spec = transform_card(self.spec)
        validate_card(self.spec)

        draw_methods = {
            "text": self._draw_text,
            "image": self._draw_image,
            "circle": self._draw_shape_circle,
            "ellipse": self._draw_shape_ellipse,
            "polygon": self._draw_shape_polygon,
            "regular-polygon": self._draw_shape_regular_polygon,
            "rectangle": self._draw_shape_rectangle,
        }

        for element in self.spec.get("elements", []):
            element_type = element.get("type")
            if draw_method := draw_methods.get(element_type):
                try:
                    draw_method(element)
                except Exception as e:
                    logger.error(f"Error drawing element {element_type}: {e}")
                    # Continue drawing other elements

        return self.card

    def build(self, output_path: Path):
        """
        Builds the card image and saves it to the specified path.
        Args:
            output_path (Path): The path where the card image will be saved.
        """
        card = self.render()
        card.save(output_path)
        logger.info(f"(✔) Card saved to {output_path}")
