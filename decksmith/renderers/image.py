"""
This module contains the ImageRenderer class for drawing images on cards.
"""

import operator
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

from decksmith.image_ops import ImageOps
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
        Returns:
            Image.Image: The updated card image.
        """
        assert element.pop("type") == "image", "Element type must be 'image'"

        path_str = element["path"]
        path = Path(path_str)

        if not path.is_absolute() and self.base_path:
            potential_path = self.base_path / path
            if potential_path.exists():
                path = potential_path

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        img = Image.open(path)

        img = ImageOps.apply_filters(img, element.get("filters", {}))

        position = calculate_pos_func(element)
        if "anchor" in element:
            anchor_point = apply_anchor((img.width, img.height), element.pop("anchor"))
            position = tuple(map(operator.sub, position, anchor_point))

        layer = Image.new("RGBA", card.size, (0, 0, 0, 0))
        if img.mode == "RGBA":
            layer.paste(img, position, mask=img)
        else:
            layer.paste(img, position)

        card = Image.alpha_composite(card, layer)

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

        return card
