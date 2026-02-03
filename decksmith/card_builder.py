"""
This module contains the CardBuilder class,
which is used to create card images based on a YAML specification.
"""

import operator
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image, ImageDraw

from decksmith.logger import logger
from decksmith.renderers.image import ImageRenderer
from decksmith.renderers.shapes import ShapeRenderer
from decksmith.renderers.text import TextRenderer
from decksmith.utils import apply_anchor
from decksmith.validate import transform_card, validate_card


class CardBuilder:
    """
    A class to build a card image based on a YAML specification.
    Attributes:
        spec (Dict[str, Any]): The YAML specification for the card.
        card (Image.Image): The PIL Image object representing the card.
        draw (ImageDraw.ImageDraw): The PIL ImageDraw object for drawing on the card.
        element_positions (Dict[str, Tuple[int, int, int, int]]):
            A dictionary mapping element IDs to their bounding boxes.
    """

    def __init__(self, spec: Dict[str, Any], base_path: Optional[Path] = None):
        """
        Initializes the CardBuilder with a YAML specification.
        Args:
            spec (Dict[str, Any]): The YAML specification for the card.
            base_path (Optional[Path]): The base path for resolving relative file paths.
        """
        self.spec = spec
        self.base_path = base_path
        width = self.spec.get("width", 250)
        height = self.spec.get("height", 350)
        background_color = tuple(self.spec.get("background_color", (255, 255, 255, 0)))
        self.card: Image.Image = Image.new("RGBA", (width, height), background_color)
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.card, "RGBA")
        self.element_positions: Dict[str, Tuple[int, int, int, int]] = {}
        if "id" in spec:
            self.element_positions[self.spec["id"]] = (0, 0, width, height)

        self.text_renderer = TextRenderer(base_path)
        self.image_renderer = ImageRenderer(base_path)
        self.shape_renderer = ShapeRenderer()

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
        relative_identifier, anchor = element["relative_to"]
        if relative_identifier not in self.element_positions:
            raise ValueError(
                f"Element with id '{relative_identifier}' not found for relative positioning."
            )

        parent_bbox = self.element_positions[relative_identifier]
        anchor_point = apply_anchor(parent_bbox, anchor)

        offset = tuple(element.get("position", [0, 0]))
        return tuple(map(operator.add, anchor_point, offset))

    def _store_element_position(
        self, element_identifier: str, bbox: Tuple[int, int, int, int]
    ):
        """Stores the bounding box of an element."""
        self.element_positions[element_identifier] = bbox

    def render(self) -> Image.Image:
        """
        Renders the card image by drawing all elements specified in the YAML.
        Returns:
            Image.Image: The rendered card image.
        """
        self.spec = transform_card(self.spec)
        validate_card(self.spec)

        for element in self.spec.get("elements", []):
            element_type = element.get("type")
            try:
                if element_type == "text":
                    self.card = self.text_renderer.render(
                        self.card,
                        element,
                        self._calculate_absolute_position,
                        self._store_element_position,
                    )
                    self.draw = ImageDraw.Draw(self.card, "RGBA")
                elif element_type == "image":
                    self.image_renderer.render(
                        self.card,
                        element,
                        self._calculate_absolute_position,
                        self._store_element_position,
                    )
                elif element_type in [
                    "circle",
                    "ellipse",
                    "polygon",
                    "regular-polygon",
                    "rectangle",
                ]:
                    self.card = self.shape_renderer.render(
                        self.card,
                        element,
                        self._calculate_absolute_position,
                        self._store_element_position,
                    )
                    # Re-create draw object because shape renderer might have composited a new image
                    self.draw = ImageDraw.Draw(self.card, "RGBA")
            except Exception as e:
                logger.error("Error drawing element %s: %s", element_type, e)
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
        logger.info("(✔) Card saved to %s", output_path)
