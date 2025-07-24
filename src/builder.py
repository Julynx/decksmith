"""
This module contains the CardBuilder class,
which is used to create card images based on a JSON specification.
"""

import json
from PIL import Image, ImageDraw, ImageFont
from .utils import get_wrapped_text, apply_anchor
import operator


class CardBuilder:
    """
    A class to build a card image based on a JSON specification.
    Attributes:
        spec (dict): The JSON specification for the card.
        card (Image): The PIL Image object representing the card.
        draw (ImageDraw): The PIL ImageDraw object for drawing on the card.
    """

    def __init__(self, spec_path):
        """
        Initializes the CardBuilder with a JSON specification file.
        Args:
            spec_path (str): Path to the JSON specification file.
        """
        with open(spec_path, "r", encoding="utf-8") as f:
            self.spec = json.load(f)
        width = self.spec.get("width", 250)
        height = self.spec.get("height", 350)
        bg_color = tuple(self.spec.get("background_color", [255, 255, 255]))
        self.card = Image.new("RGB", (width, height), bg_color)
        self.draw = ImageDraw.Draw(self.card)
        self.element_positions = {}

    def _calculate_absolute_position(self, element: dict) -> tuple:
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
            raise ValueError(f"Element with id '{relative_id}' not found for relative positioning.")

        parent_bbox = self.element_positions[relative_id]
        anchor_point = apply_anchor(parent_bbox, anchor)

        offset = tuple(element.get("position", [0, 0]))
        return tuple(map(operator.add, anchor_point, offset))

    def _draw_text(self, element: dict):
        """
        Draws text on the card based on the provided element dictionary.
        Args:
            element (dict): A dictionary containing text properties such as
                            'text', 'font_path', 'font_size', 'position',
                            'color', and 'width'.
        """
        assert element.pop("type") == "text", "Element type must be 'text'"

        # Convert font_path to a font object
        if font_path := element.pop("font_path", False):
            font_size = element.pop("font_size", 12)
            element["font"] = ImageFont.truetype(font_path, font_size)
        else:
            element["font"] = ImageFont.load_default()

        # Split text according to the specified width
        if line_length := element.pop("width", False):
            element["text"] = get_wrapped_text(element["text"], element["font"], line_length)

        # Convert position and color to tuples
        if position := element.pop("position", False):
            element["position"] = tuple(position)
        if color := element.pop("color", False):
            element["fill"] = tuple(color)

        # Rename color to fill
        if "color" in element:
            element["fill"] = element.pop("color")

        # Apply anchor manually (because PIL does not support anchor for multiline text)
        original_pos = self._calculate_absolute_position(element)
        element["position"] = original_pos

        if "anchor" in element:
            bbox = self.draw.textbbox((0, 0), element["text"], font=element.get("font"))
            anchor_point = apply_anchor(bbox, element.pop("anchor"))
            element["position"] = tuple(map(operator.sub, original_pos, anchor_point))

        # Unpack the element dictionary and draw the text
        pos = element.pop("position")
        text = element.pop("text")
        self.draw.text(pos, text, **element)

        # Store position if id is provided
        if "id" in element:
            bbox = self.draw.textbbox(pos, text, font=element.get("font"))
            self.element_positions[element["id"]] = bbox

    def _draw_image(self, element):
        """
        Draws an image on the card based on the provided element dictionary.
        Args:
            element (dict): A dictionary containing image properties such as
                            'path', 'size', and 'position'.
        """
        # Ensure the element type is 'image'
        assert element.pop("type") == "image", "Element type must be 'image'"

        # Load the image from the specified path
        path = element["path"]
        img = Image.open(path)

        # Resize the image if a size is specified
        size = element.get("size")
        if size:
            img = img.resize(tuple(size))

        # Convert position to a tuple
        position = tuple(element.get("position", [0, 0]))

        # Apply anchor if specified (because PIL does not support anchor for images)
        position = self._calculate_absolute_position(element)
        if "anchor" in element:
            anchor_point = apply_anchor((img.width, img.height), element.pop("anchor"))
            position = tuple(map(operator.sub, position, anchor_point))

        # Paste the image onto the card at the specified position
        self.card.paste(img, position)

        # Store position if id is provided
        if "id" in element:
            self.element_positions[element["id"]] = (
                position[0],
                position[1],
                position[0] + img.width,
                position[1] + img.height,
            )

    def build(self, output_path):
        """
        Builds the card image by drawing all elements specified in the JSON.
        Args:
            output_path (str): The path where the card image will be saved.
        """
        for el in self.spec.get("elements", []):
            el_type = el["type"]
            if el_type == "text":
                self._draw_text(el)
            elif el_type == "image":
                self._draw_image(el)
            # extend with more element types here
        self.card.save(output_path)
        print(f"Card saved to {output_path}")


if __name__ == "__main__":
    builder = CardBuilder("data/card_spec.json")
    builder.build("output/card.png")
