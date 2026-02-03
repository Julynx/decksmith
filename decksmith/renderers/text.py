"""
This module contains the TextRenderer class for drawing text on cards.
"""

import operator
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from decksmith.logger import logger
from decksmith.utils import apply_anchor, get_wrapped_text


class TextRenderer:
    """
    A class to render text elements on a card.
    """

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path

    def render(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        calculate_pos_func,
        store_pos_func,
    ) -> Image.Image:
        """
        Draws text on the card.
        Args:
            card (Image.Image): The card image object.
            element (Dict[str, Any]): The text element specification.
            calculate_pos_func (callable): Function to calculate absolute position.
            store_pos_func (callable): Function to store element position.
        Returns:
            Image.Image: The updated card image.
        """
        assert element.pop("type") == "text", "Element type must be 'text'"

        element = self._prepare_text_element(element)

        original_pos = calculate_pos_func(element)
        element["position"] = original_pos

        layer = Image.new("RGBA", card.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, "RGBA")

        # Calculate anchor offset if needed
        if "anchor" in element:
            bbox = draw.textbbox(
                xy=(0, 0),
                text=element.get("text"),
                font=element["font"],
                spacing=element.get("line_spacing", 4),
                align=element.get("align", "left"),
            )
            anchor_point = apply_anchor(bbox, element.pop("anchor"))
            element["position"] = tuple(map(operator.sub, original_pos, anchor_point))

        # Draw text
        draw.text(
            xy=element.get("position"),
            text=element.get("text"),
            fill=element.get("color", None),
            font=element["font"],
            spacing=element.get("line_spacing", 4),
            align=element.get("align", "left"),
            stroke_width=element.get("stroke_width", 0),
            stroke_fill=element.get("stroke_color", None),
        )

        card = Image.alpha_composite(card, layer)

        # Store position
        if "id" in element:
            bbox = draw.textbbox(
                xy=element.get("position"),
                text=element.get("text"),
                font=element["font"],
                spacing=element.get("line_spacing", 4),
                align=element.get("align", "left"),
            )
            store_pos_func(element["id"], bbox)

        return card

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
                logger.error("Could not load font: %s. Using default.", font_path)
                element["font"] = ImageFont.load_default(font_size)
        else:
            element["font"] = ImageFont.load_default(font_size)

        if font_variant := element.pop("font_variant", None):
            try:
                element["font"].set_variation_by_name(font_variant)
            except AttributeError:
                logger.warning(
                    "Font variant '%s' not supported for this font.", font_variant
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
