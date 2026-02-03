"""
This module contains the ImageRenderer class for drawing images on cards.
"""

import operator
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

from decksmith.image_ops import ImageOps
from decksmith.logger import logger
from decksmith.utils import apply_anchor


class ImageRenderer:
    """
    A class to render image elements on a card.
    """

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path

    def render(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        calculate_pos_func,
        store_pos_func,
    ):
        """
        Draws an image on the card.
        Args:
            card (Image.Image): The card image object.
            element (Dict[str, Any]): The image element specification.
            calculate_pos_func (callable): Function to calculate absolute position.
            store_pos_func (callable): Function to store element position.
        """
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
            logger.error("Image not found: %s", path, traceback.format_exc())
            return

        img = ImageOps.apply_filters(img, element.get("filters", {}))

        position = calculate_pos_func(element)
        if "anchor" in element:
            anchor_point = apply_anchor((img.width, img.height), element.pop("anchor"))
            position = tuple(map(operator.sub, position, anchor_point))

        if img.mode == "RGBA":
            card.paste(img, position, mask=img)
        else:
            card.paste(img, position)

        if "id" in element:
            store_pos_func(
                element["id"],
                (
                    position[0],
                    position[1],
                    position[0] + img.width,
                    position[1] + img.height,
                ),
            )
