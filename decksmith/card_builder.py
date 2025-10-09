"""
This module contains the CardBuilder class,
which is used to create card images based on a JSON specification.
"""

import operator
from pathlib import Path
from typing import Dict, Any, Tuple, List

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from .utils import get_wrapped_text, apply_anchor
from .validate import validate_card, transform_card


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

    def __init__(self, spec: Dict[str, Any]):
        """
        Initializes the CardBuilder with a JSON specification.
        Args:
            spec (Dict[str, Any]): The JSON specification for the card.
        """
        self.spec = spec
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

    def _draw_text(self, element: Dict[str, Any]):
        """
        Draws text on the card based on the provided element dictionary.
        Args:
            element (Dict[str, Any]): A dictionary containing text properties.
        """
        assert element.pop("type") == "text", "Element type must be 'text'"

        # print(f"DEBUG: {element["text"]=}")

        if pd.isna(element["text"]):
            element["text"] = " "

        # Convert font_path to a font object
        font_size = element.pop("font_size", 10)
        if font_path := element.pop("font_path", False):
            element["font"] = ImageFont.truetype(
                font_path,
                font_size,
                encoding="unic",
            )
        else:
            element["font"] = ImageFont.load_default(font_size)

        # Apply font_variant
        if font_variant := element.pop("font_variant", None):
            element["font"].set_variation_by_name(font_variant)

        # Split text according to the specified width
        if line_length := element.pop("width", False):
            element["text"] = get_wrapped_text(
                element["text"], element["font"], line_length
            )

        # Convert position and color to tuples
        if position := element.pop("position", [0, 0]):
            element["position"] = tuple(position)
        if color := element.pop("color", [0, 0, 0]):
            element["color"] = tuple(color)
        if stroke_color := element.pop("stroke_color", None):
            element["stroke_color"] = (
                tuple(stroke_color) if stroke_color is not None else stroke_color
            )

        # Apply anchor manually (because PIL does not support anchor for multiline text)
        original_pos = self._calculate_absolute_position(element)
        element["position"] = original_pos

        if "anchor" in element:
            bbox = self.draw.textbbox(
                xy=(0, 0),
                text=element.get("text"),
                font=element["font"],
                spacing=element.get("line_spacing", 4),
                align=element.get("align", "left"),
                direction=element.get("direction", None),
                features=element.get("features", None),
                language=element.get("language", None),
                stroke_width=element.get("stroke_width", 0),
                embedded_color=element.get("embedded_color", False),
            )
            anchor_point = apply_anchor(bbox, element.pop("anchor"))
            element["position"] = tuple(map(operator.sub, original_pos, anchor_point))

        # Unpack the element dictionary and draw the text
        self.draw.text(
            xy=element.get("position"),
            text=element.get("text"),
            fill=element.get("color", None),
            font=element["font"],
            spacing=element.get("line_spacing", 4),
            align=element.get("align", "left"),
            direction=element.get("direction", None),
            features=element.get("features", None),
            language=element.get("language", None),
            stroke_width=element.get("stroke_width", 0),
            stroke_fill=element.get("stroke_color", None),
            embedded_color=element.get("embedded_color", False),
        )

        # Store position if id is provided
        if "id" in element:
            bbox = self.draw.textbbox(
                xy=element.get("position"),
                text=element.get("text"),
                font=element["font"],
                spacing=element.get("line_spacing", 4),
                align=element.get("align", "left"),
                direction=element.get("direction", None),
                features=element.get("features", None),
                language=element.get("language", None),
                stroke_width=element.get("stroke_width", 0),
                embedded_color=element.get("embedded_color", False),
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
        return img.crop(crop_values)

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
            # pylint: disable=E1101
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        if direction == "vertical":
            # pylint: disable=E1101
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        return img

    def _draw_image(self, element: Dict[str, Any]):
        """
        Draws an image on the card based on the provided element dictionary.
        Args:
            element (Dict[str, Any]): A dictionary containing image properties.
        """
        # Ensure the element type is 'image'
        assert element.pop("type") == "image", "Element type must be 'image'"

        # Load the image from the specified path
        path = element["path"]
        img = Image.open(path)

        img = self._apply_image_filters(img, element.get("filters", {}))

        # Convert position to a tuple
        position = tuple(element.get("position", [0, 0]))

        # Apply anchor if specified (because PIL does not support anchor for images)
        position = self._calculate_absolute_position(element)
        if "anchor" in element:
            anchor_point = apply_anchor((img.width, img.height), element.pop("anchor"))
            position = tuple(map(operator.sub, position, anchor_point))

        # Paste the image onto the card at the specified position
        if img.mode == "RGBA":
            self.card.paste(img, position, mask=img)
        else:
            self.card.paste(img, position)

        # Store position if id is provided
        if "id" in element:
            self.element_positions[element["id"]] = (
                position[0],
                position[1],
                position[0] + img.width,
                position[1] + img.height,
            )

    def _draw_shape_circle(self, element: Dict[str, Any]):
        """
        Draws a circle on the card based on the provided element dictionary.
        Args:
            element (Dict[str, Any]): A dictionary containing circle properties.
        """
        assert element.pop("type") == "circle", "Element type must be 'circle'"

        radius = element["radius"]
        size = (radius * 2, radius * 2)

        # Calculate absolute position for the element's anchor
        absolute_pos = self._calculate_absolute_position(element)

        # Convert color and outline to a tuple if specified
        if "color" in element:
            element["fill"] = tuple(element["color"])
        if "outline_color" in element:
            element["outline_color"] = tuple(element["outline_color"])

        # Apply anchor if specified
        if "anchor" in element:
            # anchor_offset is the offset of the anchor from the top-left corner
            anchor_offset = apply_anchor(size, element.pop("anchor"))
            # top_left is the target position minus the anchor offset
            absolute_pos = tuple(map(operator.sub, absolute_pos, anchor_offset))

        # The center of the circle is the top-left position + radius
        center_pos = (absolute_pos[0] + radius, absolute_pos[1] + radius)

        # Create a temporary layer for proper alpha compositing
        layer = Image.new("RGBA", self.card.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")

        # Draw the circle on the temporary layer
        layer_draw.circle(
            center_pos,
            radius,
            fill=element.get("fill", None),
            outline=element.get("outline_color", None),
            width=element.get("outline_width", 1),
        )

        # Composite the layer onto the card
        self.card = Image.alpha_composite(self.card, layer)
        self.draw = ImageDraw.Draw(self.card, "RGBA")

        # Store position if id is provided
        if "id" in element:
            # The stored bbox is based on the top-left position
            self.element_positions[element["id"]] = (
                absolute_pos[0],
                absolute_pos[1],
                absolute_pos[0] + size[0],
                absolute_pos[1] + size[1],
            )

    def _draw_shape_ellipse(self, element: Dict[str, Any]):
        """
        Draws an ellipse on the card based on the provided element dictionary.
        Args:
            element (Dict[str, Any]): A dictionary containing ellipse properties.
        """
        assert element.pop("type") == "ellipse", "Element type must be 'ellipse'"

        # Get size
        size = element["size"]

        # Calculate absolute position
        position = self._calculate_absolute_position(element)

        # Convert color and outline to a tuple if specified
        if "color" in element:
            element["fill"] = tuple(element["color"])
        if "outline_color" in element:
            element["outline_color"] = tuple(element["outline_color"])

        # Apply anchor if specified
        if "anchor" in element:
            # For anchoring, we need an offset from the top-left corner.
            # We calculate this offset based on the element's size.
            anchor_offset = apply_anchor(size, element.pop("anchor"))
            # We subtract the offset from the calculated absolute position
            # to get the top-left corner of the bounding box.
            position = tuple(map(operator.sub, position, anchor_offset))

        # Compute bounding box from the final position and size
        bounding_box = (
            position[0],
            position[1],
            position[0] + size[0],
            position[1] + size[1],
        )

        # Create a temporary layer for proper alpha compositing
        layer = Image.new("RGBA", self.card.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")

        # Draw the ellipse on the temporary layer
        layer_draw.ellipse(
            bounding_box,
            fill=element.get("fill", None),
            outline=element.get("outline_color", None),
            width=element.get("outline_width", 1),
        )

        # Composite the layer onto the card
        self.card = Image.alpha_composite(self.card, layer)
        self.draw = ImageDraw.Draw(self.card, "RGBA")

        # Store position if id is provided
        if "id" in element:
            self.element_positions[element["id"]] = bounding_box

    def _draw_shape_polygon(self, element: Dict[str, Any]):
        """
        Draws a polygon on the card based on the provided element dictionary.
        Args:
            element (Dict[str, Any]): A dictionary containing polygon properties.
        """
        assert element.pop("type") == "polygon", "Element type must be 'polygon'"

        # Get points and convert to tuples
        points = element.get("points", [])
        if not points:
            return
        points = [tuple(p) for p in points]

        # Compute bounding box relative to (0,0)
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        bounding_box = (min_x, min_y, max_x, max_y)

        # Calculate absolute position for the element's anchor
        absolute_pos = self._calculate_absolute_position(element)

        # Convert color and outline to a tuple if specified
        if "color" in element:
            element["fill"] = tuple(element["color"])
        if "outline_color" in element:
            element["outline_color"] = tuple(element["outline_color"])

        # This will be the top-left offset for the points
        offset = absolute_pos

        # Apply anchor if specified
        if "anchor" in element:
            # anchor_point is the coordinate of the anchor within the relative bbox
            anchor_point = apply_anchor(bounding_box, element.pop("anchor"))
            # The final offset is the target position minus the anchor point's relative coord
            offset = tuple(map(operator.sub, absolute_pos, anchor_point))

        # Translate points by the final offset
        final_points = [(p[0] + offset[0], p[1] + offset[1]) for p in points]

        # Create a temporary layer for proper alpha compositing
        layer = Image.new("RGBA", self.card.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")

        # Draw the polygon on the temporary layer
        layer_draw.polygon(
            final_points,
            fill=element.get("fill", None),
            outline=element.get("outline_color", None),
            width=element.get("outline_width", 1),
        )

        # Composite the layer onto the card
        self.card = Image.alpha_composite(self.card, layer)
        self.draw = ImageDraw.Draw(self.card, "RGBA")

        # Store position if id is provided
        if "id" in element:
            # The stored bbox is the relative bbox translated by the offset
            self.element_positions[element["id"]] = (
                min_x + offset[0],
                min_y + offset[1],
                max_x + offset[0],
                max_y + offset[1],
            )

    def _draw_shape_regular_polygon(self, element: Dict[str, Any]):
        """
        Draws a regular polygon on the card based on the provided element dictionary.
        Args:
            element (Dict[str, Any]): A dictionary containing regular polygon properties.
        """
        assert (
            element.pop("type") == "regular-polygon"
        ), "Element type must be 'regular-polygon'"

        radius = element["radius"]
        size = (radius * 2, radius * 2)

        # Calculate absolute position for the element's anchor
        absolute_pos = self._calculate_absolute_position(element)

        # Convert color and outline to a tuple if specified
        if "color" in element:
            element["fill"] = tuple(element["color"])
        if "outline_color" in element:
            element["outline_color"] = tuple(element["outline_color"])

        # Apply anchor if specified
        if "anchor" in element:
            # anchor_offset is the offset of the anchor from the top-left corner
            anchor_offset = apply_anchor(size, element.pop("anchor"))
            # top_left is the target position minus the anchor offset
            absolute_pos = tuple(map(operator.sub, absolute_pos, anchor_offset))

        # The center of the polygon is the top-left position + radius
        center_pos = (absolute_pos[0] + radius, absolute_pos[1] + radius)

        # Create a temporary layer for proper alpha compositing
        layer = Image.new("RGBA", self.card.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")

        # Draw the regular polygon on the temporary layer
        layer_draw.regular_polygon(
            (center_pos[0], center_pos[1], radius),
            n_sides=element["sides"],
            rotation=element.get("rotation", 0),
            fill=element.get("fill", None),
            outline=element.get("outline_color", None),
            width=element.get("outline_width", 1),
        )

        # Composite the layer onto the card
        self.card = Image.alpha_composite(self.card, layer)
        self.draw = ImageDraw.Draw(self.card, "RGBA")

        # Store position if id is provided
        if "id" in element:
            # The stored bbox is based on the top-left position
            self.element_positions[element["id"]] = (
                absolute_pos[0],
                absolute_pos[1],
                absolute_pos[0] + size[0],
                absolute_pos[1] + size[1],
            )

    def _draw_shape_rectangle(self, element: Dict[str, Any]):
        """
        Draws a rectangle on the card based on the provided element dictionary.
        Args:
            element (Dict[str, Any]): A dictionary containing rectangle properties.
        """
        assert element.pop("type") == "rectangle", "Element type must be 'rectangle'"

        # print(f"DEBUG: {element=}")

        # Get size
        size = element["size"]

        # Calculate absolute position
        position = self._calculate_absolute_position(element)

        # Convert color, outline and corners to a tuple if specified
        if "color" in element:
            element["fill"] = tuple(element["color"])
        if "outline_color" in element:
            element["outline_color"] = tuple(element["outline_color"])
        if "corners" in element:
            element["corners"] = tuple(element["corners"])

        # Apply anchor if specified
        if "anchor" in element:
            # For anchoring, we need an offset from the top-left corner.
            # We calculate this offset based on the element's size.
            anchor_offset = apply_anchor(size, element.pop("anchor"))
            # We subtract the offset from the calculated absolute position
            # to get the top-left corner of the bounding box.
            position = tuple(map(operator.sub, position, anchor_offset))

        # Compute bounding box from the final position and size
        bounding_box = (
            position[0],
            position[1],
            position[0] + size[0],
            position[1] + size[1],
        )

        # print(f"DEBUG: Transformed {element=}")

        # Create a temporary layer for proper alpha compositing
        layer = Image.new("RGBA", self.card.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")

        # Draw the rectangle on the temporary layer
        layer_draw.rounded_rectangle(
            bounding_box,
            radius=element.get("corner_radius", 0),
            fill=element.get("fill", None),
            outline=element.get("outline_color", None),
            width=element.get("outline_width", 1),
            corners=element.get("corners", None),
        )

        # Composite the layer onto the card
        self.card = Image.alpha_composite(self.card, layer)
        self.draw = ImageDraw.Draw(self.card, "RGBA")

        # Store position if id is provided
        if "id" in element:
            self.element_positions[element["id"]] = bounding_box

    def build(self, output_path: Path):
        """
        Builds the card image by drawing all elements specified in the JSON.
        Args:
            output_path (Path): The path where the card image will be saved.
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
                draw_method(element)

        self.card.save(output_path)
        print(f"(✔) Card saved to {output_path}")
