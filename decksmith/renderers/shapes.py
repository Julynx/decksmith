"""
This module contains the ShapeRenderer class for drawing shapes on cards.
"""

import operator
from typing import Any, Dict

from PIL import Image, ImageDraw

from decksmith.utils import apply_anchor


class ShapeRenderer:
    """
    A class to render shape elements on a card.
    """

    def render(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        calculate_pos_func,
        store_pos_func,
    ) -> Image.Image:
        """
        Draws a shape on the card.
        Args:
            card (Image.Image): The card image object.
            element (Dict[str, Any]): The shape element specification.
            calculate_pos_func (callable): Function to calculate absolute position.
            store_pos_func (callable): Function to store element position.
        Returns:
            Image.Image: The updated card image.
        """
        element_type = element.get("type")
        draw_methods = {
            "circle": self._draw_shape_circle,
            "ellipse": self._draw_shape_ellipse,
            "polygon": self._draw_shape_polygon,
            "regular-polygon": self._draw_shape_regular_polygon,
            "rectangle": self._draw_shape_rectangle,
        }

        if draw_method := draw_methods.get(element_type):
            return draw_method(card, element, calculate_pos_func, store_pos_func)
        return card

    def _draw_shape_generic(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        draw_func,
        size_func,
        calculate_pos_func,
        store_pos_func,
    ) -> Image.Image:
        """Generic method to draw shapes."""
        size = size_func(element)
        absolute_pos = calculate_pos_func(element)

        if "color" in element:
            element["fill"] = tuple(element["color"])
        if "outline_color" in element:
            element["outline_color"] = tuple(element["outline_color"])

        if "anchor" in element:
            anchor_offset = apply_anchor(size, element.pop("anchor"))
            absolute_pos = tuple(map(operator.sub, absolute_pos, anchor_offset))

        layer = Image.new("RGBA", card.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer, "RGBA")

        draw_func(layer_draw, absolute_pos, element)

        card = Image.alpha_composite(card, layer)

        if "id" in element:
            store_pos_func(
                element["id"],
                (
                    absolute_pos[0],
                    absolute_pos[1],
                    absolute_pos[0] + size[0],
                    absolute_pos[1] + size[1],
                ),
            )
        return card

    def _draw_shape_circle(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        calculate_pos_func,
        store_pos_func,
    ) -> Image.Image:
        assert element.pop("type") == "circle", "Element type must be 'circle'"
        radius = element["radius"]

        def draw(layer_draw, pos, element):
            center_pos = (pos[0] + radius, pos[1] + radius)
            layer_draw.circle(
                center_pos,
                radius,
                fill=element.get("fill", None),
                outline=element.get("outline_color", None),
                width=element.get("outline_width", 1),
            )

        return self._draw_shape_generic(
            card,
            element,
            draw,
            lambda _: (radius * 2, radius * 2),
            calculate_pos_func,
            store_pos_func,
        )

    def _draw_shape_ellipse(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        calculate_pos_func,
        store_pos_func,
    ) -> Image.Image:
        assert element.pop("type") == "ellipse", "Element type must be 'ellipse'"
        size = element["size"]

        def draw(layer_draw, pos, element):
            bbox = (pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
            layer_draw.ellipse(
                bbox,
                fill=element.get("fill", None),
                outline=element.get("outline_color", None),
                width=element.get("outline_width", 1),
            )

        return self._draw_shape_generic(
            card, element, draw, lambda _: size, calculate_pos_func, store_pos_func
        )

    def _draw_shape_polygon(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        calculate_pos_func,
        store_pos_func,
    ) -> Image.Image:
        assert element.pop("type") == "polygon", "Element type must be 'polygon'"
        points = [tuple(point) for point in element.get("points", [])]
        if not points:
            return card

        min_horizontal = min(point[0] for point in points)
        max_horizontal = max(point[0] for point in points)
        min_vertical = min(point[1] for point in points)
        max_vertical = max(point[1] for point in points)
        bbox_size = (max_horizontal - min_horizontal, max_vertical - min_vertical)

        def draw(layer_draw, pos, element):
            # pos is the top-left of the bounding box
            # We need to shift points so that (min_horizontal, min_vertical) aligns with pos
            offset_horizontal = pos[0] - min_horizontal
            offset_vertical = pos[1] - min_vertical
            final_points = [
                (point[0] + offset_horizontal, point[1] + offset_vertical)
                for point in points
            ]

            layer_draw.polygon(
                final_points,
                fill=element.get("fill", None),
                outline=element.get("outline_color", None),
                width=element.get("outline_width", 1),
            )

        return self._draw_shape_generic(
            card, element, draw, lambda _: bbox_size, calculate_pos_func, store_pos_func
        )

    def _draw_shape_regular_polygon(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        calculate_pos_func,
        store_pos_func,
    ) -> Image.Image:
        assert element.pop("type") == "regular-polygon", (
            "Element type must be 'regular-polygon'"
        )
        radius = element["radius"]

        def draw(layer_draw, pos, element):
            center_pos = (pos[0] + radius, pos[1] + radius)
            layer_draw.regular_polygon(
                (center_pos[0], center_pos[1], radius),
                n_sides=element["sides"],
                rotation=element.get("rotation", 0),
                fill=element.get("fill", None),
                outline=element.get("outline_color", None),
                width=element.get("outline_width", 1),
            )

        return self._draw_shape_generic(
            card,
            element,
            draw,
            lambda _: (radius * 2, radius * 2),
            calculate_pos_func,
            store_pos_func,
        )

    def _draw_shape_rectangle(
        self,
        card: Image.Image,
        element: Dict[str, Any],
        calculate_pos_func,
        store_pos_func,
    ) -> Image.Image:
        assert element.pop("type") == "rectangle", "Element type must be 'rectangle'"
        size = element["size"]
        if "corners" in element:
            element["corners"] = tuple(element["corners"])

        def draw(layer_draw, pos, element):
            bbox = (pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
            layer_draw.rounded_rectangle(
                bbox,
                radius=element.get("corner_radius", 0),
                fill=element.get("fill", None),
                outline=element.get("outline_color", None),
                width=element.get("outline_width", 1),
                corners=element.get("corners", None),
            )

        return self._draw_shape_generic(
            card, element, draw, lambda _: size, calculate_pos_func, store_pos_func
        )
